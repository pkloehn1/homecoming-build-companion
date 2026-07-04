#!/usr/bin/env bash

set -Eeuo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required (owner/repo)}"
: "${PR_NUMBER:?PR_NUMBER is required}"
: "${JOB_STATUS:?JOB_STATUS is required}"
: "${STATUS_CONTEXT:?STATUS_CONTEXT is required}"
: "${TARGET_URL:?TARGET_URL is required}"
: "${GH_TOKEN:?GH_TOKEN is required}"

sha=$(gh api "repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}" --jq '.head.sha') || {
  printf "Error: failed to resolve head SHA for PR #%s in %s\n" "${PR_NUMBER}" "${GITHUB_REPOSITORY}" >&2
  exit 2
}

if [[ -z "${sha}" || "${sha}" == "null" ]]; then
  printf "Error: No head SHA available for PR #%s in %s. The PR may not exist or the API response is missing .head.sha.\n" "${PR_NUMBER}" "${GITHUB_REPOSITORY}" >&2
  exit 2
fi

state="error"
if [[ "${JOB_STATUS}" == "success" ]]; then
  state="success"
elif [[ "${JOB_STATUS}" == "failure" ]]; then
  state="failure"
fi

printf "Posting status context '%s' (state=%s) to %s@%.12s\n" "${STATUS_CONTEXT}" "${state}" "${GITHUB_REPOSITORY}" "${sha}" >&2

gh api -X POST "repos/${GITHUB_REPOSITORY}/statuses/${sha}" \
  -f state="${state}" \
  -f context="${STATUS_CONTEXT}" \
  -f description="Reported by GitHub Actions (${JOB_STATUS})" \
  -f target_url="${TARGET_URL}" >/dev/null || {
  printf "Error: failed to post status context '%s' to %s@%.12s\n" "${STATUS_CONTEXT}" "${GITHUB_REPOSITORY}" "${sha}" >&2
  exit 1
}
