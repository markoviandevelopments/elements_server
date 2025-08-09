#!/bin/bash

# Script to forcefully free port 6001 by killing associated processes.
# Handles IPv4/IPv6, TIME_WAIT states, and uses multiple tools for reliability.
# Runs with verbose logging and configurable timeouts.
# Warning: May break desktop if killing X server or similar processes.

# Version and logging setup
VERSION="2.1"
LOG_FILE="/tmp/kill_port_6001.log"
PORT=6001
MAX_WAIT_SECONDS=300
SLEEP_INTERVAL=5

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Starting script version $VERSION to free port $PORT."

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
    log_message "Error: Must run with sudo."
    exit 1
fi

# Detect available tools
HAS_LSOF=$(command -v lsof &>/dev/null && echo 1 || echo 0)
HAS_FUSER=$(command -v fuser &>/dev/null && echo 1 || echo 0)
HAS_SS=$(command -v ss &>/dev/null && echo 1 || echo 0)
HAS_NETSTAT=$(command -v netstat &>/dev/null && echo 1 || echo 0)

if [ $HAS_LSOF -eq 0 ] && [ $HAS_FUSER -eq 0 ]; then
    log_message "Error: Need lsof or fuser installed."
    exit 1
fi

if [ $HAS_SS -eq 1 ]; then
    NETCMD="ss -tuln"
elif [ $HAS_NETSTAT -eq 1 ]; then
    NETCMD="netstat -tuln"
else
    log_message "Error: Need ss or netstat installed."
    exit 1
fi

log_message "Tools detected: lsof=$HAS_LSOF, fuser=$HAS_FUSER, ss=$HAS_SS, netstat=$HAS_NETSTAT."

# Function to check if port is in use
is_port_in_use() {
    if [ $HAS_SS -eq 1 ]; then
        $NETCMD | awk '{print $5}' | grep -q ":$PORT\$"
    elif [ $HAS_NETSTAT -eq 1 ]; then
        $NETCMD | awk '{print $4}' | grep -q ":$PORT\$"
    fi
}

# Function to get PIDs using the port
get_pids() {
    local pids=""
    if [ $HAS_FUSER -eq 1 ]; then
        pids=$(fuser -n tcp $PORT 2>/dev/null; fuser -n udp $PORT 2>/dev/null)
    elif [ $HAS_LSOF -eq 1 ]; then
        pids=$(lsof -ti :$PORT 2>/dev/null)
    fi
    echo "$pids" | tr '\n' ' ' | sed 's/ //g'
}

# Function to kill a single PID
kill_pid() {
    local pid=$1
    log_message "Killing PID $pid (SIGTERM)."
    kill -15 "$pid" 2>/dev/null
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        log_message "Forcing kill on PID $pid (SIGKILL)."
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi
    kill -0 "$pid" 2>/dev/null && return 1 || { log_message "Killed PID $pid."; return 0; }
}

# Kill processes
pids=$(get_pids)
if [ -z "$pids" ]; then
    log_message "No processes on port $PORT."
else
    log_message "PIDs on port $PORT: $pids"
    for pid in $pids; do
        kill_pid "$pid" || log_message "Failed to kill PID $pid."
    done
fi

# Backup kill with fuser if available
if [ $HAS_FUSER -eq 1 ]; then
    log_message "Backup kill using fuser."
    fuser -k -15 -n tcp $PORT 2>/dev/null; fuser -k -15 -n udp $PORT 2>/dev/null
    sleep 2
    fuser -k -9 -n tcp $PORT 2>/dev/null; fuser -k -9 -n udp $PORT 2>/dev/null
fi

# Wait for port to free
wait_start=$(date +%s)
while is_port_in_use; do
    elapsed=$(( $(date +%s) - wait_start ))
    if [ $elapsed -ge $MAX_WAIT_SECONDS ]; then
        log_message "Error: Port $PORT still in use after $MAX_WAIT_SECONDS seconds. Investigate or reboot."
        exit 1
    fi
    log_message "Port $PORT still in use. Waited $elapsed seconds. Sleeping $SLEEP_INTERVAL..."
    sleep $SLEEP_INTERVAL
done

log_message "Port $PORT is free. Script completed."
exit 0
