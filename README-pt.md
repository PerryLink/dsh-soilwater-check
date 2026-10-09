# dsh-soilwater-check — Verificação da integridade e da coerência aritmética do registo de monitorização de solo e águas subterrâneas

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-soilwater-check` lê um registo de monitorização de solo e águas subterrâneas —o cabeçalho do projeto mais uma linha por ponto e parâmetro— e verifica a integridade e a aritmética desse próprio registo: se cada linha indica o seu ponto e o seu parâmetro, se o resultado registado é analisável como número, se a data de amostragem é analisável e não é posterior à data de verificação, se está registada uma norma aplicável, se o veredicto de superação concorda com a relação entre o resultado e o limite que o próprio registo declara, se não há números de amostra repetidos, se o cabeçalho declara o projeto e a fase de monitorização, e se não resta nenhum marcador de modelo na coluna do parâmetro.

## Como é a saída

![Terminal demo of dsh-soilwater-check: real output over its SW-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-soilwater-check/main/docs/assets/dsh-soilwater-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `SW-002` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| O registo diz «达标», mas o resultado é superior ao limite escrito ao lado. Isso é detetado? | Sim. `SW-005` compara o resultado com o limite que o próprio registo declara e assinala a linha quando o veredicto não concorda com essa comparação. Não traz limites próprios, por isso não consegue detetar um limite retirado da norma ou da categoria de uso do solo errada, e um veredicto fora das listas configuradas é reportado em separado. |
| A célula `result` diz `未检出` ou `<0.01`, porque o valor está abaixo do limite de deteção. O que faz a verificação? | `SW-002` reporta-o. A regra lê apenas a parte numérica da célula (`0.85` e `1.2×10-3` são aceites), pelo que a notação de limite de deteção é reportada como não analisável de propósito — registe o valor e coloque a observação noutra coluna, ou desative a regra. Verifica se é analisável, não se o valor é verdadeiro nem se o método está correto. |
| Uma linha deixa a coluna `standard` vazia. | `SW-004` exige que a norma esteja preenchida em todas as linhas que tenham essa coluna. Verifica que uma norma está escrita, não que seja a norma aplicável: se a norma registada corresponde ao uso do solo e ao meio é uma questão substantiva que o plugin deixa ao leitor. |
| Uma linha regista uma data de amostragem posterior à data de verificação e outra escreve a data como `2026/3/15`. | `SW-003` reporta um `sampledAt` posterior à data de verificação. A regra lê `2026-03-15` e `2026-03-15 09:30`; qualquer outro formato é reportado como não analisável em vez de ser ignorado em silêncio. Compara apenas datas: não julga se o dado é fiável. |
| O mesmo `labNo` aparece em duas linhas, porque uma amostra foi analisada para vários parâmetros. | `SW-006` reporta um número de amostra repetido, porque a repetição quebra a ligação entre o relatório do laboratório e o registo; a comparação ignora espaços. Vários parâmetros de uma mesma amostra a partilhar um número de amostra é a forma prevista: mantenha-os em linhas separadas, mas não reutilize a coluna do número de linha. Sem coluna de número de amostra, a regra reporta-se em `skipped` em vez de passar em silêncio. |
| A célula `parameter` ainda diz `待填` ou `【】`, porque o registo foi copiado do modelo. | `SW-008` reporta o marcador que resta na coluna do parâmetro (`【`, `】`, `{{`, `XXX`, `待填`, `TBD`, `示例` e termos semelhantes, editáveis no pacote de regras). Note que `SW-001` apenas exige que o nome do ponto ou o parâmetro esteja preenchido, pelo que um marcador conta como preenchido ali; é a regra dos marcadores que o deteta. Nenhuma das duas julga se o fator é o que deve ser monitorizado. |

## Normas que segue

| Documento | Número | Regras que o citam |
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
dsh plugin --profile <name> add dsh-soilwater-check
dsh --profile <name> --dump-config | grep 'dsh-soilwater-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/soilwater-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

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
