"""
Text-to-Speech Module
Converts text to speech audio using multiple TTS engines
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TTSEngine(ABC):
    """Abstract base class for TTS engines"""
    
    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bool:
        """
        Synthesize speech from text
        
        Args:
            text: Input text
            output_path: Path to save audio file
            voice: Voice ID (engine-specific)
            speed: Speech speed multiplier
            pitch: Pitch multiplier
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_voices(self) -> List[Dict[str, str]]:
        """Get available voices"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get engine name"""
        pass


class Pyttsx3TTS(TTSEngine):
    """TTS engine using pyttsx3 (offline, system voices)"""
    
    def __init__(self):
        self.engine = None
        self._initialize()
    
    def _initialize(self):
        """Initialize pyttsx3 engine"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            logger.info("pyttsx3 TTS engine initialized")
        except ImportError:
            logger.error("pyttsx3 not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bool:
        """Synthesize speech using pyttsx3"""
        try:
            # Set voice if specified
            if voice and voice != 'default':
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if voice in v.id or voice in v.name:
                        self.engine.setProperty('voice', v.id)
                        break
            
            # Set rate (speed)
            rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(rate * speed))
            
            # Note: pyttsx3 doesn't support pitch adjustment directly
            
            # Save to file
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            logger.info(f"Audio saved to: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            return False
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Get available system voices"""
        try:
            voices = self.engine.getProperty('voices')
            return [
                {
                    'id': v.id,
                    'name': v.name,
                    'language': getattr(v, 'languages', ['en'])[0] if hasattr(v, 'languages') else 'en'
                }
                for v in voices
            ]
        except Exception:
            return [{'id': 'default', 'name': 'Default', 'language': 'en'}]
    
    def get_name(self) -> str:
        return "pyttsx3"


class GTTSEngine(TTSEngine):
    """TTS engine using Google Text-to-Speech (requires internet)"""
    
    def __init__(self):
        self._check_import()
    
    def _check_import(self):
        """Check if gTTS is installed"""
        try:
            import gtts
            logger.info("gTTS engine available")
        except ImportError:
            logger.warning("gTTS not installed")
            raise
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bool:
        """Synthesize speech using gTTS"""
        try:
            from gtts import gTTS
            
            # Determine language
            lang = voice if voice else 'en'
            
            # Create TTS
            tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
            
            # Save to file
            tts.save(str(output_path))
            
            # Adjust speed if needed (using pydub)
            if speed != 1.0:
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_mp3(output_path)
                    audio = audio.speedup(playback_speed=speed)
                    audio.export(output_path, format="mp3")
                except Exception as e:
                    logger.warning(f"Could not adjust speed: {e}")
            
            logger.info(f"Audio saved to: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            return False
    
    def get_voices(self) -> List[Dict[str, str]]:
        """Get available languages"""
        return [
            {'id': 'en', 'name': 'English', 'language': 'en'},
            {'id': 'es', 'name': 'Spanish', 'language': 'es'},
            {'id': 'fr', 'name': 'French', 'language': 'fr'},
            {'id': 'de', 'name': 'German', 'language': 'de'},
            {'id': 'it', 'name': 'Italian', 'language': 'it'},
            {'id': 'pt', 'name': 'Portuguese', 'language': 'pt'},
            {'id': 'zh-CN', 'name': 'Chinese (Simplified)', 'language': 'zh'},
            {'id': 'ja', 'name': 'Japanese', 'language': 'ja'},
            {'id': 'ko', 'name': 'Korean', 'language': 'ko'},
        ]
    
    def get_name(self) -> str:
        return "gTTS"


class TTSManager:
    """Manager for TTS engines with fallback support"""
    
    def __init__(self, preferred_engine: str = 'pyttsx3'):
        self.engine = None
        self.available_engines = {}
        self._initialize_engines(preferred_engine)
    
    def _initialize_engines(self, preferred_engine: str):
        """Initialize TTS engines"""
        # Try pyttsx3 (offline, always works)
        try:
            self.available_engines['pyttsx3'] = Pyttsx3TTS()
            logger.info("✓ pyttsx3 engine available")
        except Exception as e:
            logger.warning(f"pyttsx3 not available: {e}")
        
        # Try gTTS (requires internet)
        try:
            self.available_engines['gtts'] = GTTSEngine()
            logger.info("✓ gTTS engine available")
        except Exception as e:
            logger.warning(f"gTTS not available: {e}")
        
        # Set preferred engine
        if preferred_engine in self.available_engines:
            self.engine = self.available_engines[preferred_engine]
            logger.info(f"Using {preferred_engine} as primary TTS engine")
        elif self.available_engines:
            # Use first available
            self.engine = list(self.available_engines.values())[0]
            logger.info(f"Using {self.engine.get_name()} as primary TTS engine")
        else:
            raise RuntimeError("No TTS engines available")
    
    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Input text
            output_path: Path to save audio file
            voice: Voice ID
            speed: Speech speed (0.5 - 2.0)
            pitch: Pitch adjustment (0.5 - 2.0)
        
        Returns:
            True if successful
        """
        if not self.engine:
            logger.error("No TTS engine available")
            return False
        
        # Validate parameters
        if not text.strip():
            logger.error("Empty text provided")
            return False
        
        if not 0.5 <= speed <= 2.0:
            logger.warning(f"Speed {speed} out of range, clipping to [0.5, 2.0]")
            speed = max(0.5, min(2.0, speed))
        
        if not 0.5 <= pitch <= 2.0:
            logger.warning(f"Pitch {pitch} out of range, clipping to [0.5, 2.0]")
            pitch = max(0.5, min(2.0, pitch))
        
        # Synthesize
        logger.info(f"Synthesizing speech with {self.engine.get_name()}...")
        success = self.engine.synthesize(text, output_path, voice, speed, pitch)
        
        if success:
            logger.info(f"✓ Speech synthesis complete: {output_path}")
        else:
            logger.error("✗ Speech synthesis failed")
        
        return success
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get available voices for current engine"""
        if not self.engine:
            return []
        return self.engine.get_voices()
    
    def switch_engine(self, engine_name: str) -> bool:
        """Switch to a different TTS engine"""
        if engine_name in self.available_engines:
            self.engine = self.available_engines[engine_name]
            logger.info(f"Switched to {engine_name} TTS engine")
            return True
        else:
            logger.error(f"Engine {engine_name} not available")
            return False


if __name__ == '__main__':
    # Test TTS
    print("Testing TTS engines...")
    
    manager = TTSManager()
    print(f"Active engine: {manager.engine.get_name()}")
    print(f"Available engines: {list(manager.available_engines.keys())}")
    
    # Test synthesis
    test_text = "Hello! This is a test of the text to speech system."
    output = "test_audio.wav"
    
    success = manager.text_to_speech(test_text, output)
    if success:
        print(f"✓ Audio saved to: {output}")
    else:
        print("✗ Synthesis failed")
