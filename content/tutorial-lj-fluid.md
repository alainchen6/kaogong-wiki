# 教程 1 · Ar Lennard-Jones 流体

> **软件目标**：用 5 个模块跑通一次真实 MD，并读懂 g(r)、MSD、密度。  
> **化学目标**：理解 LJ 势、近邻壳层、液体结构、扩散与温度的关系。  
> **来源**：[LAMMPS Tutorial 1 — Lennard-Jones fluid](https://lammpstutorials.github.io/sphinx/build/html/tutorial1/lennard-jones-fluid.html)（Simon Gravelle 等，LiveCoMS 2025）。平台用 metal 单位复现同一物理场景。

## 你会学到

<div class="home-grid">
  <div class="home-card">
    <span class="card-tag">化学</span>
    <strong>LJ 势与液体结构</strong>
    <p>ε、σ、截断；g(r) 第一峰/第二峰；配位数；MSD 与扩散系数。</p>
  </div>
  <div class="home-card">
    <span class="card-tag">软件</span>
    <strong>流体盒子 + NVT + 三种分析</strong>
    <p>添加/修改模块，读 Inspector，运行 LAMMPS，在结果页看曲线并导出。</p>
  </div>
</div>

## 先看结果

![LJ 流体 RDF](/wiki/assets/img/results-rdf.png)
<span class="img-caption">本机结果：800 Ar，85 K，g(r) 第一峰约 3.78 Å，远场趋于 1；温度在 85 K 附近波动。</span>

## 1. 化学背景：为什么是 LJ？

Ar 是单原子惰性气体，没有方向性共价键，最常用的模型就是 Lennard-Jones：

<div class="equation">E(r) = 4ε [ (σ/r)<sup>12</sup> − (σ/r)<sup>6</sup> ]</div>

- `r⁻¹²` 是短程排斥（原子核/电子云重叠）；
- `r⁻⁶` 是长程吸引（瞬时偶极）；
- `σ` 是势能过零的距离；
- `ε` 是势阱深度，决定“粘”的强度；
- 最低点在 `1.122σ`，能量 `−ε`。

我们用的 Ar 参数：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| ε | 0.0103 eV | 约 119.8 K × kB |
| σ | 3.405 Å | LJ 直径 |
| cutoff | 8.5 Å | 约 2.5σ |

液体 Ar 在 85 K、约 1.4 g/cm³ 下是致密流体。温度升高，g(r) 峰变矮、变宽，MSD 斜率变大。

> [!CHEMISTRY]
> g(r) 不是“键长分布”，而是**任意一对原子的距离分布**相对于理想气体的偏离。第一峰位置≈最可几近邻距离；第二峰说明液体仍有短程有序，但远场趋于 1，说明没有长程晶体有序。

## 2. 在平台里搭建

### 2.1 创建示例

1. 打开 `/`；
2. 点「新建研究」；
3. 选「教程 1 · Ar LJ 流体」。

模型树应当出现：

```text
结构：Ar 流体        800 atoms
力场：Ar LJ          components = Ar:0.0103:3.405, cutoff=8.5
模拟：能量最小化      500 步
模拟：NVT 85 K       4000 步, 2 fs, Nose-Hoover
分析：Ar-Ar RDF      10 Å, 200 bins
分析：Ar MSD         max 80 frames
分析：密度分布        z, 100 bins
```

![模型树](/wiki/assets/img/model-builder.png)
<span class="img-caption">教程 1 的模型树。注意 3D 视口标注「输入构型」：这是运行前结构，不是轨迹。</span>

### 2.2 逐个检查参数

点「Ar 流体」：

| 参数 | 值 | 为什么 |
| --- | --- | --- |
| `species` | `Ar:800` | 800 个 Ar，统计量足够且本地几秒可跑 |
| `box` | 34 Å | 对应约 1.35 g/cm³ 的液体密度 |
| `min_distance` | 2.2 Å | 避免初始原子重叠；不是物理截断 |
| `seed` | 2025 | 固定随机种子，预览/运行可复现 |

点「Ar LJ」：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `components` | `Ar:0.0103:3.405` | 多组分接口；这里只有一个组分 |
| `cutoff` | 8.5 Å | 2.5σ；再大更准但更慢 |

点「NVT 85 K」：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `temperature` | 85 K | 低于 Ar 临界温度，处于液体区 |
| `steps` | 4000 | 4 ps（2 fs/步） |
| `timestep` | 0.002 ps | LJ 液体常用 2 fs |
| `thermostat` | nose/hoover | 正则系综采样 |
| `damp` | 0.2 ps | 控温时间尺度 |

> [!TIP]
> 如果你把 `timestep` 改成 0.01 ps，能量可能爆炸。LJ 体系的安全步长取决于最慢振动/最快碰撞；2 fs 是稳妥起点。

## 3. 运行

点右上角「运行」。Console 里应看到：

- `read_data` 读入 800 atoms；
- `pair_style lj/cut 8.5`；
- `minimize` 收敛；
- `fix nvt` + `run 4000`；
- `Total wall time`。

状态变成 `completed` 后，点「结果」。

## 4. 结果怎么读

### 4.1 Thermo

- **Temp**：应在 85 K 附近波动；Nose-Hoover 的瞬时温度会上下跳，这是正常的；
- **PotEng**：负值，约 −45 eV 量级（800 个 Ar 的总势能）；
- **Press**：小体系瞬时压力涨落很大，不要用单帧判断；
- **Density**：约 1.35 g/cm³（由盒子体积和总质量决定）。

### 4.2 g(r)

- 第一峰约 **3.78 Å**：液体 Ar 的最可几近邻距离；
- 第一峰后有一个谷，再出现第二峰（约 6–7 Å）；
- `r > 8 Å` 后趋近 **1**：说明远场没有长程有序；
- 第一峰高度约 3，比晶体低得多，符合液体。

如果 g(r) 远场不趋于 1，通常说明归一化、帧数或盒子有问题。这个平台曾经在“多帧 RDF”上出过归一化 bug，已修复并有回归测试；所以**远场趋近 1** 是一个很好的自检。

### 4.3 MSD

MSD 随时间近似线性增长，说明 Ar 在液体中扩散。平台输出的是最小镜像位移，适合短时间/致密体系；长时间扩散建议用 unwrap 轨迹另算。

`MSD = 6Dt`，所以你可以对线性段做斜率拟合得到 D。平台目前只画曲线，不自动拟合。

### 4.4 密度分布

沿 z 的密度应近似均匀（液体），没有明显孔道/界面峰。若你看到强峰，可能是盒子太小、初始构型未平衡，或分析轴选错。

## 5. 动手改一改

### 练习 A：升温

把 NVT 温度从 85 K 改成 120 K，重新运行。观察：

- g(r) 第一峰是否变矮/变宽？
- MSD 斜率是否变大？
- 密度是否基本不变（NVT 固定体积）？

### 练习 B：改密度

把 `box` 从 34 Å 改成 30 Å（约 1.95 g/cm³，更致密），保持 800 原子。观察压力是否显著升高、g(r) 峰是否变高。  
注意：过于致密 + 2.2 Å 最小间距可能无法放置，平台会报错。

### 练习 C：换成混合物

把 `species` 改成：

```text
Ar:600
Kr:200
```

把 LJ 的 `components` 改成：

```text
Ar:0.0103:3.405
Kr:0.0140:3.60
```

平台会自动生成 Ar-Ar、Ar-Kr、Kr-Kr 三组混合参数。看 RDF 的 `Ar-Kr` 曲线；思考为什么混合物的 g(r) 不是简单平均。

> [!TIP]
> 改完参数后不需要点“保存”；Inspector 会自动持久化。运行前检查右上角是否还有黄色警告。

## 6. 边界与常见坑

- **这不是官方教程的逐字输入**：官方用 `units lj`、随机气体盒子；这里用 metal 单位、Ar 参数、致密液体盒子，物理场景等价但不是同一组数字。
- **最小化不是平衡**：`minimize` 只是消除重叠；液体结构由 NVT 采样得到。
- **初始构型是随机的**：固定 seed 保证可复现，但不同 seed 会有不同轨迹。
- **g(r) 的统计误差**：4000 步、23 帧只是教学量级；正式计算要更长、多 seed、block average。
- **3D 预览不是轨迹**：它显示输入构型；不要把截图当作最终液体结构。

## 7. 对应平台能力

| 能力 | 模块 |
| --- | --- |
| 随机流体盒子 | `structure.fluid` |
| 多组分 LJ + 混合 | `forcefield.lj`（`components`） |
| 能量最小化 | `sim.minimize` |
| NVT + Nose-Hoover | `sim.nvt` |
| g(r) / 配位数 | `analysis.rdf` |
| MSD | `analysis.msd` |
| 密度分布 | `analysis.density` |

> [!NOTE]
> 这套模块可以用于任何 LJ 流体/气体混合物，不限于 Ar。把元素、ε/σ、温度换掉即可；教程没有为 Ar 写专用代码。
