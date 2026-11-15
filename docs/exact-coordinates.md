# 5点Cosmohedron：有理数座標の凸十角形とcanonical 2-form

## 解いている問題

この研究ラボには、Cosmohedraの面の数・Hasse図・高次元への組合せ列挙が既にある。ただし、多面体の具体的な座標・支持超平面・canonical formの計算は空白だった。

今回、5点の**組合せ型**に対して以下を追加する。

1. 有理数座標で表した厳密な凸十角形。五角形の各頂点を切り落として実現する。
2. 各辺を単独の対角線または二つの非交差対角線による分割に対応付ける。ファセットは計10本。
3. 10本の支持半空間（A X + B Y + C >= 0）を出し、すべての頂点で正確に非負であることを検査。
4. 選んだ凸十角形のcanonical logarithmic 2-form F(X,Y) dX wedge dYを、隣接する辺の法線の行列式の和から構成。
5. 各辺の相対内部で、対応する一次極を掛けた値が有限かつ正であることを検査。辺の定義式を正の有理数倍してもFが不変なことをテスト。

## 操作と結果

```bash
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_coordinates.py
python -m research coordinates --output research/results/cosmohedron-5-coordinates.json
```

出力JSONは頂点座標、面の不等式、各辺と頂点の接続関係、非交差分割によるファセットラベル、面積、canonical 2-formの有理関数を含む。

数値シミュレーションやランダム探索ではない。SymPyの有理数と記号演算に基づく厳密な計算。

## 重要な制約

**この計算はCosmohedronの唯一の実現を与えるものではない。** 5点Cosmohedronと同じ面の組合せを持つ、具体的な凸十角形を一つ構成している。一般の正の幾何学ではcanonical formは選んだ埋め込みに依存するため、この式を宇宙論相関関数・波動関数、またはArkani-Hamedらの特定の運動学的構成と同一視しない。

6点以上の高次元Cosmohedraの不等式、projectivity、物理側の境界条件、canonical formの実現は別途研究を要する。論文の既知結果を確認することも、新しい定理の証明や新発見とは区別する。

## 次の検証仮説

- 5点の論文固有の不等式と、本実装の有理数座標系の間の正確な幾何学的関係を調べる。
- 6点の三次元Cosmohedronについて、既存の面束と整合する有理数座標・支持超平面を探す。
- 研究結果の来歴と証拠を研究台帳へ記録し、構成・単なる予想・数学的証明を区別する。

参考: [Cosmohedra](https://doi.org/10.1007/JHEP11(2025)029)、[Combinatorics of the Cosmohedron](https://arxiv.org/abs/2603.03425)。

