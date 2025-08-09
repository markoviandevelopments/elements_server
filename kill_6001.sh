#!/bin/bash

# Check if lsof is installed
if ! command -v lsof &> /dev/null; then
    echo "Error: lsof is not installed. Please install it (e.g., 'sudo apt install lsof' on Ubuntu)."
    exit 1
fi

# Check if netstat or ss is installed
if command -v ss &> /dev/null; then
    NETCMD="ss -tuln"
elif command -v netstat &> /dev/null; then
    NETCMD="netstat -tuln"
else
    echo "Warning: Neither ss nor netstat is installed. Cannot check socket status."
    NETCMD="echo"
fi

# Find processes using port 6001 (IPv4 and IPv6)
pids=$(sudo lsof -ti :6001 -ti :6001,IPv6 2>/dev/null)

# Check if any processes were found
if [ -z "$pids" ]; then
    echo "No processes found using port 6001."
else
    # Loop through each PID and kill the process
    for pid in $pids; do
        echo "Found process with PID $pid using port 6001."
        # Try graceful termination first
        sudo kill -15 "$pid" 2>/dev/null
        sleep 1
        # Check if process is still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "Process $pid did not terminate gracefully. Forcing kill..."
            sudo kill -9 "$pid" 2>/dev/null
        fi
        if [ $? -eq 0 ]; then
            echo "Successfully killed process with PID $pid."
        else
            echo "Failed to kill process with PID $pid."
        fi
    done
fi

# Verify port is no longer in use
if $NETCMD | grep -q 6001; then
    echo "Warning: Port 6001 is still in use (possibly in TIME_WAIT). Waiting 10 seconds..."
    sleep 10
    if $NETCMD | grep -q 6001; then
        echo "Error: Port 6001 is still occupied. Try changing the port in your script or rebooting."
        exit 1
    fi
else
    echo "Port 6001 is now free."
fi

exit 0
