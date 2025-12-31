# SUMO-MCP 系统开发实施计划

基于您的需求及 `SUMO-MCP 拓展功能开发指南.md` 文档，我制定了以下详细的开发实施计划。本项目旨在构建一个基于 Model Context Protocol (MCP) 的智能交通仿真平台，实现大模型对 SUMO 仿真引擎的自主调用与优化。

## 阶段一：环境准备与架构搭建 (Environment & Architecture)
**目标**：构建稳健的基础开发环境，确保依赖正确，并在本地跑通 "Hello World" 级别的 MCP 服务。
1.  **环境初始化**：
    *   检查并配置 Python 3.10+ 环境。
    *   使用 `uv` 初始化项目，配置 `pyproject.toml`。
    *   安装核心依赖：`fastmcp`, `sumolib`, `traci`, `sumo-rl`, `pandas`。
2.  **SUMO 引擎集成**：
    *   协助检查或指导安装 Eclipse SUMO。
    *   配置系统环境变量 `SUMO_HOME`，确保 Python 脚本能定位到 SUMO 二进制文件。
3.  **项目骨架生成**：
    *   创建符合模块化设计的目录结构：
        ```text
        sumo-mcp/
        ├── src/
        │   ├── server.py       # MCP 服务器入口
        │   ├── tools/          # 工具模块 (Network, Route, Signal, Analysis)
        │   ├── resources/      # 资源模块
        │   └── workflows/      # 复杂工作流编排
        ├── tests/              # 测试用例
        ├── doc/                # 文档
        └── pyproject.toml      # 依赖管理
        ```

## 阶段二：技术验证 (PoC)
**目标**：验证 MCP 协议与 SUMO 的通信链路，消除技术风险。
1.  **最小化 MCP 服务器**：
    *   使用 `FastMCP` 创建一个基础服务器实例。
    *   实现工具 `get_sumo_info`：验证能否调用系统中的 `sumo` 命令并返回版本信息。
2.  **基础仿真调用验证**：
    *   实现工具 `run_simple_simulation`：接受一个 `.sumocfg` 路径，通过 `traci` 启动仿真并返回简单的统计数据（如车辆数）。
    *   **风险评估**：验证 Windows 环境下 `stdio` 通信的稳定性。

## 阶段三：工程化开发 (Core Engineering)
**目标**：按照指南实现四大核心功能模块，封装 SUMO 的命令行工具。
1.  **Network 模块 (网络)**：
    *   封装 `netconvert`：实现从 OSM/XML 到 `.net.xml` 的转换工具。
    *   封装 `netgenerate`：支持生成网格（Grid）或蜘蛛网（Spider）路网。
2.  **Route 模块 (路径)**：
    *   封装 `randomTrips`：基于路网生成随机车辆需求。
    *   封装 `duarouter`：计算车辆的最优路径。
3.  **Signal 模块 (信号)**：
    *   实现信号灯状态查询工具（基于 `traci`）。
    *   集成 `sumo-rl` 环境的基本接口，为 RL 扩展做准备。
4.  **Analysis 模块 (分析)**：
    *   解析 `fcd-output` (Floating Car Data) XML 文件。
    *   使用 `pandas` 生成关键指标报告（平均等待时间、排队长度）。

## 阶段四：工作流集成与智能化 (Workflows & Intelligence)
**目标**：实现文档中描述的端到端自动化流程。
1.  **Sim Gen & Eval 工作流**：
    *   编排 "下载路网 -> 转换路网 -> 生成需求 -> 运行仿真 -> 输出报告" 的自动化链条。
2.  **Prompt 模板设计**：
    *   设计 `system_prompt`，指导 LLM 如何合理调用上述工具（例如：先检查路网文件是否存在，再运行仿真）。

## 阶段五：质量保障与交付 (QA & Delivery)
1.  **测试体系**：
    *   编写单元测试：针对每个 MCP 工具函数的输入输出进行测试。
    *   编写集成测试：模拟一个完整的仿真周期。
2.  **文档编写**：
    *   生成 `README.md`：包含安装指南、启动命令。
    *   生成 `API.md`：列出所有注册的 MCP 工具及其参数说明。

---
**确认事项**：
如果您同意此计划，我将首先从 **阶段一：环境准备与架构搭建** 开始执行。请确认是否继续。