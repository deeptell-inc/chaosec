---
asset: claims-ledger
version: 1.0.0
生成元入力: S17 ファクトチェック（target: paper/main.tex）
依存工程: S17（追記）/ S7・S8（引用整合の突合）
生成日: 2026-07-10
更新責任工程: S17
---

# claims-ledger — 主張台帳（target: paper/main.tex, supplement.tex）

## スキーマ
claim / 種別(数値·事実/引用帰属/因果/定義·用語/新規性) / 判定(SUPPORTED/PARTIALLY/UNSUPPORTED/CONTRADICTED/UNVERIFIABLE) / 出典 / 確認日 / 反証探索(有/無)

## 抽出した claim（優先度順: 新規性 > 結論支持 > 数値 > 引用帰属）

| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| N1 | 監視下でのスカー vs 熱的部分空間の符号性能の直接比較（コヒーレント情報）は初 | 新規性 | **SUPPORTED** | 独立2検索経路とも該当なし＋一次情報 arXiv:2503.22618（最近接研究は容量を計算せず） | 2026-07-10 | 有（反証探索＝先行研究の能動探索、null） |
| L2 | Paviglianiti–Silva はPXPスカーの連続時間 projective σ^z 測定で γ_c=0.013±0.002 を報告 | 数値/引用帰属 | **SUPPORTED**（本文修正後） | arXiv:2503.22618 (PRL 135,090402) 本文「γ_c=0.013±0.002」 | 2026-07-10 | 有（原論文直接取得・プロトコル確認） |
| — | ↑ 訂正: 本文の "weak continuous monitoring" は誤り（実際は projective）。main/supplement 修正済 | — | CONTRADICTED→修正 | 同上 | 2026-07-10 | — |
| C6 | staggered M は創発su(2)スカー動力学の秩序変数（Choi 2019） | 引用帰属 | **SUPPORTED**（"generator"→"order parameter" に厳密化） | Choi et al. PRL 122,220603 (2019); arXiv:1812.05561 | 2026-07-10 | 有 |
| C3 | ETH は近似KL条件を与える | 引用帰属/因果 | SUPPORTED | Brandão PRL 123,110502; Bao–Cheng JHEP 08(2019)152; Qasim–Pollack arXiv:2510.26758（精読済） | 2026-07-10 | 有 |
| C2 | MIPT は符号化転移＝創発QEC | 引用帰属 | SUPPORTED | Choi–Bao–Qi–Altman PRL 125,030505 (2020)（正典・メタデータ検証済） | 2026-07-10 | 無（正典帰属） |
| C4 | スカーの実験的発見（Bernien 2017, 51原子） | 引用帰属 | SUPPORTED | Bernien et al. Nature 551,579 (2017)（正典・メタデータ検証済） | 2026-07-10 | 無（正典帰属） |
| D1 | 自チーム数値（ΔC_R, Var J²=32.5/0, 密度gap, C_R^scar=1 等）は再現可能 | 数値 | SUPPORTED（自計算） | 本リポジトリ: pytest 11/11＋scripts/*.py＋results/*.json（2経路: driver出力＋テストベンチ） | 2026-07-10 | 有（アンサンブル・アーティファクトの自己反証を実施） |
| L1 | PXP Z2リバイバル t≈4.71, F≈0.743 (L=12) | 数値/事実 | SUPPORTED | 自計算（scarcode-demo）＋文献整合（Turner2018/Bernien2017 の周期≈4.8） | 2026-07-10 | 有 |

## S17 判定サマリ
- CONTRADICTED 1件（L2 の "weak" 記述）→ **本文・Supplement 修正済み・再コンパイル OK**。
- 新規性 N1・主要文献数値 L2 は独立2経路＋一次情報で SUPPORTED（二重確認規則を充足）。
- 自チーム数値 D1 は外部一次情報の対象外だが、再現可能コード＋テストで検証済（自己反証＝アンサンブル平均化による初期結果の反転を実施）。
- UNVERIFIABLE / 未解決の claim: なし。

## 追記（2026-07-16 敵対的パネル後の是正、S17続き）
| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| P1 | thermal Var J²=18.1（旧本文値） | 数値 | **CONTRADICTED→修正** | パネルA/B: リポジトリ内に出所なし（孤児）。scripts/casimir_variance.py 新設 → ensemble mean 6.06, range 2.07–16.52。本文を「mean 6.1, range 2–17」に修正 | 2026-07-16 | 有（同一手法で再計算） |
| P2 | local ΔC_R「−0.03..−0.06, band excluding zero (all L)」（旧本文） | 数値/事実 | **CONTRADICTED→修正** | L=12 local = −0.0076±0.0092（ゼロを含む）。本文をレンジ−0.008..−0.06＋L=12例外の明示に修正 | 2026-07-16 | 有 |
| P3 | spin-1 local「statistically comparable |ΔC_R|≲0.1」（旧本文） | 数値/事実 | **PARTIALLY→修正** | L=8 p=0.04 で+0.171、L=6 p=0.04 でz≈2.4（3パラメータ設定で符号一貫）。低p注意を明記し「no systematic advantage」に修正。機構的優位とはしない（p=0.12で符号反転・多重比較未補正） | 2026-07-16 | 有（3設定SEM解析） |
| P4 | 静的KL比 1.4–2.4 (L=10–14) | 数値 | **SUPPORTED（是正後）** | 孤児だったが scripts/kl_static.py 新設 → 2.39/1.38/1.47 で引用と一致 | 2026-07-16 | 有 |
| P5 | γ_c 残差6×の説明「rate convention」（旧本文） | 因果 | **UNSUPPORTED→修正** | 循環的（γ=p/dtは既に連続時間換算）。プロトコル・推定量差への正直な帰属に書き換え（未定量と明記） | 2026-07-16 | 有 |
