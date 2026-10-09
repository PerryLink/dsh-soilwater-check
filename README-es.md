# dsh-soilwater-check — Verificación de integridad y coherencia aritmética del registro de monitoreo de suelo y agua subterránea

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-soilwater-check` lee un registro de monitoreo de suelo y agua subterránea —la cabecera del proyecto más una fila por punto y parámetro— y comprueba la integridad y la aritmética de ese mismo registro: que cada fila nombre su punto y su parámetro, que el resultado registrado se pueda analizar como número, que la fecha de muestreo se pueda analizar y no sea posterior a la fecha de verificación, que se registre una norma aplicable, que el veredicto de superación concuerde con la relación entre el resultado y el límite que el propio registro declara, que no se repita ningún número de muestra, que la cabecera declare el proyecto y la fase de monitoreo, y que no quede ningún marcador de plantilla en la columna del parámetro.

## Cómo se ve la salida

![Terminal demo of dsh-soilwater-check: real output over its SW-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-soilwater-check/main/docs/assets/dsh-soilwater-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `SW-002` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| El registro dice «达标», pero el resultado supera el límite escrito al lado. ¿Se detecta? | Sí. `SW-005` compara el resultado con el límite que el propio registro declara y señala la fila cuando el veredicto no concuerda con esa comparación. No incorpora ningún límite propio, así que no puede detectar un límite tomado de la norma o de la categoría de uso del suelo equivocada, y un veredicto fuera de sus listas configuradas se informa por separado. |
| La celda `result` dice `未检出` o `<0.01`, porque el valor está por debajo del límite de detección. ¿Qué hace la comprobación? | `SW-002` lo informa. La regla lee solo la parte numérica de la celda (`0.85` y `1.2×10-3` se aceptan), así que la notación de límite de detección se informa como no analizable a propósito: registre el valor y ponga la observación en otra columna, o desactive la regla. Comprueba que se pueda analizar, no si la cifra es real ni si el método es correcto. |
| Una fila deja vacía la columna `standard`. | `SW-004` exige que la norma esté rellenada en toda fila que lleve esa columna. Comprueba que se escriba una norma, no que sea la que corresponde: si la norma registrada concuerda con el uso del suelo y el medio es una cuestión sustantiva que el plugin deja al lector. |
| Una fila registra una fecha de muestreo posterior a la fecha de verificación y otra escribe la fecha como `2026/3/15`. | `SW-003` informa de un `sampledAt` posterior a la fecha de verificación. La regla lee `2026-03-15` y `2026-03-15 09:30`; cualquier otra forma se informa como no analizable en lugar de omitirse en silencio. Solo compara fechas: no juzga si el dato es fiable. |
| El mismo `labNo` aparece en dos filas, porque una muestra se analizó para varios parámetros. | `SW-006` informa de un número de muestra repetido, porque la repetición rompe el enlace entre el informe del laboratorio y el registro; la comparación ignora los espacios. Varios parámetros de una misma muestra que comparten un número de muestra es la forma prevista: manténgalos en filas separadas, pero no reutilice la columna del número de fila. Si no hay columna de número de muestra, la regla se informa en `skipped` en lugar de pasar en silencio. |
| La celda `parameter` todavía dice `待填` o `【】`, porque el registro se copió de la plantilla. | `SW-008` informa del marcador que queda en la columna del parámetro (`【`, `】`, `{{`, `XXX`, `待填`, `TBD`, `示例` y términos similares, editables en el paquete de reglas). Tenga en cuenta que `SW-001` solo pide que el nombre del punto o el parámetro esté rellenado, así que un marcador cuenta como relleno allí; la regla de marcadores es la que lo detecta. Ninguna de las dos juzga si el factor es el que se debe monitorear. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-soilwater-check
dsh --profile <name> --dump-config | grep 'dsh-soilwater-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/soilwater-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soilwater-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soilwater-check contributors.
