# Kaogong Wiki

<div class="home-hero">
  <div class="home-badges">
    <span class="pill accent">通用 LAMMPS 工作台</span>
    <span class="pill">M2.2</span>
    <span class="pill">LAMMPS 22 Jul 2025</span>
    <span class="pill">可复现示例</span>
  </div>
  <h2>把化学问题拆成模块，再把模块交给 LAMMPS。</h2>
  <p>
    Kaogong 不是某篇论文的展示页，也不是某个材料的专用工具。它像 COMSOL 的
    Model Builder：你选择结构、力场、模拟和分析模块，填参数，运行真实的 LAMMPS 计算，
    再从结果页读回曲线和结构信息。
  </p>
  <p>
    这份 Wiki 用五个公开的 LAMMPS 教学实例做“软件实操 + 化学知识”的双线教程：
    每一步既告诉你<strong>在界面哪里点</strong>，也解释<strong>背后的物理/化学量是什么</strong>。
  </p>
  <div class="home-actions">
    <a class="home-btn primary" href="/wiki/getting-started/">5 分钟上手 →</a>
    <a class="home-btn" href="/wiki/tutorial-lj-fluid/">从第一个教程开始</a>
  </div>
</div>

<div class="home-stats">
  <div class="home-stat"><strong>31</strong><span>通用模块（结构 / 力场 / 模拟 / 分析 / 数据）</span></div>
  <div class="home-stat"><strong>5</strong><span>可运行的 LAMMPS 教学实例</span></div>
  <div class="home-stat"><strong>196</strong><span>自动化测试（183 单元 + 13 真实 LAMMPS 集成）</span></div>
</div>

## 先选一条路径

<div class="home-grid">
  <a class="home-card" href="/wiki/chemistry-primer/">
    <span class="card-tag">化学优先</span>
    <strong>我想先弄懂物理/化学，再学软件</strong>
    <p>从力场、系综、RDF、MSD、GCMC 这些概念开始，再回到模块参数。</p>
  </a>
  <a class="home-card" href="/wiki/getting-started/">
    <span class="card-tag">软件优先</span>
    <strong>我想先跑起来，再理解参数</strong>
    <p>五分钟创建第一个研究、运行 LAMMPS、打开结果页，再逐步补化学背景。</p>
  </a>
</div>

## 五个实例：软件操作 + 化学知识

每个教程都按同一结构组织：**你会学到 → 先看结果 → 化学背景 → 在平台里怎么搭 → 参数逐项解释 → 结果怎么读 → 动手改一改 → 边界与来源**。

<div class="tutorial-list">
  <a class="tutorial-item" href="/wiki/tutorial-lj-fluid/">
    <span class="tutorial-num">01</span>
    <span><strong>Ar Lennard-Jones 流体</strong><span>LJ 势、g(r)、MSD、密度；入门第一课</span></span>
    <em>入门 · 15 min</em>
  </a>
  <a class="tutorial-item" href="/wiki/tutorial-cu-eam/">
    <span class="tutorial-num">02</span>
    <span><strong>Cu 的 EAM 金属模拟</strong><span>嵌入原子势、fcc 晶格、热振动、势文件库</span></span>
    <em>入门 · 18 min</em>
  </a>
  <a class="tutorial-item" href="/wiki/tutorial-si-tersoff/">
    <span class="tutorial-num">03</span>
    <span><strong>Si 的 Tersoff 共价晶体</strong><span>键序势、金刚石结构、多体势文件</span></span>
    <em>进阶 · 18 min</em>
  </a>
  <a class="tutorial-item" href="/wiki/tutorial-cu-npt/">
    <span class="tutorial-num">04</span>
    <span><strong>Cu 的 NPT 与密度</strong><span>恒压系综、热膨胀、压力涨落</span></span>
    <em>进阶 · 16 min</em>
  </a>
  <a class="tutorial-item" href="/wiki/tutorial-zif8-gcmc/">
    <span class="tutorial-num">05</span>
    <span><strong>ZIF-8 的 CH4 吸附等温线</strong><span>MOF、UFF、TraPPE、GCMC 压力扫描</span></span>
    <em>进阶 · 25 min</em>
  </a>
</div>

![示例教程界面](/wiki/assets/img/examples.png)
<span class="img-caption">「新建研究 / 示例教程」：每个示例只是模块与参数的数据组合，可编辑、可复用。</span>

## 为什么这些示例不是“写死的流程”？

> [!IMPORTANT]
> 示例存放在 `packages/matforge/data/examples.json`，内容只有 `name / description / level / source / goal / expected / tags / modules[]`。
> 后端 `build_study()` 按 `modules[]` 实例化模块，`resolve_study()` 走和用户手搭 Study 完全相同的一套解析。
> 没有为任何教程增加专用 API、专用模块或专用 UI 分支。

这意味着：

- 你可以把「教程 1」改成 5000 个 Ar、100 K、不同截断，它仍然只是同一个 `structure.fluid + forcefield.lj + sim.nvt` 组合；
- 你可以把「教程 5」换成自己的 CIF、自己的电荷和气体，流程不变；
- 新增示例 = 编辑 JSON + 重启 API，而不是改 Python 控制流。

> [!NOTE]
> Wiki 是静态站点，源码在 `wiki/`，由 `wiki/build.py` 从 Markdown 生成；Web 应用通过 FastAPI 的 `/wiki` 路径托管它。
> 页面里的截图来自本机真实运行，不是示意图。

## 你会在这份 Wiki 里看到什么

| 部分 | 内容 |
| --- | --- |
| [5 分钟上手](/wiki/getting-started/) | 打开、选示例、运行、看结果 |
| [界面导览](/wiki/ui-tour/) | Model Tree、Inspector、3D 视口、Console、Results |
| [化学模拟速查](/wiki/chemistry-primer/) | 力场、系综、PBC、RDF、MSD、GCMC 的最小知识集 |
| [模块参考](/wiki/modules/) | 31 个模块的参数、单位、适用边界 |
| 五个教程 | 软件实操与化学解释逐段对应 |
| [3D 预览可信度](/wiki/visualization/) | 哪些是真实坐标，哪些只是示意 |
| [常见问题](/wiki/faq/) | 单位、势文件、电荷、报错与性能 |
| [添加模块与示例](/wiki/extending/) | 数据驱动扩展示例与模块 |

> [!CHEMISTRY]
> 这套教程不要求你先学完计算化学。每个教程会在用到概念时解释它，并用本机实测值告诉你“结果大概应该长什么样”。
> 但请记住：教学参数不是论文参数；换体系、换力场、换电荷，数值会变。

## 平台能力：不只五个教程

教程覆盖“入门五课”，平台本身还提供通用工作流。这些页面同样按“软件操作 + 化学/数值背景”组织：

| 主题 | 你会学到 |
| --- | --- |
| [力学与热输运](/wiki/mechanics-thermal/) | 有限应变求弹性常数、Müller-Plathe 反向 NEMD 求热导率、XRD 峰位与晶格的关系 |
| [吸附热力学](/wiki/adsorption-thermo/) | Henry 常数、等量吸附热（van't Hoff / 涨落）、IAST 选择性与其有效性检查 |
| [批量、续跑与远程](/wiki/workflows/) | 运行队列、服务重启恢复、失败点重跑、restart 续算、SSH + Slurm 提交 |
| [输入导入与报告](/wiki/workflows/) | 把已有 `in.lammps` 变成模块链、导出可复现 zip、生成可打印 HTML 报告 |
| [让 Agent 改模块链](/wiki/agent/) | 自然语言 → 计划卡 → 批准/拒绝 → 模块改动 + 快照回滚 |
| [聚合物构建](/wiki/polymer/) | 用 SMILES 重复单元生成有键合拓扑的链，以及为什么初始密度不能太高 |
| [与 Materials Studio 对齐](/wiki/ms-alignment/) | MS 教程能力逐条对照：已有、等价、缺口与原因 |
