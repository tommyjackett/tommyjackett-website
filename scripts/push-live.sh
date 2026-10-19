#!/usr/bin/env bash
# Push tommyjackett-website and wait for the GitHub Pages deploy to match the local file.
# Same pattern as repos/tng-website/scripts/push-live.sh. Token: TOMMY AI/.secrets/github-token-tommyjackett-website.txt
# Usage: scripts/push-live.sh [file-to-verify]   (default: index.html)
# SITE is the staging URL until DNS is switched, then change it to https://tommyjackett.com
set -uo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
BASE="$(cd "$DIR/../.." && pwd)"
export GH_T="$(tr -d '[:space:]' < "$BASE/.secrets/github-token-tommyjackett-website.txt")"
SITE="${SITE:-https://tommyjackett.github.io/tommyjackett-website}"
FILE="${1:-index.html}"

cd "$DIR"
git -c credential.helper= -c credential.helper='!f(){ echo username=tommyjackett; echo "password=$GH_T"; };f' push origin main

live_matches() {
  diff <(curl -sL "$SITE/$FILE?cb=$(date +%s)") "$DIR/$FILE" >/dev/null 2>&1
}

for attempt in 1 2 3 4 5 6; do
  for i in 1 2 3 4 5 6 7 8 9; do
    sleep 10
    if live_matches; then
      echo "LIVE: $SITE/$FILE matches local (attempt $attempt, ~$((i*10))s)"
      exit 0
    fi
  done
  echo "attempt $attempt: not live after 90s, re-dispatching the deploy workflow"
  curl -s -X POST -H "Authorization: token $GH_T" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/tommyjackett/tommyjackett-website/actions/workflows/deploy-pages.yml/dispatches" \
    -d '{"ref":"main"}' >/dev/null
done

echo "FAILED: still not live after ~9 minutes of retries. Check https://www.githubstatus.com"
exit 1
