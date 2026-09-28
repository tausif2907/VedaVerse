# frames.py
import cv2
import os

def capture_frame(frame_index):
    """Capture a single frame and save it as an image."""
    cap = cv2.VideoCapture(0)  # Start webcam capture
    ret, frame = cap.read()
    if ret:
        # Define the output folder and file path
        folder_path = 'Folder_with_Frames'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Create the folder if it doesn't exist

        # Save the frame as a PNG image
        cv2.imwrite(os.path.join(folder_path, f'frame{frame_index}.png'), frame)
        print(f"Frame {frame_index} saved!")
    else:
        print("Failed to capture frame.")
    
    cap.release()  # Release the webcam
