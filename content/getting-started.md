# 5 分钟上手

这一页只做一件事：让你在浏览器里跑完一次真实 LAMMPS 计算，并知道结果在哪里看。
不先讲理论，理论放在每个教程和[化学速查](/wiki/chemistry-primer/)里。

![Model Builder](/wiki/assets/img/model-builder.png)
<span class="img-caption">主界面：左侧模型树，中间 3D 视口，右侧 Inspector，底部 LAMMPS 控制台。</span>

## 0. 打开应用

如果服务已经在运行，直接打开：

```text
http://127.0.0.1:8000
```

如果还没启动：

```bash
cd /path/to/lammps
MATFORGE_HOME=$PWD/.matforge \
MATFORGE_LAMMPS_BIN=$PWD/vendor/lammps/build/lmp \
  .venv/bin/uvicorn matforge.api.main:app --host 127.0.0.1 --port 8000
```

> [!TIP]
> 页面右上角的「LAMMPS」状态点是绿色，表示后端找到了 `lmp` 可执行文件。红色时先看 [常见问题](/wiki/faq/)。

## 1. 先创建一个示例研究

1. 点顶部「**新建研究**」；
2. 在弹窗里选「**教程 1 · Ar LJ 流体**」；
3. 它会自动生成 5 个模块：流体盒子、LJ 力场、能量最小化、NVT、RDF/MSD/密度。

![示例教程](/wiki/assets/img/examples.png)
<span class="img-caption">示例卡片带 level、来源、练什么、看什么；点击卡片即可创建。</span>

> [!NOTE]
> 「示例」不是只读演示。创建后它就是普通的 Study，你可以改任何参数、删模块、加模块、复制成新研究。

## 2. 看懂模型树

左侧模型树就是这次计算的“配方”，从上到下按顺序执行：

```text
结构：Ar 流体（800 atoms）
力场：Ar LJ（ε/σ/截断）
模拟：能量最小化 → NVT 85 K
分析：Ar-Ar RDF / Ar MSD / 密度分布
```

- 点任意一个模块，右侧 **Inspector** 会显示它的参数；
- 参数修改后会自动保存，并刷新 3D 预览和校验；
- 模块左侧的开关可以临时禁用某个模块；
- 「+ 添加模块」打开模块库，按类别添加结构/力场/模拟/分析模块。

## 3. 运行

点右上角「**运行**」。

底部控制台会实时显示 LAMMPS 的 stdout，顶部状态从 `running` 变成 `completed`。
你可以同时观察：

- 3D 视口：当前研究的**输入构型**（不是最终轨迹）；
- Console：LAMMPS 实际输出；
- 右侧 Inspector：缺项/警告/错误。

> [!WARNING]
> 3D 视口显示的是运行前的输入结构，不是 MD 最终帧。成键是按距离推断的示意。详见 [3D 预览可信度](/wiki/visualization/)。

## 4. 看结果

运行完成后，点顶部「**结果**」。你会看到：

| 结果 | 含义 |
| --- | --- |
| Thermo | 温度、势能、总能、压力、体积、密度随步数变化 |
| RDF | g(r)，径向分布函数 |
| MSD | 均方位移，判断扩散趋势 |
| Density | 沿 x/y/z 的密度分布 |
| Structure | 结构摘要（元素、原子数、晶胞） |
| Simulation | 作业状态、退出码、工作目录 |

![RDF 结果](/wiki/assets/img/results-rdf.png)
<span class="img-caption">教程 1 的 g(r)：第一峰约 3.78 Å，远场趋于 1。结果是本机真实运行。</span>

结果页右上角可以「导出结果」为 JSON。原始文件在 `.matforge/projects/<project>/runs/<run_id>/`。

## 5. 三个最常用的修改

### 改温度/步数

选中 `NVT 85 K` 模块，在 Inspector 改 `temperature` 或 `steps`，再运行。
温度改变会直接影响 g(r) 峰高、MSD 斜率和压力涨落。

### 改结构

- 用 `晶体结构` 改元素/晶格/晶胞常数/超胞；
- 用 `流体盒子` 改元素、数量、盒长；
- 用 `内置晶体库` 选真实 MOF CIF；
- 用 `导入结构` 上传自己的 CIF/XYZ/POSCAR。

### 换力场

- 简单体系：`Lennard-Jones`；
- 金属：`EAM 势`（选 `Cu_u3.eam` 等势文件）；
- 共价/多体：`自定义力场`（`tersoff` + `Si.tersoff`）；
- MOF/有机小分子：`力场库（UFF + 电荷）`；
- 有文献参数：`自定义力场` 直接填 `pair_style` / `pair_coeff`。

## 6. 你已经完成了一次真实计算

检查一下：

- Console 最后有 `Total wall time`；
- 结果页有 `Thermo` 和至少一个分析结果；
- 状态是 `completed`；
- 工作目录里有 `log.lammps`、`system.data`、`in.matforge`、`traj.lammpstrj`。

下一步建议：

1. 跟着 [教程 1](/wiki/tutorial-lj-fluid/) 理解 g(r) 和 MSD；
2. 再走 [教程 2](/wiki/tutorial-cu-eam/) 学 EAM 和势文件；
3. 最后用 [教程 5](/wiki/tutorial-zif8-gcmc/) 做一次 MOF 吸附等温线。

> [!TIP]
> 遇到红色报错，先看结果页的「Simulation」和运行目录里的 `log.lammps` 最后 20 行；常见原因在 [常见问题](/wiki/faq/) 里有对照表。
