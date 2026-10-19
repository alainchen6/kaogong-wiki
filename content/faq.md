# 常见问题与排错

## 运行相关

### 顶部 LAMMPS 状态是红色

后端没有找到 `lmp`。检查：

```bash
ls vendor/lammps/build/lmp
MATFORGE_LAMMPS_BIN=$PWD/vendor/lammps/build/lmp .venv/bin/uvicorn matforge.api.main:app
```

或者构建：

```bash
./scripts/build-lammps.sh
```

### 点运行没反应 / 立即失败

按顺序看：

1. Inspector 是否有红色错误（缺结构/力场/模拟）；
2. Console 最后几行；
3. `runs/<run_id>/log.lammps` 最后 20 行；
4. `runs/<run_id>/stderr.txt`。

### `Unrecognized pair_style` / `Unknown pair style`

LAMMPS 构建没有包含对应 package，或 `pair_style` 拼错。检查：

```bash
vendor/lammps/build/lmp -h | grep -i tersoff
```

### `Cannot open potential file`

势文件没有 staging 成功。平台会写 `missing_potentials.txt`。检查：

- 文件名是否裸名（不要写绝对路径）；
- 是否在 `vendor/lammps/potentials`；
- 或设置 `MATFORGE_POTENTIALS_DIR` 指向你的势文件目录；
- `pair_coeff` 里引用的文件名和 `potential_file` 是否一致。

> [!WARNING]
> 平台只接受 basename，防止 `../` 路径穿越。不要把绝对路径直接填进 `file`。

### `Incorrect format in EAM file` / 元素不匹配

最常见原因：把 setfl 的 `Cu_u3.eam` 用成了 `eam/alloy`，或元素顺序写错。

| 文件 | 正确 style |
| --- | --- |
| `Cu_u3.eam` | `eam` |
| `Al_jnp.eam` | `eam` |
| `Al_zhou.eam.alloy` | `eam/alloy` |
| `*.eam.fs` | `eam/fs` |

### 能量爆炸 / `Lost atoms`

- 时间步太大：先降到 0.001 ps；
- 初始结构重叠：先做能量最小化；
- 密度过高：扩大盒子；
- 势参数单位不对：确认 ε/eV、σ/Å；
- 温度过高：先低温平衡。

## 结构与单位

### 我的 CIF 导入后原子数不对

CIF 可能包含：

- 对称性展开（ASE 会展开）；
- disorder/部分占据；
- 溶剂/客体分子；
- 非标准晶胞设置。

先看 3D 视口和元素统计，再用 `structure.supercell`/删除原子（后续功能）处理。

### 为什么默认是 metal 单位？

平台面向 LAMMPS 通用计算，`metal`（eV/Å/ps/bar/K）对金属、MOF、分子都常用。LJ 教程用 Ar 参数换算到 metal，物理等价。

### 压力/密度看起来不对

小体系瞬时压力涨落很大。优先看：

- 平均密度/体积；
- 温度是否稳定；
- 是否达到平衡（前 1/3 轨迹丢弃）；
- 是否 NVT 固定体积导致压力偏离。

## 电荷与 GCMC

### 净电荷不为 0 会怎样？

平台会警告；如果开启 `neutralize`，会把残余电荷均匀加到所有原子上。这只是数值处理，不是物理电荷模型。正式计算请用 DDEC/拟电荷并保证中性。

### 为什么 CO2 吸附等温线不理想？

CO2 有四极矩/点电荷，对框架电荷和长程静电非常敏感。检查：

1. 框架是否有合理电荷；
2. 是否只用了 `coul/cut` 而没有 kspace；
3. guest 模型是否匹配（TraPPE 3-site）；
4. 是否需要极化/四极矩模型。

### GCMC 一直不吸附 / 吸附太多

- 压力点是否合理（0.001–100 bar）；
- `overlap_cutoff` 是否太大；
- 孔道是否可达（窗口太小）；
- 温度是否过高；
- 电荷是否过强/过弱；
- 步数是否足够（先看 `Atoms` 是否稳定）。

## 结果解读

### RDF 远场不趋于 1

可能：

- 归一化/帧数问题（平台已修复多帧归一化，并有回归测试）；
- 盒子太小；
- 轨迹不是同一组分；
- 分析 cutoff 接近盒子一半。

### MSD 出现平台

- 固体：正常，热振动；
- 液体但长时间：轨迹未 unwrap，最小镜像导致假平台；
- 温度太低/未平衡。

### 结果页没有 RDF

检查：

- 是否添加了 `analysis.rdf` 模块；
- 模拟是否产生 `traj.lammpstrj`；
- `max_frames` 是否 ≥2；
- 结果是否为 `other`（看错误信息）。

## 3D 与界面

### 3D 里原子/键看起来不对

3D 是输入构型 + 距离启发式成键。不是最终轨迹，也不是化学拓扑。详见 [3D 预览可信度](/wiki/visualization/)。

### 页面刷新后结果还在吗？

在。Study 和结果保存在 `.matforge/projects/...`；刷新会重新载入。原始日志/轨迹在 `runs/`。

### 能导出什么？

结果页「导出结果」导出当前 Study + 结果的 JSON。原始 LAMMPS 文件可直接从 runs 目录取。

## 性能

| 现象 | 建议 |
| --- | --- |
| 大体系 3D 卡 | >5000 原子不画键；可切线框/关晶胞 |
| LAMMPS 慢 | 减少步数/超胞；增大时间步需谨慎；用更多线程需重建 LAMMPS |
| GCMC 慢 | 减少压力点/步数；减小截断；扩大 `exchanges` 不一定更快 |
| 结果页卡 | 减少 `max_frames`/`nbins` |

> [!TIP]
> 先跑一个“小体系 + 少步数”验证模块链，再放大。不要一上来 100 万原子 + 1e6 步。
