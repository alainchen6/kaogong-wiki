# 教程 3 · Si 的 Tersoff 共价晶体

> **软件目标**：学会用 `forcefield.custom` 挂载多体势文件，跑通共价晶体的 NVT + RDF。  
> **化学目标**：理解键序势、金刚石结构、共价键的方向性与配位数。  
> **来源**：[LAMMPS `pair_style tersoff`](https://docs.lammps.org/pair_tersoff.html)；示例参考 [threebody examples](https://github.com/lammps/lammps/tree/stable/examples/threebody)；势文件 `Si.tersoff`。

## 你会学到

<div class="home-grid">
  <div class="home-card">
    <span class="card-tag">化学</span>
    <strong>共价键不是弹簧</strong>
    <p>Tersoff 的键序 b<sub>ij</sub> 随局部环境变化；Si 金刚石配位数 4；第一近邻 2.35 Å。</p>
  </div>
  <div class="home-card">
    <span class="card-tag">软件</span>
    <strong>自定义 pair_style + 势文件</strong>
    <p>如何在 Inspector 填 `tersoff`、`pair_coeff`、`potential_file`，并让平台自动 staging。</p>
  </div>
</div>

## 1. 化学背景：为什么 Si 需要 Tersoff？

Si 是共价晶体，每个 Si 与 4 个近邻形成四面体键。简单的两体 LJ 无法描述：

- 键强依赖键角/配位数；
- 表面/缺陷处会重构；
- 熔化/相变需要正确的能量排序。

Tersoff 势：

<div class="equation">E = ½ Σ<sub>i</sub> Σ<sub>j≠i</sub> f<sub>C</sub>(r<sub>ij</sub>) [ f<sub>R</sub>(r<sub>ij</sub>) + b<sub>ij</sub> f<sub>A</sub>(r<sub>ij</sub>) ]</div>

- `f_R`：近程排斥；
- `f_A`：吸引；
- `b_ij`：键序，取决于 i 周围其他原子的角度/距离；
- `f_C`：光滑截断。

因为 `b_ij` 依赖环境，Tersoff 能描述“键越拥挤越弱”的物理，比 LJ 更适合共价材料。

> [!CHEMISTRY]
> 金刚石结构的 Si：每个原子 4 个近邻，键长 2.35 Å，键角 109.47°。RDF 第一峰对应 2.35 Å，第二峰约 3.84 Å。温度升高，峰变宽；如果结构非晶化，第二峰以后会明显变平。

## 2. 在平台里搭建

1. 「新建研究」→「教程 3 · Si Tersoff 共价晶体」；
2. 模型树：

```text
结构：Si diamond       2×2×2 = 64 atoms, a=5.431 Å
力场：Si.tersoff       pair_style=tersoff
                       pair_coeff=* * Si.tersoff Si
                       potential_file=Si.tersoff
模拟：能量最小化        500 步
模拟：NVT 300 K        2000 步, 1 fs
分析：Si-Si RDF        8 Å, 200 bins
```

### 2.1 结构

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `formula` | `Si` | 硅 |
| `lattice` | `diamond` | 金刚石结构 |
| `a` | 5.431 Å | Si 的实验晶格常数 |
| `nx,ny,nz` | 2,2,2 | 64 原子，教学规模 |

### 2.2 力场：自定义 `pair_style`

`forcefield.custom` 是通用入口，不只为 Tersoff：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `pair_style` | `tersoff` | 多体势 |
| `pair_coeff` | `* * Si.tersoff Si` | 第一行：所有类型对；文件；元素映射 |
| `kspace` | 空 | Tersoff 不需要长程静电 |
| `potential_file` | `Si.tersoff` | 平台从势文件库解析并复制到工作目录 |

生成到 LAMMPS 输入里的内容大致是：

```lammps
pair_style tersoff
pair_coeff * * Si.tersoff Si
```

> [!WARNING]
> `pair_coeff` 的格式由 `pair_style` 决定，平台不会替你猜。写错时 LAMMPS 会在日志里报错；先看 `log.lammps` 的最后一条命令。

### 2.3 模拟

- 300 K：室温，Si 仍是金刚石结构；
- 2000 步 × 1 fs = 2 ps：教学量级；
- 最小化：消除初始理想结构的力；
- NVT：正则系综。

## 3. 运行与结果

### 3.1 Thermo

- 温度在 300 K 附近波动；
- 势能约 −293 eV（64 原子，绝对值取决于势的参考）；
- 密度约 **2.33 g/cm³**，与 Si 实验值 2.33 一致；
- 压力瞬时值可能为负/正，小体系涨落大。

### 3.2 RDF

- 第一峰 **2.34 Å**，对应 Si-Si 共价键；
- 第二峰约 3.8–3.9 Å；
- 第一峰面积约 4（配位数 4），不是 12（金属 fcc）或 6（简单立方）。

比较教程 2 的 Cu：Cu 第一峰 2.54 Å、配位 12；Si 第一峰 2.34 Å、配位 4。  
**RDF 是区分“金属密堆”和“共价四面体网络”的最快方法之一。**

> [!CHEMISTRY]
> 配位数不是从峰高直接读，而是对 `4πρg(r)r²` 积分到第一峰后的第一个极小。平台结果里同时给出 `coordination` 累积曲线，可以直接看。

## 4. 动手改一改

### 练习 A：升温到 1000 K

Si 的熔点约 1687 K，1000 K 仍是固态，但热振动更强。观察 RDF 峰是否变宽、第一峰面积是否仍约 4。

### 练习 B：换势文件

LAMMPS potentials 里还有 `Si.tersoff.mod`。把 `potential_file` 和 `pair_coeff` 里的文件名一起换掉，重新运行，比较第一峰/能量。  
注意：**文件名必须同时改两处**，否则 `pair_coeff` 会找不到文件。

### 练习 C：故意写错

把 `pair_coeff` 改成 `* * Si.tersoff`（漏掉元素映射），运行，观察 LAMMPS 报错，再改回来。  
这是学习“输入格式由 pair_style 决定”的好方法。

## 5. 边界

- Tersoff 适合共价晶体/半导体，不适合金属（用 EAM）或分子液体（用 LJ/力场库）。
- 64 原子、2 ps 是教学规模；正式计算要更大超胞、更长轨迹。
- 平台不自动判断“是否熔化”；需要看 RDF/MSD/配位数或可视化轨迹。
- 3D 预览是输入结构；最终结构看轨迹。

## 6. 对应平台能力

| 能力 | 模块 |
| --- | --- |
| 金刚石结构 | `structure.crystal`（`diamond`） |
| 多体势 + 势文件 | `forcefield.custom` + `potential_file` |
| 最小化 / NVT | `sim.minimize` / `sim.nvt` |
| RDF / 配位数 | `analysis.rdf` |
