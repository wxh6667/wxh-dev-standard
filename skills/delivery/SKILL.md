---
name: delivery
description: Perform the final software delivery gate after implementation and deployment. Use before declaring a project complete, handing it to a customer, or finishing an end-to-end flow. Verify source, frontend/backend behavior, database changes, CNB image, Compose startup, persistence, docs, and known limitations.
---

# Delivery

A deliverable should be reproducible by someone other than the implementing agent.

## Final gate

- Required user flows work in the delivered environment.
- Frontend and backend use the intended contract and no temporary mocks remain unless explicitly required.
- Database migrations/initialization needed by the release are included and tested.
- Tests/build checks relevant to the change passed, with any unrun checks stated.
- Production image came from CNB and the delivered registry tag is identified.
- Production Compose pulls the image and starts using the intended `.env`; no local production build dependency remains.
- Bind-mounted persistence paths are documented and important data survives container recreation where applicable.
- No secrets, private keys, registry credentials, real `.env`, debug artifacts or unnecessary generated files were committed.
- README/deployment notes contain only commands/config actually required.

Report what was completed, the exact deployed image/version, verification performed, and any remaining external dependency or limitation. Do not mark partial work as fully delivered.
