# 界面导览

Kaogong 的主界面是一个 Model Builder，而不是一张固定报表。理解下面五个区域，后面的教程就只是“换模块、换参数”。

![Model Builder](/wiki/assets/img/model-builder.png)

## 1. 顶部：Study 与运行

| 控件 | 作用 |
| --- | --- |
| 项目名 / Study 下拉 | 切换当前研究；每个 Study 保存自己的模块链 |
| 新建研究 | 从示例或空白创建 |
| 模型 / 结果 Tab | 在搭建与结果之间切换 |
| LAMMPS 状态点 | 后端是否找到 LAMMPS 可执行文件 |
| 导入 in | 粘贴已有 `in.lammps`，解析成模块链（见 [工作流](/wiki/workflows/)） |
| 运行 | 解析模块 → 生成输入 → 提交本地 LAMMPS |
| 续跑 | 从上次的 `restart.final` 接着积分（仅 completed 后出现） |
| 队列 | 多个 Study 排队运行、限并发、失败点重跑 |
| 扫描 | 复制当前 Study 成一组参数不同的子研究 |
| Agent | 右侧面板，用自然语言改模块链（见 [Agent](/wiki/agent/)） |
| Wiki | 打开这份文档 |
| 状态 pill | draft / running / completed / failed |

一个 Study 就是一个可保存、可复用、可运行的“计算配方”。模块改了会自动保存到项目目录，不需要手动“保存”。

## 2. 左侧：Model Tree

模型树按类别分组：

```text
结构 / 几何
  └─ Ar 流体
力场 / 势函数
  └─ Ar LJ
模拟
  ├─ 能量最小化
  └─ NVT 85 K
分析
  ├─ Ar-Ar RDF
  ├─ Ar MSD
  └─ 密度分布
```

操作：

- **点击**：选中模块，右侧显示参数；
- **开关**：临时禁用模块（比如先不算 RDF）；
- **+ 添加模块**：打开模块库；
- **删除**：在 Inspector 底部；
- **排序**：Inspector 底部上/下箭头。

> [!IMPORTANT]
> 模块顺序有意义：结构必须在力场前，力场必须在模拟前；分析可以放在最后。顺序错了，Inspector 会给出缺项提示。

## 3. 中间：3D 视口

3D 视口用 three.js 实时渲染：

- 原子：实例化球体；
- 键：按距离推断的圆柱；
- 晶胞：实际 `cell.matrix` 的边；
- 交互：旋转、缩放、平移、自动旋转、重置视角；
- 表现：球棍 / 空间填充 / 线框。

它显示的是**输入构型**；运行完成后可以切到「轨迹」模式，用滑杆/播放按钮回放真实 dump 帧
（会按 `stride` 抽帧，帧数太多时只加载前 100 帧）。细节见 [3D 预览可信度](/wiki/visualization/)。

## 4. 右侧：Inspector

Inspector 根据模块的声明式参数 schema 自动生成表单。常见的参数类型：

| 类型 | 例子 |
| --- | --- |
| string | 化学式、势文件名、元素顺序 |
| number | 温度、压力、ε、σ、截断 |
| integer | 步数、超胞倍数、分箱数 |
| enum | 晶格类型、控温器、电荷模式、吸附质 |
| boolean | 是否中和净电荷 |
| text | 手动电荷、pair_coeff、元素:数量 |
| file | 由「从文件读取」按钮填入 CIF/XYZ/POSCAR 文本 |

Inspector 还会显示：

- 缺项/错误（红色）；
- 警告（黄色），例如净电荷不为 0、缺少势文件；
- 计算流程完成度（结构 → 力场 → 模拟 → 分析）。

## 5. 底部：Console

运行后，LAMMPS 的 stdout 通过 WebSocket 实时推送到 Console。它能帮你判断：

- 是否成功 `read_data`；
- 是否找到势文件；
- 是否出现 `ERROR` / `WARNING`；
- 运行是否真的结束（`Total wall time`）。

Console 可以折叠/展开和清空，但**原始日志仍在** `runs/<run_id>/log.lammps`。

## 6. 结果页

结果页按类型展示：

| 类型 | 适合看什么 |
| --- | --- |
| Thermo | 温度/能量是否稳定，压力/密度量级 |
| RDF | 近邻距离、配位数、无序/晶体结构 |
| MSD | 扩散趋势，`MSD ~ 6Dt` |
| Density | 沿某个轴的密度均匀性/孔道分布 |
| Isotherm | GCMC 的 uptake–压力曲线 |
| Charges | 每个类型的平均电荷与 ε/σ |
| Simulation | 作业状态、退出码、工作目录 |

右上角「导出结果」把当前 Study 和结果打包成 JSON。

## 7. 文件在哪里

```text
.matforge/
  projects/<project_id>/
    studies/<study_id>/study.json        # 模块链
    studies/<study_id>/results/*.json    # 结果
    runs/<run_id>/
      in.matforge                       # 生成的 LAMMPS 输入
      system.data                       # 结构 + 质量 + 电荷
      log.lammps
      traj.lammpstrj
      job.json
```

这意味着你可以：

- 直接检查/复用生成的 LAMMPS 输入；
- 用 OVITO/VMD 打开轨迹；
- 把 `study.json` 复制给同事；
- 用脚本批量创建 Study（见 [添加模块与示例](/wiki/extending/)）。

## 8. 轨迹、扫描、Data 与 Agent

- **轨迹**：运行后点视口「轨迹」，拖动/播放 `traj.lammpstrj`；可切 2×2×2 周期镜像。
  有拓扑时按显式 bonds 画键，否则回到距离启发式。
- **扫描**：顶部「扫描」选模块/参数/值，平台克隆多个子 Study；可勾选立即运行。
- **Data**：在模块库「数据」中加入 `实验数据`，选择 NIST/CSV 数据集；结果页会叠加实验点。
- **分析**：配位数、键角、孔体积、XRD 在结果页自动出图/表。
- **Agent**：顶部「Agent」打开侧栏；goal → 计划/消息/批准，复用已有 Agent 运行时。
- **导出**：结果页「JSON / LAMMPS / 报告」分别导出结果、可运行 zip、HTML 报告。

## 9. 一次完整操作的心里模型

```text
Study
  → resolve_study()：模块链 → Structure + ForceFieldSpec + Phase[] + Analysis[]
  → SimulationSpec：单位、边界、原子风格、输出
  → write_run_inputs()：system.data + in.matforge
  → LocalRunner：lmp 子进程
  → parse_log / iter_dump_frames
  → StudyResult[]：thermo / rdf / msd / density / isotherm / charges
```

你在 UI 上改的每一个参数，最终都落在这条链的某一层；没有“演示数据”分支。

> [!TIP]
> 如果你想确认“预览和运行是不是同一套”，打开 `.matforge/.../system.data`，对比 3D 视口里的原子数、元素和晶胞长度即可。坐标可能因 LAMMPS 的旋转/包裹而不同，但几何是同一套。
