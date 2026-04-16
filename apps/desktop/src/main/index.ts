import { app, BrowserWindow } from 'electron';
import path from 'path';
import { initDatabase, closeDatabase } from '@cutback/core';
import { createLogger } from '@cutback/shared';
import { presetLoader } from '@cutback/preset-manager';
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

  // 1.5. 프리셋 디렉토리 설정
  const presetsDir = isDev()
    ? path.join(__dirname, '..', '..', '..', '..', 'presets')
    : path.join(process.resourcesPath, 'presets');
  presetLoader.setBaseDir(presetsDir);

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

app.on('ready', async () => {
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
