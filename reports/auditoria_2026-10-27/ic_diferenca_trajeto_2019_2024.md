# IC da diferença 2019→2024 — TRAJETO_INSEGURO, Brasil, total

## A. Microdados (método usado pela pipeline, `series.build_series`)

* 2019: 11.6001 % (EP 0.2554); 2024: 12.4723 % (EP 0.3337)
* d = 0.8721 p.p.; EP(d) = √(EP₁² + EP₂²) = 0.4202; IC 95% = [0.0485; 1.6958]; |d|/EP(d) = 2.075 (> 1,96 → significativa)
* conferência com `microdata_series.csv`: diff_pp 0.8721, IC [0.0485; 1.6958], significant_5pct true

## B. Só com os IC publicados (aproximação)

* PENSE_2019: 11.6032 [11.1024; 12.1039] (célula Tema_09_Seguranca_2019_20260615.xls::9.7.1!B13); assimetria (sup−est) − (est−inf) = -0.0000
* PENSE_2024: 12.4722 [11.8161; 13.1284] (célula Tema_09_Seguranca_XLSX_20260525.zip!Tabelas 9.7.xlsx::9.7.1!B13); assimetria (sup−est) − (est−inf) = +0.0000
* EP derivado: 2019 0.2555 (microdados 0.2554); 2024 0.3348 (microdados 0.3337)
* d = 0.8691 p.p.; EP(d) ≈ 0.4211; IC 95% ≈ [0.0437; 1.6945]; |d|/EP(d) = 2.064

## C. Sobreposição dos IC publicados (não é teste)

* os IC se sobrepõem (11.82 < 12.10) e mesmo assim a diferença é significativa: sobreposição não serve como teste.

## D. Sensibilidade ao arredondamento (método B)

* usando os valores impressos com 2 casas (11.6, [11.1; 12.1]; 12.47, [11.82; 13.13]) e variando cada um em ±0,005 (±0,01 na diferença): o limite inferior do IC da diferença vai de 0.0290 a 0.0630.

