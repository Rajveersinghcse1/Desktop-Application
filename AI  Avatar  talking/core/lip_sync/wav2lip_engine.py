"""
Wav2Lip Lip Sync Engine
Synchronize lip movements with audio
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import cv2

logger = logging.getLogger(__name__)


class Wav2LipEngine:
    """Wav2Lip model for lip synchronization"""
    
    def __init__(self, model_path: str, device: str = 'cpu'):
        """
        Initialize Wav2Lip engine
        
        Args:
            model_path: Path to Wav2Lip model file
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_path = Path(model_path)
        self.device = device
        self.model = None
        self.initialized = False
        
        # Model parameters
        self.img_size = 96
        self.fps = 25
        self.mel_step_size = 16
        
        logger.info(f"Initializing Wav2Lip engine with model: {model_path}")
    
    def initialize(self) -> bool:
        """Load the Wav2Lip model"""
        try:
            import torch
            
            if not self.model_path.exists():
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            # Load model
            checkpoint = torch.load(
                self.model_path,
                map_location=torch.device(self.device)
            )
            
            # Create model architecture
            from .wav2lip_model import Wav2Lip
            self.model = Wav2Lip()
            self.model.load_state_dict(checkpoint['state_dict'])
            
            self.model.eval()
            if self.device == 'cuda':
                self.model = self.model.cuda()
            
            self.initialized = True
            logger.info("✓ Wav2Lip model loaded successfully")
            return True
        
        except ImportError:
            logger.error("PyTorch not installed. Install with: pip install torch torchvision")
            return False
        
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip model: {e}")
            return False
    
    def generate(
        self,
        face_video_path: str,
        audio_path: str,
        output_path: str,
        fps: int = 25,
        quality: str = 'balanced',
        progress_callback=None
    ) -> bool:
        """
        Generate lip-synced video
        
        Args:
            face_video_path: Path to input video with face
            audio_path: Path to audio file
            output_path: Path to save output video
            fps: Output video FPS
            quality: Quality preset ('fast', 'balanced', 'high')
            progress_callback: Callback function(percentage)
        
        Returns:
            True if successful
        """
        if not self.initialized:
            if not self.initialize():
                return False
        
        logger.info("Generating lip-synced video...")
        logger.info(f"  Face video: {face_video_path}")
        logger.info(f"  Audio: {audio_path}")
        logger.info(f"  Output: {output_path}")
        
        try:
            # Load video frames
            video_stream = cv2.VideoCapture(face_video_path)
            frames = []
            
            while True:
                ret, frame = video_stream.read()
                if not ret:
                    break
                frames.append(frame)
            
            video_stream.release()
            
            if not frames:
                logger.error("No frames found in video")
                return False
            
            logger.info(f"Loaded {len(frames)} frames")
            
            # Load audio mel spectrogram
            mel = self._load_mel_spectrogram(audio_path)
            
            # Generate lip-synced frames
            synced_frames = self._process_frames(
                frames, mel, progress_callback
            )
            
            # Save output video
            success = self._save_video(
                synced_frames, output_path, audio_path, fps
            )
            
            if success:
                logger.info(f"✓ Lip-synced video saved: {output_path}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error generating lip sync: {e}")
            return False
    
    def _load_mel_spectrogram(self, audio_path: str) -> np.ndarray:
        """Load audio and extract mel spectrogram"""
        try:
            import librosa
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract mel spectrogram
            mel = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_mels=80,
                hop_length=160,
                win_length=400,
                fmin=55,
                fmax=7600
            )
            
            # Convert to log scale
            mel = librosa.power_to_db(mel, ref=np.max)
            
            return mel.T
        
        except Exception as e:
            logger.error(f"Error loading audio mel spectrogram: {e}")
            raise
    
    def _process_frames(
        self,
        frames: list,
        mel: np.ndarray,
        progress_callback=None
    ) -> list:
        """Process frames with Wav2Lip model"""
        import torch
        
        synced_frames = []
        mel_chunks = self._get_mel_chunks(mel, len(frames))
        
        logger.info(f"Processing {len(frames)} frames...")
        
        for i, (frame, mel_chunk) in enumerate(zip(frames, mel_chunks)):
            # Detect face
            face_det = self._detect_face(frame)
            if face_det is None:
                logger.warning(f"No face detected in frame {i}, using original")
                synced_frames.append(frame)
                continue
            
            # Prepare inputs
            face_tensor = self._preprocess_face(face_det)
            mel_tensor = torch.FloatTensor(mel_chunk).unsqueeze(0)
            
            if self.device == 'cuda':
                face_tensor = face_tensor.cuda()
                mel_tensor = mel_tensor.cuda()
            
            # Generate lip-synced face
            with torch.no_grad():
                pred = self.model(mel_tensor, face_tensor)
            
            # Post-process
            synced_face = self._postprocess_face(pred)
            
            # Blend back into frame
            synced_frame = self._blend_face(frame, synced_face, face_det)
            synced_frames.append(synced_frame)
            
            # Progress callback
            if progress_callback:
                progress_callback((i + 1) / len(frames) * 100)
        
        return synced_frames
    
    def _get_mel_chunks(self, mel: np.ndarray, num_frames: int) -> list:
        """Split mel spectrogram into chunks"""
        mel_idx_multiplier = 80.0 / self.fps
        chunks = []
        
        for i in range(num_frames):
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + self.mel_step_size > len(mel):
                start_idx = len(mel) - self.mel_step_size
            
            mel_chunk = mel[start_idx:start_idx + self.mel_step_size, :]
            chunks.append(mel_chunk)
        
        return chunks
    
    def _detect_face(self, frame: np.ndarray) -> Optional[Tuple]:
        """Detect face in frame"""
        # Use face detection from face_detection module
        from core.face_detection import FaceDetectionManager
        
        detector = FaceDetectionManager()
        faces = detector.detect_faces(frame)
        
        if not faces:
            return None
        
        # Return largest face
        return max(faces, key=lambda f: f['area'])
    
    def _preprocess_face(self, face_det: dict) -> 'torch.Tensor':
        """Preprocess face for model input"""
        import torch
        
        face_img = face_det['image']
        
        # Resize to model input size
        face_img = cv2.resize(face_img, (self.img_size, self.img_size))
        
        # Normalize
        face_img = face_img.astype(np.float32) / 255.0
        face_img = (face_img - 0.5) / 0.5
        
        # Convert to tensor
        face_tensor = torch.FloatTensor(face_img).permute(2, 0, 1).unsqueeze(0)
        
        return face_tensor
    
    def _postprocess_face(self, pred: 'torch.Tensor') -> np.ndarray:
        """Post-process model output"""
        pred = pred.squeeze(0).cpu().numpy()
        pred = pred.transpose(1, 2, 0)
        
        # Denormalize
        pred = (pred * 0.5 + 0.5) * 255.0
        pred = np.clip(pred, 0, 255).astype(np.uint8)
        
        return pred
    
    def _blend_face(
        self,
        frame: np.ndarray,
        synced_face: np.ndarray,
        face_det: dict
    ) -> np.ndarray:
        """Blend synced face back into frame"""
        x, y, w, h = face_det['bbox']
        
        # Resize synced face to original bbox
        synced_face = cv2.resize(synced_face, (w, h))
        
        # Create blended frame
        result = frame.copy()
        result[y:y+h, x:x+w] = synced_face
        
        return result
    
    def _save_video(
        self,
        frames: list,
        output_path: str,
        audio_path: str,
        fps: int
    ) -> bool:
        """Save frames to video with audio"""
        try:
            from core.video import VideoProcessor
            
            # Save frames as temporary video
            temp_video = str(Path(output_path).parent / "temp_video.mp4")
            
            # Get frame size
            h, w = frames[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (w, h))
            
            for frame in frames:
                out.write(frame)
            
            out.release()
            
            # Combine with audio
            processor = VideoProcessor()
            success = processor.combine_video_audio(
                temp_video, audio_path, output_path
            )
            
            # Cleanup
            Path(temp_video).unlink(missing_ok=True)
            
            return success
        
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            return False


if __name__ == '__main__':
    # Test Wav2Lip engine
    print("Wav2Lip Lip Sync Engine")
    print("=" * 60)
    print("Note: Requires PyTorch and downloaded Wav2Lip model")
    print("Run model_manager.py first to download models")
