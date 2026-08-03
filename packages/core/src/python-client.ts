import {
  createLogger,
  PYTHON_SERVICES,
  Transcript,
  STTRequest,
  STTResponse,
} from '@cutback/shared';
import * as zmq from 'zeromq';
import { stat } from 'fs/promises';

const logger = createLogger('python-client');

/**
 * Python 서비스 클라이언트
 *
 * cutback-stt.exe (또는 dev 모드 python main.py) 가 띄우는 ZeroMQ REP 서버와
 * Node.js 측에서 직접 통신한다.
 *
 * 중요:
 *   - 이전 구현은 매 요청마다 `spawn('python', ['-c', ...])` 를 호출했음.
 *   - 그러면 사용자 PC 에 python 이 PATH 에 없으면 즉시 ENOENT 로 실패.
 *   - 번들된 cutback-stt.exe 는 '서버'만 돌리므로 클라이언트 통신은 Node 에서.
 *
 * zeromq 6.x (N-API) 는 prebuilt 바이너리를 제공하며 electron-builder 의
 * @electron/rebuild 가 Electron ABI 에 맞춰 자동 처리한다.
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

    // 고정 10분 타임아웃은 롱폼에서 못 버틴다.
    // CPU + small 실측이 약 3.6x 실시간이므로 30분 영상이면 8분 남짓 걸리고,
    // 느린 PC 나 더 긴 영상은 그대로 타임아웃에 걸려 자막이 통째로 날아갔다.
    // 오디오 길이에 비례해 넉넉히 잡는다. (16kHz mono 16-bit PCM = 32000 B/s)
    const timeout = await this.estimateTranscribeTimeout(audioPath);
    const response = await this.sendRequest<STTResponse>(request, timeout);

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
   * 오디오 길이에 비례한 STT 타임아웃 (ms).
   *
   * 실시간의 1/8 속도(=CPU small 실측 3.6x 의 두 배 이상 여유)까지 버티고,
   * 최소 10분은 보장한다. 파일을 못 읽으면 기본값으로 폴백.
   */
  private async estimateTranscribeTimeout(audioPath: string): Promise<number> {
    try {
      const { size } = await stat(audioPath);
      const seconds = size / 32000; // 16kHz mono 16-bit PCM
      const budgetMs = seconds * 8 * 1000;
      const timeout = Math.max(this.timeout, Math.ceil(budgetMs));
      logger.info('STT timeout budget', {
        audioSeconds: Math.round(seconds),
        timeoutMinutes: Math.round(timeout / 60000),
      });
      return timeout;
    } catch {
      return this.timeout;
    }
  }

  /**
   * 재시도 래퍼
   */
  private async sendRequest<T>(
    request: unknown,
    timeoutMs?: number
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        return await this.doSend<T>(request, timeoutMs);
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
   * Node.js zeromq 패키지로 직접 REQ/REP 통신
   *
   * 매 요청마다 새 소켓을 열고 닫는다. 지속 소켓을 유지할 수도 있지만
   * zmq REQ 상태 머신이 엄격해서 timeout/error 후 복구가 까다롭다.
   * short-lived 소켓이 더 안전.
   */
  private async doSend<T>(request: unknown, timeoutMs?: number): Promise<T> {
    // zeromq 를 top-level import 로 로드 (동적 require 는 Electron 에서 resolve 실패)
    const effectiveTimeout = timeoutMs ?? this.timeout;
    const sock = new zmq.Request();
    sock.receiveTimeout = effectiveTimeout;
    sock.sendTimeout = effectiveTimeout;
    // 연결 실패 시 오래 대기하지 않도록
    sock.linger = 0;

    const endpoint = `tcp://127.0.0.1:${this.sttPort}`;

    try {
      sock.connect(endpoint);
      await sock.send(JSON.stringify(request));

      const [replyBuf] = await sock.receive();
      const replyStr = replyBuf.toString();

      try {
        return JSON.parse(replyStr) as T;
      } catch {
        throw new Error(`Failed to parse STT service reply: ${replyStr}`);
      }
    } finally {
      try {
        sock.close();
      } catch {
        // ignore
      }
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
