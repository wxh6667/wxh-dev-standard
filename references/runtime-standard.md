# Runtime & Delivery Defaults

This file is the canonical source for deployment defaults shared by Docker/CNB/deployment Skills.

## Business image boundary

A custom image maps to an independently deployable business runtime type. A normal full-stack system that is delivered and scaled as one unit should default to one custom business image even if it contains frontend assets, backend runtime and nginx/static serving. Do not manufacture separate custom images merely to mirror source-code layers.

If the system truly has independently deployed runtime types (for example an API service and a separate long-running worker that must version/scale independently), each type may have its own image. This exception should come from runtime needs, not aesthetics.

Official dependency images such as MySQL, PostgreSQL, Redis, RabbitMQ or vendor services are infrastructure dependencies and do not count as custom business images. Avoid rebuilding them without a concrete reason.

## Production build

Production images are built by CNB/CI, not by the developer machine. Local language builds/tests are fine; local Docker builds may be used only when a task explicitly calls for non-production debugging and must not become evidence that the production CNB image works.

Default registry namespace:

```text
registry.cn-shanghai.aliyuncs.com/heilaowang/<project>
```

Prefer immutable version/commit tags plus an optional `latest` convenience tag.

## File layout

```text
project/
├── .cnb.yml
├── docker-compose.yml
├── .env                 # production host only, not committed
├── .env.example
├── docker/
│   ├── Dockerfile
│   └── ... runtime support files
├── data/                # when bind-mounted persistence is required
└── logs/                # when host-visible logs are required
```

Keep existing project layout when it is already coherent; do not relocate files only to match this example unless the task asks for normalization.

## Compose & environment

Production compose should use `image:` rather than `build:`. Aim for `docker-compose.yml + .env` as the only configuration files an operator needs to copy/edit before `docker compose pull && docker compose up -d`.

`.env` defaults to `PORT=<host-port>` when possible. Add database URLs, secrets or other variables only when the application cannot safely provide them another way. Real `.env` values stay off Git.

## Persistence

Prefer bind mounts with visible host paths, e.g. `./data:/app/data`, so backup/migration is obvious. Do not introduce named/anonymous Docker volumes by default. Existing volumes with real data are not disposable merely because the standard prefers bind mounts.
