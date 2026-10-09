# dsh-soilwater-check — मिट्टी और भूजल निगरानी रजिस्टर की पूर्णता और अंकगणितीय सुसंगति की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-soilwater-check` मिट्टी और भूजल निगरानी का एक रजिस्टर पढ़ता है — परियोजना हेडर और प्रत्येक बिंदु तथा पैरामीटर की एक पंक्ति — और उसी रजिस्टर की पूर्णता और अंकगणित की जाँच करता है: क्या प्रत्येक पंक्ति में उसका बिंदु और पैरामीटर दर्ज है, क्या दर्ज परिणाम संख्या के रूप में पढ़ा जा सकता है, क्या नमूना-दिनांक पढ़ा जा सकता है और जाँच-दिनांक से बाद का नहीं है, क्या कोई लागू मानक दर्ज है, क्या सीमा-अतिक्रमण का निर्णय परिणाम और रजिस्टर में ही लिखी सीमा के संबंध से मेल खाता है, क्या कोई नमूना क्रमांक दोहराया नहीं गया है, क्या हेडर परियोजना और निगरानी-चरण घोषित करता है, और क्या पैरामीटर कॉलम में कोई टेम्पलेट प्लेसहोल्डर शेष नहीं है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-soilwater-check: real output over its SW-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-soilwater-check/main/docs/assets/dsh-soilwater-check-demo.png)

इस प्लगइन का अपने ही `SW-002` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| रजिस्टर में «达标» लिखा है, पर परिणाम उसके साथ लिखी सीमा से अधिक है। क्या यह पकड़ में आता है? | हाँ। `SW-005` परिणाम की तुलना रजिस्टर में ही दर्ज सीमा से करता है और जहाँ निर्णय इस तुलना से मेल नहीं खाता वह पंक्ति दर्ज करता है। इसमें अपनी कोई सीमा नहीं आती, इसलिए गलत मानक या गलत भूमि-उपयोग श्रेणी से ली गई सीमा यह नहीं पकड़ सकता, और विन्यस्त सूचियों से बाहर का निर्णय अलग से दर्ज होता है। |
| `result` सेल में `未检出` या `<0.01` लिखा है, क्योंकि मान पहचान-सीमा से नीचे है। जाँच क्या करती है? | `SW-002` इसे दर्ज करता है। नियम सेल का केवल संख्यात्मक भाग पढ़ता है (`0.85` और `1.2×10-3` स्वीकार्य हैं), इसलिए पहचान-सीमा वाला लेखन जान-बूझकर अपठनीय बताया जाता है — मान दर्ज करें और टिप्पणी किसी अन्य कॉलम में रखें, या इस नियम को बंद कर दें। यह केवल पठनीयता देखता है, यह नहीं कि अंक सच है या विधि सही है। |
| एक पंक्ति में `standard` कॉलम खाली छोड़ दिया गया है। | `SW-004` अपेक्षा करता है कि जिस भी पंक्ति में यह कॉलम हो, उसमें मानक भरा हो। यह देखता है कि मानक लिखा गया है, यह नहीं कि वही लागू होता है: दर्ज मानक भूमि-उपयोग और माध्यम से मेल खाता है या नहीं, यह ठोस प्रश्न है जिसे प्लगइन पाठक पर छोड़ता है। |
| एक पंक्ति में नमूना-दिनांक जाँच-दिनांक के बाद का है, और दूसरी में दिनांक `2026/3/15` लिखा है। | `SW-003` जाँच-दिनांक के बाद के `sampledAt` को दर्ज करता है। यह `2026-03-15` और `2026-03-15 09:30` पढ़ता है; कोई अन्य रूप चुपचाप छोड़े जाने के बजाय अपठनीय के रूप में दर्ज होता है। यह केवल दिनांकों की तुलना करता है — आँकड़ा विश्वसनीय है या नहीं, यह नहीं आँकता। |
| एक ही `labNo` दो पंक्तियों में है, क्योंकि एक नमूने के कई पैरामीटर जाँचे गए। | `SW-006` दोहराया गया नमूना क्रमांक दर्ज करता है, क्योंकि दोहराव से प्रयोगशाला रिपोर्ट और रजिस्टर का संबंध टूट जाता है; तुलना में रिक्त स्थान छोड़ दिए जाते हैं। एक ही नमूने के कई पैरामीटर एक ही नमूना क्रमांक साझा करें — यही अपेक्षित रूप है: उन्हें अलग पंक्तियों में रखें, पर पंक्ति-क्रमांक कॉलम दोबारा न भरें। रजिस्टर में नमूना-क्रमांक कॉलम ही न हो तो यह नियम चुपचाप पास होने के बजाय `skipped` में दर्ज होता है। |
| `parameter` सेल में अब भी `待填` या `【】` लिखा है, क्योंकि रजिस्टर टेम्पलेट से कॉपी किया गया। | `SW-008` पैरामीटर कॉलम में बचे प्लेसहोल्डर को दर्ज करता है (`【`, `】`, `{{`, `XXX`, `待填`, `TBD`, `示例` जैसे शब्द, जिनकी सूची नियम-पैक में बदली जा सकती है)। ध्यान दें कि `SW-001` केवल यह देखता है कि बिंदु का नाम या पैरामीटर इनमें से कम से कम एक भरा हो, इसलिए प्लेसहोल्डर वहाँ भरा हुआ माना जाता है; इसे पकड़ने वाला नियम प्लेसहोल्डर वाला ही है। दोनों में से कोई यह नहीं आँकता कि निगरानी किया जाने वाला कारक सही चुना गया है या नहीं। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-soilwater-check
dsh --profile <name> --dump-config | grep 'dsh-soilwater-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/soilwater-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soilwater-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soilwater-check contributors.
