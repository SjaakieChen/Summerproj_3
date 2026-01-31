import tigre
import numpy as np
import tigre.algorithms as algs
from pathlib import Path
import datetime
import os
import matplotlib.pyplot as plt
from stl import mesh
from skimage import measure
from config import RECONSTRUCTION_CONFIG, VISUALIZATION_CONFIG

def reconstruct_volume(projections, geo, angles, output_dir=None, stl_threshold=None):
    """
    Perform FDK reconstruction on the projection data.
    
    Args:
        projections (numpy.ndarray): Projection data
        geo (tigre.geometry): Geometry configuration
        angles (numpy.ndarray): Projection angles
        output_dir (str, optional): Directory to save results
        stl_threshold (float, optional): Threshold value for STL conversion (0-1)
        
    Returns:
        numpy.ndarray: Reconstructed volume
    """
    # Use config threshold if none provided
    if stl_threshold is None:
        stl_threshold = RECONSTRUCTION_CONFIG['stl_threshold']
    
    # Optionally apply a circular mask
    if RECONSTRUCTION_CONFIG.get('apply_circular_mask', False):
        h, w = projections.shape[1], projections.shape[2]
        center_x, center_y = w // 2, h // 2
        radius = min(center_x, center_y)
        
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        mask = dist_from_center <= radius
        
        projections = projections * mask[np.newaxis, :, :]
    
    # Perform FDK reconstruction
    reconstructed = algs.fdk(projections, geo, angles, filter=RECONSTRUCTION_CONFIG['filter_type'])
    
    # Create timestamped output directory if specified
    if output_dir is not None:
        # Create model directory
        model_dir = Path(output_dir) / "model"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as numpy array
        np.save(model_dir / "reconstruction.npy", reconstructed)
        
        # Save visualization slices
        save_visualization_slices(reconstructed, model_dir)
        
        # Save as STL
        save_stl(reconstructed, model_dir, threshold=stl_threshold)
        
    return reconstructed

def save_visualization_slices(volume, output_path):
    """
    Save visualization slices of the reconstructed volume.
    
    Args:
        volume (numpy.ndarray): Reconstructed volume
        output_path (Path): Path to save visualizations (parent directory)
    """
    # Plot and save slices
    plt.figure(figsize=(15, 5))
    
    # YZ Slice
    plt.subplot(131)
    slice_yz = volume[volume.shape[0]//2, :, :]
    plt.imshow(slice_yz, cmap='gray')
    plt.title('YZ Slice')
    plt.colorbar()
    
    # XZ Slice
    plt.subplot(132)
    slice_xz = volume[:, volume.shape[1]//2, :]
    plt.imshow(slice_xz, cmap='gray')
    plt.title('XZ Slice')
    plt.colorbar()
    
    # XY Slice
    plt.subplot(133)
    slice_xy = volume[:, :, volume.shape[2]//2]
    plt.imshow(slice_xy, cmap='gray')
    plt.title('XY Slice')
    plt.colorbar()
    
    plt.tight_layout()
    # Save in parent directory
    plt.savefig(output_path.parent / "middle_slices.png")
    plt.close()

def save_stl(volume, output_path, threshold=0.5):
    """
    Convert volume to STL file using marching cubes.
    
    Args:
        volume (numpy.ndarray): Reconstructed volume
        output_path (Path): Path to save STL file
        threshold (float): Threshold value for surface extraction (0-1)
    """
    # Normalize volume to 0-1 range
    vmin, vmax = volume.min(), volume.max()
    normalized_volume = (volume - vmin) / (vmax - vmin)

    # Remove 3D cylindrical mask: use the full normalized volume
    # Apply threshold
    binary_volume = normalized_volume > threshold
    
    # Generate mesh using marching cubes
    vertices, faces, normals, values = measure.marching_cubes(binary_volume, level=0.5)
    
    # Create the mesh
    surface_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            surface_mesh.vectors[i][j] = vertices[face[j]]
    
    # Save the STL file
    stl_path = output_path / "model.stl"
    surface_mesh.save(str(stl_path)) 