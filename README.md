# CityPulse

![CityPulse product demo](docs/assets/citypulse-15s-product-demo.gif)

CityPulse is a production-minded SRE take-home project for managing city population data with a FastAPI service, Elasticsearch persistence, Docker Compose, Kubernetes Helm packaging, and Terraform bonus deployments.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.15-orange)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![Helm](https://img.shields.io/badge/Helm-chart-0F1689)
![Terraform](https://img.shields.io/badge/Terraform-bonus-7B42BC)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

## What Reviewers Should Notice

- The API has health, readiness, upsert, and query endpoints with automated tests.
- Readiness checks the Elasticsearch backing store instead of returning a static success.
- The same Helm chart deploys the app and demo Elasticsearch on Kubernetes.
- Docker Compose gives a fast local review path with both app and database.
- Bonus Terraform modules cover local Minikube and a low-cost public AWS K3s demo.
- The reflection documents production scaling, observability, security, and HA considerations.

## Quick Start

Run locally with Docker Compose:

```bash
docker compose up --build
```

Open the dashboard:

```text
http://localhost:8000
```

Stop the stack:

```bash
docker compose down
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Liveness check that returns `OK` |
| `GET` | `/readyz` | Readiness check backed by Elasticsearch health |
| `PUT` | `/cities/{city}` | Insert or update a city population |
| `GET` | `/cities/{city}` | Retrieve a city population |

Example requests:

```bash
curl http://localhost:8000/healthz
```

```bash
curl -X PUT http://localhost:8000/cities/Dubai \
  -H 'Content-Type: application/json' \
  -d '{"population":3331420}'
```

```bash
curl http://localhost:8000/cities/Dubai
```

## Architecture

![CityPulse root architecture](docs/assets/citypulse-root-architecture.png)

CityPulse keeps the application layer small and observable: FastAPI handles the REST and dashboard surface, Elasticsearch stores normalized city records, Docker Compose supports local review, and Helm packages the app/database for Kubernetes.

Additional visuals:

- [API surface](docs/assets/citypulse-api-surface.png)
- [API request lifecycle](docs/assets/citypulse-api-lifecycle.png)

## Local Python Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Run the app against an existing Elasticsearch instance:

```bash
export ELASTICSEARCH_URL=http://localhost:9200
export ELASTICSEARCH_INDEX=citypulse-cities
uvicorn app.main:app --reload
```

## Kubernetes Deployment With Helm

The chart is portable across local, cloud, and on-prem Kubernetes. By default it deploys CityPulse plus a simple single-node Elasticsearch instance suitable for demos.

```bash
helm upgrade --install citypulse ./helm/citypulse \
  --namespace citypulse \
  --create-namespace \
  --set image.repository=umar20/citypulse \
  --set image.tag=1.1.0
```

To use managed Elasticsearch instead:

```bash
helm upgrade --install citypulse ./helm/citypulse \
  --namespace citypulse \
  --create-namespace \
  --set image.repository=umar20/citypulse \
  --set image.tag=1.1.0 \
  --set elasticsearch.enabled=false \
  --set env.elasticsearchUrl=https://your-elasticsearch.example.com
```

Port-forward the service:

```bash
kubectl port-forward -n citypulse svc/citypulse 8080:80
```

Open:

```text
http://localhost:8080
```

## Bonus Terraform Deployments

### Minikube

![CityPulse Minikube Terraform architecture](docs/assets/bonus-minikube-architecture.png)

The `bonus/minikube-terraform` module creates a Minikube cluster and installs CityPulse with the same Helm chart:

```bash
cd bonus/minikube-terraform
terraform init
terraform apply -auto-approve
kubectl port-forward -n citypulse svc/citypulse 8080:80
```

### AWS K3s

![CityPulse AWS K3s Terraform architecture](docs/assets/bonus-aws-k3s-architecture.png)

The `bonus/aws-k3s-terraform` module creates a short-lived public demo on AWS using one EC2 instance running K3s. It uses the same Docker image and Helm chart, creates a Route 53 record, and avoids EKS control-plane and AWS load balancer costs.

```bash
cd bonus/aws-k3s-terraform
terraform init
terraform apply -auto-approve
```

Default public URL:

```text
http://citypulse.clawstack.cloud
```

Clean up after review:

```bash
terraform destroy -auto-approve
```

## Validation

```bash
pytest
helm lint ./helm/citypulse
helm template citypulse ./helm/citypulse
terraform -chdir=bonus/minikube-terraform fmt -check -recursive
terraform -chdir=bonus/aws-k3s-terraform fmt -check -recursive
```

## Repository Layout

```text
app/      FastAPI application, Elasticsearch store, and dashboard UI
helm/     Kubernetes Helm chart for CityPulse and demo Elasticsearch
bonus/    Terraform modules for Minikube and AWS K3s deployments
docs/     Architecture visuals and implementation reflection
tests/    API and dashboard tests
```

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `ELASTICSEARCH_URL` | `http://localhost:9200` | Elasticsearch endpoint |
| `ELASTICSEARCH_INDEX` | `citypulse-cities` | Index used for city records |

## Reflection

See [docs/reflection.md](docs/reflection.md) for implementation challenges and production scaling suggestions.
