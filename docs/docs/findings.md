# KDD Findings

## Q1: Which genres have the most titles?
- International Movies — 2752
- Dramas — 2427
- Comedies — 1674
- International TV Shows — 1351
- Documentaries — 869

## Q2: Maturity rating distribution by type
- TV-MA / Movie — 2062
- TV-14 / Movie — 1427
- TV-MA / TV Show — 1145
- R / Movie — 797
- TV-14 / TV Show — 733

## Q3: Directors appearing most often
- Rajiv Chilaka — 19
- Raúl Campos, Jan Suter — 18
- Marcus Raboy — 16
- Suhas Kadav — 16
- Jay Karas — 14
- Cathy Garcia-Molina — 13
- Martin Scorsese — 12
- Youssef Chahine — 12

## Q4: Release year distribution
- Peak: 2018 (1147 titles)
- 2019: 1030
- 2017: 1032
- 2020: 953
- 2016: 902
- Older content (pre-2000): sparse, single digits per year

## Observations
- International content dominates the catalog (unexpected — worth discussing in the report)
- Movies outnumber TV Shows roughly 2:1 in the raw counts
- Content production accelerated sharply from 2015 onwards
- ~30% of rows have no director (missing data — KDD limitation)
- The `director` field in the top-directors result mixes individual directors with pairs — an artefact of how the source CSV stores multiple names in one cell