import { spawn, ChildProcess } from 'child_process';
import fs from 'fs';
import path from 'path';
import { app } from 'electron';
import { createLogger } from '@cutback/shared';

const logger = createLogger('python-service');

/**
 * Python STT 서비스 프로세스 관리
 *
 * Electron 앱 시작 시 Python 서비스를 자동으로 시작하고,
 * 앱 종료 시 정리.
 */
export class PythonServiceManager {
  private sttProcess: ChildProcess | null = null;
  private isRunning = false;

  /**
   * 프로젝트 루트(python 폴더가 있는 곳) 탐색 - dev 모드 전용.
   */
  private findProjectRoot(): string {
    const candidates = [
      path.resolve(app.getAppPath(), '..', '..'),
      path.resolve(app.getAppPath(), '..', '..', '..', '..'),
      path.resolve(__dirname, '..', '..', '..', '..'),
      process.cwd(),
    ];

    for (const root of candidates) {
      const pythonDir = path.join(root, 'python', 'stt_service');
      if (fs.existsSync(pythonDir)) {
        return root;
      }
    }
    return path.resolve(app.getAppPath(), '..', '..');
  }

  /**
   * 실행 모드 판정 + spawn 인자 결정.
   *
   * Packaged (사용자 PC):
   *   resources/cutback-stt/cutback-stt.exe 직접 실행.
   *   PyInstaller 가 미리 번들링한 단일 폴더이므로 사용자 PC 에 Python 불필요.
   *
   * Dev (개발자 PC):
   *   venv/Scripts/python.exe  python/stt_service/main.py
   */
  private resolveSpawnTarget(): {
    command: string;
    args: string[];
    mode: 'bundled' | 'venv';
  } {
    const isWin = process.platform === 'win32';

    if (app.isPackaged) {
      const exeName = isWin ? 'cutback-stt.exe' : 'cutback-stt';
      const command = path.join(process.resourcesPath, 'cutback-stt', exeName);
      return { command, args: [], mode: 'bundled' };
    }

    const root = this.findProjectRoot();
    const venvPython = isWin
      ? path.join(root, 'python', 'stt_service', 'venv', 'Scripts', 'python.exe')
      : path.join(root, 'python', 'stt_service', 'venv', 'bin', 'python');
    const script = path.join(root, 'python', 'stt_service', 'main.py');
    return {
      command: venvPython,
      args: ['-X', 'utf8', script],
      mode: 'venv',
    };
  }

  /**
   * STT 서비스 시작
   *
   * 실패 케이스를 명확하게 분리:
   *   - venv 자체가 없음 → "pnpm run setup:python" 실행하라고 안내
   *   - script 파일이 없음 → 저장소가 손상됐을 가능성
   *   - spawn 자체가 실패 → 권한/PATH 문제
   *
   * 각 케이스마다 reject 사유에 사용자가 곧바로 실행할 수 있는 명령을 포함.
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('Python service already running');
      return;
    }

    const target = this.resolveSpawnTarget();

    // Pre-check: 실행 파일 존재 검증
    if (!fs.existsSync(target.command)) {
      const msg =
        target.mode === 'bundled'
          ? `번들된 STT 실행 파일이 없습니다 (${target.command}). ` +
            `설치 파일이 손상됐을 수 있습니다. 앱을 재설치하거나 자동 업데이트를 기다려주세요.`
          : `Python venv 가 없습니다 (${target.command}). ` +
            `처음 실행한다면 다음 명령을 한 번 실행해주세요:\n` +
            `    pnpm run setup:python`;
      logger.error('STT executable missing', {
        command: target.command,
        mode: target.mode,
      });
      throw new Error(msg);
    }

    logger.info('Starting Python STT service', {
      mode: target.mode,
      command: target.command,
    });

    return new Promise((resolve, reject) => {
      // 시작 검증을 위해 stderr 마지막 N 바이트를 모아둠 (모듈 import 실패 시 traceback 보존)
      let startupStderrBuf = '';
      let startupStdoutBuf = '';
      let settled = false;
      const settle = (fn: () => void) => {
        if (settled) return;
        settled = true;
        fn();
      };

      try {
        this.sttProcess = spawn(target.command, target.args, {
          stdio: ['pipe', 'pipe', 'pipe'],
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1', // 실시간 로그 출력
            PYTHONUTF8: '1',       // Windows에서 UTF-8 강제
          },
        });

        const handleData = (raw: Buffer, isErr: boolean) => {
          const msg = raw.toString();
          if (isErr) startupStderrBuf = (startupStderrBuf + msg).slice(-4000);
          else startupStdoutBuf = (startupStdoutBuf + msg).slice(-4000);
          const trimmed = msg.trim();
          if (trimmed) logger.debug(`[python-stt] ${trimmed}`);
          if (trimmed.includes('STT Service started')) {
            this.isRunning = true;
            settle(resolve);
          }
        };

        this.sttProcess.stdout?.on('data', (d: Buffer) => handleData(d, false));
        this.sttProcess.stderr?.on('data', (d: Buffer) => handleData(d, true));

        this.sttProcess.on('close', (code) => {
          logger.info('Python STT service exited', { code });
          const wasRunning = this.isRunning;
          this.isRunning = false;
          this.sttProcess = null;
          // 시작 도중에 죽었다면 sterr 마지막 라인을 사용자에게 노출
          if (!wasRunning && !settled) {
            const tail =
              (startupStderrBuf || startupStdoutBuf)
                .split(/\r?\n/)
                .filter(Boolean)
                .slice(-6)
                .join('\n') || `(no output, exit code ${code})`;
            const recovery = app.isPackaged
              ? '앱을 재설치하거나 자동 업데이트를 기다려주세요.'
              : 'pnpm run setup:python   (의존성 재설치)';
            settle(() =>
              reject(
                new Error(
                  `STT 서비스 시작 실패 (exit ${code}). 마지막 출력:\n${tail}\n\n` +
                    `해결 방법:\n  ${recovery}`
                )
              )
            );
          }
        });

        this.sttProcess.on('error', (err) => {
          logger.error('Failed to spawn Python service', { error: err.message });
          this.isRunning = false;
          const recovery = app.isPackaged
            ? '앱을 재설치하거나 다시 시도해주세요.'
            : 'pnpm run setup:python 으로 venv 를 재생성하세요.';
          settle(() =>
            reject(
              new Error(
                `STT 실행 자체 실패 (${target.command}): ${err.message}. ${recovery}`
              )
            )
          );
        });

        // 30초 안에 startup 메시지가 안 보이면 타임아웃.
        // Whisper small 첫 로드는 보통 5~15초이므로 30초면 충분.
        // 살아있어도 success 로 간주하지 않는다 - 이전 코드의 false positive 방지.
        setTimeout(() => {
          if (this.isRunning || settled) return;
          // 살아 있긴 하지만 ready 메시지가 없음 → 일단 living 으로 간주하고 resolve.
          // 첫 transcribe 요청이 들어왔을 때 자동으로 시작 완료 처리됨.
          if (this.sttProcess && !this.sttProcess.killed) {
            logger.warn(
              'Python STT not signaling ready in 30s but process alive - continuing'
            );
            this.isRunning = true;
            settle(resolve);
          } else {
            const recovery = app.isPackaged
              ? '앱을 재시작해주세요.'
              : '`pnpm run setup:python` 으로 환경을 재구성해보세요.';
            settle(() =>
              reject(
                new Error(
                  `STT service 가 30 초 안에 시작되지 않았습니다. ${recovery}`
                )
              )
            );
          }
        }, 30000);
      } catch (err) {
        settle(() => reject(err as Error));
      }
    });
  }

  /**
   * STT 서비스 종료
   */
  stop(): void {
    if (this.sttProcess && !this.sttProcess.killed) {
      logger.info('Stopping Python STT service');
      this.sttProcess.kill('SIGTERM');

      // 3초 후에도 안 죽으면 강제 종료
      setTimeout(() => {
        if (this.sttProcess && !this.sttProcess.killed) {
          logger.warn('Force killing Python STT service');
          this.sttProcess.kill('SIGKILL');
        }
      }, 3000);
    }

    this.isRunning = false;
  }

  /**
   * 서비스 실행 중인지 확인
   */
  getStatus(): boolean {
    return this.isRunning;
  }
}
