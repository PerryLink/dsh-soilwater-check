import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/soilwater-check.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
          "project": "某某场地调查",
          "phase": "初步调查",
          "period": "2026 年第一季度",
          "rows": [
                {
                      "序号": "1",
                      "点位名称": "S1 表层土",
                      "介质": "土壤",
                      "位置": "厂区北侧空地",
                      "采样深度": "0.2",
                      "采样日期": "2026-03-05",
                      "样品编号": "TR-2026-0018",
                      "监测项目": "砷",
                      "监测结果": "12.5",
                      "单位": "mg/kg",
                      "执行标准": "GB 36600—2018 第二类用地筛选值",
                      "标准限值": "60",
                      "超标情况": "达标",
                      "检测单位": "某某检测有限公司"
                }
          ]
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
