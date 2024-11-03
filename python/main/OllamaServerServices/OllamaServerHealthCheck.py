from python.main.OllamaServerServices.ollama_service import OllamaService
import requests
import time


def wait_for_server():
    """Wait for Ollama server to be ready"""
    max_attempts = 30
    print("Checking server health...")
    for attempt in range(max_attempts):
        try:
            print(f"Health check attempt {attempt + 1}/{max_attempts}")
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                print("OllamaServerServices health check succeeded!")
                return True
        except requests.exceptions.ConnectionError:
            print(f"OllamaServerServices not ready yet, waiting... (attempt {attempt + 1})")
            time.sleep(1)
    return False


# Start the server
print("Initializing Ollama server...")
with OllamaService() as server:
    # Check if process started successfully
    if server.process is None or server.process.poll() is not None:
        print("OllamaServerServices process failed to start or terminated immediately")
        # Get any error output
        if server.process:
            _, stderr = server.process.communicate()
            print(f"OllamaServerServices error output: {stderr}")
    else:
        print("OllamaServerServices process is running, checking if it's responsive...")

        # Wait longer for server to be ready
        if wait_for_server():
            print("OllamaServerServices is ready!")
            try:
                response = requests.get('http://localhost:11434/api/tags')
                print("Available models:", response.json())
            except Exception as e:
                print(f"Error making API call: {e}")

            print("Keeping server running for testing...")
            time.sleep(60)
        else:
            print("OllamaServerServices failed to respond to health checks")

print("Script completed")