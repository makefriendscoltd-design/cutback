/**
 * @cutback/crosscut-planner
 *
 * Mode B: 러프컷 타임라인 생성
 * - 문장-클립 매칭 결과 → 타임라인 배치
 * - 길이 조정 전략 (트리밍, 속도, 반복, 프리즈)
 * - EDL/CapCut JSON 내보내기
 */

export { CrosscutPlanner } from './crosscut-planner.js';
export { TimelineBuilder } from './timeline-builder.js';
export { AdjustmentStrategy } from './adjustment-strategy.js';
