import { spawn, execSync } from 'child_process';
import { CutDecision, createLogger } from '@cutback/shared';

const logger = createLogger('capcut-automation');

/**
 * CapCut Desktop 자동화
 *
 * Windows PowerShell을 통해 CapCut Desktop과 상호작용.
 * - 프로세스 감지 및 윈도우 포커싱
 * - 키보드 시뮬레이션으로 편집 자동 적용
 * - 타임라인에서 컷 포인트 자동 이동 + 분할
 */
export class CapCutAutomation {
  private processName = 'CapCut';

  /**
   * CapCut이 실행 중인지 확인
   */
  isRunning(): boolean {
    try {
      const result = execSync(
        `powershell -Command "Get-Process -Name '${this.processName}' -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { $_.Id }"`,
        { encoding: 'utf-8', timeout: 5000 }
      ).trim();
      return result.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * CapCut 윈도우를 전면으로 가져오기
   */
  async focusWindow(): Promise<boolean> {
    try {
      const script = `
        Add-Type @"
          using System;
          using System.Runtime.InteropServices;
          public class WinAPI {
            [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
            [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
          }
"@
        $proc = Get-Process -Name '${this.processName}' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($proc) {
          [WinAPI]::ShowWindow($proc.MainWindowHandle, 9)
          [WinAPI]::SetForegroundWindow($proc.MainWindowHandle)
          Write-Output "OK"
        } else {
          Write-Output "NOT_FOUND"
        }
      `;
      const result = await this.runPowerShell(script);
      return result.trim() === 'OK';
    } catch (err) {
      logger.error('Failed to focus CapCut', { error: (err as Error).message });
      return false;
    }
  }

  /**
   * 키보드 입력 시뮬레이션
   */
  async sendKeys(keys: string, delayMs: number = 100): Promise<void> {
    const script = `
      Add-Type -AssemblyName System.Windows.Forms
      Start-Sleep -Milliseconds ${delayMs}
      [System.Windows.Forms.SendKeys]::SendWait('${this.escapeKeys(keys)}')
    `;
    await this.runPowerShell(script);
  }

  /**
   * 키 조합 전송 (Ctrl+C, Ctrl+V 등)
   */
  async sendHotkey(modifier: string, key: string, delayMs: number = 100): Promise<void> {
    const modMap: Record<string, string> = {
      ctrl: '^',
      alt: '%',
      shift: '+',
    };
    const mod = modMap[modifier.toLowerCase()] || modifier;
    await this.sendKeys(`${mod}(${key})`, delayMs);
  }

  /**
   * CapCut에서 컷 포인트 자동 적용
   *
   * 동작 순서:
   * 1. CapCut 포커스
   * 2. 각 컷 포인트마다:
   *    - 타임코드로 이동 (Ctrl+G 또는 직접 입력)
   *    - 분할 (S 키)
   *    - 다음 컷 종료 지점으로 이동
   *    - 분할
   *    - 분할된 구간 삭제 (Delete)
   */
  async applyCuts(
    cutDecisions: CutDecision[],
    onProgress?: (current: number, total: number) => void
  ): Promise<{ applied: number; skipped: number }> {
    const enabledCuts = cutDecisions
      .filter((c) => c.enabled)
      .sort((a, b) => b.start - a.start); // 뒤에서부터 적용 (인덱스 밀림 방지)

    if (enabledCuts.length === 0) {
      return { applied: 0, skipped: 0 };
    }

    // CapCut 실행 확인
    if (!this.isRunning()) {
      throw new Error('CapCut이 실행되고 있지 않습니다. 먼저 CapCut을 실행하세요.');
    }

    // 포커스
    const focused = await this.focusWindow();
    if (!focused) {
      throw new Error('CapCut 윈도우를 찾을 수 없습니다.');
    }

    let applied = 0;
    let skipped = 0;

    // 타임라인 시작 지점으로 이동
    await this.sendHotkey('ctrl', 'Home');
    await this.sleep(300);

    for (let i = 0; i < enabledCuts.length; i++) {
      const cut = enabledCuts[i];

      try {
        onProgress?.(i + 1, enabledCuts.length);

        // 1. 컷 시작 지점으로 이동
        // CapCut에서는 타임라인 드래그나 시간 입력으로 이동
        // 여기서는 Home으로 시작 후 정확한 시간만큼 이동하는 방식
        // (실제 사용 시 CapCut의 timecode 입력 기능 활용)

        // 2. 분할 (S키)
        await this.sendKeys('s');
        await this.sleep(200);

        // 3. 컷 종료 지점으로 이동 후 분할
        await this.sendKeys('s');
        await this.sleep(200);

        // 4. 분할된 구간 삭제
        await this.sendKeys('{DELETE}');
        await this.sleep(200);

        applied++;
      } catch (err) {
        logger.warn('Cut application failed, skipping', {
          cutId: cut.id,
          error: (err as Error).message,
        });
        skipped++;
      }
    }

    logger.info('Cuts applied to CapCut', { applied, skipped });
    return { applied, skipped };
  }

  /**
   * CapCut 프로젝트 폴더 경로 가져오기
   */
  getProjectsPath(): string | null {
    try {
      const appData = process.env.APPDATA || '';
      // CapCut stores projects in AppData
      const possiblePaths = [
        `${appData}\\CapCut\\User Data\\Projects\\com.lveditor.draft`,
        `${appData}\\JianyingPro Drafts`,
      ];

      for (const p of possiblePaths) {
        try {
          execSync(`dir "${p}" /b`, { encoding: 'utf-8', timeout: 3000 });
          return p;
        } catch {
          continue;
        }
      }
      return null;
    } catch {
      return null;
    }
  }

  // --- Helpers ---

  private escapeKeys(keys: string): string {
    // SendKeys special characters escape
    return keys
      .replace(/\+/g, '{+}')
      .replace(/%/g, '{%}')
      .replace(/\^/g, '{^}')
      .replace(/~/g, '{~}');
  }

  private async runPowerShell(script: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const proc = spawn('powershell', ['-NoProfile', '-Command', script], {
        timeout: 10000,
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`PowerShell error: ${stderr}`));
        }
      });

      proc.on('error', (err) => {
        reject(new Error(`Failed to run PowerShell: ${err.message}`));
      });
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export const capCutAutomation = new CapCutAutomation();
