# 教程 5 · ZIF-8 的 CH4 吸附等温线

> **软件目标**：用真实 MOF CIF + UFF + GCMC 压力扫描，得到一张吸附等温线。  
> **化学目标**：MOF/孔道、化学势与逸度、GCMC 插入/删除、uptake、等温线形状、电荷为什么重要。  
> **来源**：[LAMMPS `fix gcmc`](https://docs.lammps.org/fix_gcmc.html)；结构来自 RASPA2/CoRE MOF 的 ZIF-8 CIF；气体参数为 TraPPE 甲烷。

## 你会学到

<div class="home-grid">
  <div class="home-card">
    <span class="card-tag">化学</span>
    <strong>MOF 吸附</strong>
    <p>孔道/窗口、μVT 系综、压力→化学势、uptake、Type I 等温线、电荷与极性气体。</p>
  </div>
  <div class="home-card">
    <span class="card-tag">软件</span>
    <strong>内置 CIF + 力场库 + GCMC</strong>
    <p>选择真实结构、自动分配 guest 类型、多压力点扫描、在结果页读等温线。</p>
  </div>
</div>

## 先看结果

| P / bar | uptake / mmol g⁻¹ | 物理含义 |
| --- | --- | --- |
| 0.1 | ≈ 0.08 | 低压，主要看强吸附位点 |
| 1 | ≈ 0.85 | 常压，接近工程相关区间 |
| 10 | ≈ 5.22 | 高压，逐渐接近孔体积饱和 |

本机结果（298 K，ZIF-8，276 atoms，UFF + TraPPE CH4，每点 6000 步）。数值会随 seed/步数/电荷模型变化。

## 1. 化学背景：ZIF-8 是什么？

ZIF-8 是沸石咪唑酯骨架（Zeolitic Imidazolate Framework）：

- Zn²⁺ 与 2-甲基咪唑配位；
- 四面体 Zn 节点，形成 SOD 拓扑；
- 孔道/窗口约 3.4 Å（窗口），空腔约 11.6 Å；
- 比表面积高、热/化学稳定性好；
- 常用于气体分离、吸附、催化。

平台内置的 `ZIF-8.cif` 是 276 原子的常规晶胞（C8H10N4Zn 的 12 倍），来自真实结构数据库。

> [!CHEMISTRY]
> MOF 的“孔”不是空盒子，而是由原子表面围成的空腔。吸附质能进去，是因为孔窗口大于分子动力学直径，且孔壁与分子有吸引作用。

## 2. 化学背景：GCMC 在做什么？

GCMC 在 **μVT** 系综下采样：

- 固定化学势 μ、体积 V、温度 T；
- 允许分子数 N 变化；
- 尝试插入、删除、平移、旋转。

插入接受概率：

<div class="equation">P<sub>insert</sub> = min[1, (V/(N+1)Λ³) exp(β(μ − ΔU))]</div>

- `ΔU`：插入前后的势能差；
- `Λ`：热 de Broglie 波长；
- `μ`：由压力/逸度给出；
- 低压时 μ 低，插入少；高压时 μ 高，插入多。

`fix gcmc` 的 `pressure` 关键字让 LAMMPS 从压力算 μ，所以你可以直接输入 bar。

## 3. 力场：UFF + TraPPE

### 框架

`力场库（UFF + 电荷）`：

- UFF 通用非键参数（Rappé 1992）；
- 框架元素 Zn/C/N/H 各自分配 ε/σ；
- Lorentz-Berthelot 混合；
- 本教程 `charge_mode = none`，因为 CH4 中性、UFF 非键模型已经能给出合理趋势。

### 气体

`guest = CH4`，使用 TraPPE 单站点甲烷：

| 参数 | 值 |
| --- | --- |
| ε/kB | 148 K |
| σ | 3.73 Å |
| 电荷 | 0 |

> [!WARNING]
> CO2 是极性/四极矩分子，对框架电荷非常敏感。内置 CO2 是 TraPPE 3-site 带电荷模型；如果你直接把 CO2 放进一个**没有校准电荷**的框架，等温线可能明显偏离实验。定量 CO2 吸附请用文献 DDEC/拟电荷，并验证静电能处理（kspace/截断）。

## 4. 在平台里搭建

1. 「新建研究」→「教程 5 · ZIF-8 CH4 等温线」；
2. 模型树：

```text
结构：ZIF-8              内置 CIF，276 atoms
力场：UFF + 电荷           engine=uff, cutoff=12 Å, charge_mode=none
模拟：CH4 等温线          298 K, pressures=0.1,1,10 bar
                          guest=CH4, steps=6000, exchanges=100
分析：密度分布            z
```

### 4.1 结构

`structure.library` → `ZIF-8`。  
3D 视口显示真实 CIF 的 Zn/N/C/H 框架。注意：视口是**输入框架**，不显示 GCMC 插入的 CH4。

### 4.2 力场参数

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `engine` | `uff` | 元素级 UFF |
| `cutoff` | 12 Å | 非键截断 |
| `charge_mode` | `none` | 本教程中性气体；框架电荷全 0 |
| `neutralize` | true | 无净电荷时无作用 |

平台会为 CH4 自动追加一个 guest 原子类型、生成 molecule 模板，并写进 `system.data`/`in.matforge`；你不需要手工编辑 LAMMPS 文件。

### 4.3 GCMC 参数

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `temperature` | 298 K | 常温 |
| `pressures` | `0.1, 1, 10` | 三个压力点，逐点独立平衡 |
| `guest` | `CH4` | 内置 TraPPE 模型 |
| `steps` | 6000 | 每点步数；生产段取后半段 |
| `exchanges` | 100 | 每步交换/移动次数 |
| `overlap_cutoff` | 0.8 Å | 拒绝严重重叠 |
| `seed` | 12345 | 可复现 |

> [!TIP]
> 压力点是对数分布（0.1/1/10），因为吸附等温线在低压段变化最快。想做完整等温线，可加 `0.01, 0.03, 0.3, 3, 30`。

## 5. 运行与结果

### 5.1 运行过程

一个 `sim.gcmc` 模块会生成多个 phase：

```text
phase 1: 0.1 bar → 清空 guest → 平衡 → 生产
phase 2: 1 bar   → 清空 guest → 平衡 → 生产
phase 3: 10 bar  → 清空 guest → 平衡 → 生产
```

每个 phase 的 thermo 里 `Atoms` 包含框架 + guest；平台用：

<div class="equation">n<sub>guest</sub> = Atoms − N<sub>framework</sub></div>

再除以每个分子的原子数，得到分子数，最后：

<div class="equation">uptake = n<sub>molecules</sub> × 1000 / M<sub>framework</sub></div>

### 5.2 等温线

结果页的 `Isotherm`：

- 横轴 log(P/bar)；
- 纵轴 uptake / mmol g⁻¹；
- 每个点来自对应 phase 的生产段平均；
- 曲线单调上升，低压段斜率大，高压段逐渐变缓。

![结果页](/wiki/assets/img/results.png)
<span class="img-caption">结果页：温度/能量、RDF、MSD、密度、等温线、电荷表；不同 Study 显示不同结果类型。</span>

### 5.3 为什么 0.1 bar 已经有一定吸附？

ZIF-8 的孔道对 CH4 有吸引力，低压下强吸附位点先被占据。等温线的低压段斜率反映“亲和力”，高压段反映“容量”。

## 6. 动手改一改

### 练习 A：增加压力点

把 `pressures` 改成：

```text
0.01, 0.03, 0.1, 0.3, 1, 3, 10
```

运行后看曲线是否更完整。点多 = 更慢。

### 练习 B：升温

改成 348 K，重新运行。预期 uptake 下降，因为吸附是放热过程。

### 练习 C：换气体

把 `guest` 改成 `CO2`，保持 `charge_mode=none`。观察等温线是否与 CH4 不同。  
然后思考：CO2 带四极矩和点电荷，而框架没有电荷；这个模型缺了什么？下一步应该查什么？

> [!CHEMISTRY]
> 这不是“CO2 模拟错了”，而是模型边界：没有框架电荷/极化，CO2 的静电作用被忽略。定量工作要用文献电荷、可能的四极矩/极化模型，并验证 kspace。

## 7. 进阶：二元混合气与选择性

把 `mixture` 填成：

```text
CH4:0.5
Ar:0.5
```

压力列表仍表示**总压**；每个组分分压 = 总压 × 分数。平台会为每个组分建独立 `fix gcmc` group，结果页给出：

- 分组分 uptake；
- 选择性 `S_i = (x_i/y_i)/(x_ref/y_ref)`；
- block SEM（误差棒）；
- 原子数/质量平衡检查。

本机实测（ZIF-8，298 K，CH4/Ar 1:1）：

| P / bar | CH4 / mmol g⁻¹ | Ar / mmol g⁻¹ | S(Ar/CH4) |
| --- | --- | --- | --- |
| 1 | 0.50 | 0.64 | 1.27 |
| 10 | 3.07 | 2.38 | 0.78 |

这说明在这个粗模型里，低压 Ar 略占优、高压 CH4 略占优；真实分离结论需要校准电荷/力场并用实验验证。

## 8. 边界与常见坑

- **UFF 只有非键项**：适合刚性框架 + GCMC；柔性框架会塌陷，需要含键/角/二面角的力场。
- **电荷**：`none` 适合中性气体快速筛选；极性气体需要文献电荷；`electrostatics=pppm` 时体系必须中性。
- **采样**：6000 步是教学量级；正式等温线要更长、多 seed、block average/误差棒。
- **孔道可达性**：GCMC 可能卡在窗口；需要足够长的平衡和 `overlap_cutoff`。
- **3D 预览**：显示框架输入构型，不显示插入的 CH4。
- **单位**：压力 bar、uptake mmol/g；平台按 metal 单位写 LAMMPS 输入。

## 9. 对应平台能力

| 能力 | 模块 |
| --- | --- |
| 真实 MOF CIF | `structure.library` |
| UFF + 类型/混合 | `forcefield.library` |
| TraPPE CH4 + molecule | `adsorbates.json` + guest 类型 |
| 多压力 GCMC | `sim.gcmc` |
| 等温线 | `StudyRunner._save_isotherm` + 结果页 |
| 孔道密度 | `analysis.density` |
