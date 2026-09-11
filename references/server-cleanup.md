# Server Cleanup Reference

Use with `skills/server-cleanup/SKILL.md`. This is for deployment-server resources, not AI rule cleanup.

Start with read-only inventory:

```bash
df -h
docker ps -a
docker images
docker volume ls
docker network ls
docker system df

du -sh /* 2>/dev/null | sort -h
for p in /www /dData /data /root; do
  [ -d "$p" ] && { echo "===== $p ====="; du -sh "$p"/* 2>/dev/null | sort -h; }
done
```

Before removing a Docker object, trace whether it is referenced by a running compose project, container, bind mount, backup procedure, database, certificate, upload path or current rollback image. Prefer targeted commands (`docker rm <id>`, `docker rmi <image>`, explicit file removal) over broad prune commands.

Common low-risk candidates after verification include dangling images, old replaced images not referenced by any current compose deployment, obsolete stopped containers with no unique data, expired temporary archives, oversized disposable build caches, and rotated logs beyond retention. Unknown volumes/directories are never low-risk candidates.

After cleanup rerun `docker ps`, `docker system df`, `df -h`, important port/listener checks and application health requests. Record space released and any assets intentionally retained because ownership was uncertain.
