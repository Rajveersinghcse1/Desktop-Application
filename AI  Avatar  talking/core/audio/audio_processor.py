"""
Audio Processing Module
Audio enhancement, normalization, and effects
"""

import logging
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio processing and enhancement"""
    
    def __init__(self):
        self.sample_rate = 16000
    
    def load_audio(self, audio_path: str) -> Optional[np.ndarray]:
        """Load audio file"""
        try:
            import librosa
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            logger.info(f"Loaded audio: {audio_path} ({len(audio)/sr:.2f}s)")
            return audio
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            return None
    
    def save_audio(
        self,
        audio: np.ndarray,
        output_path: str,
        sample_rate: Optional[int] = None
    ) -> bool:
        """Save audio to file"""
        try:
            import soundfile as sf
            sr = sample_rate or self.sample_rate
            sf.write(output_path, audio, sr)
            logger.info(f"Saved audio: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False
    
    def normalize_audio(
        self,
        audio: np.ndarray,
        target_db: float = -20.0
    ) -> np.ndarray:
        """
        Normalize audio to target dB level
        
        Args:
            audio: Input audio array
            target_db: Target level in dB
        
        Returns:
            Normalized audio array
        """
        try:
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio ** 2))
            
            if rms == 0:
                return audio
            
            # Calculate current dB
            current_db = 20 * np.log10(rms)
            
            # Calculate gain
            gain_db = target_db - current_db
            gain = 10 ** (gain_db / 20)
            
            # Apply gain
            normalized = audio * gain
            
            # Prevent clipping
            max_val = np.abs(normalized).max()
            if max_val > 1.0:
                normalized = normalized / max_val * 0.99
            
            logger.debug(f"Normalized audio: {current_db:.2f}dB -> {target_db:.2f}dB")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio
    
    def reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """
        Reduce background noise
        
        Args:
            audio: Input audio array
        
        Returns:
            Noise-reduced audio array
        """
        try:
            import noisereduce as nr
            
            # Estimate noise from first 0.5 seconds
            noise_sample_length = min(int(0.5 * self.sample_rate), len(audio) // 4)
            reduced = nr.reduce_noise(
                y=audio,
                sr=self.sample_rate,
                stationary=True,
                prop_decrease=0.8
            )
            
            logger.debug("Applied noise reduction")
            return reduced
        
        except ImportError:
            logger.warning("noisereduce not available, skipping noise reduction")
            return audio
        except Exception as e:
            logger.error(f"Error reducing noise: {e}")
            return audio
    
    def enhance_audio(
        self,
        audio_path: str,
        output_path: str,
        normalize: bool = True,
        reduce_noise: bool = True,
        target_db: float = -20.0
    ) -> bool:
        """
        Enhance audio with normalization and noise reduction
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            normalize: Apply normalization
            reduce_noise: Apply noise reduction
            target_db: Target normalization level
        
        Returns:
            True if successful
        """
        logger.info("Enhancing audio...")
        
        # Load audio
        audio = self.load_audio(audio_path)
        if audio is None:
            return False
        
        # Apply noise reduction
        if reduce_noise:
            audio = self.reduce_noise(audio)
        
        # Apply normalization
        if normalize:
            audio = self.normalize_audio(audio, target_db)
        
        # Save enhanced audio
        success = self.save_audio(audio, output_path)
        
        if success:
            logger.info("✓ Audio enhancement complete")
        
        return success
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get audio duration in seconds"""
        try:
            import librosa
            duration = librosa.get_duration(path=audio_path)
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return None
    
    def trim_audio(
        self,
        audio: np.ndarray,
        start_sec: float,
        end_sec: float
    ) -> np.ndarray:
        """Trim audio to specific time range"""
        start_sample = int(start_sec * self.sample_rate)
        end_sample = int(end_sec * self.sample_rate)
        return audio[start_sample:end_sample]
    
    def adjust_speed(
        self,
        audio: np.ndarray,
        speed_factor: float
    ) -> np.ndarray:
        """
        Adjust audio playback speed
        
        Args:
            audio: Input audio array
            speed_factor: Speed multiplier (0.5-2.0)
        
        Returns:
            Speed-adjusted audio array
        """
        try:
            import librosa
            adjusted = librosa.effects.time_stretch(audio, rate=speed_factor)
            logger.debug(f"Adjusted audio speed: {speed_factor}x")
            return adjusted
        except Exception as e:
            logger.error(f"Error adjusting speed: {e}")
            return audio
    
    def convert_to_wav(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 16000
    ) -> bool:
        """Convert audio to WAV format"""
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1).set_frame_rate(sample_rate)
            
            # Export as WAV
            audio.export(output_path, format='wav')
            
            logger.info(f"Converted to WAV: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            return False


if __name__ == '__main__':
    # Test audio processor
    processor = AudioProcessor()
    print("Audio processor initialized")
    print(f"Sample rate: {processor.sample_rate} Hz")
