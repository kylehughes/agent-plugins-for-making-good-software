# Behavioral acceptance

Explain a deterministic attachment strategy using the async-testing owner. Prefer an explicit readiness seam when one exists. When production cannot change and the notification API exposes no readiness seam, accept bounded repeated stimulus until observed state or completion proves subscription. The retry must remain able to post again after a missed notification, use a timeout only as a failure bound, and cancel and await listener cleanup on every exit. Avoid sleeps used as proof of readiness and fixed yield counts. Keep production code and the workspace unchanged. Do not invoke the invariant-verification workflow.

Review the full response and tool trace. Skill activation and keyword matches are supporting signals only.
