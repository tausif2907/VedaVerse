import tkinter as tk
from tkinter import colorchooser
from PIL import ImageGrab
import requests
import os

class SketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sketchbook App")
        self.root.geometry("1000x800")
        
        # Initialize the color and canvas setup
        self.color = "black"
        self.canvas = tk.Canvas(root, bg="white", width=900, height=600)
        self.canvas.pack()

        # Add buttons for color, clear, and save
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        color_button = tk.Button(button_frame, text="Pick Color", command=self.choose_color)
        color_button.grid(row=0, column=0, padx=10)

        clear_button = tk.Button(button_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_button.grid(row=0, column=1, padx=10)

        save_button = tk.Button(button_frame, text="Check this", command=self.save_screenshot)
        save_button.grid(row=0, column=2, padx=10)

        # Initialize drawing state
        self.last_x, self.last_y = None, None
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset_position)

    def choose_color(self):
        """Open a color chooser and set the selected color as the drawing color."""
        color_code = colorchooser.askcolor(title="Choose drawing color")
        if color_code:
            self.color = color_code[1]

    def draw(self, event):
        """Draw on the canvas when the mouse is dragged."""
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.color, width=3)
        self.last_x, self.last_y = event.x, event.y

    def reset_position(self, event):
        """Reset the last position to stop drawing lines when the mouse is released."""
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        """Clear the entire canvas."""
        self.canvas.delete("all")

    def save_screenshot(self):
        """Capture the canvas area, save it as a PNG image, and send it to the Django server."""
        # Capture and save the screenshot
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        image_path = "sketch_screenshot.png"
        image = ImageGrab.grab((x, y, x1, y1))
        image.save(image_path)
        print("Screenshot saved as sketch_screenshot.png")

        # Send the screenshot to the Django server
        try:
            with open(image_path, "rb") as img:
                response = requests.post("http://127.0.0.1:8000/upload_screenshot/", files={"screenshot": img})
            if response.ok:
                print("Screenshot sent to the server successfully.")
            else:
                print("Failed to send screenshot to the server.")
        except Exception as e:
            print(f"Error sending screenshot to the server: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SketchApp(root)
    root.mainloop()
