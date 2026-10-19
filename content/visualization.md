# 3D 预览：什么是真的，什么是示意的

这一页专门回答一个容易误解的问题：

> 3D 视口里的结构，和真正跑 LAMMPS 的结构是同一个吗？能保证和“真实结果”一样吗？

短答：**坐标/元素/晶胞来自同一份输入结构；视觉呈现（半径、颜色、成键）是示意性的；预览不是 MD 最终轨迹。**

## 1. 用什么做的？

代码：`apps/web/src/components/StructureViewer.tsx`。

| 元素 | 实现 |
| --- | --- |
| 原子 | `THREE.InstancedMesh` + `SphereGeometry`，每个原子一个实例 |
| 键 | `THREE.InstancedMesh` + `CylinderGeometry`，按距离推断 |
| 晶胞 | `THREE.LineSegments`，直接画 `cell.matrix` 的 8 个顶点/12 条边 |
| 相机/交互 | `PerspectiveCamera` + `OrbitControls` |
| 渲染 | `WebGLRenderer` |

没有用 OVITO、VMD、NGL、ASE 渲染器，也没有服务端生成图片。前端拿到 JSON 后实时建场景。

## 2. 数据从哪里来？

```text
GET /api/projects/<pid>/studies/<sid>/preview
  → StudyRunner.preview()
  → resolve_study()
  → structure_payload(resolved.structure)
  → { species, positions, cell, charges, ... }
  → StructureViewer
```

`resolve_study()` 和 `run` 用的是同一套解析；`run` 写 `system.data` 时也用同一个 `Structure`，只是经过 `to_lammps_box()` 旋转/包裹以符合 LAMMPS 的 restricted triclinic 约定。

所以：

- ✅ 元素种类、原子数、坐标、晶胞参数是真的；
- ✅ 内置 CIF 是真实 CIF；晶体/流体由通用 builder 生成；
- ✅ 固定 seed 的随机流体，预览/运行一致；
- ❌ 不是 MD 最终帧，也不是 GCMC 插入气体后的构型。

> [!IMPORTANT]
> 预览和 LAMMPS data 的 **Cartesian 坐标不一定逐位相同**：LAMMPS 会把任意晶胞旋转到 `a` 沿 x、`b` 在 xy 平面，并把原子包裹进盒子。旋转/包裹不改变距离和角度，所以是同一个物理构型。

## 3. 哪些是“示意”的？

### 原子半径

| 表现 | 半径 |
| --- | --- |
| 球棍 | 约 0.42 × 共价半径 |
| 空间填充 | 约 0.62 × 范德华半径 |
| 线框 | 约 0.18 × 共价半径 |

这些是为了看清结构，不是真实电子云/原子尺寸。空间填充也不是 100% 范德华球。

### 颜色

`ELEMENT_COLORS` 是自定义调色板，接近但不等同于 CPK。同一种元素在不同表示下颜色一致，但不代表任何物理量。

### 成键

```text
cutoff = (covalent_i + covalent_j) × 1.25
```

- 纯距离启发式，不是化学拓扑；
- 惰性气体（He/Ne/Ar/Kr/Xe/Rn）不画键；
- >5000 原子不画键；
- 最多 20000 条键；
- 键的粗细/颜色是示意。

所以它可能多画/少画键。**不要用 3D 视口的连线做化学键分析**；用 RDF/配位数或轨迹后处理。

### 周期镜像

只画主晶胞，不自动复制 periodic images。孔道/界面体系在边界处看起来可能不完整，但计算仍是周期的。

## 4. 预览 ≠ 最终结果

| 你想看 | 当前 3D 预览 | 正确做法 |
| --- | --- | --- |
| 初始构型 | ✅ 显示 | 直接用 |
| MD 最终构型 | ❌ 不显示 | 用 OVITO/VMD 打开 `traj.lammpstrj` |
| GCMC 插入的分子 | ❌ 不显示 | 看轨迹/密度分布 |
| 轨迹动画 | ❌ 没有 | 外部工具或后续“轨迹回放”模块 |
| 周期镜像 | ❌ 不复制 | 外部工具或后续增强 |

![模型树与 3D](/wiki/assets/img/model-builder.png)
<span class="img-caption">视口标题旁标注「输入构型」，提醒这不是轨迹帧。</span>

## 5. 为什么仍然值得用？

- 快速检查 CIF 是否导入正确（原子数、元素、盒长）；
- 检查超胞/流体盒子是否合理；
- 检查框架是否重叠/断裂；
- 给教程和讨论一个直观参照；
- 不替代科学可视化，但能避免“空结构/错元素”的低级错误。

## 6. 如何自己验证“预览=输入”？

1. 打开 `.matforge/projects/<pid>/runs/<run_id>/system.data`；
2. 看 `Atoms` 行数与元素（`Masses` 注释）；
3. 看盒子 `xlo xhi` / `ylo yhi` / `zlo zhi`；
4. 和视口标题的 `formula · n atoms`、晶胞边长对比。

坐标可能因旋转/包裹不同，但原子数、元素、晶胞长度应一致。

> [!TIP]
> 如果视口元素/原子数和 `system.data` 不一致，优先怀疑：CIF 对称性展开、disorder、超胞/导入模块顺序、或者预览被旧缓存。刷新页面/重选 Study 再试。

## 7. 下一步可以怎么增强？

- 轨迹帧滑块（读 `traj.lammpstrj`，按帧渲染）；
- 周期镜像复制（2×2×2）；
- 按拓扑/键表成键，而不是距离；
- 按 RDF/配位数着色；
- 原子选择/测量距离/角度；
- 导出当前视角 PNG。

这些是增强项，不是当前已保证的能力。
