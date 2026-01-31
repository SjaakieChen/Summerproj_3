import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from config import VISUALIZATION_CONFIG

class VideoProcessor:
    def __init__(self, video_path, target_size=(512, 512)):
        self.video_path = Path(video_path)
        self.target_size = target_size
        self.cap = None
        
    def __enter__(self):
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_path}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap is not None:
            self.cap.release()
            
    def process_frame(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Rotate 90 degrees clockwise
        rotated = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
        
        # Resize
        resized = cv2.resize(rotated, self.target_size)
        
        # Log inversion
        log_inverted = -np.log((resized.astype(float) + 1) / 256.0)
        
        return log_inverted
        
    def extract_projection_frames(self, num_frames=200, output_dir=None):
        frames = []
        first_frame = None
        first_original = None
        
        for i in range(num_frames):
            ret, frame = self.cap.read()
            if not ret:
                break
                
            if i == 0:
                first_original = frame.copy()
                
            processed_frame = self.process_frame(frame)
            frames.append(processed_frame)
            
            # Save visualization of first frame
            if i == 0 and output_dir is not None:
                first_frame = processed_frame
                # The output_dir for projections is now the main output directory
                save_first_frame_comparison(first_frame, first_original, output_dir)
            
        return np.array(frames)

def save_first_frame_comparison(frame, original_frame, output_dir):
    """
    Save visualization of the first processed frame compared to the original.
    
    Args:
        frame (numpy.ndarray): The processed frame
        original_frame (numpy.ndarray): The original frame before processing
        output_dir (Path): Directory to save the visualization
    """
    plt.figure(figsize=(10, 5))
    
    # Plot original frame
    plt.subplot(121)
    plt.imshow(cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB))
    plt.title('Original Cropped Frame')
    plt.axis('off')
    
    # Plot processed frame
    plt.subplot(122)
    plt.imshow(frame, cmap='gray')
    plt.colorbar()
    plt.title('Processed Frame for Reconstruction')
    plt.axis('off')
    
    plt.tight_layout()
    # Save the figure in the main output directory
    output_path = Path(output_dir)
    plt.savefig(output_path / "first_frame_comparison.png", dpi=150)
    plt.close() 