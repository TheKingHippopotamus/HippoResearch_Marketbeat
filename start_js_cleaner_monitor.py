#!/usr/bin/env python3
"""
Background daemon script to run the JavaScript cleaner monitor.
This script runs the monitor in the background and logs to a file.
"""

import subprocess
import sys
import os
import time
import signal
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('js_cleaner_daemon.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def start_monitor():
    """Start the JavaScript cleaner monitor in the background"""
    try:
        logger.info("🚀 Starting JavaScript cleaner monitor daemon...")
        
        # Run the monitor script
        cmd = [sys.executable, "inject_js_cleaner.py", "--monitor", "--dir", "articles"]
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"✅ Monitor daemon started with PID: {process.pid}")
        logger.info("📝 Monitor is now running in the background")
        logger.info("📄 Logs are being written to js_cleaner.log")
        logger.info("⏹️ To stop the monitor, run: pkill -f 'inject_js_cleaner.py --monitor'")
        
        # Save PID to file for easy management
        with open('js_cleaner_monitor.pid', 'w') as f:
            f.write(str(process.pid))
        
        return process
        
    except Exception as e:
        logger.error(f"❌ Error starting monitor: {e}")
        return None

def stop_monitor():
    """Stop the JavaScript cleaner monitor"""
    try:
        # Try to read PID from file
        if os.path.exists('js_cleaner_monitor.pid'):
            with open('js_cleaner_monitor.pid', 'r') as f:
                pid = int(f.read().strip())
            
            # Kill the process
            os.kill(pid, signal.SIGTERM)
            logger.info(f"✅ Stopped monitor process (PID: {pid})")
            
            # Remove PID file
            os.remove('js_cleaner_monitor.pid')
        else:
            # Try to find and kill by process name
            subprocess.run(['pkill', '-f', 'inject_js_cleaner.py --monitor'], 
                         capture_output=True)
            logger.info("✅ Stopped monitor process")
            
    except Exception as e:
        logger.error(f"❌ Error stopping monitor: {e}")

def check_status():
    """Check if the monitor is running"""
    try:
        if os.path.exists('js_cleaner_monitor.pid'):
            with open('js_cleaner_monitor.pid', 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                logger.info(f"✅ Monitor is running (PID: {pid})")
                return True
            except OSError:
                logger.info("❌ Monitor is not running (PID file exists but process is dead)")
                os.remove('js_cleaner_monitor.pid')
                return False
        else:
            logger.info("❌ Monitor is not running (no PID file)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking status: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python start_js_cleaner_monitor.py start   - Start the monitor")
        print("  python start_js_cleaner_monitor.py stop    - Stop the monitor")
        print("  python start_js_cleaner_monitor.py status  - Check monitor status")
        print("  python start_js_cleaner_monitor.py restart - Restart the monitor")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        if check_status():
            logger.info("⚠️ Monitor is already running")
        else:
            start_monitor()
    
    elif command == 'stop':
        stop_monitor()
    
    elif command == 'status':
        check_status()
    
    elif command == 'restart':
        logger.info("🔄 Restarting monitor...")
        stop_monitor()
        time.sleep(2)
        start_monitor()
    
    else:
        logger.error(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 