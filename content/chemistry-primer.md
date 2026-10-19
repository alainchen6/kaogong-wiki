# 化学模拟速查

这一页是“够用就好”的知识地图：你不需要先成为计算化学专家，但需要知道每个参数在物理上代表什么。教程里遇到概念时可以回来查。

## 1. 我们到底在算什么？

经典分子模拟不解电子波函数，而是把原子/分子看成粒子，用**经验力场**描述它们之间的相互作用，然后：

- **能量最小化**：找局部低能结构；
- **MD**：按牛顿方程积分，采样温度/压力下的构象；
- **MC / GCMC**：按统计力学概率接受移动/插入/删除，采样平衡分布；
- **分析**：从轨迹或构型算 g(r)、MSD、密度、吸附量。

Kaogong 把这些步骤拆成模块；LAMMPS 负责实际积分/采样。

> [!CHEMISTRY]
> “力场”不是量子化学。它用简单的解析函数近似原子间相互作用，计算快、能处理百万原子，但精度取决于参数。换力场，数值会变；这不是 bug。

## 2. 单位制：metal

平台默认使用 LAMMPS 的 `metal` 单位：

| 量 | 单位 |
| --- | --- |
| 长度 | Å |
| 能量 | eV |
| 时间 | ps |
| 温度 | K |
| 压力 | bar |
| 质量 | g/mol |
| 电荷 | e |

常见换算：

```text
1 kcal/mol = 0.0433641 eV
1 eV = 96.485 kJ/mol
1 bar = 0.986923 atm = 100 kPa
1 fs = 0.001 ps
```

> [!WARNING]
> 教程里有时写“LJ 单位”的公式（ε=1、σ=1、T*=1）。Kaogong 的示例把 Ar 的 ε/σ 换算成 eV/Å，仍用 metal 单位跑；物理等价，但输入数字不同。

## 3. Lennard-Jones 势

最常见的非键相互作用：

<div class="equation">E<sub>LJ</sub>(r) = 4ε [ (σ/r)<sup>12</sup> − (σ/r)<sup>6</sup> ]</div>

- **σ**：势能为 0 的距离，近似“原子直径”；
- **ε**：势阱深度，近似“结合强度”；
- 最小值在 `r = 2^(1/6) σ ≈ 1.122 σ`，能量 `−ε`；
- 通常截断到 `2.5σ` 或 `3σ`。

Ar 的常用参数：`ε/kB ≈ 119.8 K`，`σ ≈ 3.405 Å`，换算成 `ε ≈ 0.0103 eV`。

多组分之间常用 **Lorentz-Berthelot** 混合：

```text
σ_ij = (σ_i + σ_j)/2
ε_ij = sqrt(ε_i ε_j)
```

> [!TIP]
> 在平台里，`Lennard-Jones` 模块的 `components` 就是填 `元素:ε:σ`，例如 `Ar:0.0103:3.405`；留空则所有类型共用一组 ε/σ。

## 4. EAM：金属的多体势

金属里的电子云是“集体”的，简单两两 LJ 不够。EAM（Embedded Atom Method）把能量写成：

<div class="equation">E = Σ<sub>i</sub> F<sub>i</sub>(ρ<sub>i</sub>) + ½ Σ<sub>i≠j</sub> φ<sub>ij</sub>(r<sub>ij</sub>)</div>

- `ρ_i = Σ_j ρ_j(r_ij)`：i 处的电子密度；
- `F_i(ρ_i)`：嵌入能；
- `φ_ij`：两体排斥/吸引。

EAM 参数通常以势文件形式提供（如 `Cu_u3.eam`）。平台从 `vendor/lammps/potentials` 或 `MATFORGE_POTENTIALS_DIR` 解析裸文件名，运行时复制到工作目录。

> [!CHEMISTRY]
> EAM 是金属/合金的常用势，不适合共价分子或 MOF 框架。它能较好地描述 Cu 的晶格常数、弹性、表面能等。

## 5. Tersoff：共价键的键序势

共价材料（Si、C、GaAs 等）需要“键强随局部环境变化”的模型。Tersoff 的形式：

<div class="equation">E = ½ Σ<sub>i</sub> Σ<sub>j≠i</sub> f<sub>C</sub>(r<sub>ij</sub>) [ f<sub>R</sub>(r<sub>ij</sub>) + b<sub>ij</sub> f<sub>A</sub>(r<sub>ij</sub>) ]</div>

- `f_R`：排斥项；
- `f_A`：吸引项；
- `b_ij`：键序，取决于周围原子几何；
- `f_C`：截断函数。

Si 的金刚石结构、2.35 Å 近邻、3.84 Å 次近邻，都可以从 RDF 里读出来。

## 6. 周期性边界与晶胞

周期性边界条件（PBC）把盒子看成无限重复：

- 原子从左边出去，从右边进来；
- 计算距离用**最小镜像**（minimum image）；
- 盒子必须足够大，避免原子与自己的镜像相互作用。

平台用 `cell.matrix` 表示三个晶格矢量，支持立方、正交、三斜。LAMMPS 要求 restricted triclinic，所以运行前会把结构旋转到 `a` 沿 x、`b` 在 xy 平面；这是**旋转**，不改变距离和角度。

> [!WARNING]
> 3D 预览只画主晶胞，不自动画周期镜像。边界处的视觉不完整，但计算仍是周期的。

## 7. 系综：NVE / NVT / NPT

| 系综 | 固定 | 常见用途 |
| --- | --- | --- |
| NVE | N, V, E | 能量守恒、扩散测试 |
| NVT | N, V, T | 恒温结构/动力学 |
| NPT | N, P, T | 密度、热膨胀、相变 |
| μVT (GCMC) | μ, V, T | 吸附、孔道气体 |

- **控温器**：Nose-Hoover（常用，能正确采样正则系综）、Berendsen（快速弛豫但不等价）、Langevin（随机力+摩擦）；
- **控压器**：Nose-Hoover barostat；
- **时间步**：金属/共价体系通常 1 fs；LJ 流体可到 2–5 fs；太大导致能量爆炸。

NPT 的密度：

<div class="equation">ρ = (Σ m<sub>i</sub>) / V</div>

热膨胀系数：

<div class="equation">α = (1/V)(∂V/∂T)<sub>P</sub></div>

小体系的瞬时压力涨落很大，**看平均密度比看单帧压力更可靠**。

## 8. RDF：g(r) 怎么读

径向分布函数：

<div class="equation">g(r) = V / (N<sub>A</sub> N<sub>B</sub>) · ⟨Σ<sub>i∈A</sub> Σ<sub>j∈B</sub> δ(r − r<sub>ij</sub>)⟩ / (4πr² dr)</div>

直观理解：

- `g(r) = 0`：这个距离上不可能有原子（排斥核）；
- `g(r) = 1`：与理想气体相同；
- 峰：近邻壳层；
- 峰位：最可能的距离；
- 积分 `4πρ∫g(r)r²dr`：配位数。

晶体 RDF 是一系列尖峰；液体是宽峰后趋于 1；气体接近 1。

> [!WARNING]
> 平台成键可视化是按距离推断的，不是从 RDF 或拓扑来的。RDF 本身是数值积分，不是画图“看起来像”。

## 9. MSD 与扩散

均方位移：

<div class="equation">MSD(t) = ⟨ |r<sub>i</sub>(t) − r<sub>i</sub>(0)|² ⟩</div>

长时间扩散区：

<div class="equation">MSD(t) = 6 D t</div>

所以 `D = slope / 6`。平台目前输出 MSD 曲线，不自动拟合 D；你可以导出 JSON 自己拟合。

> [!TIP]
> 轨迹要用 LAMMPS 的 unwrap 坐标，否则原子跨越周期边界时 MSD 会出现假平台。平台当前分析使用最小镜像，适合短时间/致密体系；长扩散体系请用 `dump_modify unwrap yes` 的轨迹另行分析。

## 10. GCMC 与吸附等温线

巨正则系综固定化学势 μ、体积 V、温度 T。`fix gcmc` 做三件事：

1. 随机插入一个吸附质分子；
2. 随机删除一个；
3. 平移/旋转已经存在的分子。

插入接受概率大致为：

<div class="equation">P<sub>insert</sub> = min[1, (V/(N+1)Λ³) exp(β(μ − ΔU))]</div>

- `Λ`：热 de Broglie 波长；
- `ΔU`：插入前后的势能差；
- `μ`：由压力/逸度换算。

平台用 `pressure` 关键字，让 LAMMPS 从压力算 μ。吸附量：

<div class="equation">uptake [mmol/g] = n<sub>guest</sub> × 1000 / M<sub>framework</sub></div>

其中 `M_framework` 是晶胞内框架的摩尔质量（g/mol）。

> [!CHEMISTRY]
> 低压看“结合位点”，高压看“孔体积/饱和”。MOF 的吸附等温线常见 Type I（微孔）或 Type IV/V（介孔/呼吸）。ZIF-8 的 CH4 是典型微孔吸附。

## 11. 电荷与静电

MOF/极性气体不能忽略静电：

- 框架电荷（DDEC、QEq、拟电荷）；
- 吸附质电荷（CO2 的 C=+0.70，O=−0.35 等）；
- 短程测试可用 `coul/cut`；定量计算用 `coul/long` + `pppm`；
- 平台 `forcefield.library` 可选 `electrostatics=pppm`，自动生成 `lj/cut/coul/long` + `kspace_style pppm`；
- 电荷可 none/formal/manual/per_atom（CSV/DDEC 文本/文件）；QEq 求解器未内置，导入外部电荷即可。

> [!WARNING]
> `forcefield.library` 的 `formal` 电荷是元素级形式电荷，不保证中性；`manual` 允许你填文献电荷。净电荷不为 0 时平台会警告/中和，但中和只是数值处理，不是物理电荷模型。

## 12. 最小知识清单

如果你只记住五件事：

1. **力场决定物理**：LJ/EAM/Tersoff/UFF 各有适用边界；
2. **单位要一致**：平台默认 eV/Å/ps/bar/K；
3. **PBC + 足够大的盒子**；
4. **NVT 看结构，NPT 看密度，GCMC 看吸附**；
5. **RDF 看近邻，MSD 看扩散，等温线看容量/亲和力**。
