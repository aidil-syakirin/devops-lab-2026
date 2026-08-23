# Resume Tracker Web App

A containerized Flask application that serves a static resume page and
records visitor activity in PostgreSQL.

This project is a hands-on DevOps home lab focused on Docker, GitHub
Actions CI/CD, automated testing, immutable image versioning,
self-hosted deployment, health validation, and automatic rollback.

------------------------------------------------------------------------

## Project Overview

The application consists of:

-   A static resume webpage
-   A Flask/Gunicorn backend API
-   PostgreSQL for visitor records
-   Docker and Docker Compose for containerization
-   GitHub Actions for CI and CD
-   Docker Hub as the container registry
-   A self-hosted GitHub Actions runner for deployment into the home lab

The application exposes API endpoints for recording and retrieving
visits, together with a `/health` endpoint used by both CI and
post-deployment validation.

------------------------------------------------------------------------

## Architecture

``` text
Developer
   |
   | Push / Pull Request
   v
GitHub Repository
   |
   v
GitHub Actions CI (GitHub-hosted runner)
   |
   |-- PostgreSQL test service
   |-- Initialize test database
   |-- Build linux/amd64 Docker image
   |-- Database health test
   |-- POST /visit smoke test
   |-- GET /visits smoke test
   |
   | Push event only
   v
Docker Hub
resume-tracker:<commit-sha>
   |
   | CI success triggers CD
   v
GitHub Actions CD (self-hosted runner VM)
   |
   | SSH
   v
Application VM
   |
   |-- Pull exact commit-SHA image
   |-- Docker Compose deployment
   |-- Post-deployment health check
   |-- Automatic rollback on failure
   `-- Docker image cleanup after success
        |
        +-- Flask / Gunicorn
        `-- PostgreSQL
```

The CI and CD runners are intentionally separated. CI uses a
GitHub-hosted runner for reproducible builds and tests, while CD uses a
self-hosted runner inside the home lab because it requires SSH access to
the private application VM.

------------------------------------------------------------------------

## Tech Stack

**Application**

-   Python 3.11
-   Flask
-   Gunicorn
-   SQLAlchemy
-   PostgreSQL 17

**Containers / Infrastructure**

-   Docker
-   Docker Compose
-   Linux virtual machines
-   KVM/QEMU home-lab environment

**CI/CD**

-   GitHub Actions
-   GitHub-hosted CI runner
-   Self-hosted CD runner
-   Docker Hub container registry
-   SSH-based deployment

------------------------------------------------------------------------

## Repository Structure

``` text
.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── Dockerfile
├── Dockerfile.db
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   └── routes.py
├── deploy/
│   └── nginx-health-proxy.conf.example
├── docker/
│   └── init.sql
├── docker-compose.yml
├── requirements.txt
├── script/
├── static/
│   └── index.html
└── wsgi.py
```

------------------------------------------------------------------------

## Continuous Integration (CI)

The CI workflow is defined in `.github/workflows/ci.yml` and runs on a
GitHub-hosted Ubuntu runner.

### Triggers

CI runs for:

-   Pushes to `local-mini-pc`
-   Pull requests targeting `main`

Pull-request CI validates proposed changes without publishing or
deploying an image. Docker Hub authentication and image publishing are
restricted to push-triggered CI runs.

### CI Flow

``` text
Checkout repository
        |
        v
Start PostgreSQL 17 service
        |
        v
Initialize schema from docker/init.sql
        |
        v
Build linux/amd64 application image
        |
        v
Start application test container
        |
        v
GET /health
        |
        v
POST /visit
        |
        v
GET /visits + validate test record
        |
        v
Push only? ---- No ---> CI complete (PR validation)
   |
  Yes
   |
   v
Login to Docker Hub
        |
        v
Push :latest and :<commit-sha>
```

### CI Tests

The pipeline currently performs several integration/smoke checks:

1.  **PostgreSQL service health** --- GitHub Actions starts PostgreSQL
    17 and waits for `pg_isready` to report the database healthy.
2.  **Database initialization** --- `docker/init.sql` is applied to the
    temporary CI database before application testing.
3.  **Application/database health** --- `/health` verifies that the
    Flask application can connect to PostgreSQL.
4.  **Visit creation test** --- CI sends a `POST /visit` request with a
    test visitor.
5.  **Visit retrieval test** --- CI calls `GET /visits` and verifies
    that the test visitor is returned.

The same Docker image that passes these tests is the image that is
published for deployment.

------------------------------------------------------------------------

## Immutable Image Versioning

Successful push-triggered builds are published to Docker Hub with two
tags:

``` text
resume-tracker:latest
resume-tracker:<7-character-commit-sha>
```

The commit SHA is used for deployment rather than relying on `latest`.

For example:

``` text
resume-tracker:a1b2c3d
```

This makes each deployment traceable to a specific Git commit and allows
previous application versions to be redeployed during rollback.

------------------------------------------------------------------------

## Continuous Deployment (CD)

The CD workflow is defined in `.github/workflows/cd.yml`.

It is triggered using GitHub Actions `workflow_run` after
`CI Resume App` completes for the `local-mini-pc` branch. The deployment
job additionally checks that:

-   CI completed successfully
-   The upstream CI event was a `push`

This prevents pull-request validation runs from deploying application
images.

### Self-Hosted Runner

CD runs on a dedicated self-hosted Linux VM.

The runner uses a dedicated `runner` account and connects to the
application VM over SSH using a deployment key. The remote `deploy`
account has access to the Docker deployment operations required by the
pipeline.

``` text
GitHub
   |
   v
runner-vm
(self-hosted GitHub Actions runner)
   |
   | SSH
   v
vm-resume
(application + PostgreSQL)
```

------------------------------------------------------------------------

## Deployment Flow

CD reads `github.event.workflow_run.head_sha` from the successful CI run
and converts it to the same seven-character SHA used by CI.

The deployment process is:

1.  Determine the exact successful CI commit SHA.
2.  Pull `resume-tracker:<commit-sha>` on the application VM.
3.  Save the currently running image reference as `.previous_image`.
4.  Supply the new image through the `APP_IMAGE` variable.
5.  Run `docker compose up -d web`.
6.  Call `GET /health` against the deployed application.
7.  Verify the image reference used by the running `flask-api`
    container.
8.  Remove unused Docker images after a successful deployment.

`docker-compose.yml` uses:

``` yaml
web:
  image: ${APP_IMAGE}
```

This allows the same Compose definition to deploy either a new
SHA-tagged release or a previous image during rollback.

------------------------------------------------------------------------

## Automatic Rollback

Before replacing the application container, CD records the currently
running image in `.previous_image`.

If the post-deployment `/health` check fails, the pipeline
automatically:

1.  Reads the previous image reference.
2.  Pulls the previous image if necessary.
3.  Redeploys it through Docker Compose.
4.  Runs the health check again to verify recovery.
5.  Marks the GitHub Actions deployment as failed even when rollback
    succeeds.

This distinction is intentional: a successful rollback means the service
recovered, but the new release itself still failed.

``` text
Deploy new image
      |
      v
Health check
   /       \
 PASS     FAIL
  |         |
  |         v
  |      Rollback
  |         |
  |         v
  |    Verify recovery
  |         |
  |         v
  |    Workflow FAILED
  |
  v
Prune unused images
  |
  v
Workflow SUCCESS
```

------------------------------------------------------------------------

## Pull Request Validation

Pull requests targeting `main` execute the same build and application
tests but do not publish Docker images.

The `main` branch is protected by a GitHub ruleset requiring the CI
status check to pass before a pull request can be merged.

This was validated using both successful and intentionally failing pull
requests. A failing CI check prevents the PR from being merged into
`main`.

------------------------------------------------------------------------

## Docker Compose

The application VM runs two Compose services:

-   `web` --- Flask/Gunicorn application using the SHA-tagged image
    supplied through `APP_IMAGE`
-   `db` --- PostgreSQL 17 with a persistent named volume and database
    health check

The database uses the `postgres_data` named volume so application
container replacement does not remove database data.

------------------------------------------------------------------------

## Security / Deployment Practices

The project currently applies several basic deployment practices:

-   GitHub repository secrets are used for Docker Hub credentials and
    application VM connection information.
-   A dedicated self-hosted runner account is used instead of running
    the GitHub Actions runner as root.
-   SSH key authentication is used between the runner VM and application
    VM.
-   Deployment uses immutable commit-SHA image tags.
-   CD only runs after successful push-triggered CI.
-   Pull requests must pass CI before merging to `main`.
-   The previous application image is retained as deployment state for
    rollback.

------------------------------------------------------------------------

## Learning Outcomes

This project provided hands-on practice with:

-   Building Docker images in GitHub Actions
-   Understanding GitHub-hosted versus self-hosted runners
-   Running service containers during CI
-   Integration testing Flask against PostgreSQL
-   API smoke testing with `curl`
-   Docker image registries and authentication
-   Commit-SHA based artifact versioning
-   Separating CI from CD workflows
-   Passing the successful CI commit into CD using
    `workflow_run.head_sha`
-   SSH-based deployment to a Linux server
-   Deploying immutable images using Docker Compose
-   Post-deployment health validation
-   Automatic rollback and rollback verification
-   Correctly reporting a failed release after successful recovery
-   Docker image lifecycle cleanup
-   Pull-request validation and required status checks

------------------------------------------------------------------------

## Future Improvements

The CI/CD portion of the project is functionally complete. Future work
will focus on broader infrastructure and operations topics rather than
adding unnecessary pipeline complexity.

Possible next improvements include:

-   Linux patching and configuration automation with Ansible
-   Infrastructure provisioning using Terraform
-   Monitoring and alerting
-   Centralized application/container logging
-   HTTPS and public domain configuration if the application is exposed
    externally
-   Visitor analytics dashboard

------------------------------------------------------------------------

## Author

Aidil Syakirin
