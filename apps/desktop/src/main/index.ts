import { app, BrowserWindow, protocol } from 'electron';
import { createReadStream } from 'fs';
import { stat } from 'fs/promises';
import { Readable } from 'stream';
import path from 'path';
import { initDatabase, closeDatabase, initCalibrationRepository } from '@cutback/core';
import { createLogger } from '@cutback/shared';
import { presetLoader } from '@cutback/preset-manager';
import { setFontsDir } from '@cutback/shorts-composer';
import { registerIPCHandlers } from './ipc-handlers';
import { PythonServiceManager } from './python-service';
import { runPreflight } from './preflight';
import { initUpdater } from './updater';

const logger = createLogger('main');

let mainWindow: BrowserWindow | null = null;
let pythonManager: PythonServiceManager | null = null;

function isDev(): boolean {
  return process.env.NODE_ENV === 'development' || !app.isPackaged;
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Cutback - AI 편집 어시스턴트',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev()) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'right' });
  } else {
    mainWindow.loadFile(
      path.join(__dirname, '..', 'renderer', 'index.html')
    );
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  logger.info('Main window created', { isDev: isDev() });
}

async function initialize(): Promise<void> {
  logger.info('Initializing Cutback...');

  // 1. DB 초기화
  const dbPath = path.join(app.getPath('userData'), 'cutback.db');
  initDatabase(dbPath);
  logger.info('Database ready', { path: dbPath });

  // 1.1. Calibration repository 초기화 (preset learning)
  initCalibrationRepository(app.getPath('userData'));
  logger.info('Calibration repository ready');

  // 1.5. 프리셋 디렉토리 설정
  const presetsDir = isDev()
    ? path.join(__dirname, '..', '..', '..', '..', 'presets')
    : path.join(process.resourcesPath, 'presets');
  presetLoader.setBaseDir(presetsDir);

  // 1.6. Mode C 자막 폰트 디렉토리 설정 (esbuild 번들이라 __dirname 기반 기본값이 안 맞음)
  const fontsDir = isDev()
    ? path.join(__dirname, '..', '..', '..', '..', 'packages', 'shorts-composer', 'assets', 'fonts')
    : path.join(process.resourcesPath, 'fonts');
  setFontsDir(fontsDir);

  // 1.7. Preflight 환경 점검 (실패 시에도 boot 는 계속 - UI 가 사용자에게 안내)
  // 다른 PC 에서 ffmpeg/python venv 가 없으면 여기서 즉시 발견된다.
  try {
    const report = runPreflight(true);
    logger.info('Preflight complete', {
      overall: report.overall,
      failed: report.checks.filter((c) => c.status === 'fail').map((c) => c.id),
      warned: report.checks.filter((c) => c.status === 'warn').map((c) => c.id),
    });
  } catch (err) {
    logger.warn('Preflight crashed (continuing)', {
      error: (err as Error).message,
    });
  }

  // 2. Python STT 서비스 시작
  pythonManager = new PythonServiceManager();
  try {
    await pythonManager.start();
    logger.info('Python STT service started');
  } catch (err) {
    logger.warn('Python STT service failed to start (will retry on demand)', {
      error: (err as Error).message,
    });
  }

  // 3. IPC 핸들러 등록 (getter 함수로 전달 - mainWindow는 나중에 생성됨)
  registerIPCHandlers(() => mainWindow);
  logger.info('IPC handlers registered');
}

// --- App lifecycle ---

/**
 * 로컬 영상 파일을 video 태그에서 재생하기 위한 custom protocol.
 * Electron 의 webSecurity 가 file:// 직접 접근을 차단하기 때문에,
 * cutback-media://<absolute-path> 형태로 요청 → main 이 해당 파일을 stream 으로 응답.
 *
 * 사용 예 (renderer): `<video src="cutback-media:///D:/videos/foo.mp4" />`
 *
 * 보안 메모: 임의 파일 시스템 접근을 허용하므로, 프로덕션에선 path 화이트리스트
 * (e.g. job 의 videoPath/assetPaths 만) 를 거치는 게 안전. 지금은 dev 단순화.
 */
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'cutback-media',
    privileges: {
      standard: true,
      secure: true,
      supportFetchAPI: true,
      stream: true,
      bypassCSP: true,
    },
  },
]);

app.on('ready', async () => {
  // protocol.handle 은 ready 후에만 등록 가능
  protocol.handle('cutback-media', async (request) => {
    const rangeHeader = request.headers.get('range');
    logger.info('cutback-media request', {
      url: request.url,
      method: request.method,
      range: rangeHeader,
    });
    try {
      const url = new URL(request.url);
      const encoded = url.pathname.replace(/^\//, '');
      const filePath = decodeURIComponent(encoded);

      const fileStat = await stat(filePath);
      const fileSize = fileStat.size;
      const ext = filePath.toLowerCase().split('.').pop() ?? '';
      const contentType =
        ext === 'mp4'
          ? 'video/mp4'
          : ext === 'mov'
          ? 'video/quicktime'
          : ext === 'webm'
          ? 'video/webm'
          : ext === 'mkv'
          ? 'video/x-matroska'
          : ext === 'mp3'
          ? 'audio/mpeg'
          : ext === 'wav'
          ? 'audio/wav'
          : 'application/octet-stream';

      // Range 헤더 처리 (video seeking 필수)
      if (rangeHeader) {
        const match = rangeHeader.match(/bytes=(\d*)-(\d*)/);
        if (match) {
          const start = match[1] ? parseInt(match[1], 10) : 0;
          const end = match[2] ? parseInt(match[2], 10) : fileSize - 1;
          const chunkSize = end - start + 1;
          const stream = createReadStream(filePath, { start, end });
          logger.info('cutback-media 206', {
            filePath,
            range: `${start}-${end}/${fileSize}`,
            chunkSize,
          });
          return new Response(Readable.toWeb(stream) as ReadableStream, {
            status: 206,
            headers: {
              'Content-Range': `bytes ${start}-${end}/${fileSize}`,
              'Accept-Ranges': 'bytes',
              'Content-Length': String(chunkSize),
              'Content-Type': contentType,
            },
          });
        }
      }

      // 전체 파일 응답
      const stream = createReadStream(filePath);
      logger.info('cutback-media 200', { filePath, fileSize, contentType });
      return new Response(Readable.toWeb(stream) as ReadableStream, {
        status: 200,
        headers: {
          'Content-Length': String(fileSize),
          'Content-Type': contentType,
          'Accept-Ranges': 'bytes',
        },
      });
    } catch (err) {
      logger.error('cutback-media protocol error', {
        url: request.url,
        error: (err as Error).message,
        stack: (err as Error).stack,
      });
      return new Response('Not found', { status: 404 });
    }
  });

  await initialize();
  createWindow();
  // 4. Auto-updater (packaged 모드에서만 동작 - dev 모드는 자동 skip)
  initUpdater(() => mainWindow);
  logger.info('Cutback ready');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  logger.info('Shutting down...');
  pythonManager?.stop();
  closeDatabase();
});

// 미처리 예외 잡기
process.on('uncaughtException', (err) => {
  logger.error('Uncaught exception', { error: err.message, stack: err.stack });
});

process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled rejection', { reason: String(reason) });
});
