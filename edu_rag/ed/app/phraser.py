import re
import torch
from transformers import pipeline

# Suppress serialization warnings (optional if confident about data safety)
import warnings
warnings.filterwarnings("ignore", message="Defaulting to unsafe serialization.*")

# Initialize rephrase pipeline
print("Initializing rephrase pipeline...")
device = 0 if torch.cuda.is_available() else -1

text_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    device=device,
    torch_dtype=torch.float32  # Ensure proper dtype handling
)
print(f"Pipeline initialized on device: {'GPU' if device == 0 else 'CPU'}")

def rephrase_text(text):
    print(f"Rephrasing text: {text}")
    prompt = f"Rephrase: {text}"
    generated = text_pipeline(prompt, max_length=len(text) + 50, num_return_sequences=1)
    rephrased_text = generated[0]["generated_text"].replace(prompt, "").strip()
    print(f"Rephrased text: {rephrased_text}")
    return rephrased_text

def ai_summarize(text):
    print(f"Summarizing text: {text}")
    prompt = f"Summarize: {text}"
    generated = text_pipeline(prompt, max_length=150, num_return_sequences=1)
    summarized_text = generated[0]["generated_text"].replace(prompt, "").strip()
    print(f"Summarized text: {summarized_text}")
    return summarized_text

def ai_paraphrase(text):
    print(f"Paraphrasing text: {text}")
    prompt = f"Paraphrase: {text}"
    generated = text_pipeline(prompt, max_length=150, num_return_sequences=1)
    paraphrased_text = generated[0]["generated_text"].replace(prompt, "").strip()
    print(f"Paraphrased text: {paraphrased_text}")
    return paraphrased_text

def generate_new_content(topic):
    print(f"Generating new content about: {topic}")
    prompt = f"Write a detailed article about {topic}."
    generated = text_pipeline(prompt, max_length=300, num_return_sequences=1, do_sample=True, temperature=0.7)
    generated_content = generated[0]["generated_text"].replace(prompt, "").strip()
    print(f"Generated content: {generated_content}")
    return generated_content

def parse_instruction(instruction):
    print(f"Parsing user instruction: {instruction}")
   
    # Define patterns for different instructions
    patterns = {
        "rephrase": r"rephrase",
        "replace_image": r"replace (the )?(?P<target>\w+) (image )?with (?P<replacement>[\w\s]+)",
        "summarize": r"summarize",
        "paraphrase": r"paraphrase",
        "generate": r"generate (new )?content (about|for) (?P<topic>.+)"
    }
   
    # Check for each pattern and return the corresponding action
    for action, pattern in patterns.items():
        match = re.search(pattern, instruction)
        if match:
            if action == "replace_image":
                target = match.group("target").strip()
                replacement = match.group("replacement").strip()
                return action, target, replacement
            elif action == "generate":
                topic = match.group("topic").strip()
                return action, topic, None
            return action, None, None
   
    return None, None, None
