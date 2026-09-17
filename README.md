# GreenLeaf Gardens - 3-Tier Application on AWS EKS

A full-stack, three-tier application for managing gardening business operations, deployed on Amazon EKS with Kubernetes. The project demonstrates a complete containerized stack with:

- Frontend: Nginx serving the web UI
- Backend: Flask REST API
- Database: MySQL persistence layer

## Architecture

Frontend (Nginx)
  ↓
Backend (Flask API)
  ↓
MySQL Database

## Tech Stack

- AWS EC2
- Amazon EKS
- Amazon ECR
- Docker
- Kubernetes
- Nginx
- Python Flask
- MySQL
- eksctl
- kubectl
- EBS CSI Driver

## Project Structure

```text
aws-eks-three-tier-application/
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── index.html
├── mysql/
│   ├── Dockerfile
│   └── init.sql
├── kubernetes/
│   ├── backend/
│   │   ├── backend-deployment.yaml
│   │   └── backend-service.yaml
│   ├── frontend/
│   │   ├── frontend-deployment.yaml
│   │   └── frontend-service.yaml
│   ├── mysql/
│   │   ├── mysql-deployment.yaml
│   │   ├── mysql-service.yaml
│   │   └── mysql-pvc.yaml
│   ├── namespace.yaml
│   └── secrets.yaml
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE (if added separately)
```

## Features

The application provides a dashboard for managing:

- Products
- Customers
- Orders
- Employees
- Garden Projects
- Revenue and business insights

## Backend API

The Flask service exposes REST endpoints for dashboard data and CRUD operations, including:

- `/api/health`
- `/api/dashboard`
- `/api/products`
- `/api/customers`
- `/api/employees`
- `/api/orders`
- `/api/projects`

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/Bhuvanesh-432/aws-eks-three-tier-application.git
cd aws-eks-three-tier-application
```

### 2. Configure Environment

Copy the example environment file and update the values if needed:

```bash
cp .env.example .env
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This starts the frontend, backend, and MySQL database locally.

## AWS EKS Deployment

### 1. Create EKS Cluster

```bash
eksctl create cluster \
  --name greenleaf-cluster \
  --region eu-north-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2
```

### 2. Configure kubectl

```bash
aws eks update-kubeconfig \
  --region eu-north-1 \
  --name greenleaf-cluster
```

### 3. Install EBS CSI Driver

```bash
eksctl utils associate-iam-oidc-provider \
  --region eu-north-1 \
  --cluster greenleaf-cluster \
  --approve
```

```bash
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster greenleaf-cluster \
  --region eu-north-1 \
  --force
```

### 4. Deploy Kubernetes Resources

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/mysql/
kubectl apply -f kubernetes/backend/
kubectl apply -f kubernetes/frontend/
```

### 5. Verify Deployment

```bash
kubectl get pods -n greenleaf
kubectl get svc -n greenleaf
kubectl get pvc -n greenleaf
```

## Kubernetes Resources

### Deployments

- frontend
- backend
- mysql

### Services

- frontend-service (LoadBalancer)
- backend-service (ClusterIP)
- mysql-service (ClusterIP)

### Storage

- PersistentVolumeClaim
- AWS EBS-backed storage

## Application URL

```text
http://ac5e87aaf065d4fd8b88f98e5321b2b8-205638751.eu-north-1.elb.amazonaws.com/
```

## Docker Images

### Backend

```text
821263771829.dkr.ecr.eu-north-1.amazonaws.com/greenleaf-backend:latest
```

### Frontend

```text
821263771829.dkr.ecr.eu-north-1.amazonaws.com/greenleaf-frontend:latest
```

### MySQL

```text
821263771829.dkr.ecr.eu-north-1.amazonaws.com/greenleaf-mysql:latest
```

## Notes

This project is intended to demonstrate a practical AWS EKS deployment workflow for a containerized application, including service networking, database persistence, and Kubernetes resource management.

## Author

Bhuvanesh Thangaraj

AWS | Docker | Kubernetes | DevOps Engineer
