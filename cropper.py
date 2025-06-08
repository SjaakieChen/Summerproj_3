import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import numpy as np

class VideoCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cropper")
        
        # Initialize variables
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.line_start = None
        self.line_end = None
        self.is_drawing = False
        self.scale = 1.0  # Store the scale factor
        self.x_offset = 0
        self.y_offset = 0
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Create buttons
        self.load_btn = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_btn.pack(pady=5)
        
        self.crop_btn = tk.Button(self.root, text="Crop Video", command=self.crop_video)
        self.crop_btn.pack(pady=5)
        self.crop_btn.config(state='disabled')
        
        # Create canvas for video display
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(pady=5)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
    def load_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("MOV files", "*.mov"), ("All files", "*.*")]
        )
        
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.display_frame()
                self.crop_btn.config(state='normal')
            else:
                messagebox.showerror("Error", "Could not read video file")
                
    def display_frame(self):
        if self.current_frame is not None:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            
            # Calculate scale to fit frame in canvas while maintaining aspect ratio
            height, width = frame_rgb.shape[:2]
            self.scale = min(800/width, 600/height)
            new_width = int(width * self.scale)
            new_height = int(height * self.scale)
            
            # Calculate offsets to center the frame
            self.x_offset = (800 - new_width) // 2
            self.y_offset = (600 - new_height) // 2
            
            # Resize frame
            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(400, 300, image=self.photo)
            
            # Draw line if exists
            if self.line_start and self.line_end:
                # Draw the horizontal line
                self.canvas.create_line(
                    self.line_start[0], self.line_start[1],
                    self.line_end[0], self.line_end[1],
                    fill="red", width=2
                )
                
                # Calculate square dimensions based on line length
                line_length = abs(self.line_end[0] - self.line_start[0])
                center_x = (self.line_start[0] + self.line_end[0]) // 2
                center_y = self.line_start[1]
                
                # Draw the square preview
                square_size = line_length
                x1 = center_x - square_size // 2
                y1 = center_y - square_size // 2
                x2 = center_x + square_size // 2
                y2 = center_y + square_size // 2
                
                # Draw semi-transparent overlay
                self.canvas.create_rectangle(0, 0, 800, 600, fill="gray", stipple="gray50", outline="")
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="", outline="red", width=2
                )
    
    def on_mouse_down(self, event):
        self.is_drawing = True
        self.line_start = (event.x, event.y)
        self.line_end = (event.x, event.y)
        
    def on_mouse_move(self, event):
        if self.is_drawing:
            # Only update x coordinate to keep line horizontal
            self.line_end = (event.x, self.line_start[1])
            self.display_frame()
            
    def on_mouse_up(self, event):
        self.is_drawing = False
        self.display_frame()
        
    def crop_video(self):
        if not self.video_path or not self.line_start or not self.line_end:
            messagebox.showerror("Error", "Please load a video and draw a horizontal line")
            return
            
        # Create output directory if it doesn't exist
        output_dir = "cropped_video_data"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get output filename
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_cropped.mp4")
        
        # Calculate square dimensions based on line length
        line_length = abs(self.line_end[0] - self.line_start[0])
        center_x = (self.line_start[0] + self.line_end[0]) // 2
        center_y = self.line_start[1]
        
        # Convert coordinates to original video coordinates
        x_center = int((center_x - self.x_offset) / self.scale)
        y_center = int((center_y - self.y_offset) / self.scale)
        square_size = int(line_length / self.scale)
        
        # Calculate final square coordinates
        x1 = x_center - square_size // 2
        y1 = y_center - square_size // 2
        x2 = x1 + square_size
        y2 = y1 + square_size
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.cap.get(cv2.CAP_PROP_FPS), (square_size, square_size))
        
        # Reset video capture
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Process video
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Crop frame to square
            cropped_frame = frame[y1:y2, x1:x2]
            out.write(cropped_frame)
            
        # Release resources
        out.release()
        messagebox.showinfo("Success", f"Cropped video saved to {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCropper(root)
    root.mainloop()
