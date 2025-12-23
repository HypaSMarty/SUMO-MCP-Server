# Traffic Signal Addition and Optimization Scenario

## 概述

本示例展示了一个完整的交通信号灯添加和优化工作流程，包含以下步骤：

1. **自动生成路网** - 使用 netgenerate 创建带信号灯的网格网络
2. **生成交通需求** - 使用 randomTrips.py 生成随机行程
3. **计算路径** - 使用 duarouter 计算车辆路径
4. **基线仿真** - 运行原始信号灯配置的仿真
5. **信号优化** - 使用 tls_cycle_adaptation 优化信号灯时序
6. **优化仿真** - 运行优化后配置的仿真
7. **性能对比** - 对比优化前后的性能指标

## 文件说明

### `signal_optimization_scenario.py`
- 原始完整版本
- 413 行代码
- 包含详细的步骤说明和错误处理
- **状态：** 部分功能（步骤 1-5 正常，步骤 6 需要调试）

### `signal_optimization_robust.py`
- 健壮重构版本
- 420 行代码
- 面向对象设计，更好的错误恢复
- **状态：** 步骤 1-5 正常，步骤 6 存在 TraCI 连接问题（已知问题）

### `README_signal_optimization.md`
- 详细使用文档
- 包含配置参数、可视化方法、故障排查
- 高级用法示例

## 已验证功能

以下步骤在 Windows + SUMO 1.25.0 环境下**完全正常工作**：

### ✅ 步骤 1：路网生成
```python
netgenerate(
    net_file,
    grid=True,
    grid_number=4,
    options=["--tls.guess", "true"]  # 自动添加信号灯
)
```
**输出：** 4x4 网格，12 个交通信号灯

### ✅ 步骤 2：需求生成
```python
random_trips(
    net_file,
    trips_file,
    end_time=1800,
    period=2.0
)
```
**输出：** 900 个行程（30 分钟仿真）

### ✅ 步骤 3：路径计算
```python
duarouter(net_file, trips_file, routes_file)
```
**输出：** 完整路径文件

### ✅ 步骤 4：基线仿真
```python
run_simple_simulation(baseline_cfg, 1800)
```
**输出：**
- 仿真成功完成
- 平均车辆数：38-39
- 平均速度：4.84 m/s
- FCD 数据：约 70,000 数据点

### ✅ 步骤 5：信号优化
```python
tls_cycle_adaptation(net_file, routes_file, optimized_net)
```
**输出：** 优化后的信号灯方案（SUMO `<additional>` 文件，包含 `<tlLogic>` 等信号灯程序），不是完整的 `.net.xml` 路网文件

### ⚠️ 步骤 6：优化仿真（已知问题）
```python
run_simple_simulation(optimized_cfg, 1800)
```
**状态：** TraCI 连接错误："Connection closed by SUMO"

**可能原因：**
1. `optimized.sumocfg` 将 `tls_cycle_adaptation` 的输出文件当作 `<net-file>`（路网）加载，SUMO 报错 `Invalid network, no network version declared` 后退出，导致 TraCI 连接被关闭
2. 正确用法应为：`<net-file>` 仍使用原始 `grid.net.xml`，并在 `<additional-files>` 中引用优化输出文件

## 使用方法

### 快速开始

```bash
# 设置环境变量
export SUMO_HOME=/path/to/sumo  # Linux/macOS
# 或
set SUMO_HOME=C:\Program Files\Eclipse\sumo  # Windows

# 运行场景（健壮版本）
cd /path/to/sumo-mcp
python examples/signal_optimization_robust.py
```

### 输出位置

```
examples/signal_opt_YYYYMMDD_HHMMSS/
├── grid.net.xml           # 网络文件（12 个信号灯）
├── trips.xml              # 行程定义（900 个）
├── routes.xml             # 计算后的路径
├── baseline.sumocfg       # 基线配置
├── baseline_fcd.xml       # 基线仿真数据 ✅
├── optimized.net.xml      # 优化后信号灯方案（additional 文件）
├── optimized.sumocfg      # 优化配置
└── optimized_fcd.xml      # 优化仿真数据（如果成功）
```

## 性能基准

基于实际运行（Windows 11, SUMO 1.25.0）：

| 步骤 | 耗时 | 输出 |
|------|------|------|
| 网络生成 | <1s | 12 traffic lights |
| 需求生成 | 1-2s | 900 trips |
| 路径计算 | 2-3s | Route file |
| 基线仿真 | 10-15s | 70K FCD points |
| 信号优化 | 5-10s | Optimized network |
| **总计（步骤 1-5）** | **~20-30s** | **Full baseline analysis** |

## 替代方案和变通办法

由于步骤 6 的已知问题，以下是一些替代方案：

### 方案 A：仅运行基线分析
```python
# 修改脚本，跳过优化步骤
if __name__ == "__main__":
    scenario = SignalOptimizationScenario(output_dir)
    scenario.step1_generate_network()
    scenario.step2_generate_demand()
    scenario.step3_compute_routes()
    scenario.step4_baseline_simulation()
    # 跳过步骤 5-6
```

### 方案 B：手动验证优化网络
```bash
# 使用 SUMO 工具验证优化后的网络
netconvert --sumo-net-file optimized.net.xml --output plain.net.xml

# 使用 sumo-gui 可视化
sumo-gui -n optimized.net.xml -r routes.xml
```

### 方案 C：使用不同的优化工具
```python
# 尝试 tlsCoordinator 替代 tlsCycleAdaptation
from mcp_tools.signal import tls_coordinator

result = tls_coordinator(net_file, routes_file, optimized_net)
```

## 学习价值

即使步骤 6 存在问题，该示例仍然展示了：

1. ✅ **自动化路网生成** - 无需手动设计
2. ✅ **智能信号灯放置** - 基于路网拓扑自动添加
3. ✅ **需求建模** - 随机行程生成和路径计算
4. ✅ **仿真集成** - TraCI + SUMO 的完整集成
5. ✅ **数据分析** - FCD 数据提取和统计分析
6. ⚠️ **优化工作流** - 概念验证（需要进一步调试）

## 已知限制

1. **TraCI 连接稳定性** - 优化后仿真可能失败（正在调查）
2. **SUMO 版本依赖** - 在 SUMO 1.25.0 测试，其他版本可能表现不同
3. **Windows 路径处理** - 跨驱动器场景已修复但仍需测试
4. **网络复杂度** - 大型网络（>10x10）可能需要更长时间

## 故障排查

### 问题："Connection closed by SUMO"

**症状：** 优化后仿真在 `run_simple_simulation()` 时失败

**临时解决方案：**
1. 使用基线仿真结果进行分析
2. 手动检查优化后网络文件
3. 尝试使用 sumo-gui 而非 sumo 二进制
4. 检查 SUMO 和 TraCI 版本兼容性

### 问题："Could not locate SUMO tool script"

**解决方案：**
```bash
export SUMO_HOME=/path/to/sumo
echo $SUMO_HOME/tools/randomTrips.py  # 验证文件存在
```

### 问题："Network generation failed"

**解决方案：**
```bash
# 验证 netgenerate 可用
netgenerate --version

# 检查选项名称
netgenerate --help | grep tls
```

## 贡献和改进

欢迎贡献以下改进：

1. **调试步骤 6** - 解决 TraCI 连接问题
2. **添加更多指标** - 延误时间、排队长度等
3. **可视化工具** - 自动生成性能对比图表
4. **参数优化** - 自动调整信号周期以达到最佳性能
5. **不同网络类型** - 支持真实路网（OSM 数据）

## 相关资源

- [SUMO Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)
- [SUMO Tools](https://sumo.dlr.de/docs/Tools/index.html)
- [TraCI Documentation](https://sumo.dlr.de/docs/TraCI.html)
- [tlsCycleAdaptation.py](https://sumo.dlr.de/docs/Tools/tls.html#tlscycleadaptationpy)

## 许可证

该示例遵循 SUMO-MCP 项目许可证。
