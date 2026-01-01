"""Video conversion utilities for automatic MP4 conversion on upload."""
import os
import subprocess
import shutil
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile


def convert_to_mp4(input_path: str, output_path: str) -> bool:
    """
    Convert video file to MP4 format using ffmpeg.
    
    Args:
        input_path: Full path to input video file
        output_path: Full path to output MP4 file
    
    Returns:
        True if conversion successful, False otherwise
    """
    # Check if ffmpeg is available
    if not shutil.which('ffmpeg'):
        print("WARNING: ffmpeg not found. Cannot convert video to MP4.")
        return False
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Run ffmpeg conversion
        # -c:v libx264: H.264 video codec (most compatible)
        # -preset fast: faster encoding (still good quality)
        # -crf 23: quality level (lower = better, 23 is good balance)
        # -c:a aac: AAC audio codec (widely supported)
        # -b:a 128k: audio bitrate
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # Overwrite output file
            output_path
        ]
        
        # Run conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            print(f"✓ Successfully converted to MP4: {output_path}")
            return True
        else:
            print(f"✗ FFmpeg conversion failed: {result.stderr.decode()}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"✗ Video conversion timeout: {input_path}")
        return False
    except Exception as e:
        print(f"✗ Error converting video: {str(e)}")
        return False


def should_convert_to_mp4(filename: str) -> bool:
    """
    Check if file should be converted to MP4.
    
    Args:
        filename: Name of the uploaded file
    
    Returns:
        True if file is not already MP4 and is a video format that can be converted
    """
    # List of formats that should be converted to MP4
    convertible_formats = ['.mov', '.mkv', '.avi', '.webm', '.flv', '.wmv', '.m4v', '.ts', '.mts']
    
    filename_lower = filename.lower()
    
    # Already MP4
    if filename_lower.endswith('.mp4'):
        return False
    
    # Check if it's a convertible format
    return any(filename_lower.endswith(fmt) for fmt in convertible_formats)


def get_mp4_filename(original_filename: str) -> str:
    """
    Get MP4 filename from original filename.
    
    Args:
        original_filename: Original uploaded filename (e.g., 'video.mov')
    
    Returns:
        MP4 filename (e.g., 'video.mp4')
    """
    # Remove extension and add .mp4
    name_without_ext = os.path.splitext(original_filename)[0]
    return f"{name_without_ext}.mp4"
