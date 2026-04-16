/**
 * Auto-update via electron-updater + GitHub Releases.
 *
 * 동작:
 *   1) 앱 부팅 5초 후 자동으로 업데이트 확인
 *   2) 새 버전 발견 → 백그라운드 다운로드
 *   3) 다운로드 완료 → renderer 에 알림 (UPDATE_STATUS)
 *   4) 사용자가 "지금 재시작" 클릭 → quitAndInstall()
 *   5) 또는 다음 앱 종료 시 자동 적용
 *
 * Renderer 에서:
 *   const off = window.api.onUpdateStatus((s) => { ... })
 *   await window.api.checkUpdates()       // 수동 확인
 *   await window.api.installUpdate()      // 다운로드 완료 후 재시작
 *
 * Dev 모드 (`pnpm dev`) 에서는 동작하지 않음 (electron-updater 자체 가드).
 */

import { app, BrowserWindow } from 'electron';
import { autoUpdater } from 'electron-updater';
import { createLogger } from '@cutback/shared';

const logger = createLogger('updater');

export type UpdateStatus =
  | { phase: 'idle' }
  | { phase: 'checking' }
  | { phase: 'available'; version: string; releaseNotes?: string }
  | { phase: 'not-available'; version: string }
  | { phase: 'downloading'; percent: number; transferred: number; total: number }
  | { phase: 'downloaded'; version: string }
  | { phase: 'error'; message: string };

let lastStatus: UpdateStatus = { phase: 'idle' };
let initialized = false;

function emit(getMainWindow: () => BrowserWindow | null, status: UpdateStatus): void {
  lastStatus = status;
  const win = getMainWindow();
  if (win && !win.isDestroyed()) {
    win.webContents.send('update:status', status);
  }
  logger.info('Update status', status);
}

export function initUpdater(getMainWindow: () => BrowserWindow | null): void {
  if (initialized) return;
  initialized = true;

  // Dev 모드 / 패키징 안 된 빌드는 skip (electron-updater 가 어차피 throw)
  if (!app.isPackaged) {
    logger.info('Skipping auto-updater in dev mode');
    return;
  }

  // 자동 다운로드: 사용자 동의 없이 백그라운드로 받음 (소형 앱이라 OK).
  // 설치는 명시적으로 quitAndInstall() 호출했을 때만.
  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;
  autoUpdater.allowPrerelease = false;

  autoUpdater.on('checking-for-update', () => {
    emit(getMainWindow, { phase: 'checking' });
  });

  autoUpdater.on('update-available', (info) => {
    emit(getMainWindow, {
      phase: 'available',
      version: info.version,
      releaseNotes:
        typeof info.releaseNotes === 'string' ? info.releaseNotes : undefined,
    });
  });

  autoUpdater.on('update-not-available', (info) => {
    emit(getMainWindow, { phase: 'not-available', version: info.version });
  });

  autoUpdater.on('download-progress', (p) => {
    emit(getMainWindow, {
      phase: 'downloading',
      percent: Math.round(p.percent),
      transferred: p.transferred,
      total: p.total,
    });
  });

  autoUpdater.on('update-downloaded', (info) => {
    emit(getMainWindow, { phase: 'downloaded', version: info.version });
  });

  autoUpdater.on('error', (err) => {
    emit(getMainWindow, { phase: 'error', message: err.message });
  });

  // 부팅 5초 후 자동 확인 (창 생성/IPC 등록 끝난 다음)
  setTimeout(() => {
    autoUpdater.checkForUpdates().catch((e) => {
      logger.warn('Initial update check failed', { error: (e as Error).message });
    });
  }, 5000);

  // 1시간마다 자동 재확인 (장시간 켜둔 사용자도 받음)
  setInterval(
    () => {
      autoUpdater.checkForUpdates().catch((e) => {
        logger.debug('Periodic update check failed', { error: (e as Error).message });
      });
    },
    60 * 60 * 1000
  );

  logger.info('Auto-updater initialized', {
    feedURL: autoUpdater.getFeedURL(),
  });
}

/** 수동 확인 (renderer 의 "업데이트 확인" 버튼) */
export async function checkUpdatesManually(): Promise<UpdateStatus> {
  if (!app.isPackaged) {
    return { phase: 'not-available', version: app.getVersion() };
  }
  try {
    await autoUpdater.checkForUpdates();
    return lastStatus;
  } catch (err) {
    const msg = (err as Error).message;
    return { phase: 'error', message: msg };
  }
}

/** 다운로드 완료 후 즉시 재시작 + 설치 */
export function installNow(): void {
  if (!app.isPackaged) return;
  // quitAndInstall(isSilent=true, isForceRunAfter=true)
  // - isSilent: NSIS UI 안 띄우고 백그라운드 설치
  // - isForceRunAfter: 설치 후 앱 자동 재실행
  autoUpdater.quitAndInstall(true, true);
}

export function getLastUpdateStatus(): UpdateStatus {
  return lastStatus;
}
