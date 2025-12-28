"""
Face Detection Module
Detects faces in images using multiple backends
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FaceDetector(ABC):
    """Abstract base class for face detectors"""
    
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array (RGB)
        
        Returns:
            List of (x, y, width, height, confidence) tuples
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get detector name"""
        pass


class MediaPipeDetector(FaceDetector):
    """Face detector using MediaPipe"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.detector = None
        self._initialize()
    
    def _initialize(self):
        """Initialize MediaPipe detector"""
        try:
            import mediapipe as mp
            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=self.confidence_threshold
            )
            logger.info("MediaPipe face detector initialized")
        except ImportError:
            logger.error("MediaPipe not installed")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Detect faces using MediaPipe"""
        if self.detector is None:
            return []
        
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = image[:, :, ::-1] if image.shape[2] == 3 else image
        else:
            image_rgb = image
        
        results = self.detector.process(image_rgb)
        
        faces = []
        if results.detections:
            h, w = image.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                confidence = detection.score[0]
                
                faces.append((x, y, width, height, confidence))
        
        return faces
    
    def get_name(self) -> str:
        return "MediaPipe"


class OpenCVDetector(FaceDetector):
    """Face detector using OpenCV Haar Cascades"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.detector = None
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenCV detector"""
        try:
            import cv2
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            logger.info("OpenCV face detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV detector: {e}")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Detect faces using OpenCV"""
        import cv2
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        
        # Detect faces
        faces_raw = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Convert to standard format (add confidence = 1.0)
        faces = [(x, y, w, h, 1.0) for (x, y, w, h) in faces_raw]
        
        return faces
    
    def get_name(self) -> str:
        return "OpenCV"


class FaceDetectionManager:
    """Manager for face detection with fallback support"""
    
    def __init__(self, preferred_method: str = 'mediapipe', confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.detector = None
        self.available_detectors = {}
        
        # Try to initialize detectors
        self._initialize_detectors(preferred_method)
    
    def _initialize_detectors(self, preferred_method: str):
        """Initialize face detectors"""
        # Try MediaPipe
        try:
            self.available_detectors['mediapipe'] = MediaPipeDetector(self.confidence_threshold)
            logger.info("✓ MediaPipe detector available")
        except Exception as e:
            logger.warning(f"MediaPipe detector not available: {e}")
        
        # Try OpenCV
        try:
            self.available_detectors['opencv'] = OpenCVDetector(self.confidence_threshold)
            logger.info("✓ OpenCV detector available")
        except Exception as e:
            logger.warning(f"OpenCV detector not available: {e}")
        
        # Set preferred detector
        if preferred_method in self.available_detectors:
            self.detector = self.available_detectors[preferred_method]
            logger.info(f"Using {preferred_method} as primary detector")
        elif self.available_detectors:
            # Use first available
            self.detector = list(self.available_detectors.values())[0]
            logger.info(f"Using {self.detector.get_name()} as primary detector")
        else:
            raise RuntimeError("No face detection backends available")
    
    def detect_face(self, image_path: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect a single face in an image
        
        Args:
            image_path: Path to image file
        
        Returns:
            (x, y, width, height) tuple or None if no face found
        """
        import cv2
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self.detector.detect_faces(image_rgb)
        
        if not faces:
            logger.warning("No faces detected")
            return None
        
        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}), using first one")
        
        # Return face with highest confidence
        best_face = max(faces, key=lambda f: f[4])
        return best_face[:4]  # (x, y, w, h)
    
    def detect_faces(self, image):
        """Detect multiple faces in an image (delegates to active detector)"""
        if self.detector is None:
            logger.error("No face detector available")
            return []
        return self.detector.detect_faces(image)
    
    def validate_image(self, image_path: str) -> Tuple[bool, str]:
        """
        Validate if image has exactly one detectable face
        
        Args:
            image_path: Path to image file
        
        Returns:
            (is_valid, message) tuple
        """
        import cv2
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return False, "Failed to load image"
        
        # Check image size
        h, w = image.shape[:2]
        if w < 256 or h < 256:
            return False, "Image resolution too low (minimum 256x256)"
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self.detector.detect_faces(image_rgb)
        
        if not faces:
            return False, "No face detected in image"
        
        if len(faces) > 1:
            return False, f"Multiple faces detected ({len(faces)}). Please use an image with a single face"
        
        # Check face confidence
        confidence = faces[0][4]
        if confidence < self.confidence_threshold:
            return False, f"Face detection confidence too low ({confidence:.2f})"
        
        return True, "Face detected successfully"


if __name__ == '__main__':
    # Test face detection
    print("Testing face detection...")
    
    manager = FaceDetectionManager()
    print(f"Active detector: {manager.detector.get_name()}")
    print(f"Available detectors: {list(manager.available_detectors.keys())}")
