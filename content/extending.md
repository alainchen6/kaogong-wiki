# 添加模块与示例

这一页写给想扩展平台的人。核心原则：

> **示例是数据，模块是通用能力。**  
> 不允许为某个教程/材料在 Python 里写专用流程；新增示例优先改 JSON。

## 1. 新增一个示例（不改 Python）

1. 在界面里搭好 Study，跑通；
2. 打开 `packages/matforge/data/examples.json`；
3. 复制一个已有示例，改 `name/description/level/source/goal/expected/tags`；
4. 把 `modules[]` 换成你 Study 的 `type/label/params`；
5. 重启 API，刷新页面。

示例结构：

```json
{
  "my_example": {
    "name": "我的示例",
    "description": "一句话说明",
    "level": "入门",
    "source": "https://…",
    "source_title": "来源标题",
    "goal": "练什么",
    "expected": "看什么",
    "tags": ["LJ", "NVT"],
    "modules": [
      {"type": "structure.crystal", "label": "Cu fcc", "params": {"formula": "Cu", "lattice": "fcc", "a": 3.615}},
      {"type": "forcefield.lj", "label": "LJ", "params": {"epsilon": 0.167, "sigma": 2.315, "cutoff": 5.0}},
      {"type": "sim.nvt", "label": "NVT 300 K", "params": {"temperature": 300, "steps": 1000}}
    ]
  }
}
```

`build_study()` 会检查 `type` 是否已注册；未注册会报可读错误。  
示例参数不需要写默认值，解析器会与 `ModuleSpec` 默认值合并。

> [!IMPORTANT]
> 不要为示例在 `resolve_study()` 里加 `if template == "my_example"` 分支。示例必须走通用 resolver。

## 2. 新增一个模块

模块由三部分组成：

1. `ModuleSpec`：UI 参数 schema；
2. resolver 分支：模块 → `Structure / ForceFieldSpec / Phase / Analysis`；
3. runner 分支（如果是分析）。

### 2.1 注册 spec

在 `packages/matforge/study/modules.py` 的 `MODULES` 里加：

```python
"sim.anneal": ModuleSpec(
    type="sim.anneal",
    name="升温退火",
    category="simulation",
    description="线性升温到目标温度。",
    icon="thermometer",
    needs_structure=True,
    params=[
        _p("start", "起始温度 / K", "number", 300.0, min=1),
        _p("stop", "终止温度 / K", "number", 600.0, min=1),
        _p("steps", "步数", "integer", 1000, min=1),
    ],
    produces=["phase"],
),
```

### 2.2 加 resolver

在 `resolve_study()` 里：

```python
elif module.type == "sim.anneal":
    resolved.phases.append(
        Phase(
            name=module.label,
            kind="run",
            ensemble="nvt",
            temperature=float(params["stop"]),
            velocity=float(params["start"]),
            timestep=0.001,
            thermostat=Thermostat(start=float(params["start"]), stop=float(params["stop"])),
        )
    )
```

实际实现还要确认 LAMMPS 的 `fix nvt` 支持 `start/stop` 温度；如果不够，用 `fix_add` 注入自定义命令。**新增能力要通用**：不要绑定某个材料。

### 2.3 前端

不需要改表单：Inspector 会按 `params` 自动渲染。  
只需要给 `icon` 在 `moduleIcons.ts` 里加映射（可选，缺省会 fallback）。

### 2.4 测试

至少：

- 单元：resolver 生成正确 `Phase`/`ForceFieldSpec`；
- 集成：真实 LAMMPS 跑通并产生结果；
- 失败路径：缺参数/缺结构返回可读错误。

## 3. 势文件库

`packages/matforge/forcefield/potentials.py` 负责：

- 搜索 `MATFORGE_POTENTIALS_DIR`；
- 搜索 `vendor/lammps/potentials`；
- 只接受 basename，阻止路径穿越；
- `resolve_potential(name)` 返回绝对路径或 `None`。

新增势文件不需要改代码：把文件放进上述目录即可。  
如果要内置到包里，放 `packages/matforge/data/potentials/` 并在 `potential_dirs()` 加目录。

## 4. 气体/吸附质

`packages/matforge/data/adsorbates.json` 是真实气体模型库。新增一个气体：

```json
"MyGas": {
  "name": "MyGas · 模型名",
  "description": "…",
  "source": "文献",
  "atoms": [
    {"label": "C_g", "element": "C", "x": 0, "y": 0, "z": 0,
     "charge": 0.0, "epsilon_k": 100.0, "sigma": 3.4}
  ],
  "bonds": [],
  "angles": []
}
```

平台会自动生成 molecule 模板、guest 原子类型、mixing 对。  
参数单位是 K 和 Å；`charge` 是 e。

> [!WARNING]
> 不要凭感觉填 ε/σ。用文献/数据库，并在 `source` 写清楚。错误的参数会给出“看起来能跑但物理错误”的结果。

## 5. 新增结构数据

- 内置 CIF：`packages/matforge/data/structures/`，在 `builders.py` 的 `bundled_structures()` 映射显示名；
- 用户 CIF：走 `structure.import`，不需要改代码；
- 随机流体/晶体：用 `structure.fluid`/`structure.crystal`。

## 6. 开发检查清单

```bash
.venv/bin/ruff check packages tests
.venv/bin/mypy packages/matforge
.venv/bin/pytest -q
cd apps/web && npm run build
```

新增/修改示例后：

```bash
.venv/bin/python wiki/build.py
```

然后刷新 `/wiki/`。

> [!TIP]
> 平台的核心约束是“可组合、可追溯、可复现”。如果你发现某个功能只能通过给某个材料写 if 分支实现，那它应该被拆成通用模块或数据参数。
