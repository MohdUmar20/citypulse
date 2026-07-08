# CityPulse Minikube Terraform Bonus

This bonus module creates a local Minikube cluster and installs CityPulse with Helm.

![CityPulse Minikube Terraform architecture](../../docs/assets/bonus-minikube-architecture.png)

## What It Creates

- A one-node Minikube cluster using the Docker driver.
- A `citypulse` namespace.
- The shared `helm/citypulse` chart.
- A single-node Elasticsearch deployment for local demo storage.

## Prerequisites

- Docker Desktop running
- Terraform
- Minikube
- Helm
- kubectl
- Public CityPulse image: `umar20/citypulse:1.1.0`

## Deploy

```bash
cd bonus/minikube-terraform
terraform init
terraform apply -auto-approve
```

## Test

```bash
kubectl get pods -n citypulse
kubectl get svc -n citypulse
kubectl port-forward -n citypulse svc/citypulse 8080:80
```

Open:

```text
http://localhost:8080
```

API smoke test:

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz

curl -X PUT http://localhost:8080/cities/Dubai \
  -H 'Content-Type: application/json' \
  -d '{"population":3331420}'

curl http://localhost:8080/cities/Dubai
```

## Terraform Layout

- `versions.tf`: Terraform and provider constraints.
- `providers.tf`: Minikube and Helm provider configuration.
- `main.tf`: Minikube cluster resource.
- `helm.tf`: CityPulse Helm release.
- `variables.tf`: Inputs for cluster size, namespace, and image.
- `outputs.tf`: Useful access commands and URLs.

## Cleanup

```bash
terraform destroy -auto-approve
```

## Cloud or On-Prem Reuse

For a real Kubernetes cluster, skip the Minikube provider and install the chart directly:

```bash
helm upgrade --install citypulse ../../helm/citypulse \
  --namespace citypulse \
  --create-namespace \
  --set image.repository=umar20/citypulse \
  --set image.tag=1.1.0
```

To use managed Elasticsearch:

```bash
helm upgrade --install citypulse ../../helm/citypulse \
  --namespace citypulse \
  --create-namespace \
  --set image.repository=umar20/citypulse \
  --set image.tag=1.1.0 \
  --set elasticsearch.enabled=false \
  --set env.elasticsearchUrl=https://your-elasticsearch.example.com
```
