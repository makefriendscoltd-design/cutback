import { ipcMain, BrowserWindow, dialog, shell } from 'electron';
import { execSync } from 'child_process';
import path from 'path';
import { JobManager } from '@cutback/core';
import { presetLoader } from '@cutback/preset-manager';
import { saveEDL, saveSRT, installToCapCut, findCapCutDraftsDir, capCutAutomation, renderVideo } from '@cutback/capcut-controller';
import { IPC_CHANNELS, createLogger } from '@cutback/shared';
import { runPreflight, getHealth } from './preflight';
import { checkUpdatesManually, installNow, getLastUpdateStatus } from './updater';

const logger = createLogger('ipc');

const jobManager = new JobManager();

/**
 * 모든 IPC 핸들러 등록
 */
export function registerIPCHandlers(
  getMainWindow: () => BrowserWindow | null
): void {
  // ===== Job Management =====

  ipcMain.handle(IPC_CHANNELS.JOB_CREATE, async (_event, params) => {
    try {
      const job = await jobManager.createJob(params);

      // 비동기로 파이프라인 실행 시작
      jobManager.processJob(job.id, (stage, progress, detail) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
          jobId: job.id,
          stage,
          progress,
          detail,
        });
      }).then((results) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_COMPLETED, {
          jobId: job.id,
          results,
        });
      }).catch((err) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_ERROR, {
          jobId: job.id,
          error: (err as Error).message,
        });
      });

      return { success: true, job };
    } catch (err) {
      logger.error('Job creation failed', { error: (err as Error).message });
      return { success: false, error: (err as Error).message };
    }
  });

  ipcMain.handle(IPC_CHANNELS.JOB_LIST, async () => {
    return jobManager.listJobs();
  });

  ipcMain.handle(IPC_CHANNELS.JOB_GET, async (_event, jobId: string) => {
    const job = jobManager.getJob(jobId);
    const results = jobManager.getJobResults(jobId);
    return { job, results };
  });

  ipcMain.handle(IPC_CHANNELS.JOB_CANCEL, async (_event, jobId: string) => {
    jobManager.cancelJob(jobId);
    return { success: true };
  });

  // ===== Cut Decision Toggle =====

  ipcMain.handle(
    'cut:toggle',
    async (_event, { cutId, enabled }: { cutId: string; enabled: boolean }) => {
      jobManager.toggleCutDecision(cutId, enabled);
      return { success: true };
    }
  );

  // ===== Preset Management =====

  ipcMain.handle(IPC_CHANNELS.PRESET_LIST, async () => {
    return presetLoader.listAll();
  });

  ipcMain.handle(
    IPC_CHANNELS.PRESET_LOAD,
    async (_event, presetId: string) => {
      return presetLoader.load(presetId);
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.PRESET_SAVE,
    async (_event, { id, preset }) => {
      await presetLoader.save(id, preset);
      return { success: true };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.PRESET_DELETE,
    async (_event, presetId: string) => {
      await presetLoader.delete(presetId);
      return { success: true };
    }
  );

  // ===== File Dialog =====

  ipcMain.handle('dialog:openVideo', async () => {
    const result = await dialog.showOpenDialog({
      title: '영상 파일 선택',
      filters: [
        {
          name: '영상 파일',
          extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv'],
        },
        { name: '모든 파일', extensions: ['*'] },
      ],
      properties: ['openFile'],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  // ===== Export =====

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_EDL,
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: 'EDL 파일 저장',
        defaultPath: 'cutback-export.edl',
        filters: [{ name: 'EDL', extensions: ['edl'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      await saveEDL(
        results.cutDecisions,
        results.statistics.original_duration,
        saveResult.filePath
      );

      return { success: true, path: saveResult.filePath };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_SRT,
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: 'SRT 자막 파일 저장',
        defaultPath: 'cutback-captions.srt',
        filters: [{ name: 'SRT Subtitles', extensions: ['srt'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      await saveSRT(results.captions, saveResult.filePath);

      return { success: true, path: saveResult.filePath };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_CAPCUT,
    async (_event, { jobId }: { jobId: string }) => {
      const job = jobManager.getJob(jobId);
      const results = jobManager.getJobResults(jobId);
      if (!results || !job) return { success: false, error: 'No results found' };

      // 프리셋에서 canvas 정보 로드
      let width = 1920;
      let height = 1080;
      try {
        const preset = await presetLoader.load(job.presetId);
        if (preset.canvas) {
          width = preset.canvas.width;
          height = preset.canvas.height;
        }
      } catch { /* 프리셋 로드 실패 시 기본값 사용 */ }

      try {
        // CapCut 프로젝트 폴더에 직접 설치
        const { projectDir } = await installToCapCut(
          results.cutDecisions,
          results.captions,
          {
            videoPath: job.videoPath,
            videoDuration: Math.round(results.statistics.original_duration * 1_000_000),
            width,
            height,
          }
        );

        // CapCut이 실행 중이 아니면 자동 실행 시도
        if (!capCutAutomation.isRunning()) {
          try {
            const capCutExe = findCapCutExe();
            if (capCutExe) {
              execSync(`start "" "${capCutExe}"`, { shell: 'cmd.exe', timeout: 5000 });
              logger.info('CapCut launched', { exe: capCutExe });
            }
          } catch (launchErr) {
            logger.warn('CapCut auto-launch failed', { error: (launchErr as Error).message });
          }
        }

        return { success: true, path: projectDir, message: 'CapCut 프로젝트가 생성되었습니다. CapCut을 열면 프로젝트 목록에 나타납니다.' };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Video Render (FFmpeg) =====

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_VIDEO,
    async (_event, { jobId }: { jobId: string }) => {
      const job = jobManager.getJob(jobId);
      const results = jobManager.getJobResults(jobId);
      if (!results || !job) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: '편집 영상 저장',
        defaultPath: path.basename(job.videoPath, path.extname(job.videoPath)) + '_edited.mp4',
        filters: [{ name: 'MP4 Video', extensions: ['mp4'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      try {
        await renderVideo(
          results.cutDecisions,
          {
            videoPath: job.videoPath,
            outputPath: saveResult.filePath,
            videoDuration: results.statistics.original_duration,
          },
          (percent: number, detail: string) => {
            getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
              jobId,
              stage: 'rendering',
              progress: percent,
              detail,
            });
          }
        );
        // 렌더링 완료 후 파일 탐색기에서 보기
        shell.showItemInFolder(saveResult.filePath);
        return { success: true, path: saveResult.filePath };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== CapCut Automation =====

  ipcMain.handle('capcut:status', async () => {
    return {
      running: capCutAutomation.isRunning(),
      projectsPath: capCutAutomation.getProjectsPath(),
    };
  });

  ipcMain.handle(
    'capcut:apply',
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      try {
        const result = await capCutAutomation.applyCuts(
          results.cutDecisions,
          (current, total) => {
            getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
              jobId,
              stage: 'capcut_apply',
              progress: Math.round((current / total) * 100),
              detail: `CapCut 적용 중... (${current}/${total})`,
            });
          }
        );
        return { success: true, ...result };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Health / Preflight =====

  ipcMain.handle(IPC_CHANNELS.HEALTH_GET, async (_event, opts?: { force?: boolean }) => {
    if (opts?.force) {
      return runPreflight(true);
    }
    return getHealth();
  });

  // ===== Auto Update =====

  ipcMain.handle(IPC_CHANNELS.UPDATE_CHECK, async () => {
    return checkUpdatesManually();
  });

  ipcMain.handle(IPC_CHANNELS.UPDATE_STATUS, async () => {
    return getLastUpdateStatus();
  });

  ipcMain.handle(IPC_CHANNELS.UPDATE_INSTALL, async () => {
    installNow();
    return { success: true };
  });

  logger.info('All IPC handlers registered');
}

/**
 * CapCut Desktop 실행 파일 경로 탐색
 */
function findCapCutExe(): string | null {
  const localAppData = process.env.LOCALAPPDATA || '';
  const programFiles = process.env.ProgramFiles || 'C:\\Program Files';
  const userProfile = process.env.USERPROFILE || '';

  const possiblePaths = [
    // LOCALAPPDATA 직접 설치 (가장 흔함)
    localAppData ? path.join(localAppData, 'CapCut', 'CapCut.exe') : '',
    localAppData ? path.join(localAppData, 'CapCut', 'Apps', 'CapCut.exe') : '',
    localAppData ? path.join(localAppData, 'Programs', 'CapCut', 'CapCut.exe') : '',
    // Program Files
    path.join(programFiles, 'CapCut', 'CapCut.exe'),
    // JianyingPro (중국판)
    path.join(programFiles, 'JianyingPro', 'JianyingPro.exe'),
    // USERPROFILE 폴백
    userProfile ? path.join(userProfile, 'AppData', 'Local', 'CapCut', 'CapCut.exe') : '',
  ].filter(Boolean);

  for (const p of possiblePaths) {
    try {
      require('fs').accessSync(p);
      return p;
    } catch {
      continue;
    }
  }
  return null;
}
