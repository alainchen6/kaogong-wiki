# 批量、续跑、远程与导入导出

这四件事看起来是“工程细节”，但它们决定了你是在“玩一次模拟”，还是在“做一组可复现的计算”。平台把它们做成通用能力，不绑定任何材料。

## 1. 运行队列：一次排多个 Study

**在界面里**：顶部「队列」→ 勾选要跑的 Study → 设并发数 → 「排队并运行」。

**它做了什么**

- 每个 Study 仍然走同一个 `StudyRunner`，队列只负责“排队、限并发、记状态”；
- 队列状态写到 `projects/<项目>/batches/<批次>.json`，**服务重启后**会把“运行中”的项重置为排队并继续；
- 已完成的项不会被重复执行——所以“续跑一个批次”不会重算做完的点；
- 失败项会单独标红（带退出码和错误），点「重跑此点」只重跑它，不影响其他项。

> [!NOTE]
> 并发数指的是同时跑的 Study 数，不是 MPI 进程数。单机建议 1–2，否则 LAMMPS 之间会抢 CPU；真正的并行交给 Slurm（见第 3 节）。

## 2. 续算：从 restart 文件接着跑

每次 Study 结束都会写一个 `restart.final`（盒子、速度、拓扑都在里面）。结果页/顶部出现「续跑」按钮时：

1. 后端把上一次的 `restart.final` 作为 `read_restart` 输入；
2. 重新施加力场/系综（LAMMPS 的 restart 不保存 `fix` 和 `pair_coeff`，必须重设）；
3. 以同样的相（phase）继续积分，新的结果覆盖当前 Study 结果，旧 run 目录保留可追溯。

**什么时候该用**：只想延长生产段（比如 20 ps 不够），不要重建结构；或者作业被墙钟时间杀掉，从最近的 restart 接着跑。

> [!WARNING]
> 续跑不会自动缩短已有结果——它生成一个新的 run；如果你改了温度/压力，那叫“改参数重跑”，不是续跑。

## 3. 远程：SSH + Slurm

本地队列适合笔记本；集群上的正确做法是远程提交。设置：

```bash
MATFORGE_EXECUTION=remote
MATFORGE_REMOTE_HOST=user@cluster
MATFORGE_REMOTE_BASE_DIR=/scratch/$USER/matforge
MATFORGE_REMOTE_SCHEDULER=slurm
MATFORGE_REMOTE_PARTITION=gpu
MATFORGE_REMOTE_LAMMPS_COMMAND="lmp -in in.matforge"
```

**一次远程运行的流程**

1. `rsync` 把 run 目录传上去；
2. `sbatch --parsable` 提交（分区/核数/墙钟来自 `Resources`），拿到 job id；
3. 每 `poll_seconds` 查一次 `squeue`，结束了用 `sacct` 读最终状态和退出码；
4. 增量 `tail` 远端 stdout，实时回传到网页控制台；
5. 结束/取消/超时后 `rsync` 把 log、轨迹、restart 拉回本地，再走本地同一套解析。

> [!IMPORTANT]
> 这条路要求 `ssh` 免密（BatchMode）和 `rsync` 可用。测试里用 mock transport 验证了提交/轮询/取消/取回；**没有**真实集群可以联调，所以第一次接你们的集群时，请先用一个 100 步的小算例验证路径、分区名和 LAMMPS 模块加载（`module load`）。

## 4. 导入已有的 in.lammps

**在界面里**：顶部「导入 in」→ 粘贴 `in.lammps`（可选粘贴 `system.data`）→ 导入。

平台会解析常见子集：

| 命令 | 转换结果 |
| --- | --- |
| `units` / `atom_style` | Study 的全局设置 |
| `read_data` | 结构导入模块 |
| `pair_style` + `pair_coeff` | 力场模块参数 |
| `fix … nvt/npt/nve` | 对应系综模块（温度/步数尽量还原） |
| `timestep` / `run` | 时间步与步数 |

**不支持的命令**（变量、循环、`include`、复杂 `compute`）会**列出来**，不会被静默忽略。导入后你可以像正常 Study 一样改参数、加分析、再运行。

反过来，`导出` 会给一个 zip：`in.matforge` + `system.data` + 势文件 + `study.json`，可以直接拿去任何 LAMMPS 环境复现。

## 5. 报告与图表

- 结果页每个图有 **PNG** 导出；
- `结果 CSV` 导出所有结果的关键指标；
- `报告` 打开一个自包含 HTML：输入参数、力场/电荷/拓扑、每个结果的标量表 + 数据表、警告与诊断、复现说明。浏览器「打印 → 另存为 PDF」就是 PDF。

> [!NOTE]
> 报告是**从存储的真实结果生成的**：没有结果就没有数字。它不会替你补一个“漂亮”的曲线。
