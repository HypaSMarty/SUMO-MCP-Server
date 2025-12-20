# SUMO-MCP API 参考 (Unified Toolset)

为了提供更简洁、符合人类直觉的接口，我们将原有的 20+ 个工具合并为 7 个核心工具。每个工具通过 `action` 或 `method` 参数区分具体操作。

## 1. 路网管理 (manage_network)

管理 SUMO 路网文件的生成、转换和下载。

*   **工具名**: `manage_network`
*   **参数**:
    *   `action` (string): 操作类型，可选值：
        *   `generate`: 生成抽象路网（Grid/Spider）。
        *   `convert` (或 `convert_osm`): 将 OSM/OpenDrive 等格式转换为 SUMO 路网。
        *   `download_osm`: 从 OpenStreetMap 下载地图数据。
    *   `output_file` (string): 输出文件路径（对于 download_osm 为输出目录）。
    *   `params` (object, optional): 具体操作参数：
        *   `generate`: `{ "grid": bool, "grid_number": int }`
        *   `convert` / `convert_osm`: `{ "osm_file": string }`
        *   `download_osm`: `{ "bbox": "w,s,e,n", "prefix": string }`

## 2. 需求管理 (manage_demand)

管理交通需求生成、OD 矩阵转换和路径计算。

*   **工具名**: `manage_demand`
*   **参数**:
    *   `action` (string): 操作类型，可选值：
        *   `generate_random` (或 `random_trips`): 生成随机行程。
        *   `convert_od` (或 `od_matrix`): 将 OD 矩阵转换为行程。
        *   `compute_routes` (或 `routing`): 使用 duarouter 计算路由。
    *   `net_file` (string): 基础路网文件路径。
    *   `output_file` (string): 输出文件路径。
    *   `params` (object, optional): 具体操作参数：
        *   `generate_random` / `random_trips`: `{ "end_time": int, "period": float }`
        *   `convert_od` / `od_matrix`: `{ "od_file": string }`
        *   `compute_routes` / `routing`: `{ "route_files": string }` (输入行程文件)

## 3. 仿真控制 (control_simulation)

在线控制 SUMO 仿真实例的生命周期（需安装 GUI 或 CLI）。

*   **工具名**: `control_simulation`
*   **参数**:
    *   `action` (string): 操作类型，可选值：
        *   `connect`: 启动新仿真或连接现有实例。
        *   `step`: 向前推演仿真时间。
        *   `disconnect`: 断开连接并停止仿真。
    *   `params` (object, optional): 具体操作参数：
        *   `connect`: `{ "config_file": string, "gui": bool, "port": int }`
        *   `step`: `{ "step": float }` (默认为 0，表示一步)

## 4. 状态查询 (query_simulation_state)

在线查询仿真中的实时状态（车辆、路网等）。需在 `control_simulation` 建立连接后使用。

*   **工具名**: `query_simulation_state`
*   **参数**:
    *   `target` (string): 查询目标，可选值：
        *   `vehicle_list` (或 `vehicles`): 获取所有活跃车辆 ID。
        *   `vehicle_variable`: 获取特定车辆的具体变量。
        *   `simulation`: 获取全局仿真状态（时间、车辆数统计）。
    *   `params` (object, optional): 具体操作参数：
        *   `vehicle_variable`: `{ "vehicle_id": string, "variable": string }`
            *   `variable` 支持: `speed`, `position`, `acceleration`, `lane`, `route`

## 5. 信号优化 (optimize_traffic_signals)

执行交通信号灯优化算法。

*   **工具名**: `optimize_traffic_signals`
*   **参数**:
    *   `method` (string): 优化方法，可选值：
        *   `cycle_adaptation` (或 `Websters`): 周期自适应优化（基于 Webster 公式）。
        *   `coordination`: 绿波协调控制。
    *   `net_file` (string): 路网文件。
    *   `route_file` (string): 路由文件。
    *   `output_file` (string): 输出文件路径。

## 6. 自动化工作流 (run_workflow)

执行预定义的长流程任务。

*   **工具名**: `run_workflow`
*   **参数**:
    *   `workflow_name` (string): 工作流名称，可选值：
        *   `sim_gen_eval` (或 `sim_gen_workflow` / `sim_gen`): 自动生成路网并评估。
        *   `signal_opt` (或 `signal_opt_workflow`): 信号灯优化全流程对比。
        *   `rl_train`: 强化学习训练流程。
    *   `params` (object): 工作流参数字典。
        *   `sim_gen_eval`: `{ "output_dir", "grid_number", "steps" }`
        *   `signal_opt`: `{ "net_file", "route_file", "output_dir", ... }`
        *   `rl_train`: `{ "scenario_name", "output_dir", "episodes" }`

## 7. 强化学习任务 (manage_rl_task)

管理基于 `sumo-rl` 的强化学习任务。

*   **工具名**: `manage_rl_task`
*   **参数**:
    *   `action` (string): 操作类型，可选值：
        *   `list_scenarios`: 列出内置场景。
        *   `train_custom`: 运行自定义训练。
    *   `params` (object, optional):
        *   `train_custom`: `{ "net_file", "route_file", "algorithm", ... }`

---

## 遗留工具 (Legacy)

为了兼容性保留的独立工具：
*   `get_sumo_info`: 获取 SUMO 版本信息。
*   `run_simple_simulation`: 运行简单的配置文件仿真（离线）。
*   `run_analysis`: 解析 FCD 输出文件。
