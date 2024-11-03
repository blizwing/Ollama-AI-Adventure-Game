from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_model_with_quantization(model_path):
    # Load the model
    model = AutoModelForCausalLM.from_pretrained(model_path, low_cpu_mem_usage=True)
    # model.gradient_checkpointing_enable()  # Enable gradient checkpointing if applicable
    #
    # # Apply dynamic quantization
    # model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    return model, tokenizer

# Load the model and tokenizer once, when the program starts
def load_model():
    model_path = "E:/Programming/Project Playground/Python Projects/Discount AI Dungeon/pythonProject/python/files/model/dolphin-2.9-llama3-8b"  # replace with your safetensor model path
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    return model, tokenizer

model, tokenizer = load_model()  # Load once

# Function to generate response without reloading the model
def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(inputs['input_ids'], max_length=200)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# Main game loop
def play_game():
    print("Welcome to AI Dungeon!")
    context = "You find yourself in a dark forest..."
    while True:
        user_input = input(">>> ")
        context += f" {user_input}"
        response = generate_response(context)
        print(response)
        # Adjust context or exit condition as needed
        if user_input.lower() in ["quit", "exit"]:
            break

# Run the game
play_game()
