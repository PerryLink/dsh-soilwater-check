# dsh-soilwater-check

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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./*.tgz
dsh --profile <name> --dump-config | grep 'dsh-soilwater-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As chaves e os parâmetros de cada regra estão em [README.md](README.md#configuration) (versão principal em inglês).

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soilwater-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soilwater-check contributors.
