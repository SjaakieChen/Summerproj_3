# Micro-CT Tomographic Reconstruction Pipeline

A micro-CT / tomographic reconstruction pipeline that reconstructs 3D volumes from video of a rotating object. Extracts projection frames from video, performs FDK (Feldkamp-Davis-Kress) reconstruction using TIGRE, and exports results in multiple formats.

## Features

- **GUI video cropper** – Interactive tool to define the region of interest (ROI) by drawing a horizontal line
- **Projection extraction** – Converts video frames to log-inverted projection data
- **FDK reconstruction** – GPU-accelerated cone-beam CT reconstruction via TIGRE
- **Multiple export formats** – OME-TIFF, NumPy, STL (3D printable mesh)

## Prerequisites

- Python 3.9+
- CUDA 11.8 (for TIGRE GPU acceleration)
- NVIDIA GPU

## Installation

> **TIGRE installation:** `pip install tigre` may not work reliably. Install TIGRE first using the official instructions:
>
> https://github.com/CERN/TIGRE/blob/master/Frontispiece/python_installation.md
>
> Then run `pip install -r requirements.txt` for the remaining dependencies.

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application: `python main.py`
2. Click **Load Video** and select a `.mov` file
3. Draw a horizontal line across the object to define the square ROI
4. Click **Crop and Process**
5. The pipeline will crop the video, extract projections, run FDK reconstruction, and save outputs to a timestamped folder in `final_config/`

## Configuration

All parameters are defined in [`config.py`](config.py):

| Section | Key parameters |
|---------|----------------|
| **Reconstruction** | `filter_type` (ram_lak, shepp_logan, hamming, etc.), `stl_threshold`, `apply_circular_mask` |
| **Geometry** | `image_size`, `detector_size`, `DSD`, `DSO`, `pixel_size` |
| **Video** | `num_frames`, `target_size` |
| **Physical** | `pixel_size_x`, `pixel_size_y`, `physical_size_z`, `unit` |

## Project Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point; GUI cropper and reconstruction pipeline orchestration |
| `config.py` | All configuration parameters |
| `reconstruction.py` | FDK reconstruction, visualization slices, STL export |
| `video_processor.py` | Video frame extraction and projection preprocessing |
| `geometry_config.py` | TIGRE geometry and projection angles |
| `cropper.py` | Standalone video cropper (alternative to main.py cropper) |

## Output

For each run, a timestamped directory is created in `final_config/` containing:

- `reconstructed_volume.ome.tiff` – OME-TIFF volume (in `model/`)
- `model.stl` – 3D mesh for printing
- `middle_slices.png` – YZ, XZ, XY slice visualizations
- `first_frame_comparison.png` – Original vs processed frame
- `config.txt` – Full parameter record
