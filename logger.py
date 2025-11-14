"""
Main application with logging to a dependent daemon terminal
Terminal window is a true child process that closes automatically
"""

import socket
import subprocess
import logging
import sys
import time
import os
import atexit
import signal
from pathlib import Path

class TerminalLogHandler(logging.Handler):
    """Custom handler that sends plain text logs via UDP"""
    
    def __init__(self, host='127.0.0.1', port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.sock.sendto((msg + '\n').encode('utf-8'), (self.host, self.port))
        except Exception:
            self.handleError(record)
            
    def close(self):
        self.sock.close()
        super().close()

class LoggerManager:
    """Manages the logger and terminal daemon"""
    
    def __init__(self, port=9999, start_daemon=True):
        self.port = port
        self.daemon_process = None
        self.logger = None
        self.terminal_handler = None
        
        if start_daemon:
            self.start_daemon_terminal()
            
        self.setup_logger()
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)  # Handle Ctrl+C
        if sys.platform != 'win32':
            signal.signal(signal.SIGHUP, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.cleanup()
        sys.exit(0)
        
    def start_daemon_terminal(self):
        """Start the daemon in a new terminal window as a true child process"""
        daemon_script = Path(__file__).parent / 'daemon_terminal.py'
        
        if not daemon_script.exists():
            return
        
        # Get current process PID to pass to daemon
        parent_pid = os.getpid()
        
        if sys.platform == 'win32':
            # Windows: Start terminal as a child process that will close automatically
            cmd = [
                'python', str(daemon_script),
                '--port', str(self.port),
                '--parent-pid', str(parent_pid)
            ]
            
            # Start terminal as a true child process
            self.daemon_process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
        elif sys.platform == 'darwin':
            # macOS: Use Terminal but as a child process
            script_content = f'''
            tell application "Terminal"
                set newWindow to do script "python3 {daemon_script} --port {self.port} --parent-pid {parent_pid}"
                delay 0.5
            end tell
            '''
            self.daemon_process = subprocess.Popen(
                ['osascript', '-e', script_content]
            )
            
        else:
            # Linux: Start terminal directly as child process
            cmd_args = [
                'python3', str(daemon_script),
                '--port', str(self.port),
                '--parent-pid', str(parent_pid)
            ]
            
            terminals = [
                ['gnome-terminal', '--wait', '--'] + cmd_args,
                ['xterm', '-e'] + cmd_args,
                ['konsole', '-e'] + cmd_args,
                ['x-terminal-emulator', '-e'] + cmd_args,
            ]
            
            for term_cmd in terminals:
                try:
                    self.daemon_process = subprocess.Popen(term_cmd)
                    break
                except FileNotFoundError:
                    continue
            else:
                # Fallback: run without terminal
                self.daemon_process = subprocess.Popen(cmd_args)
        
        # Give daemon time to start
        time.sleep(2)
        
    def setup_logger(self):
        """Configure the logger with terminal handler"""
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        self.logger.handlers.clear()
        
        # Add terminal handler
        self.terminal_handler = TerminalLogHandler('127.0.0.1', self.port)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.terminal_handler.setFormatter(formatter)
        self.logger.addHandler(self.terminal_handler)
        
    def get_logger(self):
        """Get the configured logger"""
        return self.logger
    
    def redirect_stderr(self):
        """Redirect stderr to logger"""
        class StderrToLogger:
            def __init__(self, logger, level):
                self.logger = logger
                self.level = level
                self.buffer = ''
                
            def write(self, msg):
                self.buffer += msg
                if '\n' in self.buffer:
                    lines = self.buffer.split('\n')
                    for line in lines[:-1]:
                        if line.strip():
                            self.logger.log(self.level, f"STDERR: {line.strip()}")
                    self.buffer = lines[-1]
                    
            def flush(self):
                if self.buffer.strip():
                    self.logger.log(self.level, f"STDERR: {self.buffer.strip()}")
                    self.buffer = ''
        
        sys.stderr = StderrToLogger(self.logger, logging.ERROR)
        
    def cleanup(self):
        """Clean up resources and terminate daemon"""
        # Close handler
        if self.terminal_handler:
            self.terminal_handler.close()
            
        # Terminate daemon process
        if self.daemon_process:
            try:
                if sys.platform == 'win32':
                    self.daemon_process.terminate()
                    time.sleep(0.5)
                    if self.daemon_process.poll() is None:
                        self.daemon_process.kill()
                else:
                    self.daemon_process.terminate()
                    try:
                        self.daemon_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.daemon_process.kill()
            except:
                pass

# Global logger manager for cleanup
log_manager = None

def start_external_log():
    global log_manager
    
    # Initialize logger manager
    log_manager = LoggerManager(port=9999, start_daemon=True)
    logger = log_manager.get_logger()
    
    # Redirect stderr to logger
    log_manager.redirect_stderr()
    
    # Your application code here
    logger.info("Application started")