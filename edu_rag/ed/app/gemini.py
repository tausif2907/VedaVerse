import google.generativeai as genai
import os
import base64
import os
genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
def prep_image(image_path):
    # Upload the file and print a confirmation.
    sample_file = genai.upload_file(path=image_path,
                                display_name="Diagram")
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
    return sample_file
def extract_text_from_image(image_path, prompt):
    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    # Prompt the model with text and the previously uploaded image.
    response = model.generate_content([image_path, prompt])
    return response.text
# sample_file = prep_image('sketch_screenshot.png') 
# text = extract_text_from_image(sample_file, "Extract  equations and solve all of it, its an handwritten equation it can be maths,physics and chemistry  ")
# if text:
#     print("Extracted Text:")
#     print(text)
# else:
#     print("Failed to extract text from the image.")