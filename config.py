"""
Configuration parameters for tomographic reconstruction.
"""

# Reconstruction parameters
RECONSTRUCTION_CONFIG = {
    # Filter type for FDK reconstruction.
    # Available filters in TIGRE: 'ram_lak', 'shepp_logan', 'cosine', 'hamming', 'hann'
    'filter_type': 'shepp_logan',  # Using Shepp-Logan to reduce ring artifacts
    'stl_threshold': 0.4,      # Threshold for STL conversion (0-1) 0.5
    'apply_circular_mask': True #Apply a circular mask to projections
}

# Geometry parameters
GEOMETRY_CONFIG = {
    'image_size': 200,         # Size of the reconstructed volume (cubic) #150
    'detector_size': 200,      # Size of the detector (square) #150
    'DSD': 628,               # Distance Source Screen (mm) #398
    'DSO': 456,               # Distance Source Object (mm) #278
    'pixel_size': 1.0,        # Detector pixel size (mm)
}

# Video processing parameters
VIDEO_CONFIG = {
    'num_frames': 800,        # Number of frames to extract
    'target_size': (GEOMETRY_CONFIG['image_size'], GEOMETRY_CONFIG['image_size'])  # Derived from image_size
}

# Physical dimensions (in microns)
PHYSICAL_CONFIG = {
    'pixel_size_x': 1000,
    'pixel_size_y': 1000,
    'physical_size_z': 1000,
    'unit': 'um'
}

# Visualization parameters
VISUALIZATION_CONFIG = {
    'auto_contrast': True,           # Automatically adjust contrast of saved slices
    'contrast_percentiles': (1, 99)  # Lower and upper percentiles for contrast stretching
} 