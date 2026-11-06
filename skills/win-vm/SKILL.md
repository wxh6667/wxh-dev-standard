---
name: win-vm
description: 在 Linux 宿主机上按需提供低内存 Windows 虚拟机（dockurr/windows 容器 + KVM）。SSH shell 为主通道（OpenSSH Server 已装好、自启），RDP 仅在装 SSH 类一次性设置时用。内置预装 Python 3.11 完整版（C:/Python311，含 tkinter/tcl-tk，pip 源已配清华）。用于需要运行 Windows 程序、编译 Windows 产物（如 PyInstaller 打包 exe）、测试 Windows 环境的任务；VM 默认 2G 内存、允许交换、用完即停零占用。
---

# Win-VM：按需低内存 Windows 虚拟机

在 Linux 宿主机上用 dockurr/windows 容器运行按需启停的 Windows 虚拟机。VM 限额 2G（实测占用约 1.1G），空闲依赖交换分区，不用时完全释放。

**首选通道是 SSH shell，不要用 GUI 自动化。** 2026-10-30 已完成一次性配置：VM 内安装 OpenSSH Server 并设自启；此后所有操作（装软件、编译、打包、文件传输 scp）都走 ssh/sscp，全程 shell。RDP + xdotool 仅在 SSH 尚未可用的全新系统上用来做这类一次性安装，做完即弃。

## 环境事实

- 部署位置 `~/win-vm/compose.yaml`，数据 `~/win-vm/storage/`（data.img 稀疏文件），凭据 `~/win-vm/.env`（`RDP_USER=winuser`，SSH/RDP 同账号密码，权限 600）。
- 版本用 `10`（Windows 10 Pro 正式版，已装好）。**不要改成 `10l`/`11l`（LTSC）**：dockur 的 LTSC 一律是评估版，许可证过期后周期性强制关机。正式版未激活仅有桌面水印，不影响功能。
- 端口只绑 `127.0.0.1`：3389（RDP）、8006（noVNC）。**SSH 22 未映射到宿主机**，从宿主机直连容器 IP：`ssh winuser@172.30.10.2`（容器网络宿主机可直接路由；IP 可能变化，用 `docker inspect windows --format '{{json .NetworkSettings.Networks}}'` 查当前 IP）。
- 宿主机 16G 长期只剩 2G 左右可用。dockur 启动时按当时 free 值自动下调 VM 内存，低于 2G 报错退出——等几分钟重试 `up -d` 即可，安装进度和磁盘数据都保留。

## 预装环境（2026-10-30 配置，持久在 data.img）

- **OpenSSH Server**：自启，防火墙入站 22 已放行。SSH 登录即普通 token（非提权），装机器级软件会 1603 失败——需要提权时用 `Start-Process -Verb RunAs` 或提前在 RDP 会话里装好。
- **Python 3.11.9 完整版**：`C:\Python311\python.exe`，含 tkinter、tcl/tk（`C:\Python311\DLLs\tcl86t.dll`/`tk86t.dll`）、pip。已装 PyInstaller 6.22.3、psd-tools、pillow。
- **pip 全局清华镜像已配置**（2026-10-31，持久在 data.img）：`%APPDATA%\pip\pip.ini`。任何 pip 调用（包括项目脚本、venv、`pip install -r`）都走镜像，不需要逐条加 `-i`。重装系统后必须重配，否则官方源实测会 `ReadTimeoutError`：
  ```
  powershell -NoProfile -c "New-Item -ItemType Directory -Force -Path $env:APPDATA\pip | Out-Null; Set-Content -Path $env:APPDATA\pip\pip.ini -Value \"[global]`nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple`ntrusted-host = pypi.tuna.tsinghua.edu.cn`ntimeout = 60\" -Encoding ASCII"
  ```
- VM 内可直接外网下载（curl.exe 自带），华为云 Python 镜像可用：`https://mirrors.huaweicloud.com/python/...`。
- **IIS / .NET / SQL Server（2026-11-01 安装，持久在 data.img）**：IIS 10、.NET Framework 3.5（CLR 2.0）、.NET 4.5、SQL Server 2022 Express 实例 `SQLEXPRESS`；已有 `a.9100dj.com` 验收站点 `C:\inetpub\wwwroot\a9100`（IIS 站点 `JqPwTest`，端口 8080）和测试库 `jqtest`。依赖已在镜像里，不要重复下载/安装；SQL 测试口令和连接串只在 VM 内，不进入仓库。

## 标准操作流程（SSH 优先）

1. 启动：`docker compose -f ~/win-vm/compose.yaml up -d`
2. 就绪判断：`docker logs windows --tail 1` 出现 `Windows started successfully`，再等约 60 秒。
3. 连接：`sshpass -p '<密码>' ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password winuser@<容器IP> '<命令>'`（宿主机需 sshpass；无则先装）。凭据变量在 `~/win-vm/.env`：`RDP_USER` / `RDP_PASS`（SSH 与 RDP 同密码）。**必须带 `PubkeyAuthentication=no`**：宿主 ssh-agent 里 key 多时，服务端会在密码前因 "Too many authentication failures" 直接断开。
4. 传文件：`sshpass -p '<密码>' scp -q <宿主文件> "winuser@<IP>:C:/Users/winuser/<目录>/"`。一次只传一个源，目录和文件混传会失败，分开执行。**注意：SSH 会话里 `\\tsclient\shared`（RDP 共享盘）不可用**，那是 RDP 会话专属映射。scp 取回的文件权限是 600，需要交付时 `chmod 644`。
5. 执行复杂 PowerShell：引号嵌套（bash→ssh→powershell 三层）极易出错，**写 .ps1 文件 scp 过去再 `powershell -ExecutionPolicy Bypass -File` 执行**。ps1 里中文文件名经 scp 传输会乱码，脚本内用通配符（`Get-ChildItem .../*.exe`）代替中文名。
6. 用完停止：`docker compose -f ~/win-vm/compose.yaml stop`（2 分钟优雅关机）。下次启动直接开机，约 1-2 分钟。

## 路径与引号陷阱（实测踩过）

- **Windows 安装器（python.org exe）的 `TargetDir` 必须用反斜杠**：`"TargetDir=C:\Python311"`。正斜杠 `C:/Python311` 会被 MSI 报 `Error 1606: Could not access network location`（1603 失败）。SSH 命令行里反斜杠要整体加引号。
- cmd 的 `dir` 不接受正斜杠路径；PowerShell 的 `Get-Item/Test-Path` 两者都行——验证文件存在用 PowerShell。
- Windows Installer 服务（msiserver）默认 Stopped；MSI 失败时先 `Start-Service msiserver` 再重试。
- **不要用 embeddable zip 版 Python**：不含 tkinter，PyInstaller 打包 GUI 程序会缺 tcl/tk；nuget python 包同样不含 tkinter。要完整版直接用 python.org 安装包静默装（注意上一条 TargetDir 陷阱）。

## RDP 一次性设置通道（仅全新系统用）

SSH 不可用时（如重装后）才走 RDP：

1. `xfreerdp /v:127.0.0.1:3389 /u:winuser /p:<密码> /cert:ignore /drive:shared,<宿主目录> /w:1280 /h:900 +clipboard &`
2. 用 `xdotool search --name "FreeRDP"` 拿窗口 ID，`windowactivate` 后发全局按键。VM 内 Win+R/开始菜单输入用 `xdotool type --delay 40`；注意焦点必须先落到 VM 窗口，否则 Super 键会触发宿主快捷键（实测 Super+R 打开了宿主 Remmina）。
3. 管理员 cmd 安装 OpenSSH：
   ```
   powershell -c "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
   powershell -c "Set-Service sshd -StartupType Automatic; Start-Service sshd; New-NetFirewallRule -Name sshd -DisplayName OpenSSH -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22"
   ```
   安装约 2-4 分钟，出现 `Path/Online: True/RestartNeeded: False` 即成功。之后立刻切 SSH，不再回 RDP。

## 内存控制规则

- `RAM_SIZE=2G` 是上限，不主动调高；需要更多时先查 `free -h`，剩余允许才小幅上调并说明，超过 4G 需用户确认。
- VM 内存不足自然走宿主机 swap，性能下降但功能正常，工具型用途可接受。
- 启动报 "requires at least 2.0 GB of RAM" 时等内存回升重试，不删除重装（数据都在）。

## 调试与边界

- noVNC(8006) 看 console 会话，与 RDP/SSH 会话画面不同步，只用来旁观。
- 磁盘镜像损坏（异常断电）：删 `~/win-vm/storage/data.img` 重新 `up -d` 重装——**注意这会丢掉预装的 SSH/Python 环境，需按上面 RDP 通道 + Python 安装步骤重配**。
- 删除整个 VM：`docker compose down` + 删 `~/win-vm/`。
- 用途定位：工具型任务（跑安装程序、编译产物、验证行为、PyInstaller 打包）。长期驻留服务、GPU/CAD 超范围。
- 中文输出乱码：SSH 直接跑 cmd/powershell 输出 GBK 会被当 UTF-8 显示乱码，判断结果靠退出码、文件存在性检查（Test-Path）和字节数，不靠读中文文案。

## 验证打包产物

文件存在只说明构建结束，**必须实际启动 exe**：GUI 程序缺 DLL 或 Qt 插件会立刻退出。

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'   # SSH 是 session 0，GUI 平台起不来；offscreen 足以加载 Qt 全部依赖
$p = Start-Process -FilePath <exe> -PassThru
Start-Sleep -Seconds 12
-not $p.HasExited                    # True = 启动成功
Stop-Process -Id $p.Id -Force
```

这段含多层引号，按上面的规则写成 `.ps1` 再 scp 执行，不要塞进 ssh 命令行。

## 实战案例（2026-10-30）

PyInstaller 打包登机牌生成器 exe 全链路：宿主 scp 项目文件 → VM 内 `C:/Python311/python.exe -m PyInstaller boardingpass.spec --noconfirm`（约 65s）→ scp 回宿主机 → VM 内启动 exe 验证进程与运行数据目录落位。spec 里的 tcl/tk DLL 绝对路径需按目标机 Python 实际位置改（本 VM 是 `C:\Python311\DLLs\`）。

## 实战案例（2026-10-31）PySide6 项目走项目自带构建脚本

`pms-complete-delivery` 客户端：宿主 `scp -r client` 到 `C:\Users\winuser\pms\client`（脚本按 `%~dp0..` 推导项目根，必须保持 `client` 子目录层级）→ `client.bat install` → `client.bat build`（内部跑 pytest + PyInstaller + 压缩 ZIP + 清理中间目录）→ 取回 `dist\ProductionManagement` 与 `dist\ProductionManagement-V1.0.zip`。首次 `install` 因官方源超时失败，配好 pip.ini 后约 2 分钟装完 PySide6 6.11.2；构建测试+打包约 3 分钟。产物未压缩 115MB、ZIP 49.7MB，offscreen 启动 12 秒存活。带 GUI 启动批处理时用 `cmd /c ...bat build > build.log 2>&1 &` 后台跑，再用 `Get-Content -Tail` 轮询，避免 ssh 长时间阻塞。
