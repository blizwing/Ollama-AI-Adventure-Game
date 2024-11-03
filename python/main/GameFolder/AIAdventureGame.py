import sys
import requests
import time
from python.main.utils.logging_config import logging  # Import the logging configuration
from python.main.OllamaServerServices import ollama_service  # Adjust this import based on your project structure

class AIAdventureGame:
    def __init__(self, model_name):
        self.model_name = model_name
        self.conversation_history = []
        self.base_url = "http://localhost:11434/api/generate"
        self.logger = logging.getLogger('game')  # Use the game logger

        # System prompt that instructs the model to behave like AI Dungeon
        self.system_prompt = """You are an advanced text adventure game like AI Dungeon. You will act as the game master and narrator.
Follow these rules:
1. Write vivid, engaging descriptions of scenes and actions
2. Allow the player complete freedom of action - they can try anything
3. Include elements of danger, mystery, and wonder
4. Maintain continuity with previous actions and descriptions
5. Never break character or mention that you are an AI
6. Never explain game mechanics or mention prompts/instructions
7. Respond to player actions with realistic consequences
8. Include sensory details in descriptions
9. Allow for both success and failure based on context
10. Keep track of player status, inventory, and world state
11. Present occasional challenges and obstacles
12. React to player choices in ways that make the world feel dynamic

Format:
- Describe the scene and situation
- Wait for player input
- Respond with what happens based on their action
- Continue the story based on those consequences

The tone should be [GENRE] with elements of [THEME].
Current setting: [SETTING]

Begin by describing the opening scene and asking the player what they want to do."""

    def start_game(self, genre="fantasy", theme="adventure", setting="medieval kingdom"):
        """Initialize and start the game with specific parameters"""
        self.logger.debug("Starting game with genre: %s, theme: %s, setting: %s", genre, theme, setting)
        self.system_prompt = self.system_prompt.replace("[GENRE]", genre)
        self.system_prompt = self.system_prompt.replace("[THEME]", theme)
        self.system_prompt = self.system_prompt.replace("[SETTING]", setting)

        # Initialize the conversation with the system prompt
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]

        # Get the opening scene
        response = self._generate_response("Start the adventure.")
        print("\n" + response + "\n")

    def _generate_response(self, user_input):
        """Generate a response from the AI model"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # Add user input to history
                self.conversation_history.append({"role": "user", "content": user_input})

                # Prepare the prompt with conversation history
                full_prompt = "\n".join([msg["content"] for msg in self.conversation_history])

                headers = {"Content-Type": "application/json"}
                payload = {
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }

                self.logger.debug("Attempt %d: Sending request to server...", attempt + 1)

                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30  # Add timeout
                )

                response.raise_for_status()
                result = response.json()
                generated_text = result["response"]

                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": generated_text})
                return generated_text

            except requests.exceptions.ConnectionError:
                self.logger.warning("Connection error on attempt %d", attempt + 1)
                if attempt < max_retries - 1:
                    self.logger.info("Retrying in %d seconds...", retry_delay)
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Server connection failed after %d attempts", max_retries)
                    return "Error: Server connection failed. Please try again."

            except Exception as e:
                self.logger.error("Error on attempt %d: %s", attempt + 1, str(e))
                return f"Error: {str(e)}"

    def play(self):
        """Main game loop"""
        self.logger.info("Game started.")
        print("\nWelcome to AI Adventure!")
        print("Type 'quit' to exit the game.\n")

        self.start_game()

        while True:
            try:
                # Get player input
                user_input = input("\nWhat do you do? > ").strip()

                if user_input.lower() in ['quit', 'exit']:
                    self.logger.info("Player exited the game.")
                    print("\nThanks for playing!")
                    break

                if not user_input:
                    continue

                # Generate and display response
                response = self._generate_response(user_input)
                print("\n" + response + "\n")

            except KeyboardInterrupt:
                self.logger.warning("Game ended by player.")
                print("\nGame ended by player.")
                break
            except Exception as e:
                self.logger.error("An error occurred: %s", str(e))
                print(f"\nAn error occurred: {e}")
                break


def main():
    try:
        # Start the Ollama server
        with ollama_service.OllamaService() as server:
            print("Checking server health...")

            # Initial health check
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    response = requests.get('http://localhost:11434/api/tags')
                    if response.status_code == 200:
                        print("Server is healthy!")
                        break
                except requests.exceptions.ConnectionError:
                    if attempt < max_attempts - 1:
                        print(f"Server not ready, attempt {attempt + 1}/{max_attempts}")
                        time.sleep(2)
                    else:
                        raise RuntimeError("Failed to connect to server")

            # Verify model availability
            response = requests.get('http://localhost:11434/api/tags')
            models = response.json()
            print("Server is Running...")

            # Make sure your model exists
            model_name = "llama3.2:latest"  # Adjust this to match your installed model
            game = AIAdventureGame(model_name=model_name)
            game.play()

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
