"""
Generation Pipeline
Orchestrates the complete avatar generation workflow
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class GenerationPipeline:
    """Orchestrate complete avatar generation process"""
    
    def __init__(self, config: dict, database_manager, model_manager):
        """
        Initialize pipeline
        
        Args:
            config: Configuration dictionary
            database_manager: Database manager instance
            model_manager: Model manager instance
        """
        self.config = config
        self.db = database_manager
        self.model_manager = model_manager
        
        # Pipeline stages
        self.stages = [
            'validation',
            'face_detection',
            'audio_generation',
            'audio_processing',
            'lip_sync',
            'video_encoding',
            'thumbnail_generation',
            'finalization'
        ]
        
        self.current_stage = None
        self.progress = 0
        
        logger.info("Generation pipeline initialized")
    
    def generate(
        self,
        project_id: int,
        input_image: str,
        text: str,
        output_path: str,
        voice: str = 'default',
        quality: str = 'balanced',
        resolution: str = '720p',
        speed: float = 1.0,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Generate avatar video
        
        Args:
            project_id: Project database ID
            input_image: Path to input image
            text: Text to synthesize
            output_path: Path to save video
            voice: TTS voice name
            quality: Quality preset
            resolution: Output resolution
            speed: Speech speed multiplier
            progress_callback: Callback function(stage, progress, message)
        
        Returns:
            Result dictionary with status and paths
        """
        logger.info("=" * 60)
        logger.info("Starting avatar generation pipeline")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Create generation record
        generation_id = self.db.create_generation(
            project_id=project_id,
            status='processing',
            input_image=input_image,
            output_video=output_path,
            settings={
                'text': text,
                'voice': voice,
                'quality': quality,
                'resolution': resolution,
                'speed': speed
            }
        )
        
        result = {
            'success': False,
            'generation_id': generation_id,
            'output_path': None,
            'thumbnail_path': None,
            'error': None
        }
        
        try:
            # Stage 1: Validation
            self._update_stage('validation', 0, progress_callback)
            if not self._validate_inputs(input_image, text):
                raise ValueError("Input validation failed")
            self._update_stage('validation', 100, progress_callback)
            
            # Stage 2: Face Detection
            self._update_stage('face_detection', 0, progress_callback)
            face_data = self._detect_face(input_image)
            if not face_data:
                raise ValueError("No face detected in input image")
            self._update_stage('face_detection', 100, progress_callback)
            
            # Stage 3: Audio Generation
            self._update_stage('audio_generation', 0, progress_callback)
            audio_path = self._generate_audio(text, voice, speed)
            if not audio_path:
                raise ValueError("Audio generation failed")
            self._update_stage('audio_generation', 100, progress_callback)
            
            # Stage 4: Audio Processing
            self._update_stage('audio_processing', 0, progress_callback)
            processed_audio = self._process_audio(audio_path)
            self._update_stage('audio_processing', 100, progress_callback)
            
            # Stage 5: Lip Sync
            self._update_stage('lip_sync', 0, progress_callback)
            video_path = self._apply_lip_sync(
                input_image,
                processed_audio,
                quality,
                resolution,
                lambda p: self._update_stage('lip_sync', p, progress_callback)
            )
            if not video_path:
                raise ValueError("Lip sync failed")
            self._update_stage('lip_sync', 100, progress_callback)
            
            # Stage 6: Video Encoding
            self._update_stage('video_encoding', 0, progress_callback)
            final_video = self._encode_video(video_path, output_path, quality)
            self._update_stage('video_encoding', 100, progress_callback)
            
            # Stage 7: Thumbnail Generation
            self._update_stage('thumbnail_generation', 0, progress_callback)
            thumbnail_path = self._generate_thumbnail(final_video)
            self._update_stage('thumbnail_generation', 100, progress_callback)
            
            # Stage 8: Finalization
            self._update_stage('finalization', 0, progress_callback)
            
            # Calculate stats
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update database
            self.db.update_generation(
                generation_id,
                status='completed',
                output_video=final_video,
                metadata={
                    'duration': duration,
                    'thumbnail': thumbnail_path,
                    'face_data': face_data
                }
            )
            
            result['success'] = True
            result['output_path'] = final_video
            result['thumbnail_path'] = thumbnail_path
            
            self._update_stage('finalization', 100, progress_callback)
            
            logger.info("✓ Generation completed successfully")
            logger.info(f"  Output: {final_video}")
            logger.info(f"  Duration: {duration:.1f}s")
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            
            # Update database
            self.db.update_generation(
                generation_id,
                status='failed',
                metadata={'error': str(e)}
            )
            
            result['error'] = str(e)
        
        return result
    
    def _validate_inputs(self, image_path: str, text: str) -> bool:
        """Validate input parameters"""
        from core.image import ImageProcessor
        from utils.file_manager import Validators
        
        logger.info("Validating inputs...")
        
        # Validate image
        processor = ImageProcessor()
        valid, message = processor.validate_image(image_path)
        if not valid:
            logger.error(f"Invalid image: {message}")
            return False
        
        # Validate text
        valid, message = Validators.validate_text(text)
        if not valid:
            logger.error(f"Invalid text: {message}")
            return False
        
        logger.info("✓ Inputs validated")
        return True
    
    def _detect_face(self, image_path: str) -> Optional[Dict]:
        """Detect face in input image"""
        from core.face_detection import FaceDetectionManager
        from core.image import ImageProcessor
        
        logger.info("Detecting face...")
        
        # Load image
        processor = ImageProcessor()
        image = processor.load_image(image_path)
        
        # Detect faces
        detector = FaceDetectionManager()
        faces = detector.detect_faces(image)
        
        if not faces:
            logger.error("No faces detected")
            return None
        
        # Use largest face
        face = max(faces, key=lambda f: f['area'])
        
        logger.info(f"✓ Face detected: {face['confidence']:.2f} confidence")
        return face
    
    def _generate_audio(self, text: str, voice: str, speed: float) -> Optional[str]:
        """Generate speech from text"""
        from core.tts import TTSManager
        from config import paths
        
        logger.info(f"Generating audio: {len(text)} characters")
        
        # Create TTS manager
        tts = TTSManager()
        
        # Generate audio
        output_path = str(paths.cache_dir / f"tts_{datetime.now().timestamp()}.wav")
        success = tts.text_to_speech(
            text=text,
            output_path=output_path,
            voice=voice,
            speed=speed
        )
        
        if success:
            logger.info(f"✓ Audio generated: {output_path}")
            return output_path
        else:
            logger.error("Audio generation failed")
            return None
    
    def _process_audio(self, audio_path: str) -> str:
        """Process and enhance audio"""
        from core.audio import AudioProcessor
        from config import paths
        
        logger.info("Processing audio...")
        
        processor = AudioProcessor()
        
        # Load audio
        audio, sr = processor.load_audio(audio_path)
        
        # Enhance
        audio = processor.enhance_audio(audio, sr)
        
        # Save
        output_path = str(paths.cache_dir / f"processed_{Path(audio_path).name}")
        processor.save_audio(output_path, audio, sr)
        
        logger.info(f"✓ Audio processed: {output_path}")
        return output_path
    
    def _apply_lip_sync(
        self,
        image_path: str,
        audio_path: str,
        quality: str,
        resolution: str,
        progress_callback
    ) -> Optional[str]:
        """Apply lip synchronization"""
        from core.lip_sync import Wav2LipEngine
        from core.image import ImageProcessor
        from core.video import VideoProcessor
        from config import paths
        
        logger.info("Applying lip sync...")
        
        # Check if model downloaded
        model_path = self.model_manager.get_model_path('wav2lip_96')
        if not model_path:
            logger.info("Downloading Wav2Lip model...")
            success = self.model_manager.download_model('wav2lip_96')
            if not success:
                logger.error("Failed to download model")
                return None
            model_path = self.model_manager.get_model_path('wav2lip_96')
        
        # Create video from static image
        logger.info("Preparing video from image...")
        video_processor = VideoProcessor()
        
        # Load image
        image_processor = ImageProcessor()
        img = image_processor.load_image(image_path)
        
        # Get audio duration
        import librosa
        duration = librosa.get_duration(path=audio_path)
        fps = 25
        num_frames = int(duration * fps)
        
        # Create temporary video
        import cv2
        temp_video = str(paths.cache_dir / f"temp_{datetime.now().timestamp()}.mp4")
        
        h, w = img.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, (w, h))
        
        for _ in range(num_frames):
            out.write(img)
        
        out.release()
        
        # Apply Wav2Lip
        engine = Wav2LipEngine(str(model_path))
        output_path = str(paths.cache_dir / f"lipsynced_{datetime.now().timestamp()}.mp4")
        
        success = engine.generate(
            face_video_path=temp_video,
            audio_path=audio_path,
            output_path=output_path,
            fps=fps,
            quality=quality,
            progress_callback=progress_callback
        )
        
        # Cleanup
        Path(temp_video).unlink(missing_ok=True)
        
        if success:
            logger.info(f"✓ Lip sync applied: {output_path}")
            return output_path
        else:
            logger.error("Lip sync failed")
            return None
    
    def _encode_video(self, input_path: str, output_path: str, quality: str) -> str:
        """Encode final video"""
        from core.video import VideoProcessor
        
        logger.info("Encoding final video...")
        
        processor = VideoProcessor()
        
        # Get quality settings
        crf = {'fast': 28, 'balanced': 23, 'high': 18}.get(quality, 23)
        
        # Convert to final format
        success = processor.convert_format(
            input_path=input_path,
            output_path=output_path,
            video_codec='libx264',
            audio_codec='aac',
            crf=crf
        )
        
        if success:
            logger.info(f"✓ Video encoded: {output_path}")
            return output_path
        else:
            logger.error("Video encoding failed")
            return input_path
    
    def _generate_thumbnail(self, video_path: str) -> Optional[str]:
        """Generate video thumbnail"""
        from core.video import VideoProcessor
        
        logger.info("Generating thumbnail...")
        
        processor = VideoProcessor()
        
        thumbnail_path = str(Path(video_path).with_suffix('.jpg'))
        success = processor.create_thumbnail(
            video_path=video_path,
            output_path=thumbnail_path,
            timestamp=0.5
        )
        
        if success:
            logger.info(f"✓ Thumbnail created: {thumbnail_path}")
            return thumbnail_path
        else:
            logger.warning("Thumbnail generation failed")
            return None
    
    def _update_stage(self, stage: str, progress: int, callback: Optional[Callable] = None):
        """Update pipeline stage and progress"""
        self.current_stage = stage
        self.progress = progress
        
        stage_index = self.stages.index(stage) if stage in self.stages else 0
        overall_progress = (stage_index * 100 + progress) / len(self.stages)
        
        message = f"{stage.replace('_', ' ').title()}: {progress}%"
        logger.info(f"[{overall_progress:.1f}%] {message}")
        
        if callback:
            callback(stage, progress, message)


if __name__ == '__main__':
    print("Generation Pipeline")
    print("=" * 60)
    print("This module orchestrates the complete avatar generation workflow")
    print("\nStages:")
    pipeline = GenerationPipeline({}, None, None)
    for i, stage in enumerate(pipeline.stages, 1):
        print(f"  {i}. {stage.replace('_', ' ').title()}")
