import sys
import os
import os
os.environ["PATH"] = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\libnvvp;" + os.environ.get("PATH", "")
# Prune the path to avoid using the TIGRE version from the wrong project.
# This is a temporary fix; the root cause is likely a PYTHONPATH issue
# or an editable install pointing to the wrong location.
sys.path = [p for p in sys.path if os.path.join('Summerproj', 'TIGRE', 'Python') not in p]
import matplotlib
matplotlib.use('TkAgg')
import os
import datetime
from pathlib import Path
from video_processor import VideoProcessor
from geometry_config import create_geometry, create_angles
from reconstruction import reconstruct_volume
import numpy as np
from numpy2ometiff import write_ome_tiff
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from config import VIDEO_CONFIG, PHYSICAL_CONFIG, GEOMETRY_CONFIG, RECONSTRUCTION_CONFIG, VISUALIZATION_CONFIG

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
        self.cropped_path = None
        self.output_dir = None
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Create buttons
        self.load_btn = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_btn.pack(pady=5)
        
        self.crop_btn = tk.Button(self.root, text="Crop and Process", command=self.crop_video)
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
            
        # Create timestamped output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        filter_type = RECONSTRUCTION_CONFIG['filter_type']
        threshold = RECONSTRUCTION_CONFIG['stl_threshold']
        mask_status = "maskTrue" if RECONSTRUCTION_CONFIG.get('apply_circular_mask', False) else "maskFalse"
        
        # Create the new directory structure
        self.output_dir = Path("final_config") / f"{base_name}_{filter_type}_{threshold}_{mask_status}_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get output filename
        output_path = self.output_dir / f"{base_name}_cropped.mp4"
        
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
        out = cv2.VideoWriter(str(output_path), fourcc, self.cap.get(cv2.CAP_PROP_FPS), (square_size, square_size))
        
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
        self.cropped_path = str(output_path)
        
        # Close the cropping window
        self.root.destroy()

def process_video(video_path, output_dir):
    """
    Process the cropped video and perform reconstruction.
    """
    # Save configuration and video info
    config_info = {
        'Video Information': {
            'Original Video': str(video_path),
            'Cropped Video': str(Path(video_path).name),
            'Processing Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        'Reconstruction Parameters': RECONSTRUCTION_CONFIG,
        'Geometry Parameters': GEOMETRY_CONFIG,
        'Video Processing Parameters': VIDEO_CONFIG,
        'Physical Parameters': PHYSICAL_CONFIG,
        'Visualization Parameters': VISUALIZATION_CONFIG
    }
    
    # Save config to text file
    config_path = output_dir / 'config.txt'
    with open(config_path, 'w') as f:
        for section, params in config_info.items():
            f.write(f"\n{section}\n")
            f.write("=" * len(section) + "\n")
            for key, value in params.items():
                f.write(f"{key}: {value}\n")
    
    # Processing parameters
    image_size = GEOMETRY_CONFIG['image_size']
    detector_size = GEOMETRY_CONFIG['detector_size']
    
    # Channel configuration
    channel_names = ['shadow']
    
    # Process video and extract projections
    print("Processing video and extracting projections...")
    with VideoProcessor(video_path, target_size=VIDEO_CONFIG['target_size']) as processor:
        projections = processor.extract_projection_frames(
            num_frames=VIDEO_CONFIG['num_frames'], 
            output_dir=output_dir
        )
    
    # Apply a circular mask to the projections to remove artifacts from the corners
    if RECONSTRUCTION_CONFIG['apply_circular_mask']:
        print("Applying circular mask to projections...")
        detector_rows, detector_cols = projections.shape[1], projections.shape[2]
        center_y, center_x = detector_rows // 2, detector_cols // 2
        radius = min(center_x, center_y)
        
        y, x = np.ogrid[:detector_rows, :detector_cols]
        mask = (x - center_x)**2 + (y - center_y)**2 > radius**2
        
        # The background should correspond to 0 attenuation.
        # We set the area outside the circle to 0.
        projections[:, mask] = 0
    
    # Create geometry and angles for reconstruction
    print("Setting up reconstruction geometry...")
    geo = create_geometry(image_size=image_size, detector_size=detector_size)
    geo.accuracy = 0.5  # Add accuracy attribute to satisfy TIGRE's internal print command
    angles = create_angles()
    
    # Perform tomographic reconstruction
    print("Performing volume reconstruction...")
    reconstructed = reconstruct_volume(
        projections=projections,
        geo=geo,
        angles=angles,
        output_dir=output_dir
    )
    
    # Prepare data for OME-TIFF writing
    print("Preparing data for OME-TIFF export...")
    Ddata = np.expand_dims(np.asarray(reconstructed), axis=1)
    
    # Create model directory if it doesn't exist
    model_dir = output_dir / "model"
    model_dir.mkdir(exist_ok=True)
    
    # Define OME-TIFF output path
    output_filename = model_dir / 'reconstructed_volume.ome.tiff'
    
    # Write the OME-TIFF file
    print("Writing OME-TIFF file...")
    write_ome_tiff(
        data=Ddata,
        output_filename=str(output_filename),
        channel_names=channel_names,
        pixel_size_x=PHYSICAL_CONFIG['pixel_size_x'],
        pixel_size_y=PHYSICAL_CONFIG['pixel_size_y'],
        physical_size_z=PHYSICAL_CONFIG['physical_size_z'],
        Unit=PHYSICAL_CONFIG['unit'],
        imagej=False,
        create_pyramid=True,
        compression='zlib'
    )
    
    print(f"Processing complete. All results saved in: {output_dir}")

def main():
    """
    Main function that handles the complete pipeline from cropping to reconstruction.
    """
    # Create and run the cropper
    root = tk.Tk()
    cropper = VideoCropper(root)
    root.mainloop()
    
    # If a video was cropped, process it
    if cropper.cropped_path and cropper.output_dir:
        process_video(cropper.cropped_path, cropper.output_dir)
    else:
        print("No video was cropped. Exiting...")

if __name__ == "__main__":
    main()