#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/scripts/mcp-process-cleanup"
readonly SCRIPT
TEST_ROOT="$(mktemp -d /tmp/mcp-process-cleanup-test.XXXXXX)"
export MCP_CLEANUP_STATE_ROOT="$TEST_ROOT/state"
export MCP_CLEANUP_ALLOW_TEST_PROCESS=1
export CODEX_SESSION_ID=test-session

cleanup() {
  [[ -n "${worker_pid:-}" ]] && kill "$worker_pid" 2>/dev/null || true
  [[ "$TEST_ROOT" == /tmp/* || "$TEST_ROOT" == /private/tmp/* ]] || return 1
  find "$TEST_ROOT" -depth -delete
}
trap cleanup EXIT

ruby -e 'sleep 60' mcp-cleanup-test-worker &
worker_pid=$!
"$SCRIPT" register --session test-session --pid "$worker_pid" --owner-pid "$$"
"$SCRIPT" cleanup-session --dry-run | grep -q "WOULD_STOP pid=$worker_pid"
kill -0 "$worker_pid"
"$SCRIPT" cleanup-session --execute | grep -q "STOPPED pid=$worker_pid"
wait "$worker_pid" 2>/dev/null || true
if kill -0 "$worker_pid" 2>/dev/null; then
  printf 'worker survived cleanup\n' >&2
  exit 1
fi
unset worker_pid

ruby -e 'sleep 60' mcp-cleanup-test-worker &
worker_pid=$!
"$SCRIPT" register --session test-session --pid "$worker_pid" --owner-pid "$$"
sed -i.bak 's/^command_hash=.*/command_hash=tampered/' "$TEST_ROOT/state/test-session/$worker_pid.record"
"$SCRIPT" cleanup-session --execute | grep -q "STALE pid=$worker_pid"
kill -0 "$worker_pid"
kill "$worker_pid"
wait "$worker_pid" 2>/dev/null || true
unset worker_pid

ruby -e 'sleep 60' mcp-cleanup-test-owner &
owner_pid=$!
ruby -e 'sleep 60' mcp-cleanup-test-worker &
worker_pid=$!
"$SCRIPT" register --session test-session --pid "$worker_pid" --owner-pid "$owner_pid"
if "$SCRIPT" cleanup-orphans --dry-run | grep -q "pid=$worker_pid"; then
  printf 'live owner was classified as orphan\n' >&2
  exit 1
fi
kill "$owner_pid"
wait "$owner_pid" 2>/dev/null || true
"$SCRIPT" cleanup-orphans --dry-run | grep -q "WOULD_STOP pid=$worker_pid"
"$SCRIPT" cleanup-orphans --execute | grep -q "STOPPED pid=$worker_pid"
wait "$worker_pid" 2>/dev/null || true
unset worker_pid owner_pid

if "$SCRIPT" cleanup-session --session foreign-session --dry-run 2>/dev/null; then
  printf 'foreign session was accepted\n' >&2
  exit 1
fi

printf 'PASS mcp-process-cleanup\n'
