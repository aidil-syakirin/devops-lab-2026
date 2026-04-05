#!/usr/bin/env bash
# Canonical deploy entrypoint for GitHub Actions → SSM (see .github/workflows/deploy.yml).
# If your server still has a hand-edited copy, reconcile it with this file and treat this
# repo as the source of truth after merge.
set -euo pipefail

VERSION="${1:?Usage: $0 <short-git-sha>}"

APP_DIR="${DEPLOY_APP_DIR:-/home/ubuntu/app}"
cd "$APP_DIR"

set -a
[ -f .env ] && . ./.env
set +a

HUB="${DOCKERHUB_USERNAME:?Set DOCKERHUB_USERNAME in .env (must match docker-compose image prefix)}"
WEB_REPO="${HUB}/resume-tracker"

# Default matches docker-compose.yml (web publishes host 5000). If you terminate TLS or
# reverse-proxy on :80, install a vhost (see deploy/nginx-health-proxy.conf.example) and set:
#   export DEPLOY_HEALTH_URL=http://127.0.0.1/health
# or pass the same in the SSM environment.
DEPLOY_HEALTH_URL="${DEPLOY_HEALTH_URL:-http://127.0.0.1:5000/health}"

PREV_VERSION=""
if [ -f current_version.txt ]; then
  PREV_VERSION="$(tr -d '[:space:]' < current_version.txt)"
fi

cp -a docker-compose.yml docker-compose.yml.bak.deploy

docker pull "${WEB_REPO}:${VERSION}"

# Only lines with "resume-tracker:<tag>" are touched; "resume-tracker-db:..." is unchanged.
sed -i.bak-sed "s|resume-tracker:[^[:space:]]*|resume-tracker:${VERSION}|g" docker-compose.yml
rm -f docker-compose.yml.bak-sed

docker compose config >/dev/null

docker compose up -d --force-recreate --remove-orphans

if curl -fsS --max-time 60 "$DEPLOY_HEALTH_URL" >/dev/null; then
  printf '%s\n' "$VERSION" > current_version.txt
  echo "Deploy OK: ${WEB_REPO}:${VERSION}"
else
  echo "Health check failed (${DEPLOY_HEALTH_URL}); rolling back compose image tag."
  if [ -n "$PREV_VERSION" ]; then
    sed -i.bak-rollback "s|resume-tracker:[^[:space:]]*|resume-tracker:${PREV_VERSION}|g" docker-compose.yml
    rm -f docker-compose.yml.bak-rollback
  else
    mv docker-compose.yml.bak.deploy docker-compose.yml
  fi
  docker compose config >/dev/null
  docker compose up -d --force-recreate --remove-orphans
  exit 1
fi
