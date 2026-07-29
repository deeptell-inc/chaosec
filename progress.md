---
asset: progress
version: 1.0.0
生成元入力: /research-methodology（P1 起点・既存プロジェクト再開）
依存工程: なし（トラッキング）
生成日: 2026-07-10
---

# progress — 研究方法論トラッキング

起点: **P1（質問起点）**。初回入力「測定誘起相転移におけるカオス性を誤り訂正能力として
量子チャネル容量で定量化 — スカーは熱的より情報保護に優れるか？既出か？」

ワークスペース: `/Users/deeptell01/Documents/alterego/personal/chaosec/`

## 工程到達状況

| 工程 | 状態 | 主成果物 | 備考 |
|---|---|---|---|
| S1 論文検索 | done | (会話内) | openalex/web/arXiv 精読 |
| S2 情報収集 | done | (会話内) | 先行研究の構造化 |
| S3 理論基礎 | done | docs/RESULTS_SUMMARY.md §4-5 | 2チャネル criterion | **S17 未** |
| S4 テーマ策定 | done(承認済) | (会話内) | 反証テーゼで進行 |
| S5 理論実装 | done | scarcode/ | pytest 11/11 |
| S6 データ収集 | done | results/ | 図7・JSON |
| S7 論文執筆 | done | paper/main.tex (5p) | **S17 未** |
| S8 構成 | done | 7要素abstract・大小大 | |
| S9 補完 | done | (査読対応で補填) | **S17 未** |
| S10 投稿先 | done | PRX Quantum 決定 | |
| S13 パッケージ | done | scarcode 0.1.0 | PyPI/twine 検証済 |
| **S17 事実ゲート** | **done** | claims-ledger.md, factcheck-report.md | CONTRADICTED 1件修正・DoD通過 |
| S16 精度最大化 | **done** | (progress.md 内レビュー記録) | 用語統一・空節除去・DoD通過 |
| S12 投稿バンドル | **done（承認待ち）** | paper/submission-bundle/ | 要件11項目✓・Popular Summary作成・**実投稿は承認ゲート** |
| S11 プレプリント | 任意 | | S10 判断でスキップ可 |
| S14 査読対応 | 未（投稿後） | | |

## 次工程
1. **S17**: manuscript の claim 抽出 → 優先度付け → 一次情報照合 → claims-ledger 追記（進行中）
2. S16: 各成果物の批判的レビュー1周
3. S12: 投稿バンドル作成（**承認ゲート**）

## S16 レビュー記録（2026-07-10, target: paper/main.tex, supplement.tex）
- 指摘1（一貫性/中）: S17 で M を「秩序変数」に厳密化した結果、abstract・conclusion の
  "emergent-su(2) generator" と不整合 → 両所を "order parameter" に統一。
- 指摘2（体裁/低）: 空の `\begin{acknowledgments}` が空セクション見出しを生成 →
  コメントアウト（著者が投稿前に資金謝辞を追記）。
- 事実性の指摘なし（S17 で処理済み）。論理骨格の問題なし（→S8差し戻し不要）。
- 対応後 main/supplement 再コンパイル: エラー0・未定義引用0。DoD 充足。

## 保留中の承認
- S12 投稿直前（PRX Quantum）— S16/S17 通過済。**実投稿前に要ユーザー承認**（本スキルはここで停止）。

## S14/S10 再訪: PRX Quantum デスクリジェクト → Quantum へ（2026-07-27）
- PRX Quantum は編集段階リジェクト（選択性基準。技術的批判なし。APS Open Science 移管オファーは辞退）。
- ユーザー決定: **Quantum (quantum-journal.org)** へ再投稿、arXiv 先行（S11 が必須化）。
- 成果物: `paper/quantum/` — quantumarticle 版 main.tex（11pp、Supplement を Appendix A–I に統合、
  エラー0）、cover_letter（Quantum宛）、`arxiv-v1.tar.gz`（自己完結・単体コンパイル検証済）、
  SUBMISSION.md（手順書）。refs.bib は全34件に DOI 付与
  （非APS 8件+新形式APS 2件は Crossref で一次検証; Paviglianiti=10.1103/jf2f-wqkx,
  Qian=PRB 112, L180301, 10.1103/b8tq-z48t）。
- **承認ゲート（未実施）**: arXiv アップロードと Scholastica 投稿はユーザー操作。

## Codex 敵対的レビュー（2026-07-27, /codex:adversarial-review --base HEAD~1）
検出1件 [high]: 本文「same two energies」に対し実装は `thermal_ensemble(window=0.5)`
（実オフセット平均0.22・最大0.47, L=14）— エネルギー整合の過大主張＋許容窓の未開示。
是正: scripts/energy_window_robustness.py 新設（窓±0.5/±0.25/±0.10 の再計算＋オフセット
分布＋C_R–offset 相関）。結論は窓非依存（ΔC_R local −0.033→−0.031, collective −0.25→−0.21,
最タイト窓でも z≈2.4/2.8）、C_R と残差オフセットは無相関。本文（quantum版・PRXレガシー版）
とS3/Appendix C に許容窓の明示開示＋頑健性段落を追加。ledger X1 追記。

## 敵対的パネル第2回・Round 2（2026-07-28, 最も否定的な査読者→修正）
- A=Codex・B=Opus が改訂稿を再攻撃（Round 1 の蒸し返しは禁止と指示）。主要検出:
  (1) fine-J² は実質非縮退スペクトルで任意の2次元符号を1発破壊 — スカー C_R が全段
  13桁一致（未測定確率）で、R1 の「欠損は分散に追随」は熱的側ノイズの読み違え。
  (2) 純度を上げると localZ の符号が反転（E=6.6 で z=+7.2）。
  (3) 結論に旧文残存（自己矛盾）。(4) ±1σ バンドは検定でない。(5) 「different seeds」
  は誤記述（実際は窓±0.3→±0.5＋ペア規則も変更）。(6) R1 熱的プールにスカー混入・
  孤児 JSON 再発。(7) Fig2 の L=16 は別二重項パートナー。
- 対応計算: pure_rung_dfs2.py（FSA除外クリーンプール＋**多重項ビン化 Casimir**＋
  窓感度）→ binned J² で canonical 負け/E=5.3 は +0.25 で**救済成立**（非単調、
  ビン幾何が交絡）。uncertainty_audit.py（階層ブートストラップ CI 3点全てゼロ排除、
  p=0.02 深さスキャンで local も深さ安定）。l16_partner_check.py（両パートナーで
  符号頑健）。
- 本文: 3.5 を2層構造に全面改稿（構造的不可能性＋多重項分解能での純度依存救済）、
  「No Casimir measurement can be a DFS」撤回、abstract/序論/結論を canonical/
  physically-realized スコープに統一、App C に J² 窓感度＋プール衛生の小節新設。
  ledger R11–R19。abstract 1918/1920。最終 14pp・クリーンルーム両バンドとも
  エラー0・pytest 11/11。
- 注: レガシー PRX 版 (paper/main.tex, supplement.tex) はパネル改稿を反映していない
  （投稿先は Quantum 版のみが正本。レガシー版は記録として凍結）。

## 敵対的パネル第2回・Round 1（2026-07-28, /adversarial-panel: 批判的査読者→修正）
- 構成: A=Codex CLI（再現実行つき）, B=Claude Opus（独立）。各自「PRX の最も批判的な査読者」
  として Top-5 を独立生成 → ファシリテーターが全指摘を JSON/再実行で裏取り → 統合して修正。
- 最重要発見（B-1, 検証済み）: Z2-overlap 上位 L+1 選択は塔の中心段＋二重項に集中し、
  canonical 段 (E=1.33/2.74) は塔で最も混成した段。Var J²=32.5 は混成の帰結で、
  FSA 純度とともに 47.6→0.89 に減少（scripts/fsa_purity_audit.py）。
- 決定的追加計算（scripts/pure_rung_dfs.py）: 全整合可能段の chiral 対で J² 監視 →
  **全段でスカー負け**（dCR −0.16→−0.01、過剰分散比 4.3→1.6 に追随）。反証は同定に頑健、
  機構は「excess variance が制御」の 6 点単調系列に強化。スピン1のゼロ分散端点と接続。
- 新事実: 純粋段 (E≈6.6) の localZ 低 p で dCR=+0.13（減衰）。スピン1 L=8 の 20 ペア
  再実行（旧5ペア）で local dCR=+0.20/+0.10/+0.08 全 p 正 — 「changes sign」を撤回し
  「exact スカーの局所低レート優位の大 L 運命は未解決」と正直に再スコープ（abstract も）。
- その他修正: C_R 推定量開示＋深さ 40/80/160 頑健性、γ_c「交差なし」書き換え、
  "below the band at all p"・"decisively"(1.8σ)・符号付きシフト相関・L18 パラメータ差・
  s_1 Spearman 数値・熱的分散カイラル重複 (6.1→5.5) を修正/開示。best-pair 全走査で
  最良ペアも負けることを 3.3 に追加。plot_extensive.py クラッシュ・extensive.py グリッド修正。
- ledger R1–R10。本文 13pp・abstract 1919 文字（プレーン 1900、限界 1920）・エラー0。
- Round 2（最も否定的な査読者×2）を改訂稿に対して実行予定。

## 章・節見出しの導入（2026-07-28）
- これまで本文の小見出しは全て `\paragraph{...}` の行内見出しで、番号も目次項目も
  付かなかった。Quantum は分量制限が無く Appendix を本体に統合した11ページ構成なので、
  番号付き見出しで navigable にする。
- `\subsection` へ格上げ（10件）＋新設1件:
  2.1 Model, encoding, and monitored dynamics（新設。従来この節は無題で始まっていた）
  2.2 A model-independent criterion
  3.1 Thermal codes win: the apparent scar advantage is a baseline artifact
  3.2 The disadvantage persists to the largest accessible size
  3.3 Even the maximal scar code loses（新設。extensive 符号の議論が見出し無しで
      3.2 の続きに埋もれていた）
  3.4 Mechanism / 3.5 DFS rescue fails / 3.6 second model / 3.7 calibration /
  3.8 experimental accessibility、Appendix C.1 Energy-matching tolerance
- 見出し文は「主張を述べる文」という従来の方針（one-message-per-figure）を維持し、
  末尾のピリオドのみ落とした。章立ては 1 Introduction / 2 Model and diagnostics /
  3 Results / 4 Conclusion、Appendix A–I。
- 併せて既存の組版バグ2件を修正: ソース行末のハイフン（`protected-`↵`information`、
  `Scar-minus-`↵`thermal`）が出力で「protected- information」と余分な空白を生んでいた。
- 再ビルド: quantum 11pp / arxiv バンドル tar.gz・zip ともクリーンルーム 11pp・エラー0 /
  legacy main 7pp（見出し分で 6→7pp）/ submission-bundle 6pp / supplement 3pp。
  10pt超の overfull hbox は 0。

## Zenodo レコード 21336840 メタデータ修正（2026-07-28, 適用済み）
- 積み残しだった公開レコードの誤メタデータを是正。DOI は不変（10.5281/zenodo.21336840）。
  - title: 旧題「Chaotic states outperform...」→ 現行題「Scrambling, not athermality,...」
  - description: 旧題＋死んだリンク hwakaura/scarcode → 現行題＋deeptell-inc/chaosec。
    主張も本文スコープに合わせ「under every generic measurement」→「under every
    measurement we test ... PXP scar subspace」＋exact-scar の但し書きを追加。
  - notes: 「submitted to PRX Quantum」→「submitted to Quantum (quantum-journal.org)」
  - related_identifiers: GitHub リポジトリを isSupplementTo で追加（従来 null）
- 手段: `zenodo_deposit` に公開済みレコードの編集機能を追加（`--edit-record ID`）。
  actions/edit → PUT metadata → actions/publish。ライブのメタデータを取得して
  差分キーだけをパッチする方式（doi/publication_date/access_right は触らない）、
  PUT 失敗時は actions/discard で自動ロールバック。`--dry-run` は読み取りのみで差分表示。
- **検出した別問題 → 新バージョン発行で解決（ユーザー承認済）**: 公開レコードに載っているファイル
  `scarcode-repro-0.1.0.tar.gz`（7/13付）は**現行原稿を再現できない**。
  本文が参照する 5 スクリプト（energy_window_robustness / casimir_variance /
  kl_static / predictor / restyle_figures）が欠落し、Codex 修正も未反映。
  公開済みレコードのファイルは凍結されているため、差し替えには**新バージョン発行**
  （新しい version DOI が発行される）が必要。候補 `scarcode-repro-0.1.1.tar.gz` を
  `git archive HEAD` で作成し、クリーン venv で `pip install -e .` + pytest 11/11、
  5 スクリプト全存在を検証済み。
- **v0.1.1 発行済（2026-07-28）**: 新 version DOI = **10.5281/zenodo.21642056**
  （record 21642056、旧版から継承したファイルを削除して 0.1.1 を差し替え、metadata に
  version="0.1.1"）。concept DOI 10.5281/zenodo.21336839 は 21642056 へ解決することを確認。
  本文・README・DECLARATIONS・SUBMISSION.md の引用を全て新 DOI に差し替え、
  quantum 11pp / arxiv 両バンドル（tar.gz・zip ともクリーンルーム 11pp・エラー0・
  新DOI反映確認）/ legacy 6pp / submission-bundle 6pp を再ビルド。
  初版 21336840 は「スクリプト5件欠落」の欠陥版なので今後引用しない。
- ツール追加機能: `--new-version ID`（actions/newversion → 継承ファイル削除 →
  アップロード → metadata PUT（doi は落とす）→ publish）。`--dry-run` で
  ファイル置換とメタデータ差分を事前表示。オフラインテスト 19 件 pass。

## 投稿バンドル整備 zip版 + PyPI 配布物再ビルド（2026-07-28）
- Finder で作られた `paper/quantum/arxiv.zip` は arXiv に出せない構成だった:
  ネストした `arxiv/` ディレクトリ、`__MACOSX/._*` 12件、`main.pdf`（arXiv はソース
  パッケージ内の完成PDFを拒否）、`.aux/.log/.out/.blg`（AutoTeX 誤動作要因）。
- 対処: `arxiv-v1.zip` を新規作成（`zip -j -X`、tar.gz と同一の11ファイル・フラット）。
  展開してクリーンルームで pdflatex 2回 → 11pp・引用34件解決・エラー0 を確認。
  SUBMISSION.md に「Finder で zip しない」注意と zip 生成コマンドを追記。
- PyPI: dist/ が 7/10 付でパネル+Codex 修正（states.py の `return_indices`）を含んで
  いなかったため再ビルド。`twine check` 両アーティファクト PASSED、新規 venv への
  wheel インストールで import・`return_indices` 存在を確認。PyPI 上に scarcode は
  未登録（/pypi/scarcode/json が 404）なので 0.1.0 のまま初回アップロード可。
  **アップロードは未実施（要ユーザー操作）**。

## Abstract 字数制限対応（2026-07-28）
arXiv の abstract 欄上限 1920 文字に対し 2054 文字（プレーン換算 2020）で超過していた。
7要素構造（大→小→大）と全数値主張を保持したまま 1869 文字（プレーン 1850）へ圧縮:
要素(1)"entanglement" 冗語削除、(2)スカー定義を同格節に統合、(3)主語を代名詞化、
(5)"scar disadvantage"→"deficit"・関係節を制限節化、(6)spin-1 文と機構文を統合、
(7)"These results establish"→断定形。quantum版・arxiv版・PRXレガシー版の3ファイルに反映。
貼付用プレーンテキストを `paper/quantum/abstract.txt` として追加（SUBMISSION.md に手順記載）。
再ビルド: quantum 11pp / arxiv クリーンルーム 11pp・引用34件解決 / legacy 6pp、いずれもエラー0。
バンドル再生成時の落とし穴2件を SUBMISSION.md に明記（arxiv/ で bibtex 実行禁止、
tar は明示ファイル列挙 — `--exclude='*.pdf'` は図5件を落とす）。

## 敵対的パネル（2026-07-16, /adversarial-panel）
2名（Sonnet=再現検証・Opus=文献/論理、3ラウンド）。合意: 荷重数値約20項目は4桁一致で再現、文献帰属・数学は健全。検出欠陥5件（18.1孤児、L=12 band文言、spin-1≲0.1、KL比孤児、γ_c循環説明）→ **全件修正済み**（casimir_variance.py・kl_static.py新設、本文/補足/カバレター/criteria修正、全6文書クリーン再コンパイル）。パネル確度: 修正前82/100 → 修正後の想定〜95。

## Nature級パネル第3回（2026-07-28, 5軸採点→修正・データ補完）
- 採点: Codex 6.5/6.0/6.0/7.0/5.5、Opus 5/6/6/5/4。合意判定「専門誌（Quantum等）適正」。
- 最大の改稿（Opus P1・両者収束）: localZ 純度スキャンを主結果に昇格（新節3.6+新図
  purity_trend.pdf）、**改題**「Algebraic leak and thermal hybridization, not athermality,
  defeat quantum many-body scar codes under generic measurement」。
- 新事実2件: (1) 隣接段 canonical 符号は fine-J² でスカー勝ち（+0.19, CI排除、基準の予言どおり）
  → abstract を generic スコープに。(2) binned-Casimir の救済はビン幾何アーティファクト
  （±1シフトで完全入替）→ R12 を撤回、§3.5 をストレステスト込みの正直な記述に。
- データ補完: 5シード監査（全点全シード負）、p=0.02 Lスキャン（local 欠損 −0.16→−0.38 と
  L 成長、Fig 2 を2パネル化）、Casimir チャネル階層 CI、binning 対照3種。
- その他: 相図の非単調 ℓ 依存を開示（「deepens with ℓ」撤回）、リーク反例開示、
  推定量記述の算術修正、App C 数値の出所統一。ledger R20–R23。
- 最終状態: 15pp・abstract 1919/1920（プレーン1899）・エラー0・pytest 11/11・
  バンドル12ファイル（purity_trend.pdf 追加）クリーンルーム検証済み。
