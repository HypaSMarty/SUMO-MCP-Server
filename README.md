# SUMO-MCP: 基于模型上下文协议的自主交通仿真平台

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

SUMO-MCP 是一个连接大语言模型 (LLM) 与 Eclipse SUMO 交通仿真引擎的智能中间件。通过 Model Context Protocol (MCP)，它允许 AI 智能体（如 Claude, Cursor, TRAE）直接调用 SUMO 的核心功能，实现从**OpenStreetMap 数据获取**、**路网生成**、**需求建模**到**仿真运行**与**信号优化**的全流程自动化。

系统支持**离线仿真**（基于文件的工作流）和**在线交互**（实时 TraCI 控制）两种模式，满足从宏观规划到微观控制的多样化需求。

## 🚀 核心功能特性

### 1. 全面的工具链集成
聚合为 7 个符合直觉的核心 MCP 接口：

*   **路网管理 (`manage_network`)**: 统一处理抽象路网生成 (Grid/Spider)、OSM 地图下载与格式转换。
*   **需求管理 (`manage_demand`)**: 一站式生成随机行程、转换 OD 矩阵和计算车辆路由。
*   **信号优化 (`optimize_traffic_signals`)**: 集成周期自适应 (Cycle Adaptation) 和绿波协调 (Coordination) 算法。
*   **仿真与分析**: 执行标准仿真 (`run_simple_simulation`) 与 FCD 数据分析 (`run_analysis`)。

### 2. 在线实时交互 (Online Interaction)
支持通过 TraCI 协议与运行中的仿真实例进行实时交互，赋予 LLM 微观控制能力：

*   **仿真控制 (`control_simulation`)**: 启动连接、单步推演、安全断开。
*   **状态查询 (`query_simulation_state`)**: 实时获取车辆列表、速度、位置、加速度等微观数据。

### 3. 自动化智能工作流
内置端到端的自动化工作流 (`run_workflow`)，简化复杂任务：

*   **Sim Gen & Eval**: 一键执行 "生成路网 -> 生成需求 -> 路径计算 -> 仿真运行 -> 结果分析" 的完整闭环。
*   **Signal Optimization**: 自动执行 "基线仿真 -> 信号优化 -> 优化仿真 -> 效果对比" 的全流程。
*   **RL Training**: 针对内置场景或自定义路网执行强化学习训练 (`manage_rl_task`)。

### 4. 工程化与质量保障
*   **现代化依赖管理**: 采用 `uv` + `pyproject.toml`，确保环境一致性与依赖安全。
*   **类型安全**: 全面引入 Python Type Hints，通过 `mypy` (Strict Mode) 静态检查。
*   **代码规范**: 遵循 PEP 8 标准，集成 `flake8` 代码风格检查。
*   **全面测试**: 内置功能测试、性能测试与集成测试套件，确保系统稳定性。

---

## 🛠️ 环境要求

*   **操作系统**: Windows / Linux / macOS
*   **Python**: 3.10+ (强制要求，以支持最新的类型系统与 MCP SDK)
*   **SUMO**: Eclipse SUMO 1.23+ (需配置 `SUMO_HOME` 环境变量)

---

## 📦 安装指南

### 1. 获取代码
```bash
git clone <repository_url>
cd sumo-mcp
```

### 2. 环境配置 (推荐使用 uv)

我们强烈推荐使用 [uv](https://github.com/astral-sh/uv) 进行极速环境管理：

```bash
# 安装 uv (如果尚未安装)
pip install uv

# 创建虚拟环境并同步依赖
uv venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装项目依赖 (包含开发工具)
uv pip install -r pyproject.toml --all-extras
```

### 3. 环境配置 (使用 Conda/Pip)

```bash
# 创建并激活 Conda 环境
conda create -n sumo-mcp python=3.10
conda activate sumo-mcp

# 安装依赖
pip install .[dev]
```

### 4. 配置 SUMO
确保系统环境变量 `SUMO_HOME` 指向您的 SUMO 安装目录 (例如 `F:\sumo`)。

---

## 🚦 启动服务

使用 Python 启动 MCP 服务器：

```bash
python src/server.py
```

服务器启动后将监听标准输入 (stdin) 的 JSON-RPC 消息，您可以将其配置到任何支持 MCP 的宿主应用中。

**Claude Desktop 配置示例**:
```json
{
  "mcpServers": {
    "sumo-mcp": {
      "command": "path/to/your/venv/python",
      "args": ["path/to/sumo-mcp/src/server.py"]
    }
  }
}
```

---

## 💡 使用示例 (Prompt)

在配置了 MCP 的 AI 助手中，您可以尝试以下自然语言指令：

*   **工作流任务**:
    > "生成一个 3x3 的网格路网，模拟 1000 秒的交通流，并告诉我平均车速。"
    > *(AI 将调用 `manage_network` 和 `run_workflow`)*
*   **在线交互任务**:
    > "启动这个配置文件的仿真，每运行一步就告诉我 ID 为 'v_0' 的车辆速度，如果速度低于 5m/s 就提醒我。"
    > *(AI 将调用 `control_simulation` 和 `query_simulation_state`)*
*   **强化学习任务**:
    > "列出所有内置的强化学习场景，然后选择一个简单的路口场景训练 5 个回合。"
    > *(AI 将调用 `manage_rl_task` 和 `run_workflow`)*

---

## 📂 项目结构

```text
sumo-mcp/
├── src/
│   ├── server.py           # MCP 服务器入口 (LiteMCP 实现，聚合接口)
│   ├── utils/              # 通用工具
│   │   ├── connection.py   # TraCI 连接管理器
│   │   └── ...
│   ├── mcp_tools/          # 核心工具模块
│   │   ├── network.py      # 网络工具
│   │   ├── route.py        # 路径工具
│   │   ├── signal.py       # 信号工具
│   │   ├── vehicle.py      # 车辆工具
│   │   ├── rl.py           # 强化学习工具
│   │   └── analysis.py     # 分析工具
│   └── workflows/          # 自动化工作流
│       ├── sim_gen.py      # 仿真生成工作流
│       ├── signal_opt.py   # 信号优化工作流
│       └── rl_train.py     # RL 训练工作流
├── pyproject.toml          # 项目配置与依赖管理
├── requirements.lock       # 锁定依赖版本
└── README.md               # 项目文档
```

## 📄 许可证

MIT License
