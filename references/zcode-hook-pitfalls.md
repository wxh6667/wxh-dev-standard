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

Trellis 生成的 `.zcode/config.json` 若被 `trellis update` 或重新安装平台胶水覆盖，钩子命令会退回 `${ZCODE_PROJECT_DIR}` 直拼形态，此坑复发。覆盖后按本页"根治方案"重套一遍命令模板，并用"验证方法"跑一遍矩阵。
