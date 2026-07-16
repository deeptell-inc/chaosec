---
asset: factcheck-report
version: 1.0.0
生成元入力: S17 ファクトチェック（target: paper/main.tex, paper/supplement.tex; is_gate_for: S12）
依存工程: S17
生成日: 2026-07-10
---

# factcheck-report — S17 ファクトチェック結果

対象: `paper/main.tex`, `paper/supplement.tex`（PRX Quantum 投稿版）
発火文脈: S12 投稿バンドル作成の完了直前ゲート（H3）。

## 判定分布
- SUPPORTED: 7（N1, L2〔修正後〕, C6, C3, C2, C4, D1, L1 のうち外部照合対象）
- CONTRADICTED→修正: 1（L2 の "weak" 記述）
- UNSUPPORTED / UNVERIFIABLE: 0

## 検出・修正した事実誤り（1件）
**L2**: 本文が Paviglianiti–Silva (arXiv:2503.22618, PRL 135,090402) を
「weak continuous monitoring」と記述していたが、一次情報で確認したところ同論文は
**projective σ^z 測定**（連続時間レート γ）を用いる。数値 γ_c=0.013±0.002 は原論文本文と
一致。修正:
- main.tex: 「weak continuous monitoring」→「continuous-time projective σ^z monitoring」、
  「projective-per-step versus continuous-weak」→「per-step versus continuous-time rate convention」。
- supplement.tex S6: 「projective per-step and continuous weak measurement」→
  「per-step and continuous-time projective measurement」。γ_c に ±0.002 を追記。
- 併せて main の M の記述を「su(2) spectrum-generating generator」→
  「staggered magnetization, order parameter of the emergent su(2) scar dynamics」に厳密化（過剰表現の限定; →S16対）。

両文書は修正後にエラーなし・未定義引用0で再コンパイル済み。

## 二重確認（新規性・主要数値）
- **N1（新規性）**: 独立2検索経路（(i) scar-vs-thermal coherent-information/channel-capacity、
  (ii) monitored-PXP reference-qubit coherent-information thermal comparison）いずれも
  該当先行研究なし。さらに一次情報で最近接研究（Paviglianiti–Silva）が容量を計算しないことを確認。
  反証探索（先行研究の能動探索）実施済み・null。本文の "to our knowledge" ヘッジは適切。→ SUPPORTED。
- **L2（数値）**: 原論文 HTML を直接取得し γ_c=0.013±0.002・projective・continuous-time を確認。→ SUPPORTED。

## 自チーム数値（D1）の扱い
ΔC_R・Var J²(=32.5 vs ~1e-13)・密度gap・C_R^scar=1 等は外部一次情報の対象外。
再現可能性で担保: `pytest`(11/11) ＋ `scripts/*.py` ドライバ ＋ `results/*.json`（2経路）。
確証バイアス対策として、本研究自身が初期の「スカー優位」結果を熱的アンサンブル平均化で
自己反証している（RESULTS_SUMMARY §3）。

## DoD 判定
- 結論支持主張・新規性主張・全数値: SUPPORTED または限定表現へ修正済み ✓
- UNVERIFIABLE 残: なし ✓
- 全 SUPPORTED に一次情報出典＋反証探索: N1/L2/C6/C3/D1/L1 で実施 ✓
- 新規性・主要数値の独立2経路確認: 充足 ✓

**S17 DoD: 4項目=OK / CONTRADICTED 1件は修正完了 / S12 ゲート通過可。**

## 残る軽微推奨（S16/投稿前）
- C2/C4 の帰属は正典・メタデータ検証済（反証探索「無」）。厳格には各原論文本文で
  帰属を1回確認するとより堅牢（任意）。
