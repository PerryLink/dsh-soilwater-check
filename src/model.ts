/**
 * dsh-soilwater-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'soilwater_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  pointNo: ['序号', '点位编号', '编号', 'pointNo'],
  pointName: ['点位名称', '监测点位', '井号', 'pointName'],
  medium: ['介质', '监测介质', '对象类型', 'medium'],
  location: ['位置', '点位位置', '坐标', 'location'],
  depth: ['井深', '采样深度', '埋深', 'depth'],
  sampledAt: ['采样日期', '监测日期', '取样日期', 'sampledAt'],
  labNo: ['样品编号', '实验室编号', '送样编号', 'labNo'],
  parameter: ['监测项目', '监测因子', '检测项目', 'parameter'],
  result: ['监测结果', '检测结果', '结果', 'result'],
  unit: ['单位', '计量单位', 'unit'],
  standard: ['执行标准', '评价标准', '标准限值来源', 'standard'],
  limit: ['标准限值', '限值', '评价限值', 'limit'],
  exceed: ['是否超标', '超标情况', '达标情况', 'exceed'],
  lab: ['检测单位', '监测单位', '实验室', 'lab'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'points', '点位'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '工程名称'],
  phase: ['phase', '监测阶段', '监测频次'],
  period: ['period', '监测期次', '监测时段'],
  checker: ['checker', '校核人', '复核人'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '点位名称',
  'pointName',
  '监测项目',
  'parameter',
  '监测结果',
  'result',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
