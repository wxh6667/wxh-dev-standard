---
name: fingerprint-chromium
description: 运行和管理 my-fingerprint-chromium 指纹浏览器容器（基于 adryfish/fingerprint-chromium 的 Docker 镜像，CDP 127.0.0.1:9222 接入）。用于需要反检测浏览器、多账号指纹隔离、带 Xray 代理出口的浏览器自动化、Playwright/Puppeteer 接入指纹浏览器、代理质量评分检测等任务。只覆盖镜像的使用；镜像的构建与发布不在本 skill 范围内。
---

# fingerprint-chromium：指纹浏览器容器

镜像：`registry.cn-shanghai.aliyuncs.com/heilaowang/my-fingerprint-chromium:148.0.7778.215`

一个容器实例 = 一个浏览器实例。指纹身份（种子/CPU 核数/屏幕分辨率）首次启动随机生成，持久化在数据卷的 `.container-identity` 里，重启不变。源码仓库：`~/桌面/codes/my-fingerprint-chromium`（详细文档在其 `dosc/` 目录）。

## 启动与验证

```bash
docker run -d --name fp-account-1001 \
  -p 127.0.0.1:9222:9222 \
  --shm-size=2g \
  -v fp-account-1001:/data/profile \
  registry.cn-shanghai.aliyuncs.com/heilaowang/my-fingerprint-chromium:148.0.7778.215
```

带代理出口：

```bash
  -e UPSTREAM_PROXY="socks5://user:pass@proxy.example.com:1080" \
  -e BROWSER_LOCALE=zh_CN.UTF-8 \
  -e TIMEZONE=auto
```

验证 CDP（返回 `webSocketDebuggerUrl` 即就绪）：

```bash
curl http://127.0.0.1:9222/json/version
```

多实例时每实例独立的容器名、数据卷和宿主机端口（`-p 127.0.0.1:9223:9222` 依次递增）。

## 身份机制（核心规则）

- `FINGERPRINT`、`FINGERPRINT_HARDWARE_CONCURRENCY`、`SCREEN_WIDTH`/`SCREEN_HEIGHT`（成对）只接受 `random`（默认，随 profile 持久化）和 `random-each`（每次重掷不落盘）。**不支持固定数字，设了会拒绝启动。**
- `random-each` 只用于一次性会话；持久账号用它会造成"cookie 稳定但指纹每次变"的强关联信号。
- 重新掷身份：删掉数据卷里的 `.container-identity` 再重启（保留登录态和缓存，只换指纹）：

```bash
docker run --rm -v fp-account-1001:/data/profile alpine rm /data/profile/.container-identity
```

- 固定身份的唯一方式：启动前预写 `${USER_DATA_DIR}/.container-identity`（`key=value` 行，key 为 `fingerprint`、`hardware_concurrency`、`screen_resolution`，如 `1920x1080`）。
- 每次启动 stderr 输出一行 `Resolved identity: fingerprint=… hardware_concurrency=… screen=WIDTHxHEIGHT source=…`，`docker logs` 里可直接解析登记。
- 多账号纪律：每账号固定同一组数据卷、代理出口、语言、时区。同 IP 多指纹比同指纹多 IP 更容易被关联。

## 常用环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `FINGERPRINT_PLATFORM` | `linux` | `windows` / `linux` / `macos` |
| `FINGERPRINT_BRAND` / `FINGERPRINT_BRAND_VERSION` | `Chrome` / 空 | 浏览器品牌与版本 |
| `BROWSER_LOCALE` | `en_US.UTF-8` | 系统 locale，浏览器语言和 Accept-Language 从此派生 |
| `TIMEZONE` | `UTC` | `auto` 跟随代理出口 IP 时区（需设 `UPSTREAM_PROXY`，解析失败直接退出） |
| `BROWSER_MODE` | `headful-xvfb` | `headless` / `headful-xvfb` / `debug-novnc` |
| `BROWSER_EXTENSIONS` | 空 | `capsolver` 或绝对路径；空则不加载扩展 |
| `UPSTREAM_PROXY` / `PRE_PROXY` | 空 | Xray 上游/前置代理链接；空则不启动 Xray |
| `XRAY_LISTEN` | `127.0.0.1` | 改 `0.0.0.0` + 发布 `10808` 才能容器外用 Socks |
| `USER_DATA_DIR` | `/data/profile` | 建议挂命名卷 |
| `OPEN_SCORE_SITES_ON_START` | `0` | `1` 启动后自动打开评分站点 |

额外 Chromium 参数放镜像名后逐项传入（如 `--disable-spoofing=gpu`）。指纹、平台/品牌、语言/时区、代理、CDP、profile、窗口和运行模式由容器统一管理，追加参数不能覆盖这些。

## 代理（Xray）

`UPSTREAM_PROXY` 支持 VMess、VLESS（REALITY/XHTTP/gRPC/mKCP/ws/H2/QUIC/TLS）、Trojan、Shadowsocks（含 2022）、Socks5、HTTP、裸 `host:port` 和 `host:port:user:pass` 格式。

流量路径：`Chromium -> Xray(容器内 socks5://127.0.0.1:10808) -> [PRE_PROXY] -> UPSTREAM_PROXY -> 目标`。

检查代理与看日志：

```bash
docker exec fp-account-1001 check-proxy.sh
docker exec fp-account-1001 tail -n 100 /tmp/xray/xray.log
```

启动时默认做代理连通检查（`PROXY_STARTUP_CHECK=1`），失败即退出，不会静默裸连。

## 自动化接入

CDP 地址 `http://127.0.0.1:9222`：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.new_page()
    page.goto("https://browserleaks.com/canvas")
    print(page.title())
    browser.close()
```

标准 Puppeteer/Playwright 连接会发送可被页面感知的 `Runtime.enable`。对外自动化优先用 Patchright、nodriver 或 rebrowser-patches 一类修过 CDP 泄漏的驱动（同样连 9222）。

## 可视化调试（noVNC）

```bash
  -e BROWSER_MODE=debug-novnc \
  -e VNC_PASSWORD='change-me' \
  -p 127.0.0.1:6080:6080
```

浏览器打开 `http://127.0.0.1:6080/vnc.html`，CDP 仍保留。仅临时调试用，平时不开。

## 边界与故障

- 宿主机必须允许非特权 user namespace（Chrome 沙箱依赖）。启动报 `No usable sandbox` 时，放开宿主机的 `kernel.apparmor_restrict_unprivileged_userns`；镜像不提供 `--no-sandbox` 兜底。
- WebGL 走软件渲染（llvmpipe）；目标站点因此拦截时可在镜像名后追加 `--disable-spoofing=gpu` 实测对比。
- 已知内核边界（按目标站点实测，不可配置）：Pixelscan 能识别 canvas 噪声方案；fingerprint.com playground 对 Chromium + CDP 组合报 bot 信号。不要试图通过升级 Chromium 版本解决——新版本 canvas 像素读回时渲染进程崩溃，上游暂不升级。
- 出口 IP 质量比指纹调优更重要：数据中心 IP 比指纹更容易触发拦截，代理质量优先。
