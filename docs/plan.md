# SUMO-MCP 问题修复方案

## 执行摘要

当前代码在理想场景（SUMO_HOME 已设置、文件在同一驱动器、Linux/类 Unix 系统）下工作正常，但存在**多个严重的跨平台和边缘场景问题**，阻塞开源发布。

### 核心问题总结

**阻塞发布的 P0 问题：**
- 无法通过 `pip install -e .` 安装（pyproject.toml 配置缺失）
- Windows 用户无法自动检测 SUMO（未实现标准安装路径）

**生产环境风险（P1）：**
- 生成的 .sumocfg 在 Windows 跨驱动器场景下包含绝对路径，不可移植
- 错误检测依赖字符串比较，脆弱且容易误判

**设计改进空间（P2-P3）：**
- 异常处理过于宽泛，可能隐藏真实问题
- 错误消息不够详细，用户难以自行排查
- 文档和测试在 Windows 上存在兼容性问题

---

## P0 - 必须修复（阻塞发布）

### 问题 1：pyproject.toml 配置缺失

**现象：**
```
ValueError: Unable to determine which files to ship inside the wheel
The most likely cause of this is that there is no directory that matches the name of your project (sumo_mcp).
```

**根本原因：**
- `pyproject.toml` 缺少 `[tool.hatch.build.targets.wheel]` 配置
- 项目使用 `src/` 布局但未告知 hatchling 打包器

**影响范围：**
- 用户无法通过 `pip install -e .` 安装
- 无法构建 wheel 包进行分发
- 严重影响开发体验和部署流程

**修复策略：**

在 `pyproject.toml` 中添加以下配置：

```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**验证方法：**
1. 在干净的虚拟环境中执行 `pip install -e .`
2. 验证无 wheel 构建错误
3. 执行 `python -c "from server import server; print('OK')"` 验证导入成功
4. 执行 `pip install build && python -m build` 验证可构建 wheel

---

### 问题 2：Windows 标准安装路径未支持

**现象：**
- Windows 用户即使已正确安装 SUMO，如果未设置 `SUMO_HOME` 环境变量，仍然无法自动检测

**根本原因：**
- `src/utils/sumo.py:43-67` 的 `find_sumo_home()` 仅硬编码了 Linux 路径 `/usr/share/sumo`
- 未检测 Windows 常见安装位置
- 未尝试读取 Windows 注册表

**影响范围：**
- Windows 是 SUMO 主要用户平台之一
- 大多数 Windows 用户使用官方安装包，默认安装到 `C:\Program Files\Eclipse\sumo`
- 这些用户的首次体验是"找不到 SUMO"

**修复策略：**

在 `src/utils/sumo.py` 的 `find_sumo_home()` 函数中，添加 Windows 检测逻辑：

```python
def find_sumo_home() -> Optional[str]:
    """
    Resolve SUMO_HOME.

    Priority:
    1) SUMO_HOME environment variable
    2) Derive from `sumo` executable location when it matches <SUMO_HOME>/bin/sumo
    3) Platform-specific common locations:
       - Windows: C:/Program Files/Eclipse/sumo, Registry
       - Linux: /usr/share/sumo
       - macOS: /usr/local/Cellar/sumo/*/share/sumo (Homebrew)
    """
    # 1. Environment variable
    env_home = os.environ.get("SUMO_HOME")
    if env_home:
        home = Path(env_home).expanduser()
        if home.exists():
            return str(home)

    # 2. Derive from binary location
    sumo_binary = find_sumo_binary("sumo")
    candidate = _candidate_sumo_home_from_binary(sumo_binary)
    if candidate and candidate.exists():
        return str(candidate)

    # 3. Platform-specific common locations
    import sys

    if sys.platform == 'win32':
        # Windows common installation paths
        win_paths = [
            Path("C:/Program Files/Eclipse/sumo"),
            Path("C:/Program Files (x86)/Eclipse/sumo"),
            Path("D:/sumo"),  # Common custom location
            Path("C:/sumo"),
        ]
        for path in win_paths:
            if path.exists() and (path / "tools").exists():
                return str(path)

        # Try Windows Registry (optional, requires winreg)
        try:
            import winreg
            key_path = r"SOFTWARE\Eclipse\SUMO"
            for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    key = winreg.OpenKey(hive, key_path)
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    winreg.CloseKey(key)
                    if install_path and Path(install_path).exists():
                        return str(install_path)
                except FileNotFoundError:
                    continue
        except ImportError:
            pass  # winreg not available (non-Windows)

    elif sys.platform == 'darwin':
        # macOS Homebrew installation
        import glob
        homebrew_pattern = "/usr/local/Cellar/sumo/*/share/sumo"
        matches = glob.glob(homebrew_pattern)
        if matches:
            # Return the latest version
            latest = sorted(matches)[-1]
            return str(Path(latest).parent.parent.parent)

    # Linux fallback
    linux_home = Path("/usr/share/sumo")
    if linux_home.exists():
        return str(linux_home.parent)  # Return /usr/share parent

    return None
```

**验证方法：**
1. 编写单元测试 mock `sys.platform='win32'`
2. Mock `Path.exists()` 返回 True for `C:/Program Files/Eclipse/sumo`
3. 验证 `find_sumo_home()` 返回正确路径
4. 在实际 Windows 机器上测试（SUMO 安装在标准位置，不设置 SUMO_HOME）
5. 执行 `get_sumo_info` 工具，验证能正确检测

---

## P1 - 强烈建议（影响用户体验）

### 问题 3：Windows 跨驱动器路径导致 .sumocfg 不可移植

**现象：**
```xml
<net-file value="D:\sumo\tools\net\grid.net.xml"/>  <!-- 绝对路径！ -->
<route-files value="routes.xml"/>  <!-- 相对路径 -->
```

**根本原因：**
- `src/workflows/signal_opt.py:84-93` 的 `_as_cfg_path()` 函数
- 当 net/route 文件与 `output_dir` 在不同 Windows 驱动器时，`os.path.relpath()` 抛出 `ValueError`
- 代码 fallback 到绝对路径，导致配置文件不可移植

**影响范围：**
- 生成的 `.sumocfg` 包含 Windows 特定的绝对路径
- 无法在其他机器上使用
- 无法移动到其他目录
- 无法提交到版本控制系统并在团队间共享

**修复策略：**

**方案 A（推荐）：强制文件本地化**

修改 `signal_opt_workflow()` 在生成配置前，将所有输入文件复制到 `output_dir`：

```python
import shutil

def signal_opt_workflow(
    net_file: str,
    route_file: str,
    output_dir: str,
    steps: int = 3600,
    use_coordinator: bool = False
) -> str:
    """Signal Optimization Workflow with portable config files."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Localize input files to output_dir for portability
    local_net_file = os.path.join(output_dir, os.path.basename(net_file))
    local_route_file = os.path.join(output_dir, os.path.basename(route_file))

    if os.path.abspath(net_file) != os.path.abspath(local_net_file):
        shutil.copy2(net_file, local_net_file)
    if os.path.abspath(route_file) != os.path.abspath(local_route_file):
        shutil.copy2(route_file, local_route_file)

    # Use local files for all subsequent operations
    net_file = local_net_file
    route_file = local_route_file

    # ... rest of workflow ...
```

然后简化 `_as_cfg_path()` 函数，仅使用相对路径：

```python
def _as_cfg_path(file_path: str, cfg_dir: str) -> str:
    """Convert file path to relative path for portability."""
    abs_path = os.path.abspath(file_path)
    abs_cfg_dir = os.path.abspath(cfg_dir)

    try:
        rel_path = os.path.relpath(abs_path, abs_cfg_dir)
        # Only use relative path if it doesn't escape output directory
        if not rel_path.startswith(".."):
            return rel_path
    except ValueError:
        pass  # Different drives on Windows

    # Fallback: Issue warning and use basename (assume file is in same dir)
    import warnings
    warnings.warn(
        f"Cannot create portable relative path from {abs_cfg_dir} to {abs_path}. "
        f"Using basename only. Ensure files are in the same directory.",
        UserWarning
    )
    return os.path.basename(file_path)
```

**方案 B（备选）：明确文档说明限制**

如果不采用方案 A，至少在文档中明确说明：

```python
def signal_opt_workflow(...):
    """
    Signal Optimization Workflow.

    **Important:** For portable configuration files, ensure all input files
    (net_file, route_file) are on the same drive as output_dir (Windows)
    or use absolute paths that exist on all target machines.

    Generated .sumocfg files may contain absolute paths in cross-drive scenarios.
    """
```

**验证方法：**
1. 编写单元测试，使用跨驱动器路径（mock 或实际 Windows 环境）
2. 验证生成的 `.sumocfg` 仅包含相对路径或 basename
3. 验证配置文件可以移动到其他目录并正常运行
4. 在 Linux 上测试，确保不会引入回归

---

### 问题 4：find_sumo_binary 返回值语义不清晰

**现象：**
```python
sumo_binary = find_sumo_binary("sumo")
if sumo_binary == "sumo":  # 用字符串比较判断失败
    return "Error finding sumo binary..."
```

**根本原因：**
- `find_sumo_binary()` 找不到二进制时返回原始名称（如 `"sumo"`）而非 `None`
- 调用者必须用字符串比较 `== "sumo"` 来检测失败
- 这个设计脆弱：如果调用 `find_sumo_binary("sumo-gui")`，检测逻辑会失效

**影响范围：**
- 代码语义不清晰，容易误用
- 调用者需要知道传入的原始名称才能正确判断
- 返回值既可能是有效路径，也可能是无效的命令名

**修复策略：**

1. 修改 `src/utils/sumo.py` 中的 `find_sumo_binary()` 返回 `Optional[str]`：

```python
def find_sumo_binary(name: str) -> Optional[str]:
    """
    Find a SUMO binary by name.

    Resolution order:
    1) `sumolib.checkBinary()` (respects SUMO_HOME when set)
    2) `shutil.which()` (respects PATH)

    Returns:
        Absolute path to the executable if found, None otherwise.
    """
    try:
        resolved = sumolib.checkBinary(name)
        if resolved and resolved != name and Path(resolved).exists():
            return resolved
    except Exception:
        pass  # Fall through to PATH check

    which = shutil.which(name)
    return which  # Returns None if not found
```

2. 更新所有调用处，使用 `if not sumo_binary:` 判断：

```python
# src/mcp_tools/simulation.py
def run_simple_simulation(config_path: str, steps: int = 100) -> str:
    sumo_binary = find_sumo_binary("sumo")
    if not sumo_binary:  # 清晰的 None 检查
        return (
            "Error: Could not locate SUMO executable. "
            "Please ensure SUMO is installed and either `sumo` is available in PATH or `SUMO_HOME` is set."
        )
    # ...
```

**验证方法：**
1. 更新类型注解，运行 `mypy` 验证类型正确性
2. 编写单元测试，验证找不到时返回 `None`
3. 编写单元测试，验证找到时返回有效路径
4. 全局搜索 `find_sumo_binary` 的所有调用，确保都已更新

---

## P2 - 改进（提升健壮性）

### 问题 5：异常捕获过于宽泛

**位置：** `src/utils/sumo.py:20-23`

**修复策略：**

```python
def find_sumo_binary(name: str) -> Optional[str]:
    try:
        resolved = sumolib.checkBinary(name)
        # ...
    except (SystemExit, OSError, FileNotFoundError) as e:
        # Log specific error for debugging
        import logging
        logging.debug(f"sumolib.checkBinary failed for {name}: {e}")
        pass  # Fall through to PATH check
```

**验证：** 单元测试 mock 不同异常类型，验证正确处理

---

### 问题 6：错误消息不够精确

**位置：** `src/mcp_tools/simulation.py:21-25`

**修复策略：**

```python
def run_simple_simulation(config_path: str, steps: int = 100) -> str:
    sumo_binary = find_sumo_binary("sumo")
    if not sumo_binary:
        import os
        import shutil
        return (
            f"Error: Could not locate SUMO executable.\n"
            f"Diagnostics:\n"
            f"  - SUMO_HOME: {os.environ.get('SUMO_HOME', 'Not Set')}\n"
            f"  - PATH search: {shutil.which('sumo') or 'Not Found'}\n"
            f"  - sumolib check: Failed\n"
            f"\n"
            f"Please:\n"
            f"  1. Install SUMO from https://sumo.dlr.de/\n"
            f"  2. Set SUMO_HOME environment variable, OR\n"
            f"  3. Add SUMO bin directory to PATH\n"
        )
```

**验证：** 手动测试无 SUMO 环境，验证错误消息清晰度

---

### 问题 7：README 和启动脚本的环境变量说明不足

**修复策略：**

在 `README.md` 中添加平台特定的安装指南：

```markdown
## Installation & Setup

### 1. Install SUMO

**Windows:**
1. Download from https://sumo.dlr.de/
2. Run installer (default: `C:\Program Files\Eclipse\sumo`)
3. Option A: Add `C:\Program Files\Eclipse\sumo\bin` to PATH
4. Option B: Set environment variable:
   ```cmd
   setx SUMO_HOME "C:\Program Files\Eclipse\sumo"
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc
# SUMO_HOME is auto-set to /usr/share/sumo
```

**macOS (Homebrew):**
```bash
brew install sumo
export SUMO_HOME="$(brew --prefix sumo)/share/sumo"
echo 'export SUMO_HOME="$(brew --prefix sumo)/share/sumo"' >> ~/.zshrc
```

### 2. Verify Installation

```bash
python -c "from utils.sumo import find_sumo_home; print(find_sumo_home())"
```

Should output your SUMO installation path.

### Important Notes

- **SUMO_HOME is required** when using tool scripts (randomTrips.py, osmGet.py, etc.)
- **SUMO_HOME is optional** when only using binaries (sumo, netconvert, etc.) if they're in PATH
```

**验证：** 在三个平台上按文档操作，验证说明准确性

---

## P3 - 测试基础设施

### 问题 8：Windows 测试兼容性问题

**现象：** `tests/test_server_jsonrpc_smoke_without_sumo_home.py` 在 Windows 上失败
```
OSError: [WinError 10038] 在一个非套接字上尝试了一个操作
```

**根本原因：**
- 测试使用 `selectors` 模块处理进程 I/O
- Windows 的 `select()` 不支持文件描述符（仅支持 socket）

**修复策略：**

使用跨平台的进程通信方法：

```python
import sys
import subprocess
import threading
import queue

def _read_json_line(process, timeout_s=5.0):
    """Read a single JSON line from process stdout (cross-platform)."""

    if sys.platform == 'win32':
        # Windows: Use threading to avoid blocking
        result_queue = queue.Queue()

        def reader():
            try:
                line = process.stdout.readline()
                result_queue.put(("line", line))
            except Exception as e:
                result_queue.put(("error", e))

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

        try:
            result_type, result_value = result_queue.get(timeout=timeout_s)
            if result_type == "error":
                raise result_value
            return json.loads(result_value)
        except queue.Empty:
            raise TimeoutError("Timeout reading from process")
    else:
        # Unix: Use select as before
        import select
        # ... existing select-based code ...
```

**验证：** 在 Windows 和 Linux 上运行完整测试套件

---

## 实施路线图

### Phase 1: 阻塞修复 (P0) - 1-2 天
1. 修复 pyproject.toml 配置
2. 实现 Windows 路径检测
3. 验证测试通过

### Phase 2: 核心改进 (P1) - 2-3 天
4. 修复跨驱动器路径问题
5. 重构 find_sumo_binary 返回值
6. 更新所有调用处
7. 全面测试

### Phase 3: 体验优化 (P2) - 1-2 天
8. 改进异常处理
9. 增强错误消息
10. 完善文档

### Phase 4: 测试加固 (P3) - 1 天
11. 修复 Windows 测试
12. 增加跨平台集成测试

### 发布检查清单
- [ ] 所有 P0 问题已修复
- [ ] 所有 P1 问题已修复
- [ ] 在 Windows/Linux/macOS 上测试通过
- [ ] 文档已更新
- [ ] pyproject.toml 可正常构建 wheel
- [ ] 发布 v0.1.1

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Windows 注册表读取失败 | 低 | 已加 try-except，fallback 到路径检测 |
| 跨驱动器文件复制性能 | 中 | 仅在必要时复制，添加进度提示 |
| find_sumo_binary 重构引入回归 | 中 | 全面单元测试 + 集成测试覆盖 |
| 文档与代码不同步 | 低 | 在 CI 中添加文档有效性检查 |

---

## 成功指标

1. **可安装性：** `pip install -e .` 在所有平台成功率 100%
2. **自动检测率：** Windows 标准安装无需设置 SUMO_HOME 即可使用
3. **可移植性：** 生成的 .sumocfg 文件在不同机器间 100% 可用
4. **测试覆盖：** Windows/Linux/macOS 平台测试通过率 100%
5. **用户反馈：** GitHub Issues 中"找不到 SUMO"问题减少 80%
