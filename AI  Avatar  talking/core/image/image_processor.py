"""
Image Processing Module
Image operations and validation
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image processing and validation"""
    
    def __init__(self):
        pass
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image as RGB numpy array"""
        try:
            from PIL import Image
            img = Image.open(image_path).convert('RGB')
            return np.array(img)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save numpy array as image"""
        try:
            from PIL import Image
            img = Image.fromarray(image.astype('uint8'))
            img.save(output_path)
            logger.info(f"Saved image: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
    
    def resize_image(
        self,
        image: np.ndarray,
        target_size: Tuple[int, int],
        maintain_aspect: bool = True
    ) -> np.ndarray:
        """
        Resize image
        
        Args:
            image: Input image array
            target_size: (width, height) tuple
            maintain_aspect: Maintain aspect ratio
        
        Returns:
            Resized image array
        """
        try:
            from PIL import Image
            import cv2
            
            h, w = image.shape[:2]
            target_w, target_h = target_size
            
            if maintain_aspect:
                # Calculate scaling to fit within target size
                scale = min(target_w / w, target_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                
                # Resize
                resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                
                # Create canvas with target size
                canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                
                # Center the image
                y_offset = (target_h - new_h) // 2
                x_offset = (target_w - new_w) // 2
                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                
                return canvas
            else:
                return cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image
    
    def crop_face(
        self,
        image: np.ndarray,
        face_box: Tuple[int, int, int, int],
        padding: float = 0.2
    ) -> np.ndarray:
        """
        Crop image around face with padding
        
        Args:
            image: Input image array
            face_box: (x, y, width, height) tuple
            padding: Padding percentage (0.0-1.0)
        
        Returns:
            Cropped image array
        """
        try:
            x, y, w, h = face_box
            
            # Calculate padding
            pad_x = int(w * padding)
            pad_y = int(h * padding)
            
            # Calculate crop coordinates
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(image.shape[1], x + w + pad_x)
            y2 = min(image.shape[0], y + h + pad_y)
            
            # Crop
            cropped = image[y1:y2, x1:x2]
            
            logger.debug(f"Cropped face: {cropped.shape}")
            return cropped
        
        except Exception as e:
            logger.error(f"Error cropping face: {e}")
            return image
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality"""
        try:
            import cv2
            
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            
            # Merge channels
            enhanced_lab = cv2.merge([l_enhanced, a, b])
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            
            logger.debug("Applied image enhancement")
            return enhanced
        
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    def validate_image(self, image_path: str) -> Tuple[bool, str]:
        """
        Validate image file
        
        Args:
            image_path: Path to image file
        
        Returns:
            (is_valid, message) tuple
        """
        try:
            from PIL import Image
            
            # Check if file exists
            if not Path(image_path).exists():
                return False, "File does not exist"
            
            # Check file size
            file_size = Path(image_path).stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10 MB
                return False, "File size exceeds 10 MB"
            
            # Try to open image
            try:
                img = Image.open(image_path)
            except Exception as e:
                return False, f"Invalid image file: {e}"
            
            # Check format
            if img.format.lower() not in ['jpeg', 'jpg', 'png', 'bmp', 'webp']:
                return False, f"Unsupported format: {img.format}"
            
            # Check dimensions
            w, h = img.size
            if w < 256 or h < 256:
                return False, f"Image too small: {w}x{h} (minimum 256x256)"
            
            if w > 4096 or h > 4096:
                return False, f"Image too large: {w}x{h} (maximum 4096x4096)"
            
            return True, f"Valid image: {w}x{h}, {img.format}"
        
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def preprocess_for_lipsync(
        self,
        image: np.ndarray,
        target_size: Tuple[int, int] = (96, 96)
    ) -> np.ndarray:
        """Preprocess image for lip sync model"""
        try:
            import cv2
            
            # Resize to target size
            processed = cv2.resize(image, target_size)
            
            # Normalize to [0, 1]
            processed = processed.astype(np.float32) / 255.0
            
            return processed
        
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def create_thumbnail(
        self,
        image_path: str,
        thumbnail_path: str,
        size: Tuple[int, int] = (320, 180)
    ) -> bool:
        """Create thumbnail from image"""
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, quality=85)
            
            logger.info(f"Created thumbnail: {thumbnail_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return False


if __name__ == '__main__':
    # Test image processor
    processor = ImageProcessor()
    print("Image processor initialized")
