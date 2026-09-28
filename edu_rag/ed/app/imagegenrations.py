import io
import torch
from diffusers import StableDiffusionPipeline

# Initialize the Stable Diffusion pipeline
print("Loading Stable Diffusion pipeline...")
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2",
        torch_dtype=torch.float16,
        revision="fp16",  # Ensure compatibility with fp16 weights
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe.to(device)  # Move the model to GPU (CUDA)
    print(f"Using device: {device}")

    # Enable memory optimization for low-VRAM GPUs
    if device == "cuda":
        pipe.enable_attention_slicing()  # Reduces memory usage by splitting attention computation
        pipe.enable_sequential_cpu_offload()  # Offloads layers to CPU as needed
except Exception as e:
    print(f"Error loading the pipeline: {e}")
    raise e

def generate_image_from_prompt(prompt):
    """Generate an image based on the prompt using Stable Diffusion with optimizations for 4GB GPU."""
    print(f"Generating image for prompt: {prompt}")

    # Refine the prompt to make it more detailed
    refined_prompt = f"A highly detailed, realistic single image of {prompt} in 4k"
   
    # Adjust parameters for better quality
    guidance_scale = 7.5  # Moderate scale for adherence to the prompt
    height, width = 512, 512  # Resolution for 4GB GPUs

    try:
        # Ensure inference mode with torch.no_grad()
        with torch.no_grad():
            # Generate image with the pipeline
            output = pipe(
                refined_prompt,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                num_inference_steps=50,  # Number of steps for higher-quality output
            )
            image = output.images[0]

        print(f"Successfully generated image for prompt: {refined_prompt}")

        # Convert the image to a byte stream for further use
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Free up GPU memory
        torch.cuda.empty_cache()
        return img_byte_arr.read()

    except Exception as e:
        print(f"Error generating image: {e}")
        return None
