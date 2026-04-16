import { spawn } from 'child_process';
import {
  createLogger,
  PYTHON_SERVICES,
  Transcript,
  STTRequest,
  STTResponse,
} from '@cutback/shared';

const logger = createLogger('python-client');

/**
 * Python 서비스 클라이언트
 *
 * child_process로 Python 스크립트를 호출하여 ZeroMQ 서비스와 통신.
 * Node.js 측에 zeromq 네이티브 모듈이 필요 없으므로 빌드 문제 해소.
 */
export class PythonClient {
  private sttPort: number;
  private timeout: number;
  private retryAttempts: number;

  constructor(options?: { sttPort?: number; timeout?: number }) {
    this.sttPort = options?.sttPort ?? PYTHON_SERVICES.STT_PORT;
    this.timeout = options?.timeout ?? PYTHON_SERVICES.TIMEOUT_MS;
    this.retryAttempts = PYTHON_SERVICES.RETRY_ATTEMPTS;
  }

  /**
   * STT 요청
   */
  async transcribe(
    audioPath: string,
    language: string = 'ko'
  ): Promise<Transcript> {
    const request: STTRequest = {
      action: 'transcribe',
      payload: {
        audio_path: audioPath,
        language,
        word_timestamps: true,
      },
    };

    const response = await this.sendRequest<STTResponse>(request);

    if (!response.success || !response.transcript) {
      throw new Error(`STT failed: ${response.error || 'Unknown error'}`);
    }

    return response.transcript;
  }

  /**
   * 한국어 자막 맞춤법 교정 (배치)
   * 실패 시 원본 텍스트를 그대로 돌려준다.
   */
  async spellCheck(texts: string[]): Promise<string[]> {
    if (texts.length === 0) return texts;
    try {
      const response = await this.sendRequest<{
        success: boolean;
        corrected?: string[];
        available?: boolean;
        error?: string;
      }>({
        action: 'spell_check',
        payload: { texts },
      });
      if (response.success && Array.isArray(response.corrected)) {
        return response.corrected;
      }
      logger.warn('Spell check returned no correction', {
        error: response.error,
      });
      return texts;
    } catch (err) {
      logger.warn('Spell check failed, using original text', {
        error: (err as Error).message,
      });
      return texts;
    }
  }

  /**
   * Health check
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.sendRequest<{ success: boolean }>({
        action: 'health',
      });
      return response.success;
    } catch {
      return false;
    }
  }

  /**
   * 재시도 래퍼
   */
  private async sendRequest<T>(request: unknown): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        return await this.doSend<T>(request);
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        logger.warn('Request failed, retrying...', {
          attempt,
          maxAttempts: this.retryAttempts,
          error: lastError.message,
        });

        if (attempt < this.retryAttempts) {
          const delay =
            PYTHON_SERVICES.RETRY_DELAY_MS * Math.pow(2, attempt - 1);
          await this.sleep(delay);
        }
      }
    }

    throw new Error(
      `Python service request failed after ${this.retryAttempts} attempts: ${lastError?.message}`
    );
  }

  /**
   * child_process로 Python 1-shot 스크립트 실행하여 ZeroMQ 서비스 호출
   * stdin으로 JSON 전달하여 경로 특수문자 문제 방지
   */
  private doSend<T>(request: unknown): Promise<T> {
    return new Promise((resolve, reject) => {
      const pythonScript = [
        'import zmq, json, sys',
        'req = json.loads(sys.stdin.read())',
        'ctx = zmq.Context()',
        'sock = ctx.socket(zmq.REQ)',
        `sock.setsockopt(zmq.RCVTIMEO, ${this.timeout})`,
        `sock.connect("tcp://127.0.0.1:${this.sttPort}")`,
        'sock.send_string(json.dumps(req))',
        'result = sock.recv_string()',
        'print(result)',
        'sock.close()',
        'ctx.term()',
      ].join('; ');

      const proc = spawn('python', ['-X', 'utf8', '-c', pythonScript], {
        timeout: this.timeout + 5000,
        env: { ...process.env, PYTHONUTF8: '1' },
      });

      // stdin으로 JSON 전달 (특수문자 안전)
      proc.stdin.write(JSON.stringify(request));
      proc.stdin.end();

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      proc.on('close', (code: number | null) => {
        if (code === 0 && stdout.trim()) {
          try {
            resolve(JSON.parse(stdout.trim()) as T);
          } catch {
            reject(new Error(`Failed to parse Python output: ${stdout}`));
          }
        } else {
          reject(
            new Error(
              `Python process exited with code ${code}: ${stderr}`
            )
          );
        }
      });

      proc.on('error', (err: Error) => {
        reject(new Error(`Failed to spawn Python: ${err.message}`));
      });
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
