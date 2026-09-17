# 第三方 Skill 快照来源

本目录是第三方 skill 的 vendored 快照，一并入仓以便其他主机离线一键安装。
更新时从对应上游重新拷贝并刷新本表的同步日期，不手工修改第三方内容。

| 目录 | 上游 | 同步日期 | 说明 |
|------|------|----------|------|
| `cloudflare/` | https://github.com/cloudflare/skills | 2026-09-17 | 全量 14 个，含本地此前缺失的 `nextjs-on-cloudflare` |
| `mattpocock/` | https://github.com/mattpocock/skills | 2026-09-17 | engineering / productivity / misc 全量（有意排除上游 `grill-me`，与 `grilling` 重复；排除上游 `code-review`，自研版替代；排除不稳定目录 `implement-spec` / `pr` / `retro`）；`in-progress` 中仅收录本地已启用的 6 个；另有 7 个上游已不存在的本地快照（`design-an-interface`、`edit-article`、`obsidian-vault`、`qa`、`request-refactor-plan`、`ubiquitous-language`、`writing-great-skills`），来源不明、按本地版本保留 |
| `app-shell-ui/` | https://github.com/yg2224/app-shell-ui | 2026-09-17 | Apache-2.0，需整目录安装（含 assets / references） |

同步方法：

```bash
git clone --depth 1 <上游地址> /tmp/<name>
cp -r /tmp/<name>/skills/<skill> skills-vendor/<name>/<skill>
# 重新生成各 skill 目录清单后更新本表同步日期
```
