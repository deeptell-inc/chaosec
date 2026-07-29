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

## 追記（2026-07-27 Codex 敵対的レビュー後の是正、S17続き）
| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| X1 | 熱的符号は「same two energies」の固有状態から構成（旧本文） | 数値/事実 | **CONTRADICTED→修正** | Codex指摘: `thermal_ensemble(window=0.5)` により実オフセット平均0.22・最大0.47 (L=14)。scripts/energy_window_robustness.py 新設: 窓±0.5/±0.25/±0.10 で ΔC_R=−0.033/−0.034/−0.031 (local), −0.25/−0.23/−0.21 (collective) — 結論は窓非依存。アンサンブル内 C_R vs \|offset\| Spearman ρ=+0.05 (p=0.88)/0.00 (p=1.00) — 無相関。本文を「±0.5 窓・実オフセット開示・頑健性 Appendix 参照」に修正（quantum版・PRXレガシー版とも） | 2026-07-27 | 有（タイト窓再計算＋相関検定） |

## 追記（2026-07-28 敵対的パネル第2回 Round 1 後の是正、S17続き）
パネル構成: 査読者A=Codex（外部CLI、再現実行あり）、査読者B=Claude Opus（独立サブエージェント、リポジトリ直読）。両者の指摘をファシリテーターが JSON/スクリプト再実行で裏取りした上で修正。
| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| R1 | 「approximate scars carry irreducible Casimir variance」（旧 abstract/本文） | 機構 | **CONTRADICTED→修正** | B指摘＋scripts/fsa_purity_audit.py 新設: Var J² は FSA 混成度の単調関数（w=0.97→0.27 で 0.89→47.6）。本文の canonical 段は塔で最も混成した2段。ただし scripts/pure_rung_dfs.py 新設の全段スキャンで、全整合可能段でスカーは熱的隣接状態より過剰分散（比1.6–4.3）を保持し J² 監視下で全段負け（dCR −0.16→−0.01、正になる段なし）→「excess variance over thermal neighbors, deficit tracks the excess」に修正。機構は 2点比較から 6点単調系列に強化 | 2026-07-28 | 有（塔全段の動的再検証） |
| R2 | C_R は「channel capacity」（旧イントロ）／推定量未開示 | 定義 | **PARTIALLY→修正** | A指摘: 実装は40ステップ記録の最終1/4時間平均で深さとともに減衰（定常でない）。scripts/referee_audit.py part(a): 深さ40/80/160 で collective 欠損 −0.27/−0.34/−0.33 と持続 → fixed-depth retained information と再定義し推定量・深さ頑健性を本文/App B に開示 | 2026-07-28 | 有（深さ2×/4×再計算） |
| R3 | 「below the thermal band at all p」（旧 3.1/Fig1） | 数値 | **CONTRADICTED→修正** | A指摘＋JSON照合: local p=0.14 (0.0212 vs 0.0221±0.0051), p=0.16 はバンド内。「mean 以下は全 p、バンド以下は collective 全 p・local p≤0.12」に修正 | 2026-07-28 | 有 |
| R4 | spin-1 local「decays and changes sign as p grows (L=6,8)」（旧 3.6） | 数値 | **CONTRADICTED→修正** | A/B指摘: L=8 は全 p で正。B指摘の n=5 も確認（kthermal デフォルト6・プール5）→ L=8 を 20 ペアで再実行: dCR=+0.20/+0.10/+0.08（SEM 0.05–0.07）。L=6 のみ符号反転。本文を size-dependent の全面開示に修正、「no systematic advantage」を撤回し「大 L の運命は未解決」と明記。abstract も修正 | 2026-07-28 | 有（20ペア再実行） |
| R5 | 「volume-to-area crossing p_c≈0.05 を同定」（旧 App E） | 数値/事実 | **CONTRADICTED→修正** | B指摘＋JSON照合: S/(L/2) は全 p で L 単調減少（交差なし）、min-spread は p=0.10/0.14 とほぼ縮退。「交差は解像できず、p≈0.05 は最急変化スケール」に修正、γ_c 定量比較は撤回 | 2026-07-28 | 有 |
| R6 | extensive 符号の選択規則（E=0 混入・App A と不整合・再現不能グリッド） | 事実 | **PARTIALLY→修正** | A/B指摘: top-overlap 選択が E=0 塔状態を含む。referee_audit part(c): E=0 除外でも密度 0.661/0.381/0.104 vs default 0.674/0.393/0.101 — 結果不変。App I に選択規則・対照とも開示。plot_extensive.py の glob クラッシュ修正、extensive.py の ps グリッドを出荷 JSON と一致させた | 2026-07-28 | 有（除外対照実行） |
| R7 | 「scrambling が保護する」の因果主張 | 機構 | **SCOPED** | A/B 一致指摘: OTOC 等の動的カオス指標は未測定。2.2 に操作的定義（ETH 固有状態構造の意味）と限界を明示、結論にも限定句。実験的介入は未実施のまま（限界として開示） | 2026-07-28 | 部分（対照系は未実施） |
| R8 | 「decisively」= DFS gap（旧 abstract） | 表現 | **CONTRADICTED→修正** | B指摘: −0.179/0.102=1.8σ。independent seed 再実行で −0.10/−0.08/−0.06（符号頑健・大きさ変動）→ 「decisively」削除、σ と seed 感度を 3.5 に開示 | 2026-07-28 | 有（独立シード再実行） |
| R9 | best-pair 頑健性（新規） | 数値 | **SUPPORTED** | referee_audit part(b): 正エネルギー塔の全ペア走査（L=10,14, 両チャネル, p=0.10）で最良ペアも熱的平均未満（0.784 vs 0.865 collective L=14）→ 3.3 に追加 | 2026-07-28 | 有 |
| R10 | 熱的 Var J² アンサンブル「mean 6.1」（旧 3.5） | 数値 | **PARTIALLY→修正** | B指摘: 20値中カイラル縮退の重複1組 → 実効19状態、dedup mean 5.5。本文「5.5, 19 distinct states」に修正 | 2026-07-28 | 有 |

## 追記（2026-07-28 敵対的パネル第2回 Round 2 後の是正、S17続き）
査読者A=Codex・B=Opus とも「最も否定的な査読者」として改訂稿を再攻撃。指摘は全件ファシリテーターが再計算で裏取り。
| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| R11 | fine-J² の段スキャンが「欠損は過剰分散に追随」を支持（R1 の読み） | 機構 | **CONTRADICTED→修正** | B指摘＋照合: J² スペクトルは実質非縮退（987値・ギャップ>0.5 が6個）→ fine 分解能では任意の2次元符号が1発で崩壊し、スカー C_R は全段 13 桁一致（0.245/0.033/0.015 = 未測定確率）。段間変動は熱的側の統計のみ。3.5 を「2層構造」（構造的不可能性＋多重項分解能での検証）に全面書き換え | 2026-07-28 | 有（scar C_R の段非依存を確認） |
| R12 | multiplet-binned Casimir（新規, scripts/pure_rung_dfs2.py） | 数値 | **NEW RESULT** | J² を最近接 j(j+1) で5ビン化した物理的測定では、canonical 段は依然負け（−0.01/−0.11/−0.17）だが E=5.34 は +0.18/+0.25/+0.20、E=6.57 は +0.02/+0.03/+0.04 で**救済成立**。「No Casimir measurement can be a true DFS for approximate scars」を撤回→「混成が最大の（物理的にアクセスされる）段では失敗、純粋段は救済可能」に | 2026-07-28 | 有（ビン幾何の交絡も開示） |
| R13 | Round-1 の段スキャンの熱的プールにスカー自身が混入 | 数値/事実 | **CONTRADICTED→修正** | B指摘＋照合: scar_mask は外側 FSA 段を含まないため E=6.57/7.71 のプールにスカー固有状態が混入（z2_ov 0.006<0.02）。FSA 最近接状態を明示除外した pure_rung_dfs2.py で全段再計算。孤児だった pure_rung_thermal_var.json も同スクリプトに統合し重複除去（分散比 6.9/4.8/4.4/3.1、n=20 distinct）。E=7.71 は相異パートナー4個のみ→動的比較から除外と明記 | 2026-07-28 | 有（クリーン再実行） |
| R14 | 「independent rerun with different seeds」（R8 の修正文） | 事実 | **CONTRADICTED→修正** | B指摘: dfs_rescue は窓±0.3・zip ペア規則、pure_rung は窓±0.5・シャッフル規則 — シードだけの差ではない。fine-J² の窓感度を固定シードで実測: ±0.3 → −0.050/−0.035/−0.023, ±0.5 → −0.161/−0.135/−0.088（符号は4構成すべて負、大きさは3–4×変動）。本文訂正＋App C に新小節 | 2026-07-28 | 有（窓×シード分離実測） |
| R15 | 3.3「the deficit is a property of the tower」 | 事実 | **CONTRADICTED→修正** | B指摘: 走査は overlap-mask の中心段のみ（外側 FSA 段を含まず）、かつ canonical 整合の単一アンサンブルとの比較。クリーンプールの localZ では純粋段が低レートで有意に勝つ（E=6.6: +0.099, dirty +0.133 z=7.2）→「混成した中心段の性質」にスコープ、純粋段の挙動を明示参照 | 2026-07-28 | 有 |
| R16 | 序論「in every case」・結論「retain no advantage」・abstract (7) | 表現 | **CONTRADICTED→修正** | 両者指摘: canonical スコープへ統一（「the canonical scar code」「physically realized scar subspaces」）。結論の spin-1 文を 3.6 と整合（低レート優位・サイズ運命未解決） | 2026-07-28 | — |
| R17 | 深さ頑健性: local p=0.10 の "+0.000" | 数値 | **PARTIALLY→修正** | 深さ160 で +7×10⁻⁵（符号反転、両符号 C_R∼10⁻⁴で無意味）と明示。p=0.02 の深さスキャン新設: local 欠損 −0.144/−0.151/−0.127 で深さ安定 → 「情報が残る領域では深さ頑健」と正確化 | 2026-07-28 | 有（低レート深さスキャン） |
| R18 | ±1σ バンドによる符号判定 | 統計 | **PARTIALLY→修正** | 階層ブートストラップ（ペア再標本化＋軌道ノイズ伝播）を headline 3点に適用: L=14 local [−0.056,−0.024], collective [−0.317,−0.224], L=12 local [−0.042,−0.012] — 全てゼロ排除。バンドは記述統計と明記（scripts/uncertainty_audit.py） | 2026-07-28 | 有 |
| R19 | Fig 2 の L=16 が別の二重項パートナー | 数値 | **PARTIALLY→開示** | B指摘確認: L=16 は overlap 順位反転で 2.639 を選択。両パートナーで再計算: canonical −0.066/−0.306, partner −0.034/−0.150 — 符号頑健・大きさ2×変動。Fig 2 キャプションに開示（scripts/l16_partner_check.py） | 2026-07-28 | 有（両パートナー実測） |

## 追記（2026-07-28 Nature級パネル第3回後の是正、S17続き）
5軸採点: A=Codex 6.5/6.0/6.0/7.0/5.5、B=Opus 5/6/6/5/4（いずれも「専門誌が適正、Nature級未達」で一致）。
| # | claim | 種別 | 判定 | 出典 | 確認日 | 反証探索 |
|---|---|---|---|---|---|---|
| R20 | 旧タイトル「Scrambling, not athermality, protects...」 | 表現/機構 | **CONTRADICTED→改題** | 両者一致（確度88/97）: localZ の純度スキャンは純粋（=より athermal な）段ほど保護が良い単調系列（−0.069→+0.099, w=0.53→0.81, z≈7）で、タイトルの向きと逆。新タイトル「Algebraic leak and thermal hybridization, not athermality, defeat quantum many-body scar codes under generic measurement」、新節 3.6+主図 purity_trend.pdf に昇格（Opus P1: 追加計算ゼロの再フレーム） | 2026-07-28 | 有（クリーンプール再計算で傾向維持） |
| R21 | 隣接段 canonical 符号 × fine-J²（新規, uncertainty_audit --part-c） | 数値 | **NEW RESULT** | fine-J² でスカーが有意に勝つ: dCR=+0.19/+0.15/+0.13, 95%CI 全てゼロ排除（独立シード +0.189 再確認）。2チャネル基準の予言どおり（BC=0.958 高重なり＋小リーク）。abstract を「every generic measurement; su(2)適合 Casimir のみ逆転」にスコープ、App C に encoding 依存小節 | 2026-07-28 | 有（独立シード再現） |
| R22 | binned-Casimir「純度依存救済」（R12 の読み） | 機構 | **CONTRADICTED→撤回** | Opus P3 の binning 対照（nature_panel_fixes --part a）: 等幅5ビン/±1シフトで結果が完全に入替（−1シフトで canonical 含む全対が勝ち +0.10〜+0.31、+1シフトで救済消滅）。粗視化 Casimir はビン幾何支配 — 純度・分散の結論を支持しないと明記。purity 図は localZ 単独に変更 | 2026-07-28 | 有（3種の binning 実測） |
| R23 | 統計・スコープ補完 | 数値 | **SUPPORTED（補強）** | (i) 5シード監査: L=12/14 local・L=14 collective 全シード負（プール −0.024/−0.033/−0.273）→ P6 の選択的報告疑義を解消。(ii) p=0.02 Lスキャン: 情報が残る領域で local 欠損 −0.16→−0.38 と L 単調成長 → Fig 2 を2パネル化（P4）。(iii) 相図の非単調 ℓ 依存＋プロトコル差を開示（P5=Codex#5, 確度100）。(iv) 「last quarter」=記録点20%/時間10% と正確化。(v) mechanism のリーク反例（leak 1.78, C_R 0.79）開示。(vi) App C の非同梱 20-pair 値→出荷12-pair 監査値に差替 | 2026-07-28 | 有 |
