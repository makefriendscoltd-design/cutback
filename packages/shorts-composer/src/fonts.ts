/**
 * 자막용 무료 폰트 레지스트리
 *
 * 전부 SIL OFL 1.1 라이선스 — 상업적 사용/영상 임베딩 무료.
 * 폰트 파일은 scripts/ensure-fonts.js 가 assets/fonts/ 에 다운로드한다.
 * 파일이 없으면 시스템 폰트(맑은 고딕)로 폴백 (libass가 fontsdir에서 못 찾으면 시스템 검색).
 */

import fs from 'fs';
import path from 'path';

export interface FontDef {
  id: string;
  /** ASS Fontname 에 들어갈 패밀리명 (폰트 내부 이름과 일치해야 함) */
  family: string;
  /** assets/fonts/ 안의 파일명 */
  file: string;
  /** ASS Bold 플래그 */
  bold: boolean;
  license: string;
  /** ensure-fonts.js 가 사용하는 다운로드 URL */
  url: string;
}

export const FONTS: FontDef[] = [
  {
    id: 'pretendard-extrabold',
    family: 'Pretendard ExtraBold',
    file: 'Pretendard-ExtraBold.otf',
    bold: false,
    license: 'SIL OFL 1.1',
    url: 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-ExtraBold.otf',
  },
  {
    id: 'pretendard-bold',
    family: 'Pretendard',
    file: 'Pretendard-Bold.otf',
    bold: true,
    license: 'SIL OFL 1.1',
    url: 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-Bold.otf',
  },
  {
    id: 'suit-bold',
    family: 'SUIT',
    file: 'SUIT-Bold.otf',
    bold: true,
    license: 'SIL OFL 1.1',
    url: 'https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2.0/fonts/static/otf/SUIT-Bold.otf',
  },
];

export const DEFAULT_FONT_ID = 'pretendard-extrabold';

let fontsDirOverride: string | null = null;

/**
 * 폰트 디렉토리 재정의 (presetLoader.setBaseDir 패턴).
 * Electron main 은 esbuild 로 번들되어 __dirname 이 앱 dist 를 가리키므로
 * main/index.ts 에서 dev/packaged 경로를 직접 지정해야 한다.
 */
export function setFontsDir(dir: string): void {
  fontsDirOverride = dir;
}

/** 다운로드된 폰트가 놓이는 디렉토리 (CUTBACK_FONTS_DIR 로 재정의 가능) */
export function getFontsDir(): string {
  if (fontsDirOverride) return fontsDirOverride;
  if (process.env.CUTBACK_FONTS_DIR && fs.existsSync(process.env.CUTBACK_FONTS_DIR)) {
    return process.env.CUTBACK_FONTS_DIR;
  }
  // dist/fonts.js 기준 ../assets/fonts
  return path.join(__dirname, '..', 'assets', 'fonts');
}

export function getFont(fontId?: string): FontDef {
  const id = fontId ?? DEFAULT_FONT_ID;
  const font = FONTS.find((f) => f.id === id);
  if (!font) {
    throw new Error(
      `Unknown font id: ${id}. Available: ${FONTS.map((f) => f.id).join(', ')}`
    );
  }
  return font;
}

/** 폰트 파일이 실제로 존재하는지. 없으면 시스템 폰트 폴백 대상. */
export function isFontAvailable(fontId?: string): boolean {
  const font = getFont(fontId);
  return fs.existsSync(path.join(getFontsDir(), font.file));
}

/** 사용 가능한 폰트 목록 (UI 셀렉트용) */
export function listFonts(): Array<FontDef & { available: boolean }> {
  const dir = getFontsDir();
  return FONTS.map((f) => ({
    ...f,
    available: fs.existsSync(path.join(dir, f.file)),
  }));
}
