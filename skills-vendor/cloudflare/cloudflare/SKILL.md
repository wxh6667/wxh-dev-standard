---
name: cloudflare
description: 用于现有 Cloudflare 项目、明确采用 Cloudflare 的新项目，或用户要求包含 Cloudflare 的平台比较；帮助选择对应产品与专业 Skill。
---

# Cloudflare Product Selection

从用户目标和现有架构出发，仅在已采用、明确选择或正在比较 Cloudflare 时推荐对应产品。一般应用需求不自动变成 Cloudflare 迁移。

选择产品时读取 `references/product-map.md` 中相关条目，再读取匹配产品的参考或已安装专业 Skill。组合只包含满足具体需求的产品。不存在对应 Skill 时使用 [官方目录](https://developers.cloudflare.com/directory/)，不自动安装另一套能力库。

新 Cloudflare 网站与应用选型可比较 Workers + Static Assets，维护既有 Pages 时保留其部署；迁移和框架替换属于独立任务。Sandbox 根据项目实际 stable/next 版本选择 Skill，不自动升级。

检查项目版本、类型与 Wrangler 配置；按具体问题核对官方 API、兼容性、限制、价格和可用性。缓存按一致性、失效与目标版本选择，不把默认产品当作所有项目的必需项。

使用现有项目检查验证受影响行为，部署需核对实际账户、环境和在线结果。资料与验收足够时停止。
