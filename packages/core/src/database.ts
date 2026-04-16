import Database from 'better-sqlite3';
import path from 'path';
import { createLogger, PATHS } from '@cutback/shared';

const logger = createLogger('database');

let db: Database.Database | null = null;

/** SQLite 스키마 초기화 SQL */
const SCHEMA_SQL = `
  CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    video_path TEXT NOT NULL,
    preset_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error TEXT
  );

  CREATE TABLE IF NOT EXISTS cut_decisions (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    type TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.0,
    metadata TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    user_approved INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS transcripts (
    job_id TEXT PRIMARY KEY,
    full_text TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'ko',
    duration REAL NOT NULL DEFAULT 0.0,
    words_json TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS captions (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    text TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    style_json TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_cut_decisions_job ON cut_decisions(job_id);
  CREATE INDEX IF NOT EXISTS idx_captions_job ON captions(job_id);
`;

/**
 * DB 초기화 - 앱 시작 시 1회 호출
 */
export function initDatabase(dbPath?: string): Database.Database {
  const resolvedPath = dbPath || path.resolve(PATHS.DB_FILE);
  logger.info('Initializing database', { path: resolvedPath });

  db = new Database(resolvedPath);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  db.exec(SCHEMA_SQL);

  logger.info('Database initialized');
  return db;
}

/**
 * 현재 DB 인스턴스 가져오기
 */
export function getDatabase(): Database.Database {
  if (!db) {
    throw new Error('Database not initialized. Call initDatabase() first.');
  }
  return db;
}

/**
 * DB 연결 종료
 */
export function closeDatabase(): void {
  if (db) {
    db.close();
    db = null;
    logger.info('Database closed');
  }
}
