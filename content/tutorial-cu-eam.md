# 教程 2 · Cu 的 EAM 金属模拟

> **软件目标**：学会用 EAM 势文件、最小化、NVT，并看懂金属的 RDF/MSD。  
> **化学目标**：理解嵌入原子势、fcc 晶格、热振动与配位壳层。  
> **来源**：[LAMMPS `pair_style eam`](https://docs.lammps.org/pair_eam.html)；势文件 `Cu_u3.eam`（Foiles et al., *Phys. Rev. B* 33, 7983, 1986）。

## 你会学到

<div class="home-grid">
  <div class="home-card">
    <span class="card-tag">化学</span>
    <strong>金属不是 LJ 分子</strong>
    <p>EAM 的嵌入能/电子密度；fcc 的 12 个第一近邻；热振动让 RDF 峰变宽。</p>
  </div>
  <div class="home-card">
    <span class="card-tag">软件</span>
    <strong>势文件库 + EAM + NVT</strong>
    <p>选择 `eam` 变体、填势文件名、让平台自动 staging，读 RDF/MSD。</p>
  </div>
</div>

## 1. 化学背景：EAM 为什么适合金属？

金属中的价电子是离域的，不能用简单的两两 LJ 描述。EAM 把总能量写成：

<div class="equation">E = Σ<sub>i</sub> F<sub>i</sub>(ρ<sub>i</sub>) + ½ Σ<sub>i≠j</sub> φ<sub>ij</sub>(r<sub>ij</sub>)</div>

- `ρ_i = Σ_j ρ_j(r_ij)`：i 位置由周围原子贡献的电子密度；
- `F_i(ρ_i)`：把原子“嵌入”电子云所需的能量；
- `φ_ij`：两体相互作用。

关键点：一个原子的能量取决于**周围环境**，所以 EAM 能描述配位数变化、表面、缺陷、弹性，而简单 LJ 很难。

Cu 的 `Cu_u3.eam` 是 setfl 格式的 EAM 势，包含：

- 晶格常数约 3.615 Å；
- fcc 结构；
- 第一近邻 2.556 Å，第二近邻 3.615 Å，第三近邻 4.427 Å。

> [!CHEMISTRY]
> fcc 的第一配位数是 12。RDF 第一峰的面积（配位数积分）在理想晶体中应接近 12；热振动会让峰变宽，但峰位基本不变。

## 2. 在平台里搭建

1. 「新建研究」→「教程 2 · Cu EAM 金属」；
2. 模型树：

```text
结构：Cu fcc          3×3×3 = 108 atoms, a=3.615 Å
力场：Cu_u3.eam       style=eam, file=Cu_u3.eam, elements=Cu
模拟：能量最小化       500 步
模拟：NVT 300 K       3000 步, 1 fs, Nose-Hoover
分析：Cu-Cu RDF       8 Å, 200 bins
分析：Cu MSD          max 80 frames
分析：密度分布         z, 100 bins
```

### 2.1 结构参数

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `formula` | `Cu` | 元素 |
| `lattice` | `fcc` | 面心立方 |
| `a` | 3.615 Å | 实验/势文件匹配的晶格常数 |
| `nx,ny,nz` | 3,3,3 | 108 原子，适合本地快速运行 |

3D 视口应显示一个立方晶胞内的 Cu 原子。球棍模式下会画出近邻键（距离启发式），这只是可视化。

### 2.2 力场参数

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `style` | `eam` | `Cu_u3.eam` 是 setfl，不是 alloy 格式 |
| `file` | `Cu_u3.eam` | 平台从 `vendor/lammps/potentials` 或 `MATFORGE_POTENTIALS_DIR` 解析 |
| `elements` | `Cu` | `eam` 只允许单元素映射；`eam/alloy` 才需要多元素顺序 |

> [!WARNING]
> 选错变体是最常见的错误：`Cu_u3.eam` 用 `pair_style eam`；`Al_zhou.eam.alloy` 才用 `eam/alloy`。选错时 LAMMPS 会报 “incorrect format” 或元素数不匹配。

### 2.3 模拟参数

- 300 K：室温，热振动明显但不熔化（Cu 熔点约 1358 K）；
- 3000 步 × 1 fs = 3 ps：教学量级；
- Nose-Hoover：正则系综；
- 最小化：消除理想晶格的初始力。

## 3. 运行与结果

### 3.1 Thermo

- 温度在 300 K 附近波动；
- 势能约 −377 eV（108 原子，EAM 的绝对能量参考不重要，看相对变化）；
- 密度约 **8.94 g/cm³**，接近 Cu 实验值 8.96；
- 压力瞬时涨落很大，不要用单帧判断。

### 3.2 RDF

- 第一峰 **2.54 Å**（理论 2.556 Å，热振动略收缩/展宽）；
- 第二峰约 3.6 Å；
- 第三峰约 4.4 Å；
- 第一峰面积对应约 12 个近邻。

如果第一峰出现在 3.6 Å 或峰形完全不对，优先检查：

1. 晶格常数是否 3.615；
2. 势文件是否 Cu；
3. 是否误用了 `eam/alloy`；
4. 温度是否过高导致熔化。

### 3.3 MSD

Cu 在 300 K 是固体，MSD 不会线性增长，而是在一个平台附近振荡：

- 初始快速上升：热振动；
- 之后围绕平台波动：原子被晶格束缚；
- 如果 MSD 持续线性增长，说明体系可能熔化了或结构被破坏。

这与教程 1 的液体 MSD 形成对照：**同样是 MSD，固体看平台，液体看斜率**。

> [!CHEMISTRY]
> 固体的均方振幅与温度、弹性常数有关；MSD 平台不是“扩散”，而是原子在平衡位置附近的热振动。

## 4. 动手改一改

### 练习 A：改变温度

把 NVT 从 300 K 改成 800 K，重新运行。观察：

- RDF 峰是否变宽、变矮？
- MSD 平台是否升高？
- 密度是否基本不变（NVT 固定体积）？

### 练习 B：扩大体系

把超胞改成 4×4×4（256 原子）。统计更好，但运行更慢。比较 RDF 的平滑程度。

### 练习 C：换金属

把结构换成 `Al` fcc（a≈4.05 Å），力场文件换成 `Al_jnp.eam`，style 仍是 `eam`。  
注意：Al 的势文件和 Cu 不通用；元素顺序/文件必须匹配。

> [!TIP]
> 想看“势文件从哪来”，在 Inspector 里看 `file` 的帮助文字；平台只存文件名，不把势文件内容硬编码进代码。

## 5. 边界

- EAM 适合金属/合金，不适合共价晶体（用 Tersoff）或 MOF（用 UFF/文献力场）。
- 108 原子、3 ps 是教学规模；正式计算要更大超胞、更长轨迹、多 seed。
- 3D 视口是输入构型；最终热振动结构要看轨迹（OVITO/VMD）或后续轨迹回放功能。
- 平台不自动计算弹性常数、熔点、表面能；这些需要额外模块/分析。

## 6. 对应平台能力

| 能力 | 模块 |
| --- | --- |
| fcc 晶体 + 超胞 | `structure.crystal` |
| EAM 势文件 | `forcefield.eam` + `forcefield/potentials.py` |
| 最小化 / NVT | `sim.minimize` / `sim.nvt` |
| RDF / MSD / 密度 | `analysis.*` |
