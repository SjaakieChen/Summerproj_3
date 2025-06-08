import tigre
import numpy as np
from config import GEOMETRY_CONFIG

def create_geometry(image_size=None, detector_size=None):
    """
    Create TIGRE geometry configuration for cone beam tomography.
    
    Args:
        image_size (int, optional): Size of the reconstructed volume (cubic)
        detector_size (int, optional): Size of the detector (square)
        
    Returns:
        tigre.geometry: Configured geometry object
    """
    # Use config values if none provided
    if image_size is None:
        image_size = GEOMETRY_CONFIG['image_size']
    if detector_size is None:
        detector_size = GEOMETRY_CONFIG['detector_size']
    
    geo = tigre.geometry()
    
    # Distances (in mm)
    geo.DSD = GEOMETRY_CONFIG['DSD']  # Distance Source Detector
    geo.DSO = GEOMETRY_CONFIG['DSO']  # Distance Source Origin
    
    # Image parameters
    geo.nVoxel = np.array([image_size, image_size, image_size])
    geo.sVoxel = np.array([image_size, image_size, image_size])
    geo.dVoxel = geo.sVoxel / geo.nVoxel
    
    # Detector parameters
    geo.nDetector = np.array([detector_size, detector_size])
    geo.dDetector = np.array([GEOMETRY_CONFIG['pixel_size'], GEOMETRY_CONFIG['pixel_size']])
    geo.sDetector = geo.nDetector * geo.dDetector
    
    # Offsets
    geo.offOrigin = np.array([0, 0, 0])
    geo.offDetector = np.array([0, 0])
    
    # Mode
    geo.mode = "cone"
    
    return geo

def create_angles(num_angles=None):
    """
    Create projection angles for 360-degree rotation.
    
    Args:
        num_angles (int, optional): Number of projection angles
        
    Returns:
        numpy.ndarray: Array of angles in radians
    """
    if num_angles is None:
        from config import VIDEO_CONFIG
        num_angles = VIDEO_CONFIG['num_frames']
    
    return np.linspace(0, 2 * np.pi, num_angles) 