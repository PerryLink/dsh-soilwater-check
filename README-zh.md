# dsh-soilwater-check — 土壤与地下水监测台账核对

`dsh-soilwater-check` 读取一份土壤与地下水监测台账——项目表头加每个点位与监测项目一行——核对这份台账自身的齐备与算术：每条记录是否写明点位名称与监测项目、监测结果是否可解析为数值、采样日期是否可解析且不晚于核对日、是否填写了执行标准、超标判定是否与台账自己写的结果和限值的关系相符、样品编号是否重复、表头是否声明项目与监测阶段、监测项目栏是否残留模板占位符。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 台账填的是「达标」，但监测结果比旁边写的标准限值还高，能查出来吗？ | 能。`SW-005` 拿台账自己写的结果与限值相比，判定与这个关系不符时逐行报出。它不内置任何限值，所以发现不了「限值取错了标准或用地类别」；判定取值不在配置的超标／未超标两份清单内时，也会单独报出。 |
| 监测结果栏写的是「未检出」或 `<0.01`（低于检出限），会怎么处理？ | `SW-002` 会把它报出来。本条只取单元格里的数字部分（`0.85`、`1.2×10-3` 这类写法可解析），所以检出限写法会被故意判为不可解析而报出——请把 `result` 栏统一为数值、备注另设一栏，或停用本条。它只核对可解析性，不判断数值是否真实、检测方法是否正确。 |
| 有一行的「执行标准」栏是空的。 | `SW-004` 要求凡是带这一栏的行都要填写执行标准。它只核对「是否写了标准」，不核对「写的是不是应当适用的那一部」——所填标准与用地类型、监测介质是否匹配，需要查阅标准与场地资料，本插件不做。 |
| 有一行的采样日期比核对日还晚，另一行的日期写成了 `2026/3/15`。 | `SW-003` 会报出晚于核对日的 `sampledAt`。本条识别 `2026-03-15` 与 `2026-03-15 09:30` 两种写法，其它写法会作为无法解析单独报出，不会静默跳过。它只核对日期先后，不判断数据是否可靠。 |
| 同一个样品编号出现在两行上，因为同一样品做了好几个监测项目。 | `SW-006` 会报出重复的样品编号，因为重复会让检测报告与台账对不上；比较时忽略空白字符。同一样品的不同监测项目共用同一个样品编号正是正常情形——各占一行即可，但不要重复使用行号栏。台账里根本没有样品编号栏时，本条会出现在 `skipped` 中，而不是静默通过。 |
| 监测项目栏还留着「待填」或「【】」，因为台账是照模板抄的。 | `SW-008` 会报出监测项目栏残留的占位符（`【`、`】`、`{{`、`XXX`、`待填`、`TBD`、`示例` 等，词表可在规则库中调整）。注意 `SW-001` 只要求点位名称与监测项目「至少填了一个」，占位符在它那里算已填；真正抓住它的是占位符这一条。两条都不判断监测因子选得对不对。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《建设用地土壤污染状况调查技术导则》 | HJ 25.1—2019（代替 HJ 25.1-2014；条号本次未取得） | SW-001, SW-003, SW-007, SW-008 |
| 《地下水环境监测技术规范》 | HJ 164—2020（代替 HJ/T 164—2004；2020-12-01 发布、2021-03-01 实施；条号本次未取得） | SW-002, SW-006 |
| 《土壤环境质量 建设用地土壤污染风险管控标准（试行）》 | GB 36600—2018（本次未取得条文） | SW-004, SW-005 |

**Boundary:** this plugin checks a **土壤与地下水监测台账** for completeness and arithmetic — that each record
names its point and parameter, that the result parses as a number, that the sampling date is not in the future,
that an applicable standard is recorded, that the exceedance verdict agrees with how the result compares to the
limit the register states, that sample numbers are unique, that the register names its project and survey phase,
and that no placeholder survives. It does **not** decide whether a site is contaminated, whether remediation is
needed, whether remediation targets were met, or whether a survey's conclusions hold.

> ### ⚠️ What this plugin deliberately cannot do
>
> **It ships no limits, and it does not check that the limit was taken from the right standard.** `SW-005`
> compares the measured result against the limit **the register itself records** and checks that the verdict
> agrees. So it **cannot find the consequential error: a screening value taken from the wrong standard or the
> wrong land-use category.** Deciding between GB 36600's first and second category screening values, or between
> GB 36600 and GB/T 14848, turns on the land use and the medium — this plugin reads neither. That limit is
> stated in the pack's header, in `SW-004`'s and `SW-005`'s notes, and in the troubleshooting section.
>
> `SW-002` requires a parseable number, so a register that writes detection-limit notation
> (`未检出`, `<0.01`) is **reported as unparseable on purpose** — record the value with a remark, or disable the
> rule.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The regime
> lives in GB 36600—2018, GB/T 14848—2017, HJ 25.1 and HJ 164. The verification pass could not retrieve verbatim
> clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at `warn` or
> `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind` to
> `direct`.**

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-soilwater-check
dsh --profile <name> --dump-config | grep 'dsh-soilwater-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/soilwater-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soilwater-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soilwater-check contributors.
