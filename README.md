# Resume Tracker Web App

[![CI/CD  Resume App](https://github.com/aidil-syakirin/devops-lab-2026/actions/workflows/deploy.yml/badge.svg)](https://github.com/aidil-syakirin/devops-lab-2026/actions/workflows/deploy.yml)

A containerized web application that hosts my resume and logs visitor
activity into a PostgreSQL database.

This project was built as a hands-on lab to practice DevOps concepts
including containerization, CI/CD pipelines, automated deployment, and
secure networking.

------------------------------------------------------------------------

# Project Overview

The application serves a static resume webpage and records visitor
information through a Flask API.

When a visitor opens the site:

1.  The resume page is served via Nginx
2.  A request is sent to the backend API
3.  The API logs visitor information into PostgreSQL

This project simulates a real deployment workflow used in modern DevOps
environments.

------------------------------------------------------------------------

# Architecture

High level workflow:

Developer Push 
      │ 
      ▼ 
GitHub Repository 
      │ 
      ▼ 
GitHub Actions CI/CD 
      │ 
      ▼ 
Docker Image Build 
      │ 
      ▼ 
Docker Hub Registry 
      │ 
      ▼ 
Deployment Server (Linux VM) 
      │ 
      ▼
Docker Compose 
     │ 
     ▼ 
Nginx Reverse Proxy 
     │ 
     ▼ 
  Flask API 
     │ 
     ▼ 
PostgreSQL Database

------------------------------------------------------------------------

# Tech Stack

Backend - Python - Flask - PostgreSQL

Infrastructure - Docker - Docker Compose - Nginx

CI/CD - GitHub Actions - Docker Hub

Networking - Tailscale 

------------------------------------------------------------------------

# Repository Structure

.
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   └── routes.py
├── deploy.sh
├── docker
│   └── init.sql
├── docker-compose.yml
├── requirements.txt
├── static
│   └── index.html
└── wsgi.py

------------------------------------------------------------------------

# Features

-   Static resume webpage
-   REST API endpoint for visitor logging
-   PostgreSQL database for storing visit records
-   Containerized services using Docker
-   Automated CI/CD pipeline
-   Automated deployment through SSH
-   Reverse proxy using Nginx

------------------------------------------------------------------------

# CI/CD Pipeline

The project uses GitHub Actions to automate build and deployment.

Pipeline flow:

Git Push │ ▼ Build Docker Image │ ▼ Push Image to Docker Hub │ ▼ SSH to
Deployment Server │ ▼ Pull Latest Image │ ▼ Restart Containers

Deployment is triggered whenever code is pushed to the main branch.

------------------------------------------------------------------------

# Networking

The deployment server runs inside a virtual machine hosted on my local
machine.

Since the VM uses a NAT network, it is not directly reachable from the
public internet.

To securely access the server remotely, the project uses Tailscale which
creates a private mesh VPN network between devices.

Architecture:

Internet │ ▼ Tailscale Network │ ▼ Local VM (NAT Network) │ ▼ Docker
Containers

Benefits of using Tailscale:

-   Secure encrypted connection
-   No need for port forwarding
-   Works behind NAT networks
-   Simplifies remote access to the server

The CI/CD pipeline connects to the deployment server using its Tailscale
IP address during deployment.

------------------------------------------------------------------------

# Deployment

The application runs inside Docker containers on a Linux VM.

Services running in the stack:

-   Web API (Flask)
-   PostgreSQL database
-   Nginx reverse proxy

Deployment is handled using Docker Compose:

docker compose up -d

When the CI/CD pipeline runs, the server automatically:

1.  Pulls the latest Docker image
2.  Stops the current containers
3.  Starts the updated containers

------------------------------------------------------------------------

# Learning Objectives

This project helped me practice:

-   Containerizing applications using Docker
-   Managing multi-service applications with Docker Compose
-   Creating CI/CD pipelines using GitHub Actions
-   Deploying applications to a remote Linux server
-   Using reverse proxies with Nginx
-   Logging application data into PostgreSQL
-   Secure remote networking using Tailscale

------------------------------------------------------------------------

# Future Improvements

Possible enhancements for this project:

-   Visitor analytics dashboard
-   GeoIP visitor tracking
-   Authentication for admin dashboard
-   Infrastructure provisioning using Terraform
-   Monitoring and alerting
-   Domain name and HTTPS configuration

------------------------------------------------------------------------

# Author

Aidil Syakirin
