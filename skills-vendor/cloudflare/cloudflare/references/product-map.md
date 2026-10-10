# Cloudflare product map

Use this map only after Cloudflare is part of the agreed scope. Product recommendations and caching choices must be checked against the target versions, current documentation and workload requirements.

| What you need to do | Product or tool to consider | When to choose it | Skill or reference |
| --- | --- | --- | --- |
| Choose the building blocks for an AI application | AI overview | Compare Cloudflare's AI services before choosing inference, retrieval, or agent tooling | [AI docs](https://developers.cloudflare.com/ai/) |
| Choose infrastructure for a customer-facing platform | Cloudflare for Platforms | Compare running customer code with serving an app on customer domains | [Platform overview](https://developers.cloudflare.com/cloudflare-for-platforms/) |
| Choose an approach to live audio and video | Realtime | Compare application SDKs, media infrastructure, and connectivity relays | [Realtime overview](https://developers.cloudflare.com/realtime/) |
| Start a Worker or framework project | C3 | Scaffold a project using the appropriate framework template | [C3](c3/README.md); `wrangler` skill |
| Build or deploy a Next.js app on Cloudflare | vinext + Workers | Use vinext rather than OpenNext for new projects | [nextjs-on-cloudflare skill](../../nextjs-on-cloudflare/SKILL.md); [Next.js docs](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/) |
| Host a new static site, SPA, or full-stack app | Workers + Workers Static Assets | Serve site files and add server-side logic where needed | [Static Assets](static-assets/README.md); `workers-best-practices` skill |
| Build an API or handle webhooks | Workers | Run request handlers with access to Cloudflare services | `workers-best-practices` skill; [Workers docs](https://developers.cloudflare.com/workers/) |
| Maintain an existing Pages deployment | Pages + Pages Functions | Update an existing site or its server endpoints; use Workers for new projects | [Pages](pages/README.md); [Pages Functions](pages-functions/README.md) |
| Move a Pages project to Workers | Workers + Workers Static Assets | The task calls for migrating the hosting platform | [Pages migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/) |
| Let customers deploy code on your platform | Workers for Platforms | Run and manage customer Workers with per-customer controls | [Workers for Platforms](workers-for-platforms/README.md) |
| Let customers use their own domains with your app | Cloudflare for SaaS | Manage custom hostnames, TLS certificates, and origin routing; check hostname validation and apex-domain plan requirements. Combine with Workers for Platforms when customers also deploy code | [SaaS docs](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/) |
| Connect a Worker to storage or another service | Bindings | Give the Worker access to configured resources through its environment | [Bindings](bindings/README.md) |
| Run containerized services or Linux software | Containers | The workload needs a container image or software outside the Workers runtime | [Containers](containers/README.md) |
| Execute generated or untrusted code, build Code Mode tools, or create on-demand previews | Dynamic Workers | Load code at runtime in isolated Workers; check bindings, egress controls, and resource limits. Choose Sandbox when execution needs Linux or shell tools | [Dynamic Workers docs](https://developers.cloudflare.com/dynamic-workers/) |
| Give an agent a shell, filesystem, or interactive development environment | Sandbox SDK | Code execution needs a Linux environment or container tools; inspect the package line first | `sandbox-next` for new or preview projects; `sandbox-stable` for existing stable apps; [Sandbox docs](https://developers.cloudflare.com/sandbox/) |
| Upgrade a stable Sandbox app to the preview API | Sandbox SDK | The user wants the stable-to-next migration | `sandbox-migrate-to-next` skill; [migration guide](https://developers.cloudflare.com/sandbox/1-0-preview/migrate/) |
| Coordinate chat rooms, games, collaborative documents, or bookings | Durable Objects | Operations need shared state and coordination per room, document, or entity | `durable-objects` skill; [Durable Objects docs](https://developers.cloudflare.com/durable-objects/) |
| Store and recover state inside a Durable Object | Durable Object storage | Choose storage APIs, transactions, and recovery for coordinated per-entity data | [DO storage](do-storage/README.md) |
| Store application records and query them with SQL | D1 | Use a managed relational database; use Durable Objects when per-entity coordination is central | [D1](d1/README.md) |
| Connect to an existing PostgreSQL or MySQL database | Hyperdrive | Keep the existing database and optimize connections from Workers | [Hyperdrive](hyperdrive/README.md) |
| Distribute configuration or other key-value data | KV | Read-heavy key-value access fits the workload's consistency requirements | [KV](kv/README.md) |
| Store uploads, downloads, or large objects | R2 | Store files by object key; pair with D1 when searchable metadata needs SQL | [R2](r2/README.md) |
| Store versioned file trees, agent checkpoints, or repositories | Artifacts | Files need versioning and Git-compatible access; currently closed beta, so confirm access before implementation | [Artifacts](artifacts/README.md) |
| Ingest event streams into a data lake | Pipelines | Transform and deliver streaming records into R2 | [Pipelines](pipelines/README.md) |
| Manage Iceberg tables in R2 | R2 Data Catalog | Organize tables for a data lake and compatible query engines | [R2 Data Catalog](r2-data-catalog/README.md) |
| Query a data lake with SQL | R2 SQL | Analyze data in R2 Data Catalog rather than transactional application records | [R2 SQL](r2-sql/README.md) |
| Cache application responses | Workers Cache | Compare application caching against the required scope and invalidation behavior; check the patterns and limitations before choosing alternatives | [Workers Cache](https://developers.cloudflare.com/workers/cache/); see caching guidance below |
| Accelerate an existing website and control cached content | Cache/CDN | Configure caching for a proxied origin using Cache Rules, expiration settings, and purging | [Cache/CDN docs](https://developers.cloudflare.com/cache/) |
| Keep origin content in a persistent cache | Cache Reserve | Reduce origin fetches with persistent CDN cache storage | [Cache Reserve](cache-reserve/README.md) |
| Process jobs asynchronously or buffer bursts of work | Queues | Decouple producers and consumers; use Workflows for durable multi-step orchestration | [Queues](queues/README.md) |
| Run a job that retries, waits, and resumes across steps | Workflows | Coordinate durable multi-step business processes | [Workflows](workflows/README.md) |
| Start a Worker on a recurring schedule | Cron Triggers | Trigger scheduled work; combine with Queues or Workflows for the work itself | [Cron Triggers](cron-triggers/README.md) |
| Run language, embedding, image, or speech models | Workers AI | Use managed inference; verify model capabilities, schemas, and pricing | [Workers AI](workers-ai/README.md) |
| Add managed search or answers over your content | AI Search | Use a managed retrieval-augmented generation pipeline | [AI Search](ai-search/README.md) |
| Build custom semantic search or retrieval | Vectorize + Workers AI | Control embeddings, indexing, and retrieval rather than using a managed pipeline | [Vectorize](vectorize/README.md); [Workers AI](workers-ai/README.md) |
| Observe and control requests to AI providers | AI Gateway | Add inference analytics, caching, and request controls | [AI Gateway](ai-gateway/README.md) |
| Build stateful agents with tools, scheduling, or chat | Agents SDK | Implement agent behavior on Cloudflare; add Dynamic Workers or Sandbox for the required execution runtime | `agents-sdk` skill; [Agents docs](https://developers.cloudflare.com/agents/) |
| Build durable agents with TypeScript hooks | Flue | Use an open agent framework with Cloudflare and Node.js targets | [Flue](https://flueframework.com/); [getting started](https://flueframework.com/docs/guide/getting-started/); [Cloudflare target](https://flueframework.com/docs/guide/cloudflare-target/) |
| Expose tools through a remote MCP server | Workers + Agents SDK | Publish tools for MCP clients, with authentication appropriate to the service | `agents-sdk` skill, its `references/mcp.md`; [MCP docs](https://developers.cloudflare.com/agents/model-context-protocol/) |
| Automate browsers, take screenshots, or extract rendered pages | Browser Run | The task requires a browser rather than a plain HTTP request | [Browser Run](browser-rendering/README.md) |
| Connect a domain, configure DNS records, or troubleshoot resolution | DNS | Manage authoritative records and choose whether traffic is proxied through Cloudflare | [DNS docs](https://developers.cloudflare.com/dns/) |
| Configure HTTPS and certificates | SSL/TLS | Secure connections from visitors to Cloudflare and from Cloudflare to the origin | [SSL/TLS docs](https://developers.cloudflare.com/ssl/) |
| Distribute traffic across origins and fail over unhealthy servers | Load Balancing | Use health checks and traffic steering for multiple origin servers | [Load Balancing docs](https://developers.cloudflare.com/load-balancing/) |
| Connect an existing server to Cloudflare | Cloudflare Tunnel | Reach an origin without a publicly routable IP address | [Tunnel](tunnel/README.md) |
| Connect Workers to private services | Workers VPC | Access services in private networks from a Worker | [Workers VPC](workers-vpc/README.md) |
| Require employee login before accessing an internal app | Access | Put identity-based access policies in front of an internal application | `cloudflare-one` skill; [Access docs](https://developers.cloudflare.com/cloudflare-one/access-controls/) |
| Protect access to internal applications and networks | Cloudflare One | Apply identity and network access policies | `cloudflare-one` skill; [Cloudflare One docs](https://developers.cloudflare.com/cloudflare-one/) |
| Migrate existing access and network security configurations | Cloudflare One | The task is a supported migration to Cloudflare One | `cloudflare-one-migrations` skill; [Cloudflare One docs](https://developers.cloudflare.com/cloudflare-one/) |
| Proxy a TCP or UDP application | Spectrum | Protect and accelerate non-HTTP application traffic | [Spectrum](spectrum/README.md) |
| Connect a network directly to Cloudflare | Network Interconnect | Dedicated network connectivity is required | [Network Interconnect](network-interconnect/README.md) |
| Improve routing across the network | Argo Smart Routing | Optimize traffic paths to the origin | [Argo Smart Routing](argo-smart-routing/README.md) |
| Reduce Worker-to-backend latency | Smart Placement | Place Worker execution closer to the backends it calls | [Smart Placement](smart-placement/README.md) |
| Redirect URLs, rewrite paths or headers, or change origin routing | Rules | Use Redirect, Transform, or Origin Rules when configuration can express the required behavior | [Rules docs](https://developers.cloudflare.com/rules/) |
| Make small HTTP request or response changes | Snippets | Lightweight edge logic meets the need | [Snippets](snippets/README.md) |
| Protect forms from automated abuse | Turnstile | Add bot challenges and server-side token validation | `turnstile-spin` skill; [Turnstile docs](https://developers.cloudflare.com/turnstile/) |
| Filter malicious web requests | WAF | Apply application-layer rules and managed protections | [WAF](waf/README.md) |
| Protect services from denial-of-service attacks | DDoS Protection | Mitigate attacks at the relevant network or application layer | [DDoS protection](ddos/README.md) |
| Detect and control automated traffic | Bot Management | Make request decisions based on bot detection | [Bot Management](bot-management/README.md) |
| Discover and protect API endpoints | API Shield | Apply API-specific protections and validation | [API Shield](api-shield/README.md) |
| Queue visitors during traffic spikes | Waiting Room | Control admission when application capacity is limited | [Waiting Room docs](https://developers.cloudflare.com/waiting-room/) |
| Store a Worker's API keys and credentials | Workers secrets | Bind secrets to a Worker without committing values to source | `wrangler` skill; [secrets docs](https://developers.cloudflare.com/workers/configuration/secrets/) |
| Share managed secrets across services | Secrets Store | Manage reusable account-level secrets | [Secrets Store](secrets-store/README.md) |
| Control where data is processed and stored | Data Localization Suite | Evaluate regional processing and storage controls against the actual requirements | [Data Localization docs](https://developers.cloudflare.com/data-localization/) |
| Prove a claim without identifying or tracking the user | Privacy Pass | Use privacy-preserving tokens in a supported integration | [Privacy Pass docs](https://developers.cloudflare.com/privacy-pass/) |
| Store, resize, transform, and deliver images | Cloudflare Images | Use managed image processing and delivery | [Images](images/README.md) |
| Encode, store, and deliver live or on-demand video | Stream | Use managed video infrastructure | [Stream](stream/README.md) |
| Build an audio/video calling application with SDKs | RealtimeKit | Use application-level SDKs for calls and meetings | [RealtimeKit](realtimekit/README.md) |
| Build custom real-time media infrastructure | Realtime SFU | Control the application while using a selective forwarding unit for media | [Realtime SFU](realtime-sfu/README.md) |
| Relay WebRTC connections through restrictive networks | TURN Service | Clients need a connectivity relay | [TURN](turn/README.md) |
| Deliver live media over QUIC | MoQ | Use the Media over QUIC protocol; check current compatibility and availability | [MoQ docs](https://developers.cloudflare.com/moq/) |
| Send transactional email | Email Service | Send application-generated messages | `cloudflare-email-service` skill; [Email Service docs](https://developers.cloudflare.com/email-service/) |
| Forward incoming email | Email Routing | Route addresses on a domain to destination mailboxes | [Email Routing](email-routing/README.md) |
| Process incoming email in code | Email Workers | Apply custom logic to inbound messages | [Email Workers](email-workers/README.md) |
| Manage third-party tags and scripts | Zaraz | Load and manage third-party tools through Cloudflare | [Zaraz](zaraz/README.md) |
| Run locally and manage resources from the CLI | Wrangler | Develop, configure, deploy, and inspect the intended account and environment | `wrangler` skill; [Wrangler docs](https://developers.cloudflare.com/workers/wrangler/) |
| Test Worker behavior before deployment | Workers testing tools | Choose runtime tests or integration tests for the affected behavior | [Testing docs](https://developers.cloudflare.com/workers/testing/); `durable-objects` skill for DO tests |
| Embed local Worker simulation in tooling | Miniflare | A programmatic emulator is needed for a custom development or test harness | [Miniflare](miniflare/README.md) |
| Run or investigate the underlying Workers runtime | workerd | Work directly with the runtime outside normal managed deployment | [workerd](workerd/README.md) |
| Try a small Worker in the browser | Workers Playground | Explore or share a minimal example without local setup | [Workers Playground](workers-playground/README.md) |
| Build and deploy whenever code is pushed | Workers Builds | Connect a Git repository to automated builds and deployments | [Builds docs](https://developers.cloudflare.com/workers/ci-cd/builds/) |
| Preview a version, release it gradually, or roll back code | Workers versions and deployments | Manage application releases; rollback does not restore connected resource data | [Deployment docs](https://developers.cloudflare.com/workers/versions-and-deployments/); `wrangler` skill |
| Release a feature gradually or target user groups | Flagship | Change feature availability with targeting and percentage rollouts | [Flagship](flagship/README.md) |
| Manage infrastructure as code | Terraform or Pulumi | Use Terraform for declarative configuration or Pulumi for infrastructure in programming languages | [Terraform](terraform/README.md); [Pulumi](pulumi/README.md) |
| Automate account or product configuration through an API | Cloudflare REST API | Manage resources programmatically; prefer bindings for supported operations inside Workers | [REST API](api/README.md) |
| Debug failures and trace application requests | Workers Logs and Traces | Investigate runtime errors and execution paths | [Observability](observability/README.md) |
| Process Worker execution events in code | Tail Workers | Build custom log or exception processing | [Tail Workers](tail-workers/README.md) |
| Export Worker logs to another system | Workers Logpush | Deliver logs to a supported external destination | [Logpush docs](https://developers.cloudflare.com/workers/observability/logs/logpush/) |
| Measure custom application events | Workers Analytics Engine | Analyze high-cardinality event data written from Workers | [Analytics Engine](analytics-engine/README.md) |
| Measure website usage and visitor performance | Cloudflare Web Analytics | Add website analytics and real-user measurements | [Web Analytics](web-analytics/README.md) |
| Query metrics across Cloudflare products | GraphQL Analytics API | Retrieve product analytics programmatically | [GraphQL Analytics API](graphql-api/README.md) |
| Audit page speed and find loading bottlenecks | Web performance tools | Measure and improve the site's actual browser performance | `web-perf` skill; [Web Analytics](web-analytics/README.md) |
| Ask questions about an account or diagnose its configuration in the dashboard | Agent Lee | Use the dashboard's AI assistant; check current account eligibility | [Agent Lee docs](https://developers.cloudflare.com/agent-lee/) |

For example, a file-upload app can use Workers for its API, R2 for files, D1 for metadata, and Queues for processing. A document assistant can start with Workers and AI Search; use Vectorize and Workers AI when it needs custom retrieval. Recommend only the pieces the requested behavior needs.

## Find guidance for a task not listed here

Use the [Cloudflare product directory](https://developers.cloudflare.com/directory/) for additional products and their current docs. Follow links to the specific feature or API involved. Use [Choose a data or storage product](https://developers.cloudflare.com/workers/platform/storage-options/) for storage tradeoffs, and the product's limits, pricing, and migration guides when evaluating scale, cost, or an upgrade. This table maps common tasks to selected Cloudflare products; it does not enumerate every possible application.

## Caching

Compare [Workers Cache](https://developers.cloudflare.com/workers/cache/), [Cache API](https://developers.cloudflare.com/workers/runtime-apis/cache/) and KV-based caching against the workload's consistency, geographic scope, invalidation, lifetime and configured runtime. Check current [patterns](https://developers.cloudflare.com/workers/cache/examples/) and [limitations](https://developers.cloudflare.com/workers/cache/limitations/) before selecting or replacing an existing solution.
