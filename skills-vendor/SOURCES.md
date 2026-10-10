# 第三方 Skill 快照来源

本目录是第三方 skill 的 vendored 快照，一并入仓以便其他主机离线一键安装。
保留上游快照的来源与日期。本仓库允许有记录的本地策略修订；更新上游时逐项合并，不能整目录覆盖本地修订。当前修订记录见 ../migration/SKILL-OPTIMIZATION-2026-10-08.md。

| 目录 | 上游 | 同步日期 | 说明 |
|------|------|----------|------|
| `cloudflare/` | https://github.com/cloudflare/skills | 2026-09-17 | 全量 14 个，含本地此前缺失的 `nextjs-on-cloudflare` |
| `mattpocock/` | https://github.com/mattpocock/skills | 2026-09-17 | engineering / productivity / misc 全量（有意排除上游 `grill-me`，与 `grilling` 重复；排除上游 `code-review`，自研版替代；排除不稳定目录 `implement-spec` / `pr` / `retro`）；`in-progress` 中仅收录本地已启用的 6 个；另有 7 个上游已不存在的本地快照（`design-an-interface`、`edit-article`、`obsidian-vault`、`qa`、`request-refactor-plan`、`ubiquitous-language`、`writing-great-skills`），来源不明、按本地版本保留 |
| `app-shell-ui/` | https://github.com/yg2224/app-shell-ui | 2026-09-17 | Apache-2.0，需整目录安装（含 assets / references） |

同步方法：

```bash
git clone --depth 1 <上游地址> /tmp/<name>
# 先比较上游新版本、当前快照与本地策略修订，再合并相应文件
# 保留本地触发、授权、引用及各端元数据差异，运行 validate-skills.py 和 test-sync.py
# 最后更新本表同步日期
```
