## KEDA ecommerce demo (microservices)

This repo is a tiny ecommerce-style system built specifically to **demo KEDA autoscaling on YouTube**.

It contains **3 deployable components**:

- **`catalog-service`**: REST API for products
- **`order-service`**: REST API that creates orders and publishes an `orders` message to RabbitMQ
- **`worker`**: background consumer that processes `orders` messages (this is what KEDA scales)

The point of the demo: you can quickly enqueue a lot of orders and watch **KEDA scale `worker` replicas** based on **RabbitMQ queue length**.

---

## Architecture

- **HTTP**: `order-service` and `catalog-service` are standard web microservices
- **Async queue**: `order-service` publishes messages to **RabbitMQ** queue `orders`
- **Autoscaling target**: KEDA scales the `worker` deployment based on the `orders` queue depth

---

## Run locally (Docker Compose)

Prereqs: Docker Desktop

```bash
cd keda-ecommerce-demo
docker compose up --build
```

Try it:

- Catalog: `curl http://localhost:8001/products`
- Create one order: `curl -X POST http://localhost:8002/orders -H 'content-type: application/json' -d '{"items":[{"sku":"sku-1","qty":1}]}'`
- Enqueue a lot of orders fast (watch worker logs): `curl -X POST 'http://localhost:8002/orders/bulk?n=500'`

---

## Run on Kubernetes + KEDA

### Prereqs

- A cluster (kind/minikube/EKS/GKE/AKS)
- `kubectl`
- KEDA installed in the cluster

Install KEDA (example via Helm):

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace
```

### Build images for your cluster

The Kubernetes manifests reference local image names:

- `catalog-service:local`
- `order-service:local`
- `worker:local`

For **kind**:

```bash
docker build -t catalog-service:local ./catalog-service
docker build -t order-service:local ./order-service
docker build -t worker:local ./worker

kind load docker-image catalog-service:local order-service:local worker:local
```

For **minikube** (build directly inside minikube’s Docker):

```bash
eval "$(minikube docker-env)"
docker build -t catalog-service:local ./catalog-service
docker build -t order-service:local ./order-service
docker build -t worker:local ./worker
```

### Deploy the demo

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -n keda-demo -f k8s/rabbitmq.yaml
kubectl apply -n keda-demo -f k8s/catalog.yaml
kubectl apply -n keda-demo -f k8s/order.yaml
kubectl apply -n keda-demo -f k8s/worker.yaml
kubectl apply -n keda-demo -f k8s/keda-scaledobject-rabbitmq.yaml
```

Port-forward the order service:

```bash
kubectl -n keda-demo port-forward svc/order-service 8002:80
```

Generate load:

```bash
curl -X POST 'http://localhost:8002/orders/bulk?n=2000'
```

Watch autoscaling:

```bash
kubectl -n keda-demo get scaledobject,kedahpa,hpa
kubectl -n keda-demo get deploy worker -w
kubectl -n keda-demo get pods -l app=worker -w
```

---

## Notes for recording the YouTube demo

- Show `kubectl get deploy worker -w` while you enqueue orders
- Show queue growing (optional): port-forward RabbitMQ management UI:

```bash
kubectl -n keda-demo port-forward svc/rabbitmq 15672:15672
```

Then open `http://localhost:15672` (credentials are in `k8s/rabbitmq.yaml`).

