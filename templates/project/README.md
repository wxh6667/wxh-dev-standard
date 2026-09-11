# Project Template Usage

Use these files as starting points, not as a reason to overwrite working project conventions.

For a project being normalized to this standard:

1. Adapt `AGENTS.md.example` into a short project-local `AGENTS.md` only if project-specific agent facts are needed.
2. Merge `.gitignore` entries with the repository's existing ignore file; do not replace useful project-specific rules blindly.
3. Keep `.env.example` tracked and create a host-only `.env`; default to `PORT` only when possible.
4. Adapt `docker/Dockerfile.example` to the actual existing build/start commands and save the real file as `docker/Dockerfile`.
5. Adapt `docker-compose.yml` to the actual image name, internal port and required bind mounts. Production compose should pull the image and should not build it.
6. Adapt `.cnb.yml.example`, save it as repository-root `.cnb.yml`, and configure registry credentials in CNB secrets rather than source code.
7. Push code, let CNB build/push the image, then deploy with `docker compose pull && docker compose up -d` and run real frontend/backend checks.

If the existing project already has equivalent files, prefer editing those rather than creating duplicates.
