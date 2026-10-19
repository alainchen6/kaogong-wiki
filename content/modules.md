# 模块参考

平台当前有 **25 个声明式模块**。模块 = 一段可组合的计算步骤，不是 UI 小组件。每个模块都声明参数 schema，Inspector 自动渲染；新增模块 = 注册 spec + resolver 分支。

> [!TIP]
> 在应用里点「+ 添加模块」可以看到同样的分类；每个模块右侧会显示参数个数与产物。模块顺序一般应为：结构 → 力场 → 模拟 → 分析。

## 结构 / 几何

### 晶体结构 `structure.crystal`

按晶格类型和晶格常数构建晶体，底层用 ASE。

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `formula` | — | 化学式，如 `Cu`、`Si`、`NaCl`、`SrTiO3` |
| `lattice` | — | fcc / bcc / hcp / diamond / sc / rocksalt / perovskite / zincblende |
| `a` | Å | 晶格常数 |
| `nx, ny, nz` | — | 超胞倍数 |

适用：金属、简单离子晶体、共价晶体、教学模型。  
注意：复杂 MOF/有机晶体请用 CIF 导入。

### 内置晶体库 `structure.library`

从随包 CIF 中选择真实结构：

- UiO-66
- ZIF-8
- HKUST-1 (Cu-BTC)
- MIL-47

文件在 `packages/matforge/data/structures/`，保留原始引用。  
注意：这是**实验/计算准备好的 CIF**，不是力场参数；电荷仍需单独指定。

### 导入结构 `structure.import`

| 参数 | 说明 |
| --- | --- |
| `format` | CIF / XYZ / POSCAR |
| `data` | 文件文本，可粘贴或用「从文件读取」 |
| `name` | 结构名 |

底层用 ASE 读取。CIF 会展开对称性；如果 CIF 含有 disorder/部分占据，ASE 可能给出非预期原子数，导入后请检查 3D 视口与元素统计。

### 超胞 `structure.supercell`

对当前结构做 `nx × ny × nz` 复制，同时复制类型和电荷。用于扩大统计体系、避免周期镜像相互作用。

### 表面 / Slab `structure.surface`

按 Miller 指数切表面并加真空层（ASE surface）。参数：`formula`、`lattice`、`a`、`miller`（如 `1,1,1`）、`layers`、`vacuum`、面内 `nx/ny`。pbc 为 `p p f`，适合表面/吸附。

### 界面 / 双层 `structure.interface`

同面内晶胞的两块 slab 叠加 + 真空层；参数 `formula_a/b`、`layers_a/b`、`gap`、`vacuum`。只做几何堆叠，不做晶格匹配/应变最小化。

### 无定形盒子 `structure.amorphous`

按目标密度生成随机无定形初始结构；参数 `species`、`density`、`min_distance`、`seed`。是初始构型，不是平衡结构。

### 流体盒子 `structure.fluid`

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `species` | — | 每行 `元素:数量`，如 `Ar:800` |
| `box` | Å | 立方盒子边长 |
| `min_distance` | Å | 最小间距，避免初始重叠 |
| `seed` | — | 随机种子；固定 seed 保证预览/运行一致 |

适用：LJ 流体、气体混合物、无定形初始构型。  
注意：不是“平衡构型”，通常先做能量最小化/NVT；大体系 O(N²) 放置会变慢。

## 力场 / 势函数

### 力场库（UFF + 电荷）`forcefield.library`

| 参数 | 说明 |
| --- | --- |
| `engine` | 目前 UFF（Rappé 1992） |
| `cutoff` | LJ/库仑截断，Å |
| `charge_mode` | none / formal / manual / per_atom |
| `manual_charges` | `Element:charge` 每行一个 |
| `per_atom_charges` | `id,charge` 每行一个，或顺序电荷值 |
| `charge_file` | 上传 CSV/TXT（与 per_atom 二选一） |
| `electrostatics` | `cutoff` 或 `pppm`（长程，体系必须中性/周期） |
| `bonded` | 是否自动感知键并生成键合项（DREIDING-style MVP） |
| `neutralize` | 是否把净电荷均匀中和 |

会为框架元素和 GCMC guest 自动分配 LAMMPS 类型、ε/σ、molecule 模板，生成 `lj/cut` / `lj/cut/coul/cut` / `lj/cut/coul/long` 的 `pair_coeff`。

适用：MOF/有机小分子快速起步、GCMC 的框架非键项；开启 `bonded` 后可跑柔性框架 NVT/NPT。
注意：键合项是**几何平衡值 + DREIDING-style 谐振 MVP**，不是完整 UFF 键型/杂化参数；正式计算请用文献力场校验或覆盖系数。

### Lennard-Jones `forcefield.lj`

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `epsilon` | eV | 单组分 ε |
| `sigma` | Å | 单组分 σ |
| `cutoff` | Å | 截断 |
| `components` | — | 可选，多组分 `元素:ε:σ`，自动 Lorentz-Berthelot 混合 |

留空 `components` 时生成 `* * ε σ cutoff`，所有类型共用一组参数；填写后按元素生成 i≤j 的混合对。

### EAM 势 `forcefield.eam`

| 参数 | 说明 |
| --- | --- |
| `style` | `eam`（setfl）/ `eam/alloy` / `eam/fs` |
| `file` | 势文件裸文件名，如 `Cu_u3.eam` |
| `elements` | 元素顺序，如 `Cu` 或 `Cu Zr` |

势文件从 `MATFORGE_POTENTIALS_DIR` 或 `vendor/lammps/potentials` 解析，只允许 basename（防路径穿越），运行时复制到工作目录。

### 自定义力场 `forcefield.custom`

| 参数 | 说明 |
| --- | --- |
| `pair_style` | 例如 `tersoff`、`airebo 3.0`、`lj/cut/coul/long 12.0` |
| `pair_coeff` | 每行一条，原样写入 |
| `kspace` | 可选，`pppm 1e-4` 等 |
| `potential_file` | 可选，势文件裸名；自动 staging |

这是 MOF 文献力场、反应力场、多体势的通用入口。平台不校验 `pair_style` 语义，只做基本输入校验；写错时看 LAMMPS 日志。

## 数据

### 实验数据 `data.experiment`

加载内置 NIST/CSV 等温线；参数 `dataset`、`adsorbate`。与 GCMC 结果叠加时，结果页会画实验点并显示 DOI/来源。只做数据读取，不替代模拟。

## 模拟

### 能量最小化 `sim.minimize`

| 参数 | 说明 |
| --- | --- |
| `etol` | 能量容差 |
| `ftol` | 力容差 |
| `maxiter` | 最大迭代 |
| `maxeval` | 最大力评估 |

用于消除初始重叠/高能接触。最小化不是“平衡”，之后仍需 MD 或 MC。

### NVT `sim.nvt`

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `temperature` | K | 目标温度 |
| `steps` | — | 步数 |
| `timestep` | ps | 时间步 |
| `thermostat` | — | nose/hoover / berendsen / langevin / temp-rescale |
| `damp` | ps | 控温阻尼 |

平台会生成 `velocity create` + 对应的 `fix nve` / `fix nvt` 或双 fix（Berendsen/Langevin）。

### NPT `sim.npt`

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `temperature` | K | 温度 |
| `pressure` | bar | 压力 |
| `steps` | — | 步数 |
| `timestep` | ps | 时间步 |
| `damp` | ps | 温度阻尼 |

使用 Nose-Hoover barostat。需要周期性边界。小体系压力涨落大，优先看平均密度/体积。

### NVE `sim.nve`

微正则系综，无控温/控压。适合能量守恒测试、扩散、声子相关后处理。

### GCMC 吸附等温线 `sim.gcmc`

| 参数 | 单位 | 说明 |
| --- | --- | --- |
| `temperature` | K | 温度 |
| `pressures` | bar | 逗号分隔，如 `0.1, 1, 10` |
| `guest` | — | none / CO2 / CH4 / Ar / H2O / C2H4 / C2H6 / C2H2 |
| `mixture` | — | 可选，每行 `guest:fraction`，分数和为 1 |
| `steps` | — | 每个压力点步数 |
| `exchanges` | — | 每步交换/移动次数 |
| `overlap_cutoff` | Å | 重叠拒绝距离 |
| `seed` | — | 随机种子 |
| `type_index` | — | guest=none 时的单原子类型 |
| `timestep` | ps | 时间步（MC 仍需 LAMMPS 时间步） |

一个模块会生成多个 `fix gcmc` phase，每个压力点前清空 guest，取生产段后半段平均，输出 `isotherm` 结果。
填写 `mixture` 时，每个组分生成独立 group/fix，结果含分组分 uptake、选择性、block SEM 和原子数质量平衡检查。

## 分析

### 配位数 `analysis.coordination`

按元素对统计 cutoff 内平均配位数；参数 `pair`、`cutoff`、`max_frames`。

### 键角分布 `analysis.bond_angle`

使用拓扑 angle 列表统计角度分布；无拓扑时提示启用力场库的键合项。

### 孔体积 `analysis.pore`

几何探针：网格点到最近原子的最小镜像距离 > `probe_radius`；输出可及分数与 cm³/g。不是完整 Connolly 表面。

### 粉末 XRD `analysis.xrd`

从倒易格子结构因子计算 Bragg 峰位/相对强度；原子形状因子用 Z 近似，不含 Lorentz/DW，适合峰位检查。

### 径向分布函数 `analysis.rdf`

| 参数 | 说明 |
| --- | --- |
| `pair` | `A-B`，留空表示所有元素对 |
| `cutoff` | 最大 r，Å |
| `nbins` | 分箱数 |
| `max_frames` | 最多使用多少帧 |

从轨迹计算 g(r)，并给出配位数。多帧结果按帧平均。

### 均方位移 `analysis.msd`

| 参数 | 说明 |
| --- | --- |
| `max_frames` | 最多帧数 |
| `element` | 可选，只看某元素 |

使用最小镜像计算位移；长扩散体系需要 unwrap 轨迹另行分析。

### 密度分布 `analysis.density`

| 参数 | 说明 |
| --- | --- |
| `axis` | x / y / z |
| `nbins` | 分箱数 |

从轨迹最后一帧计算沿轴密度；GCMC 可看到 guest 在孔道中的分布。

## 模块组合的最小合法链

```text
结构（crystal/library/import/fluid/supercell）
  + 力场（library/lj/eam/custom）
  + 至少一个模拟（minimize/nvt/npt/nve/gcmc）
  + 可选分析（rdf/msd/density）
```

缺结构、缺力场、缺模拟都会在 Inspector 里报错，不会静默生成空输入。

> [!NOTE]
> 想新增一个模块？看 [添加模块与示例](/wiki/extending/)。示例本身只引用这些通用模块，不为教程增加专用类型。

## 新增模块速查（M2.1 / M2.2）

### analysis.elastic · 弹性常数

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| 应变幅度 ε | 0.002 | 中心差分步长；太小会被数值噪声淹没，太大会偏离线性区 |

会额外提交 12 个 LAMMPS 最小化任务（6 个应变分量 × ±ε）。输出 6×6 刚度矩阵（GPa）、
C11/C12/C44、Voigt/Reuss/Hill 平均、Zener 各向异性、Born 稳定性。
方法细节见 [力学与热输运](/wiki/mechanics-thermal/)。

### analysis.thermal · 热导率（Müller-Plathe）

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| 温度 | 0（沿用模拟温度） | 生产段目标温度 |
| 生产步数 | 20000 | 越长统计越好；决定 ΔE 的积累时间 |
| 预热/平衡步数 | 5000 / 5000 | 先建立梯度、再看线性剖面 |
| 交换间隔 | 10 步 | 越小热流越大、越容易偏离线性响应 |
| 分层数 | 20 | 必须偶数；冷层在边缘、热层在中间 |

输出 κ（W/(m·K)）、冷热层温差、温度剖面、剖面线性度 R²。R² < 0.9 会给出警告。
仅支持 `metal` / `real` 单位。

### structure.polymer · 聚合物构建器

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| 重复单元 SMILES | `*CC*` | 必须正好两个 `*` 连接点 |
| 链数 / 单体数 | 4 / 20 | 总原子数 ≈ 链数 × 单体数 × 单体原子数 |
| 目标密度 | 0.8 g/cm³ | 实际密度可能更低（受链尺寸限制），写在 provenance 里 |
| 最小原子间距 | 2.2 Å | **必须 ≥ 2.0**，否则 LJ 核心重叠导致发散 |

输出带显式 bonds/angles/dihedrals 与 molecule_ids 的结构，可直接接 `forcefield.library` 的键合项。
详见 [聚合物构建](/wiki/polymer/)。

### 分析结果的新类型

| 结果 kind | 出现位置 | 内容 |
| --- | --- | --- |
| `elastic` | 结果页「弹性常数」卡 | 刚度矩阵表 + 模数 KPI |
| `thermal` | 结果页「热导率」卡 | κ、温度剖面曲线、线性度 |

### structure.surface / structure.interface · 表面与界面

| 参数 | 说明 |
| --- | --- |
| Miller 指数 | 切割面，例如 `1,1,1` |
| 层数 / 真空层 | 决定 slab 厚度与周期性方向 |
| `a` / `a_b` | 下层/上层晶格常数；`a_b=0` 表示与下层相同 |
| 最大匹配超胞 | 不同晶格常数时，在 1..N 内搜索整数超胞使面内长度尽量匹配 |
| 界面最小间距 | 低于该值直接报错（防止原子重叠把体系炸开） |

界面会把剩余失配作为**双轴应变**施加到上层，`strain_percent` 与
`min_inter_slab_distance_a` 写进结构 provenance；Cu(111) 表面能实测 1.02 J/m²。

### structure.crystal_cell · 自定义晶胞（分数坐标）

| 参数 | 说明 |
| --- | --- |
| a / b / c / α / β / γ | 任意晶胞参数（7 大晶系都能表示） |
| 原子位点 | 每行 `<元素> <fx> <fy> <fz>`，分数坐标 |
| nx / ny / nz | 超胞 |

等价于 MS 的 Build Crystal：不依赖晶格模板，三斜/单斜也能直接建。

### structure.molecule · 分子构建器

| 参数 | 说明 |
| --- | --- |
| SMILES | 例如 `O`（水）、`CCO`（乙醇）、`c1ccccc1`（苯） |
| 分子数 | 1 = 单个探针分子；>1 = 分子液体盒子 |
| box / density | 二选一；都留 0 则按分子尺寸自动给盒子 |
| 最小间距 | 分子间最小原子距离（默认 1.6 Å） |

RDKit 生成 3D 构象，输出带显式键/角/二面角与 molecule_ids 的结构，可直接接键合力场。

### analysis.adsorption_sites · 吸附位点与结合能

| 参数 | 说明 |
| --- | --- |
| 探针分子 | 来自 `data/adsorbates.json`（CO2/CH4/Ar/H2O/…） |
| 每轴网格 | 网格分辨率（默认 12） |
| 取向数 | 刚性探针的随机取向数（默认 8） |
| 输出位点数 | 去重后保留的局部最优位点 |

用 UFF 的 LJ 参数 + 探针点电荷计算结合能，输出最稳定位点（分数坐标）、
排名、可及网格比例。**这是网格近似，不做局部优化**，结果页会注明。

### 结果页新增

| 位置 | 内容 |
| --- | --- |
| MSD 卡 | 扩散系数 D（m²/s）、维度、拟合区间 |
| 吸附位点卡 | 位点表 + 可及网格比例 + 结合能 |
| 热膨胀与热容卡 | 温度扫描的 ρ(T)、α、Cv |
