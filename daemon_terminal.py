"""
Log Receiver Daemon - Dependent on parent process
Automatically terminates when parent process ends
"""

import socket
import sys
import argparse
import os
import time
import threading

class LogReceiverDaemon:
    def __init__(self, port=9999, host='127.0.0.1', parent_pid=None):
        self.port = port
        self.host = host
        self.parent_pid = parent_pid
        self.sock = None
        self.running = True
        
    def check_parent_alive(self):
        """Check if parent process is still running"""
        if self.parent_pid is None:
            return True
            
        try:
            if sys.platform == 'win32':
                import psutil
                return psutil.pid_exists(self.parent_pid)
            else:
                # Unix: send signal 0 to check if process exists
                os.kill(self.parent_pid, 0)
                return True
        except (OSError, ImportError):
            return False
            
    def parent_monitor(self):
        """Monitor parent process in a separate thread"""
        while self.running:
            if not self.check_parent_alive():
                self.running = False
                break
            time.sleep(1)
            
    def setup_socket(self):
        """Initialize the UDP socket"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(0.5)  # Short timeout for checking shutdown
        
    def run(self):
        """Main daemon loop"""
        self.setup_socket()
        
        print(f'Log - Port {self.port}')
        print('-' * 50)
        sys.stdout.flush()
        
        # Start parent monitoring thread if parent PID provided
        if self.parent_pid:
            monitor_thread = threading.Thread(target=self.parent_monitor, daemon=True)
            monitor_thread.start()
        
        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    message = data.decode('utf-8')
                    print(message, end='')
                    sys.stdout.flush()
                except socket.timeout:
                    continue  # Check if still running
                except Exception:
                    pass  # Silently ignore errors
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.sock:
            self.sock.close()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Log Receiver Daemon')
    parser.add_argument('--port', type=int, default=9999,
                       help='Port to listen on (default: 9999)')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--parent-pid', type=int, default=None,
                       help='Parent process PID to monitor')
    
    args = parser.parse_args()
    
    daemon = LogReceiverDaemon(
        port=args.port,
        host=args.host,
        parent_pid=args.parent_pid
    )
    
    daemon.run()

if __name__ == '__main__':
    main()