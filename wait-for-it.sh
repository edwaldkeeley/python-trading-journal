#!/usr/bin/env bash
# Wrapper script to wait for a host:port to be reachable

HOSTPORT="$1"
shift
TIMEOUT=60
STRICT=""

for arg in "$@"; do
  case $arg in
    --timeout=*) TIMEOUT="${arg#*=}" ;;
    --strict) STRICT="1" ;;
  esac
done

HOST="${HOSTPORT%%:*}"
PORT="${HOSTPORT##*:}"

echo "Waiting up to $TIMEOUT seconds for $HOST:$PORT..."
for i in $(seq 1 "$TIMEOUT"); do
  if (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1; then
    echo "$HOST:$PORT is available"
    exit 0
  fi
  sleep 1
done

echo "Timeout waiting for $HOST:$PORT"
if [ -n "$STRICT" ]; then
  exit 1
fi
exit 0

