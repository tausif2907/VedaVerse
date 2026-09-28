# pdf.py
from PIL import Image
import os

def create_pdf_from_images(folder_path):
    """Convert images in the specified folder to a single PDF."""
    output_pdf_path = os.path.join(folder_path, "output.pdf")
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()  # Sort images by name if needed

    # Check if there are images in the folder
    if not image_files:
        print("No images found in the specified folder.")
    else:
        # Load images and convert them to PDF
        image_list = [Image.open(os.path.join(folder_path, img)).convert('RGB') for img in image_files]
        image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])
        print(f"PDF saved as {output_pdf_path}")

        # Clear the folder after saving the PDF
        for img in image_files:
            os.remove(os.path.join(folder_path, img))  # Delete each image file
