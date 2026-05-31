import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, 'frontend')

    print("=" * 60)
    print("KKR FAN HUB - MULTI-SERVER RUNNER")
    print("=" * 60)
    print("Starting KKR Backend Server on http://https://kkr-fan-hub.onrender.com:5000 ...")
    print("Starting KKR Frontend Server on http://https://kkr-fan-hub.onrender.com:3000 ...")
    print("=" * 60)

    # Start backend server (FastAPI with Uvicorn)
    backend_proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'backend.main:app', '--port', '5000'],
        cwd=root_dir
    )

    # Start frontend server
    frontend_proc = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3000', '--directory', frontend_dir],
        cwd=root_dir
    )

    print("Both servers are running!")
    print("- Frontend: http://https://kkr-fan-hub.onrender.com:3000")
    print("- Backend API: http://https://kkr-fan-hub.onrender.com:5000/api")
    print("Press Ctrl+C to terminate both servers.")
    print("=" * 60)

    try:
        while True:
            # Check if processes are still running
            if backend_proc.poll() is not None:
                print("Backend server stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend server stopped unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers gracefully...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Both servers have been stopped.")

if __name__ == '__main__':
    main()
