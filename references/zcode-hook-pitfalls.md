# ZCode 钩子环境坑：`${ZCODE_PROJECT_DIR}` 随 shell cwd 漂移

这是 ZCode 平台级的环境坑参考，适用于任何在 `.zcode/config.json` 里注册 command hook 的项目（典型：Trellis 生成的平台胶水）。2026-09-17 在 beer-machine 项目确诊并根治。

## 症状

对话进行中（通常执行过 `cd` 进入子目录之后），每次提交消息都弹错：

```text
hooks_prompt_block: python3: can't open file '<项目根>/<子目录>/.zcode/hooks/inject-workflow-state.py':
[Errno 2] No such file or directory
```

特点：新对话正常，"跑几个对话就变成这样"；报错的是 `UserPromptSubmit` 钩子，但 `SessionStart` / `PreToolUse` 钩子同样会中招。

## 根因（两层）

1. **ZCode 按"工具持久跟踪的 shell 当前工作目录"展开 `${ZCODE_PROJECT_DIR}`**，而不是固定的工作区根目录。对话里 `cd docker` 之后，这个模板变量在后续所有钩子命令里都展开成 `<项目根>/docker`，并把同名环境变量注入钩子进程。于是 `python3 "${ZCODE_PROJECT_DIR}/.zcode/hooks/xxx.py"` 去子目录找脚本，找不到。
2. **`python3` 打不开文件时退出码恰好是 2**，而 ZCode 的 hook 约定里 2 表示"阻止"，所以每次 prompt 都被当成 block 弹错，而不是普通失败。

附带一层：即便把脚本路径修正到仓库根，钩子脚本内部还会读 `ZCODE_PROJECT_DIR` 环境变量定位项目（例如 Trellis 的 `session-start.py` 用它拼 `/.trellis`，环境变量指向子目录时直接 `ModuleNotFoundError: No module named 'common'`）。所以**只修命令行路径不够，必须同时校正环境变量**。

## 根治方案

钩子命令不信任 `${ZCODE_PROJECT_DIR}` 的指向，以它为起点用 git 锚定到仓库真实根，路径和环境变量一起校正：

```json
{
  "type": "command",
  "command": "R=$(git -C \"${ZCODE_PROJECT_DIR}\" rev-parse --show-toplevel 2>/dev/null || echo \"${ZCODE_PROJECT_DIR}\"); export ZCODE_PROJECT_DIR=\"$R\"; exec python3 \"$R/.zcode/hooks/<脚本>.py\"",
  "timeout": 15
}
```

要点：

- `git rev-parse --show-toplevel` 从任意子目录出发都返回仓库真实根；不在 git 仓库时回退原值，行为不劣于修复前。
- 前提是仓库内**没有嵌套 git 仓库**（嵌套会让 toplevel 锚到子仓库）；有嵌套仓库的项目需要换用固定锚点。
- 用户级 hook（如 `gate-commit-trellis.py`）用绝对路径注册，天然免疫此坑，不需要改。
- `.claude/settings.json` 若用相对路径（`python3 .claude/hooks/x.py`）属同类隐患，Claude Code 平台是否同样受影响未验证，遇到再按同思路处理。

## 系统级修复（生成器模板 + 批量脚本）

上游 `@mindfoldhq/trellis` 截至 0.6.17（2026-09-11）生成的仍是脆弱形态，升级不能解决。本机系统级落地方案（2026-09-17 完成）：

1. **补丁打在全局安装的生成器模板上**：`$(npm root -g)/@mindfoldhq/trellis/dist/templates/zcode/config.json` 四条命令改为锚定形态（`{{PYTHON_CMD}}` 占位符保留）。以后 `trellis init` / 平台胶水安装生成的项目天生正确。注意：**npm 升级该包会还原模板**，升级后重跑脚本即可。
2. **批量修复/巡检脚本 `scripts/fix-zcode-hook-paths.py`**（幂等，写前带时间戳备份）：
   ```bash
   python3 scripts/fix-zcode-hook-paths.py --check <项目目录>...      # 只读巡检，有脆弱命令退出码 1
   python3 scripts/fix-zcode-hook-paths.py --trellis-template <项目目录>...  # 模板 + 项目一起修
   ```
   已经锚定的命令原样跳过，所以可安全反复执行；`trellis update` 重新生成项目配置后重跑一遍即可复原。
3. **已修复项目（2026-09-17）**：beer-machine、owncast、yshop-drink、vehicle-link；同时清理了历史遗留的子目录 `.zcode` 转发存根/副本（beer-machine 的 docker、RuoYi-App、RuoYi-Vue3、RuoYi-Java、RuoYi-Java/sql/schema，owncast 的 web，yshop-drink 的 docker）——配置锚定仓库根后这些副本不再被任何路径解析命中，留着只会漂移和误导。

限制与边界：

- 锚定命令用了 `$()` / `||`，**仅适用 POSIX shell 的 host**（本机 Linux）；Windows host 不适用此改法。
- 前提是项目 git 仓库无嵌套 `.git`，有嵌套仓库的项目不能套用。
- claude 平台模板（`.claude/settings.json` 的相对路径写法）**未改**：真实 Claude Code 的 hook 进程 cwd 锚定在项目根，相对路径成立且未观察到故障；若未来观察到同类漂移再按相同思路处理。

## 验证方法

不要只测仓库根场景。模拟"故障场景"（把 `ZCODE_PROJECT_DIR` 指到子目录）逐条执行钩子命令：

```python
import json, subprocess, os
cfg = json.load(open('.zcode/config.json'))
env = dict(os.environ, ZCODE_PROJECT_DIR="<项目根>/docker")  # 故障锚点
for event, groups in cfg['hooks']['events'].items():
    for g in groups:
        for h in g['hooks']:
            p = subprocess.run(['sh', '-c', h['command']], input=b'{}',
                               capture_output=True, env=env)
            print(event, h['command'].rsplit('/', 1)[-1], p.returncode)
```

判定标准：子目录锚点、深层子目录锚点、仓库根锚点三种场景 × 全部钩子，exit=0 且 stderr 无 `No such file` / `ModuleNotFoundError`。

## 反模式：子目录转发存根

曾在出错的子目录放小脚本转发回仓库根（`docker/.zcode/hooks/xxx.py` → 根脚本）应急，实践证明不可靠，不要再用：

- 打地鼠：shell cwd 可能落在任意子目录，每个新目录都要补存根。
- 相对层级极易写错：从 `<子目录>/.zcode/hooks/` 回仓库根的 `.zcode/hooks/` 需要上跳 **3** 级，实际写成了 2 级，存根 exec 自己，无限递归到钩子超时。
- 曾混入硬编码其它机器绝对路径（`/home/gpy/...`）的存根，换机器即坏。

## 维护提醒

Trellis 生成的 `.zcode/config.json` 若被 `trellis update` 或重新安装平台胶水覆盖，钩子命令会退回 `${ZCODE_PROJECT_DIR}` 直拼形态，此坑复发。覆盖后重跑 `scripts/fix-zcode-hook-paths.py`（含 `--trellis-template`），并用"验证方法"跑一遍矩阵。新增 Trellis 项目后建议用 `--check` 巡检一次。
