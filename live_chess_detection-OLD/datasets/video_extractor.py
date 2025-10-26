"""
YouTube video frame extraction for dataset generation.

Extracts chess positions from tournament video footage.
Handles downloading, frame extraction, and board cropping.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    from pytube import YouTube
except ImportError:
    print("Warning: pytube not installed. YouTube download disabled.")


@dataclass
class VideoConfig:
    """Configuration for video extraction."""
    video_id: str
    title: str
    time_range: Tuple[str, str]  # (start, end) in "HH:MM:SS" format
    fps: float
    board_corners: List[int]  # [top, bottom, left, right]
    initial_position: Optional[str] = None


class VideoFrameExtractor:
    """
    Extract frames from video with board cropping.
    
    Handles perspective correction and frame sampling.
    """
    
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        self.cap = cv2.VideoCapture(str(video_path))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def time_to_frame(self, time_str: str) -> int:
        """Convert HH:MM:SS to frame number."""
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
        elif len(parts) == 2:
            h = 0
            m, s = map(int, parts)
        else:
            raise ValueError(f"Invalid time format: {time_str}")
        
        total_seconds = h * 3600 + m * 60 + s
        return int(total_seconds * self.fps)
    
    def extract_frames(
        self,
        start_time: str,
        end_time: str,
        sample_fps: float,
        board_corners: List[int]
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Extract and crop frames from video.
        
        Args:
            start_time: Start time (HH:MM:SS)
            end_time: End time (HH:MM:SS)
            sample_fps: Frames per second to extract
            board_corners: [top, bottom, left, right] crop region
            
        Returns:
            List of (full_frame, cropped_board) tuples
        """
        start_frame = self.time_to_frame(start_time)
        end_frame = self.time_to_frame(end_time)
        
        frame_interval = int(self.fps / sample_fps)
        
        frames = []
        
        for frame_idx in range(start_frame, end_frame, frame_interval):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            # Crop board region
            top, bottom, left, right = board_corners
            board_crop = frame[top:bottom, left:right].copy()
            
            frames.append((frame, board_crop))
        
        return frames
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()


class YouTubeChessExtractor:
    """
    Download and extract chess positions from YouTube videos.
    
    Handles video download, frame extraction, and annotation.
    """
    
    def __init__(self, output_dir: str = "data/youtube_extracted"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, video_id: str) -> Optional[str]:
        """
        Download YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Path to downloaded video or None if failed
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(url)
            
            # Get highest resolution video
            stream = yt.streams.filter(
                progressive=True,
                file_extension='mp4'
            ).order_by('resolution').desc().first()
            
            if stream is None:
                print(f"No suitable stream found for {video_id}")
                return None
            
            # Download
            output_path = self.output_dir / "videos"
            output_path.mkdir(exist_ok=True)
            
            print(f"Downloading: {yt.title}")
            video_path = stream.download(
                output_path=str(output_path),
                filename=f"{video_id}.mp4"
            )
            
            return video_path
            
        except Exception as e:
            print(f"Error downloading {video_id}: {e}")
            return None
    
    def process_video(self, config: VideoConfig, download: bool = True):
        """
        Process video according to configuration.
        
        Downloads (if needed), extracts frames, and saves board crops.
        """
        # Download if needed
        video_path = self.output_dir / "videos" / f"{config.video_id}.mp4"
        
        if not video_path.exists() and download:
            downloaded_path = self.download_video(config.video_id)
            if downloaded_path is None:
                print(f"Failed to download {config.video_id}")
                return
            video_path = Path(downloaded_path)
        
        if not video_path.exists():
            print(f"Video not found: {video_path}")
            return
        
        # Extract frames
        print(f"Extracting frames from {config.title}...")
        extractor = VideoFrameExtractor(str(video_path))
        
        frames = extractor.extract_frames(
            start_time=config.time_range[0],
            end_time=config.time_range[1],
            sample_fps=config.fps,
            board_corners=config.board_corners
        )
        
        # Save extracted frames
        video_output = self.output_dir / config.video_id
        video_output.mkdir(exist_ok=True)
        
        (video_output / "frames").mkdir(exist_ok=True)
        (video_output / "boards").mkdir(exist_ok=True)
        
        for idx, (full_frame, board_crop) in enumerate(frames):
            # Save full frame
            frame_path = video_output / "frames" / f"frame_{idx:04d}.jpg"
            cv2.imwrite(str(frame_path), full_frame)
            
            # Save board crop
            board_path = video_output / "boards" / f"board_{idx:04d}.jpg"
            cv2.imwrite(str(board_path), board_crop)
        
        print(f"✅ Extracted {len(frames)} frames from {config.title}")


if __name__ == "__main__":
    # Example usage
    extractor = YouTubeChessExtractor()
    
    config = VideoConfig(
        video_id="rrPfmSWlAPM",
        title="Grand Prix 2023",
        time_range=("0:02:30", "0:10:00"),
        fps=1.0,
        board_corners=[88, 558, 764, 1233]
    )
    
    extractor.process_video(config, download=False)
