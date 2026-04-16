/**
 * 경량 로거 (외부 의존성 없음)
 * 콘솔 출력 + 구조화된 메타데이터
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const LEVEL_COLORS: Record<LogLevel, string> = {
  debug: '\x1b[36m',  // cyan
  info: '\x1b[32m',   // green
  warn: '\x1b[33m',   // yellow
  error: '\x1b[31m',  // red
};

const RESET = '\x1b[0m';

function getTimestamp(): string {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

function formatMessage(
  level: LogLevel,
  module: string,
  message: string,
  meta?: Record<string, unknown>
): string {
  const ts = getTimestamp();
  const color = LEVEL_COLORS[level];
  let line = `${ts} ${color}[${level.toUpperCase()}]${RESET} [${module}] ${message}`;
  if (meta && Object.keys(meta).length > 0) {
    line += ` ${JSON.stringify(meta)}`;
  }
  return line;
}

interface Logger {
  debug: (message: string, meta?: Record<string, unknown>) => void;
  info: (message: string, meta?: Record<string, unknown>) => void;
  warn: (message: string, meta?: Record<string, unknown>) => void;
  error: (message: string, meta?: Record<string, unknown>) => void;
}

const currentLevel: LogLevel =
  (process.env.LOG_LEVEL as LogLevel) || 'info';

/** 로거 생성 */
export function createLogger(module: string): Logger {
  const shouldLog = (level: LogLevel): boolean =>
    LEVEL_ORDER[level] >= LEVEL_ORDER[currentLevel];

  return {
    debug(message, meta?) {
      if (shouldLog('debug'))
        console.debug(formatMessage('debug', module, message, meta));
    },
    info(message, meta?) {
      if (shouldLog('info'))
        console.log(formatMessage('info', module, message, meta));
    },
    warn(message, meta?) {
      if (shouldLog('warn'))
        console.warn(formatMessage('warn', module, message, meta));
    },
    error(message, meta?) {
      if (shouldLog('error'))
        console.error(formatMessage('error', module, message, meta));
    },
  };
}

/** 기본 로거 */
export const logger = createLogger('app');
