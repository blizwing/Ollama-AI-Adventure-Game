import subprocess
import time
import signal
import sys
import threading
from python.main.utils.logging_config import logging  # Adjust based on your logging configuration

class OllamaService:
    def __init__(self, ollama_path="ollama"):
        """
        Initialize OllamaService with path to ollama executable.

        Args:
            ollama_path (str): Path to ollama executable, defaults to "ollama".
        """
        self.ollama_path = ollama_path
        self.process = None
        self.logger = logging.getLogger('server')  # Use the server logger

    def start(self):
        """Start the Ollama server process."""
        try:
            self.logger.info("Starting Ollama server from: %s", self.ollama_path)

            # First check if ollama exists
            if not self._check_ollama_exists():
                raise FileNotFoundError(f"Ollama executable not found at: {self.ollama_path}")

            # Check if port is already in use
            if self._check_port_in_use(11434):
                raise RuntimeError("Port 11434 is already in use. Is Ollama already running?")

            # Start ollama serve process with full output capture
            self.process = subprocess.Popen(
                [self.ollama_path, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )

            # Read stdout and stderr in a separate thread
            threading.Thread(target=self._read_output, args=(self.process.stdout,), daemon=True).start()
            threading.Thread(target=self._read_output, args=(self.process.stderr,), daemon=True).start()

            # Wait a bit for the server to start
            time.sleep(5)

            # Check if process is still running
            if self.process.poll() is not None:
                raise RuntimeError("Ollama server process terminated unexpectedly.")

            self.logger.info("Ollama server process initialized")

        except Exception as e:
            self.logger.error("Error starting Ollama server: %s", str(e))
            raise

    def _check_ollama_exists(self):
        """Check if ollama executable exists."""
        try:
            subprocess.run([self.ollama_path, "--version"],
                           capture_output=True,
                           text=True,
                           check=False)
            return True
        except FileNotFoundError:
            return False

    def _check_port_in_use(self, port):
        """Check if a port is in use."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def stop(self):
        """Stop the Ollama server process."""
        if self.process:
            self.logger.info("Stopping Ollama server...")
            self.process.terminate()  # Send SIGTERM signal

            # Wait for process to terminate
            try:
                self.process.wait(timeout=5)
                self.logger.info("Ollama server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if process doesn't terminate
                self.logger.warning("Ollama server didn't stop gracefully, forcing kill...")
                self.process.kill()
                self.logger.info("Ollama server forcefully stopped")

            # Capture any final output
            stdout, stderr = self.process.communicate()
            if stdout.strip():
                self.logger.info("Final stdout: %s", stdout)
            if stderr.strip():
                self.logger.error("Final stderr: %s", stderr)

            self.process = None

    def _read_output(self, stream):
        """Read output from a given stream (stdout or stderr)."""
        for line in iter(stream.readline, ''):
            self.logger.info(line.strip())
        stream.close()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Example usage
if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nShutting down Ollama server...")
        if server.process:
            server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start server
    server = OllamaService()

    try:
        server.start()
        print("Press Ctrl+C to stop the server")
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

def check_server_health():
    """Check if server is responsive."""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        return response.status_code == 200
    except:
        return False

def ensure_server_running(self):
    """Ensure the server is running, restarting if necessary."""
    if not self.check_server_health():
        self.logger.warning("Ollama server unresponsive, attempting to restart...")
        self.stop()
        time.sleep(5)  # Wait before trying to start again
        self.start()
