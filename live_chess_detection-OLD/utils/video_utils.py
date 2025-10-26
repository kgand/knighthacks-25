"""Video processing utilities."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional


class VideoReader:
    """Utility for reading video frames."""
    
    def __init__(self, video_path: str):
        self.path = Path(video_path)
        self.cap = cv2.VideoCapture(str(video_path))
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def read_frame(self, frame_idx: int) -> Optional[np.ndarray]:
        """Read specific frame by index."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def __iter__(self):
        """Iterate through all frames."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()


def extract_frames(
    video_path: str,
    fps: float = 1.0,
    start_time: float = 0.0,
    end_time: Optional[float] = None
) -> List[np.ndarray]:
    """
    Extract frames from video at specified FPS.
    
    Args:
        video_path: Path to video file
        fps: Frames per second to extract
        start_time: Start time in seconds
        end_time: End time in seconds (None = end of video)
        
    Returns:
        List of frames
    """
    reader = VideoReader(video_path)
    original_fps = reader.fps
    
    frame_interval = int(original_fps / fps)
    start_frame = int(start_time * original_fps)
    end_frame = int(end_time * original_fps) if end_time else reader.total_frames
    
    frames = []
    for i in range(start_frame, end_frame, frame_interval):
        frame = reader.read_frame(i)
        if frame is not None:
            frames.append(frame)
    
    return frames


def save_video(
    frames: List[np.ndarray],
    output_path: str,
    fps: float = 24.0,
    codec: str = 'MJPG'
):
    """
    Save frames as video.
    
    Args:
        frames: List of frames to save
        output_path: Output video path
        fps: Frames per second
        codec: Video codec (MJPG, mp4v, etc.)
    """
    if not frames:
        return
    
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*codec)
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    for frame in frames:
        writer.write(frame)
    
    writer.release()
