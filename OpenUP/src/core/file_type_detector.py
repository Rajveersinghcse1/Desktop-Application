"""
Enhanced File Type Detection for OpenUP
========================================
Provides reliable file type detection using magic bytes,
MIME types, and heuristic analysis - not just extensions.
"""

from __future__ import annotations

import mimetypes
import re
import struct
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class FileCategory(Enum):
    """High-level file category classification."""
    DOCUMENT = auto()
    DATA = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    ARCHIVE = auto()
    EXECUTABLE = auto()
    MODEL_3D = auto()
    GEOSPATIAL = auto()
    MEDICAL = auto()
    CODE = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class FileSignature:
    """Magic byte signature for file type identification."""
    magic_bytes: bytes
    offset: int = 0
    mask: Optional[bytes] = None  # For partial matching
    mime_type: str = ""
    category: FileCategory = FileCategory.UNKNOWN
    extensions: Tuple[str, ...] = ()
    description: str = ""


@dataclass
class FileTypeResult:
    """Result of file type detection."""
    mime_type: str
    category: FileCategory
    extension: str
    description: str
    confidence: float  # 0.0 to 1.0
    detected_by: str  # 'magic', 'extension', 'content', 'heuristic'
    
    @property
    def is_confident(self) -> bool:
        """Check if detection is confident enough to trust."""
        return self.confidence >= 0.7


class FileTypeDetector:
    """
    Intelligent file type detection using multiple strategies.
    
    Detection order:
    1. Magic bytes (highest confidence)
    2. MIME type from extension
    3. Content analysis (for text files)
    4. Heuristic fallback
    """
    
    # Common file signatures (magic bytes)
    SIGNATURES: List[FileSignature] = [
        # Images
        FileSignature(b'\x89PNG\r\n\x1a\n', 0, None, 
                     'image/png', FileCategory.IMAGE, ('.png',), 'PNG Image'),
        FileSignature(b'\xff\xd8\xff', 0, None,
                     'image/jpeg', FileCategory.IMAGE, ('.jpg', '.jpeg'), 'JPEG Image'),
        FileSignature(b'GIF87a', 0, None,
                     'image/gif', FileCategory.IMAGE, ('.gif',), 'GIF Image'),
        FileSignature(b'GIF89a', 0, None,
                     'image/gif', FileCategory.IMAGE, ('.gif',), 'GIF Image'),
        FileSignature(b'RIFF', 0, None,
                     'image/webp', FileCategory.IMAGE, ('.webp',), 'WebP Image'),
        FileSignature(b'BM', 0, None,
                     'image/bmp', FileCategory.IMAGE, ('.bmp',), 'BMP Image'),
        FileSignature(b'II*\x00', 0, None,
                     'image/tiff', FileCategory.IMAGE, ('.tif', '.tiff'), 'TIFF Image (LE)'),
        FileSignature(b'MM\x00*', 0, None,
                     'image/tiff', FileCategory.IMAGE, ('.tif', '.tiff'), 'TIFF Image (BE)'),
        
        # Documents
        FileSignature(b'%PDF', 0, None,
                     'application/pdf', FileCategory.DOCUMENT, ('.pdf',), 'PDF Document'),
        FileSignature(b'PK\x03\x04', 0, None,
                     'application/zip', FileCategory.ARCHIVE, ('.zip', '.docx', '.xlsx', '.pptx'), 'ZIP Archive'),
        FileSignature(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', 0, None,
                     'application/vnd.ms-office', FileCategory.DOCUMENT, ('.doc', '.xls', '.ppt'), 'MS Office Document'),
        
        # Archives
        FileSignature(b'Rar!\x1a\x07', 0, None,
                     'application/x-rar-compressed', FileCategory.ARCHIVE, ('.rar',), 'RAR Archive'),
        FileSignature(b'\x1f\x8b', 0, None,
                     'application/gzip', FileCategory.ARCHIVE, ('.gz', '.tgz'), 'GZIP Archive'),
        FileSignature(b'BZh', 0, None,
                     'application/x-bzip2', FileCategory.ARCHIVE, ('.bz2',), 'BZIP2 Archive'),
        FileSignature(b'\xfd7zXZ\x00', 0, None,
                     'application/x-xz', FileCategory.ARCHIVE, ('.xz',), 'XZ Archive'),
        FileSignature(b'7z\xbc\xaf\x27\x1c', 0, None,
                     'application/x-7z-compressed', FileCategory.ARCHIVE, ('.7z',), '7-Zip Archive'),
        
        # Audio
        FileSignature(b'ID3', 0, None,
                     'audio/mpeg', FileCategory.AUDIO, ('.mp3',), 'MP3 Audio'),
        FileSignature(b'\xff\xfb', 0, None,
                     'audio/mpeg', FileCategory.AUDIO, ('.mp3',), 'MP3 Audio (no ID3)'),
        FileSignature(b'OggS', 0, None,
                     'audio/ogg', FileCategory.AUDIO, ('.ogg', '.oga'), 'OGG Audio'),
        FileSignature(b'fLaC', 0, None,
                     'audio/flac', FileCategory.AUDIO, ('.flac',), 'FLAC Audio'),
        FileSignature(b'RIFF', 0, None,
                     'audio/wav', FileCategory.AUDIO, ('.wav',), 'WAV Audio'),
        
        # Video
        FileSignature(b'\x00\x00\x00\x18ftypmp4', 0, None,
                     'video/mp4', FileCategory.VIDEO, ('.mp4',), 'MP4 Video'),
        FileSignature(b'\x00\x00\x00\x1cftypisom', 0, None,
                     'video/mp4', FileCategory.VIDEO, ('.mp4',), 'MP4 Video (ISO)'),
        FileSignature(b'\x1aE\xdf\xa3', 0, None,
                     'video/webm', FileCategory.VIDEO, ('.webm', '.mkv'), 'WebM/Matroska Video'),
        FileSignature(b'RIFF', 0, None,
                     'video/avi', FileCategory.VIDEO, ('.avi',), 'AVI Video'),
        
        # 3D Models
        FileSignature(b'ply', 0, None,
                     'application/x-ply', FileCategory.MODEL_3D, ('.ply',), 'PLY 3D Model'),
        FileSignature(b'solid', 0, None,
                     'model/stl', FileCategory.MODEL_3D, ('.stl',), 'STL 3D Model (ASCII)'),
        
        # Data formats
        FileSignature(b'SQLite format 3', 0, None,
                     'application/x-sqlite3', FileCategory.DATA, ('.db', '.sqlite'), 'SQLite Database'),
        FileSignature(b'PAR1', 0, None,
                     'application/x-parquet', FileCategory.DATA, ('.parquet',), 'Apache Parquet'),
        FileSignature(b'\x89HDF', 0, None,
                     'application/x-hdf5', FileCategory.DATA, ('.h5', '.hdf5'), 'HDF5 File'),
        
        # Geospatial
        FileSignature(b'LASF', 0, None,
                     'application/x-lasf', FileCategory.GEOSPATIAL, ('.las', '.laz'), 'LAS Point Cloud'),
    ]
    
    # Extension to category mapping (fallback)
    EXTENSION_CATEGORIES: Dict[str, FileCategory] = {
        # Documents
        '.txt': FileCategory.DOCUMENT, '.md': FileCategory.DOCUMENT,
        '.log': FileCategory.DOCUMENT, '.rst': FileCategory.DOCUMENT,
        '.pdf': FileCategory.DOCUMENT, '.doc': FileCategory.DOCUMENT,
        '.docx': FileCategory.DOCUMENT, '.rtf': FileCategory.DOCUMENT,
        
        # Data
        '.csv': FileCategory.DATA, '.tsv': FileCategory.DATA,
        '.json': FileCategory.DATA, '.yaml': FileCategory.DATA,
        '.yml': FileCategory.DATA, '.xml': FileCategory.DATA,
        '.xlsx': FileCategory.DATA, '.xls': FileCategory.DATA,
        '.parquet': FileCategory.DATA, '.h5': FileCategory.DATA,
        '.hdf5': FileCategory.DATA, '.db': FileCategory.DATA,
        '.sqlite': FileCategory.DATA,
        
        # Images
        '.png': FileCategory.IMAGE, '.jpg': FileCategory.IMAGE,
        '.jpeg': FileCategory.IMAGE, '.gif': FileCategory.IMAGE,
        '.bmp': FileCategory.IMAGE, '.tiff': FileCategory.IMAGE,
        '.tif': FileCategory.IMAGE, '.webp': FileCategory.IMAGE,
        '.svg': FileCategory.IMAGE, '.ico': FileCategory.IMAGE,
        
        # Audio
        '.mp3': FileCategory.AUDIO, '.wav': FileCategory.AUDIO,
        '.flac': FileCategory.AUDIO, '.ogg': FileCategory.AUDIO,
        '.m4a': FileCategory.AUDIO, '.aac': FileCategory.AUDIO,
        
        # Video
        '.mp4': FileCategory.VIDEO, '.avi': FileCategory.VIDEO,
        '.mkv': FileCategory.VIDEO, '.mov': FileCategory.VIDEO,
        '.webm': FileCategory.VIDEO, '.wmv': FileCategory.VIDEO,
        
        # Archives
        '.zip': FileCategory.ARCHIVE, '.rar': FileCategory.ARCHIVE,
        '.tar': FileCategory.ARCHIVE, '.gz': FileCategory.ARCHIVE,
        '.7z': FileCategory.ARCHIVE, '.bz2': FileCategory.ARCHIVE,
        
        # 3D Models
        '.obj': FileCategory.MODEL_3D, '.stl': FileCategory.MODEL_3D,
        '.ply': FileCategory.MODEL_3D, '.fbx': FileCategory.MODEL_3D,
        '.gltf': FileCategory.MODEL_3D, '.glb': FileCategory.MODEL_3D,
        
        # Code
        '.py': FileCategory.CODE, '.js': FileCategory.CODE,
        '.ts': FileCategory.CODE, '.java': FileCategory.CODE,
        '.c': FileCategory.CODE, '.cpp': FileCategory.CODE,
        '.h': FileCategory.CODE, '.hpp': FileCategory.CODE,
        '.cs': FileCategory.CODE, '.go': FileCategory.CODE,
        '.rs': FileCategory.CODE, '.rb': FileCategory.CODE,
        '.php': FileCategory.CODE, '.swift': FileCategory.CODE,
        '.kt': FileCategory.CODE, '.scala': FileCategory.CODE,
        '.html': FileCategory.CODE, '.css': FileCategory.CODE,
        '.sql': FileCategory.CODE, '.sh': FileCategory.CODE,
        '.bat': FileCategory.CODE, '.ps1': FileCategory.CODE,
    }
    
    # Text file patterns for content analysis
    TEXT_PATTERNS = {
        FileCategory.DATA: [
            (re.compile(r'^\s*[\[\{]'), 'application/json'),  # JSON
            (re.compile(r'^[\w-]+:\s'), 'application/x-yaml'),  # YAML
            (re.compile(r'^<\?xml'), 'application/xml'),  # XML
            (re.compile(r'^"[^"]*"(,|$)', re.MULTILINE), 'text/csv'),  # CSV
        ],
        FileCategory.CODE: [
            (re.compile(r'^#!.*python'), 'text/x-python'),
            (re.compile(r'^#!.*bash'), 'text/x-shellscript'),
            (re.compile(r'^\s*def\s+\w+\s*\('), 'text/x-python'),
            (re.compile(r'^\s*function\s+\w+'), 'text/javascript'),
            (re.compile(r'^\s*import\s+[\w.]+'), 'text/x-python'),
            (re.compile(r'^\s*package\s+\w+'), 'text/x-java'),
        ],
        FileCategory.DOCUMENT: [
            (re.compile(r'^#\s+.+\n'), 'text/markdown'),  # Markdown header
            (re.compile(r'^\*\*\*.+\*\*\*$', re.MULTILINE), 'text/markdown'),
        ],
    }
    
    def __init__(self, read_size: int = 8192):
        """
        Initialize detector.
        
        Args:
            read_size: Number of bytes to read for magic detection
        """
        self.read_size = read_size
        mimetypes.init()
    
    def detect(self, filepath: Union[str, Path]) -> FileTypeResult:
        """
        Detect file type using multiple strategies.
        
        Args:
            filepath: Path to file
            
        Returns:
            FileTypeResult with detected information
        """
        path = Path(filepath)
        
        if not path.exists():
            return FileTypeResult(
                mime_type='application/octet-stream',
                category=FileCategory.UNKNOWN,
                extension=path.suffix.lower(),
                description='File not found',
                confidence=0.0,
                detected_by='error'
            )
        
        # Strategy 1: Magic bytes
        result = self._detect_by_magic(path)
        if result and result.confidence >= 0.9:
            return result
        
        # Strategy 2: Extension + MIME
        ext_result = self._detect_by_extension(path)
        
        # Strategy 3: Content analysis for text files
        if self._is_likely_text(path):
            content_result = self._detect_by_content(path)
            if content_result and content_result.confidence > (ext_result.confidence if ext_result else 0):
                return content_result
        
        # Return best result
        if result and ext_result:
            return result if result.confidence >= ext_result.confidence else ext_result
        return result or ext_result or FileTypeResult(
            mime_type='application/octet-stream',
            category=FileCategory.UNKNOWN,
            extension=path.suffix.lower(),
            description='Unknown file type',
            confidence=0.1,
            detected_by='fallback'
        )
    
    def _detect_by_magic(self, path: Path) -> Optional[FileTypeResult]:
        """Detect file type by magic bytes."""
        try:
            with open(path, 'rb') as f:
                header = f.read(self.read_size)
        except IOError:
            return None
        
        for sig in self.SIGNATURES:
            offset = sig.offset
            sig_len = len(sig.magic_bytes)
            
            if len(header) < offset + sig_len:
                continue
            
            chunk = header[offset:offset + sig_len]
            
            if sig.mask:
                # Apply mask for partial matching
                chunk = bytes(b & m for b, m in zip(chunk, sig.mask))
                match = chunk == bytes(b & m for b, m in zip(sig.magic_bytes, sig.mask))
            else:
                match = chunk == sig.magic_bytes
            
            if match:
                return FileTypeResult(
                    mime_type=sig.mime_type,
                    category=sig.category,
                    extension=sig.extensions[0] if sig.extensions else path.suffix.lower(),
                    description=sig.description,
                    confidence=0.95,
                    detected_by='magic'
                )
        
        return None
    
    def _detect_by_extension(self, path: Path) -> Optional[FileTypeResult]:
        """Detect file type by extension."""
        ext = path.suffix.lower()
        
        if not ext:
            return None
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        
        # Get category
        category = self.EXTENSION_CATEGORIES.get(ext, FileCategory.UNKNOWN)
        
        if mime_type:
            return FileTypeResult(
                mime_type=mime_type,
                category=category,
                extension=ext,
                description=f'{ext.upper()[1:]} File',
                confidence=0.7,
                detected_by='extension'
            )
        
        if category != FileCategory.UNKNOWN:
            return FileTypeResult(
                mime_type='application/octet-stream',
                category=category,
                extension=ext,
                description=f'{ext.upper()[1:]} File',
                confidence=0.5,
                detected_by='extension'
            )
        
        return None
    
    def _is_likely_text(self, path: Path) -> bool:
        """Check if file is likely text-based."""
        try:
            with open(path, 'rb') as f:
                sample = f.read(1024)
            
            # Check for null bytes (binary indicator)
            if b'\x00' in sample:
                return False
            
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try latin-1 (always succeeds but may indicate binary)
                text = sample.decode('latin-1')
                # Check printable ratio
                printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
                return printable / len(text) > 0.9
                
        except IOError:
            return False
    
    def _detect_by_content(self, path: Path) -> Optional[FileTypeResult]:
        """Detect text file type by content analysis."""
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(4096)
        except IOError:
            return None
        
        for category, patterns in self.TEXT_PATTERNS.items():
            for pattern, mime_type in patterns:
                if pattern.search(content):
                    return FileTypeResult(
                        mime_type=mime_type,
                        category=category,
                        extension=path.suffix.lower(),
                        description=f'{mime_type.split("/")[-1].upper()} File',
                        confidence=0.75,
                        detected_by='content'
                    )
        
        return None
    
    def get_category_for_extension(self, extension: str) -> FileCategory:
        """Get file category for an extension."""
        ext = extension.lower() if extension.startswith('.') else f'.{extension.lower()}'
        return self.EXTENSION_CATEGORIES.get(ext, FileCategory.UNKNOWN)


# Singleton instance
_detector: Optional[FileTypeDetector] = None


def get_detector() -> FileTypeDetector:
    """Get or create singleton detector instance."""
    global _detector
    if _detector is None:
        _detector = FileTypeDetector()
    return _detector


def detect_file_type(filepath: Union[str, Path]) -> FileTypeResult:
    """Convenience function for file type detection."""
    return get_detector().detect(filepath)
