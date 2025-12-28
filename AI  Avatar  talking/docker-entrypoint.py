#!/usr/bin/env python3
"""
Docker entrypoint script - Runs the application in Docker mode
Initializes database and keeps container running
"""
import os
import sys
import time
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/app')

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n[*] Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    print("=" * 60)
    print("AI Avatar Studio - Docker Mode")
    print("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize database
        print("\n[*] Initializing database...")
        from utils.database import DatabaseManager
        db = DatabaseManager()
        print("[OK] Database initialized")
        
        # Check system
        print("\n[*] Checking system requirements...")
        try:
            from utils.system_checker import SystemChecker
            checker = SystemChecker()
            results = checker.check_all()
            
            # Handle different result formats
            if isinstance(results, dict):
                print(f"[OK] System check completed")
            elif isinstance(results, list):
                passed = sum(1 for r in results if isinstance(r, dict) and r.get('passed', False))
                total = len(results)
                print(f"[OK] System check: {passed}/{total} checks passed")
            else:
                print(f"[OK] System check completed")
        except Exception as e:
            print(f"[WARNING] System check skipped: {e}")
        
        print("\n[*] AI Avatar Studio is ready!")
        print("[*] Container is running in background mode")
        print("[*] Database location: /app/data/database/projects.db")
        print("[*] Output directory: /app/output/videos/")
        print("\n[*] To interact with the container:")
        print("    docker-compose exec ai-avatar-studio /bin/bash")
        print("\n[*] Container will keep running... (Ctrl+C to stop)")
        
        # Keep container alive
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
