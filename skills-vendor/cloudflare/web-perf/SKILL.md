---
name: web-perf
description: 用于用户明确要求网站性能审计，或定位加载、交互、布局稳定性与性能退化；以测量结果确定修改和复测范围。
---

# Web Performance

先明确页面、用户症状、设备/网络及冷暖缓存条件。检查当前可用浏览器、网络和 trace 工具，不为普通审计自动安装或修改 MCP。

## 测量与定位

根据症状收集基线，使用 trace、网络请求、浏览器状态及相关源码区分服务响应、资源发现/下载、渲染和交互延迟。需要具体工具调用或构建分析时读取 `references/audit-methods.md`，仅执行相关部分。

工具不可用时继续有价值的源码或网络检查，明确未取得的测量。阈值与工具 API 使用 [web.dev](https://web.dev/articles/vitals)、[DevTools](https://developer.chrome.com/docs/devtools/performance) 和 [Lighthouse](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring) 的当前资料核对。

区分实验室测量、真实用户数据与推算，不把单次 trace 当作线上整体表现。移除资源前核对真实用途；一个场景中未出现的请求不能证明资源永久无用。估计收益说明依据，不把估计为零当作问题不存在的证据。

## 修复与复测

按实际影响优先处理具体瓶颈，保留现有功能和可访问性。审计第三方网站且没有源码时只报告证据与建议，不假装已修复。

修改后在可比条件下复测，并检查相关功能。完整审计覆盖主要指标，单一故障只检查相关路径；可访问性检查按本次范围开展，不强制扩成另一套审计。

交付测量条件、主要发现、具体修改或建议、前后结果及未覆盖部分。页面已经满足目标时停止优化。
