# 让 Agent 修改模块链

Kaogong 的 Agent 不是“聊天窗口 + 万能脚本”，而是**只能通过工具操作 Study** 的执行体。这页讲清楚它的边界、审批和回滚。

## 1. 能力边界：工具即权限

Agent 能做的事都在工具目录里：建结构、复制超胞、建模拟、提交作业、做分析、读数据集、改 Study 模块……它**不能**直接读写文件、不能执行 shell。每一步都声明副作用（read / write / execute / destructive）和是否需要审批。

改模块链的工具（`agent/tools/study.py`）：

| 工具 | 作用 |
| --- | --- |
| `list_study_modules` | 读取模块链（只读） |
| `add_module` | 按模块目录校验后追加模块 |
| `set_module_param` | 改参数（参数名不存在会拒绝） |
| `remove_module` | 删第一个匹配的模块（destructive） |
| `rollback_study` | 恢复最近一次快照 |

**每次写操作之前**，工具会把当时的 `study.json` 存到会话目录 `agent/<会话>/snapshots/`。所以“改错了”是可撤销的。

## 2. 一次典型交互

1. 打开右侧「Agent」，选「目标 Study」；
2. 输入：「给它加上 273 K 的 GCMC 模块」；
3. 面板把目标 Study 的 id 带进目标文本，规划器生成计划：

```text
1. 读取当前模块链      list_study_modules
2. 存快照(基线)        list_study_modules
3. 添加模块 sim.gcmc   add_module  (temperature=273)
```

4. 你点「批准计划」→ 执行；点「拒绝」→ 会话取消，Study 一个字节都没改；
5. 执行完点「回滚上一步」→ 从快照恢复。

## 3. 信息不足时会追问

如果目标里没有体系、方法或参数，规划器**不会猜**。它会返回一个问题计划：

> 需要补充才能安全排计划：① 目标体系（化学式 / 内置结构 / 已导入结构），② 要做哪种计算（最小化 / NVT / NPT / GCMC / 分析），③ 温度、压力或步数等关键参数。

面板上出现输入框，你补充后它会带着补充信息重新规划。这样做的原因很实际：一个“猜错的温度”会污染后面所有结果，而多问一句只花 5 秒。

## 4. 计划长什么样

```json
{
  "summary": "在 Study std_xxx 上追加模块：sim.gcmc",
  "steps": [
    {"title": "读取当前模块链", "tool": "list_study_modules", "side_effect": "read"},
    {"title": "添加模块 sim.gcmc", "tool": "add_module", "side_effect": "write",
     "requires_approval": true, "args": {"temperature": 273}}
  ],
  "success_criteria": ["模块链包含新模块", "参数与用户描述一致", "可回滚到编辑前"],
  "risks": ["新增模块可能与其他模块参数冲突，需要看诊断"]
}
```

计划是数据，不是代码：它可以被审阅、被拒绝、被编辑（API 支持传回修改后的 plan）。

## 5. 什么时候别用 Agent

- 你需要**精确复现**一组参数：手搭模块更可控；
- 目标涉及多步条件判断（“如果压力超过 10 bar 就……”）：现在还是线性计划；
- 你需要**自定义 LAMMPS 命令**：那属于 `forcefield.custom` / `raw` 的领域，让 Agent 拼字符串不是好主意。

> [!NOTE]
> LLM 规划器需要 OpenAI 兼容接口（`MATFORGE_LLM_BASE_URL/_API_KEY/_MODEL`）。没有配置时用启发式规划器：它能处理“建晶体/跑 NVT/算 RDF/改指定 Study 的模块”这类明确目标，其他情况会追问而不是瞎猜。
