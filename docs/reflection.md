# Reflection

## Challenges Faced

- The assignment is intentionally small, but making it SRE-friendly requires more than a basic API. The application needs clear health behavior, repeatable packaging, and deployment instructions that are easy to verify.
- Elasticsearch adds realistic operational concerns. The app must handle unavailable storage cleanly, and Kubernetes readiness should reflect whether the backing database can be reached.
- The admin dashboard needed to remain simple enough for the take-home scope while still proving the API can be used without external tooling.

## Production-Ready Scaling Suggestions

- Run Elasticsearch as a managed service or a highly available Kubernetes deployment with persistent volumes, multiple nodes, snapshots, and tested restore procedures.
- Add authentication and authorization for all write operations, especially the dashboard upsert flow.
- Add structured JSON logging, request IDs, metrics, and distributed tracing so operators can diagnose API and storage issues quickly.
- Configure horizontal pod autoscaling for the API, resource requests/limits, pod disruption budgets, and multiple replicas across zones.
- Add TLS at ingress, network policies, secret management, vulnerability scanning, and CI/CD gates for tests, linting, image scanning, and Helm validation.
- Add backup, retention, and disaster recovery policies for city population data.

