# RoboInvest Duplicate Process Detection System

## Overview

This system prevents duplicate RoboInvest processes from running simultaneously, which can cause:
- **Notification spam** (multiple emergency alerts)
- **System instability** (resource conflicts)
- **Inconsistent behavior** (multiple agents competing)
- **Performance degradation** (excessive resource usage)

## Components

### 1. Enhanced Startup Script (`startup.sh`)

The startup script now includes comprehensive duplicate detection:

- **Pre-startup scan**: Detects and kills existing RoboInvest processes
- **Process patterns detected**:
  - `start_enhanced_meta_agent.py`
  - `background_research_service.py`
  - `uvicorn.*fastapi_app`
  - `vite`
  - `npm run dev`
  - `enhanced_meta_agent`
  - `meta_agent`
  - `research_service`

- **Post-startup verification**: Confirms no duplicates are running
- **Detailed logging**: Shows what processes were found and killed

### 2. Duplicate Checker (`check_duplicates.sh`)

Standalone script to check for duplicate processes:

```bash
# Check for duplicates
./check_duplicates.sh

# Kill duplicates
./check_duplicates.sh kill

# Show help
./check_duplicates.sh help
```

**Output example:**
```
🔍 RoboInvest Duplicate Process Checker
======================================
📊 Current RoboInvest Processes:
--------------------------------
✅ Meta-Agent: 1 instance (PID: 12345)
⚠️  Research-Service: 2 instances (PIDs: 12346 12347)
✅ Backend-API: 1 instance (PID: 12348)
✅ Frontend: 1 instance (PID: 12349)
--------------------------------
📈 Total RoboInvest processes: 5

🚨 DUPLICATE PROCESSES DETECTED!
   This may cause:
   • Notification spam
   • System instability
   • Resource conflicts
   • Inconsistent behavior
```

### 3. Emergency Killer (`kill_duplicates.sh`)

Quick emergency script to kill all RoboInvest processes:

```bash
./kill_duplicates.sh
```

**Use when:**
- You're getting notification spam
- System is unstable
- Multiple instances are running
- Normal stop script doesn't work

### 4. Enhanced Stop Script (`stop.sh`)

The stop script now includes:
- More comprehensive process detection
- Meta-agent process cleanup
- Final verification step
- Log archiving

## Usage

### Normal Startup
```bash
./startup.sh
```
- Automatically detects and kills duplicates
- Verifies single instances are running
- Shows detailed process information

### Check for Duplicates
```bash
./check_duplicates.sh
```
- Shows current process status
- Identifies duplicates
- Provides fix recommendations

### Emergency Cleanup
```bash
./kill_duplicates.sh
```
- Kills all RoboInvest processes
- Use when experiencing issues

### Normal Shutdown
```bash
./stop.sh
```
- Cleanly stops all services
- Archives logs
- Verifies shutdown

## Troubleshooting

### If You're Still Getting Notification Spam

1. **Check for duplicates:**
   ```bash
   ./check_duplicates.sh
   ```

2. **Kill all processes:**
   ```bash
   ./kill_duplicates.sh
   ```

3. **Restart cleanly:**
   ```bash
   ./startup.sh
   ```

### If Processes Won't Die

1. **Force kill with PIDs:**
   ```bash
   ps aux | grep -E "start_enhanced_meta_agent|background_research_service|uvicorn|vite"
   kill -9 <PID1> <PID2> <PID3>
   ```

2. **Kill by port:**
   ```bash
   lsof -ti:8081 | xargs kill -9
   lsof -ti:5173 | xargs kill -9
   ```

### If Startup Fails

1. **Check for port conflicts:**
   ```bash
   lsof -i :8081
   lsof -i :5173
   ```

2. **Kill conflicting processes:**
   ```bash
   ./kill_duplicates.sh
   ```

3. **Restart:**
   ```bash
   ./startup.sh
   ```

## Prevention Tips

1. **Always use the startup script** instead of running services manually
2. **Check for duplicates** before starting if you suspect issues
3. **Use the stop script** instead of just closing terminals
4. **Monitor the logs** for any duplicate process warnings
5. **Don't run multiple terminals** with the same services

## Log Files

The system creates detailed logs:
- `backend.log` - Backend API server
- `frontend.log` - Frontend development server
- `research.log` - Background research service
- `meta_agent.log` - Enhanced meta agent

These are automatically archived when stopping services.

## Benefits

- **No more notification spam** from duplicate processes
- **Stable system operation** with single instances
- **Clear process management** with detailed logging
- **Easy troubleshooting** with dedicated tools
- **Automatic cleanup** on startup and shutdown 