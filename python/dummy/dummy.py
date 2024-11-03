import requests
import json


# Define the system prompt for AI Dungeon
SYSTEM_PROMPT = (
    "You are the Game Master of a text-based adventure game similar to AI Dungeon. "
    "Your role is to guide the player through an open-ended, interactive story by describing vivid environments, "
    "interesting characters, and challenges they encounter. The story should be immersive, creative, and flexible, "
    "allowing the player to make choices, ask questions, and explore freely.\n\n"
    "Instructions:\n"
    "1. Environment and Description:\n"
    "- Provide detailed descriptions of each scene, incorporating sensory details (sight, sound, smell, touch, taste) "
    "to create an immersive experience.\n"
    "2. Character Interaction:\n"
    "- Assume the persona of non-player characters (NPCs) when relevant, responding naturally to the player’s actions "
    "or questions.\n"
    "3. Open-Ended Choices:\n"
    "- Respond to the player’s actions by generating narrative responses that are consistent with the storyline and setting.\n"
    "4. Guiding the Story:\n"
    "- Progress the story based on the player’s input, introducing new elements, conflicts, and mysteries to keep the experience engaging.\n"
    "5. Handling Unknowns:\n"
    "- If the player asks about something not explicitly defined, invent details that fit naturally within the story world.\n"
    "6. Tone and Language:\n"
    "- Use language that suits the fantasy or adventure theme (or any genre the player has chosen).\n"
)


def query_ollama(prompt):
    # Query the Ollama model with the prompt
    url = "http://localhost:11434/api/generate"  # Adjust if needed for your local setup
    payload = {
        "model": "llama3.2:latest",
        "prompt": prompt,
        "max_tokens": 150,  # Limit token usage for faster responses
        "stream": True,  # Enable streaming
        "raw": True
    }
    headers = {"Content-Type": "application/json"}

    # Initialize the response generator
    response = requests.post(url, json=payload, headers=headers, stream=True)

    # Check if the response is successful
    if response.status_code == 200:
        generated_text = ""
        # Stream through the response
        for chunk in response.iter_content(chunk_size=1024):
            # Decode the bytes response content to a string
            response_text = chunk.decode("utf-8")
            # Parse the JSON data (it might be in chunks)
            try:
                json_data = json.loads(response_text)
                # Extract the response text from the "response" field
                generated_text += json_data.get("response", "")
            except json.JSONDecodeError:
                print("Failed to parse JSON chunk.")
        return generated_text
    else:
        print("Error querying model:", response.text)
        return "Oops! Something went wrong."


def ai_dungeon():
    print("Welcome to your AI Dungeon!")
    context = "You are an adventurer in a mysterious land."  # Initial story setup

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the game. Goodbye!")
            break

        # Combine the system prompt, context, and user input to keep a flowing story
        prompt = f"{SYSTEM_PROMPT}\n{context}\nPlayer: {user_input}\nGame Master:"
        response = query_ollama(prompt)

        print("Game Master:", response)

        # Update context with recent input and output to maintain continuity
        context += f"\nPlayer: {user_input}\nGame Master: {response}"


# Start the game
ai_dungeon()
