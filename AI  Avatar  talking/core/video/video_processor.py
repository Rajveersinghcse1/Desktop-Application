"""
Video Processing Module
FFmpeg wrapper for video operations
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict
import json

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Video processing using FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        import shutil
        path = shutil.which('ffmpeg')
        if path:
            logger.info(f"FFmpeg found: {path}")
        else:
            logger.warning("FFmpeg not found in PATH")
        return path
    
    def _find_ffprobe(self) -> Optional[str]:
        """Find FFprobe executable"""
        import shutil
        path = shutil.which('ffprobe')
        if path:
            logger.debug(f"FFprobe found: {path}")
        return path
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """Get video metadata using ffprobe"""
        if not self.ffprobe_path:
            logger.error("ffprobe not available")
            return None
        
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"ffprobe failed: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def combine_video_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        video_codec: str = 'libx264',
        audio_codec: str = 'aac',
        crf: int = 23
    ) -> bool:
        """
        Combine video and audio into single file
        
        Args:
            video_path: Input video file
            audio_path: Input audio file
            output_path: Output video file
            video_codec: Video codec (libx264, libx265, etc.)
            audio_codec: Audio codec (aac, mp3, etc.)
            crf: Constant Rate Factor (18-28, lower = better quality)
        
        Returns:
            True if successful
        """
        if not self.ffmpeg_path:
            logger.error("FFmpeg not available")
            return False
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),
                '-i', str(audio_path),
                '-c:v', video_codec,
                '-c:a', audio_codec,
                '-crf', str(crf),
                '-shortest',  # Match shortest input duration
                '-y',  # Overwrite output
                str(output_path)
            ]
            
            logger.info(f"Combining video and audio...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Video created: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            return False
        except Exception as e:
            logger.error(f"Error combining video/audio: {e}")
            return False
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """Extract audio from video"""
        if not self.ffmpeg_path:
            return False
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                str(audio_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return False
    
    def resize_video(
        self,
        input_path: str,
        output_path: str,
        width: int,
        height: int
    ) -> bool:
        """Resize video to specific dimensions"""
        if not self.ffmpeg_path:
            return False
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(input_path),
                '-vf', f'scale={width}:{height}',
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"Error resizing video: {e}")
            return False
    
    def create_thumbnail(
        self,
        video_path: str,
        thumbnail_path: str,
        time_seconds: float = 1.0
    ) -> bool:
        """Create thumbnail from video"""
        if not self.ffmpeg_path:
            return False
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),
                '-ss', str(time_seconds),
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                str(thumbnail_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"✓ Thumbnail created: {thumbnail_path}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return False
    
    def convert_format(
        self,
        input_path: str,
        output_path: str,
        format_name: str,
        quality: str = 'high'
    ) -> bool:
        """Convert video to different format"""
        quality_settings = {
            'low': {'crf': 28, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'},
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', str(input_path),
                '-c:v', 'libx264',
                '-crf', str(settings['crf']),
                '-preset', settings['preset'],
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"Error converting format: {e}")
            return False


if __name__ == '__main__':
    # Test video processor
    processor = VideoProcessor()
    print(f"FFmpeg available: {processor.ffmpeg_path is not None}")
    print(f"FFprobe available: {processor.ffprobe_path is not None}")
