#!/usr/bin/env python3
"""
CSV to JSON API Converter - Production Grade Implementation
============================================================
A clean, modular, and efficient CSV/Excel to JSON API converter.

Features:
- Multi-format input (CSV, TSV, Excel)
- Intelligent type detection and conversion
- Data validation and quality metrics
- Lightweight REST API server
- Streaming support for large files
- Clean modular architecture

Dependencies: Only essential ones - pandas, flask, flask-cors, openpyxl
Author: Refactored Production Version
Version: 3.0.0
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import signal
import sys
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from functools import wraps
from http import HTTPStatus
from io import StringIO
from pathlib import Path
from typing import (
    Any, Callable, Dict, Iterator, List, 
    Optional, Tuple, Type, TypeVar, Union
)

# Minimal required dependencies
import pandas as pd
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('csv_to_json.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""
    VERSION: str = "3.0.0"
    DEFAULT_PORT: int = 5000
    DEFAULT_HOST: str = "127.0.0.1"
    MAX_FILE_SIZE_MB: int = 500
    CHUNK_SIZE: int = 10000
    PREVIEW_LIMIT: int = 100
    MAX_SAMPLE_SIZE: int = 1000
    SUPPORTED_ENCODINGS: Tuple[str, ...] = (
        'utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii'
    )
    SUPPORTED_DELIMITERS: Tuple[str, ...] = (',', ';', '\t', '|', ':')
    DATE_FORMATS: Tuple[str, ...] = (
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
        '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S'
    )


CONFIG = AppConfig()


# =============================================================================
# DATA TYPES AND MODELS
# =============================================================================

@dataclass
class ColumnMetadata:
    """Metadata for a single column."""
    name: str
    original_name: str
    inferred_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    sample_values: List[Any] = field(default_factory=list)
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'original_name': self.original_name,
            'type': self.inferred_type,
            'null_count': self.null_count,
            'null_percentage': round(self.null_percentage, 2),
            'unique_count': self.unique_count,
            'unique_percentage': round(self.unique_percentage, 2),
            'sample_values': self.sample_values[:5],
            'min_value': self._serialize_value(self.min_value),
            'max_value': self._serialize_value(self.max_value),
            'mean_value': round(self.mean_value, 4) if self.mean_value else None
        }
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize value for JSON output."""
        if pd.isna(value):
            return None
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value


@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics."""
    total_rows: int
    total_columns: int
    total_cells: int
    null_cells: int
    completeness_score: float
    duplicate_rows: int
    uniqueness_score: float
    memory_usage_bytes: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'total_cells': self.total_cells,
            'null_cells': self.null_cells,
            'completeness_score': round(self.completeness_score, 2),
            'duplicate_rows': self.duplicate_rows,
            'uniqueness_score': round(self.uniqueness_score, 2),
            'memory_usage_mb': round(self.memory_usage_bytes / (1024 * 1024), 2)
        }


@dataclass
class ProcessingResult:
    """Result of file processing operation."""
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    columns: List[ColumnMetadata] = field(default_factory=list)
    quality_metrics: Optional[DataQualityMetrics] = None
    source_file: str = ""
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class ProcessingError(Exception):
    """Custom exception for processing errors."""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


# =============================================================================
# TYPE INFERENCE ENGINE
# =============================================================================

class TypeInferenceEngine:
    """
    Intelligent type inference engine using statistical sampling.
    
    Analyzes column values to determine the most appropriate data type
    using pattern matching and value analysis.
    """
    
    # Type patterns for string detection
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    URL_PATTERN = re.compile(
        r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    )
    PHONE_PATTERN = re.compile(
        r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}$'
    )
    UUID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    def __init__(self, sample_size: int = CONFIG.MAX_SAMPLE_SIZE):
        self.sample_size = sample_size
    
    def infer_column_type(self, series: pd.Series) -> str:
        """
        Infer the type of a pandas Series.
        
        Args:
            series: The pandas Series to analyze
            
        Returns:
            String representing the inferred type
        """
        # Get non-null values for analysis
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'null'
        
        # Sample if too large
        if len(non_null) > self.sample_size:
            sample = non_null.sample(n=self.sample_size, random_state=42)
        else:
            sample = non_null
        
        # Check pandas dtype first
        dtype = series.dtype
        
        if pd.api.types.is_integer_dtype(dtype):
            return 'integer'
        elif pd.api.types.is_float_dtype(dtype):
            # Check if it's actually integer stored as float
            if self._is_integer_float(sample):
                return 'integer'
            return 'float'
        elif pd.api.types.is_bool_dtype(dtype):
            return 'boolean'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'datetime'
        
        # For object dtype, analyze string patterns
        return self._infer_string_type(sample)
    
    def _is_integer_float(self, series: pd.Series) -> bool:
        """Check if float values are actually integers."""
        try:
            return (series == series.astype(int)).all()
        except (ValueError, TypeError):
            return False
    
    def _infer_string_type(self, sample: pd.Series) -> str:
        """Infer type from string values using pattern matching."""
        str_sample = sample.astype(str)
        total = len(str_sample)
        
        # Check for boolean-like values
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 'y', 'n'}
        bool_count = sum(1 for v in str_sample if v.lower() in bool_values)
        if bool_count / total > 0.9:
            return 'boolean'
        
        # Check for numeric values
        numeric_count = 0
        integer_count = 0
        for value in str_sample:
            try:
                float_val = float(value.replace(',', ''))
                numeric_count += 1
                if float_val == int(float_val):
                    integer_count += 1
            except (ValueError, TypeError):
                continue
        
        if numeric_count / total > 0.9:
            if integer_count == numeric_count:
                return 'integer'
            return 'float'
        
        # Check for datetime values
        date_count = self._count_date_matches(str_sample)
        if date_count / total > 0.8:
            return 'datetime'
        
        # Check for special string patterns
        patterns = [
            (self.EMAIL_PATTERN, 'email'),
            (self.URL_PATTERN, 'url'),
            (self.UUID_PATTERN, 'uuid'),
            (self.PHONE_PATTERN, 'phone')
        ]
        
        for pattern, type_name in patterns:
            match_count = sum(1 for v in str_sample if pattern.match(v))
            if match_count / total > 0.8:
                return type_name
        
        # Default to string
        unique_ratio = sample.nunique() / total
        if unique_ratio < 0.1:
            return 'category'
        
        return 'string'
    
    def _count_date_matches(self, series: pd.Series) -> int:
        """Count values that match date formats."""
        count = 0
        for value in series:
            for fmt in CONFIG.DATE_FORMATS:
                try:
                    datetime.strptime(str(value), fmt)
                    count += 1
                    break
                except ValueError:
                    continue
        return count


# =============================================================================
# DATA PROCESSOR
# =============================================================================

class DataProcessor:
    """
    Core data processing engine.
    
    Handles file loading, data cleaning, type conversion,
    and metadata generation.
    """
    
    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.type_engine = TypeInferenceEngine()
        self._column_name_registry: Dict[str, int] = {}
    
    def process_file(
        self, 
        file_path: Union[str, Path],
        preview_only: bool = False,
        preview_limit: int = None
    ) -> ProcessingResult:
        """
        Process a file and return structured result.
        
        Args:
            file_path: Path to the file to process
            preview_only: If True, only process first N rows
            preview_limit: Number of rows for preview mode
            
        Returns:
            ProcessingResult containing data and metadata
        """
        start_time = datetime.now()
        warnings: List[str] = []
        
        try:
            file_path = Path(file_path)
            
            # Validate file
            self._validate_file(file_path)
            
            # Load data
            df = self._load_file(file_path)
            logger.info(f"Loaded file with shape: {df.shape}")
            
            if df.empty:
                return ProcessingResult(
                    success=False,
                    error_message="File contains no data"
                )
            
            # Clean data
            df, clean_warnings = self._clean_dataframe(df)
            warnings.extend(clean_warnings)
            
            # Apply preview limit if needed
            if preview_only:
                limit = preview_limit or self.config.PREVIEW_LIMIT
                df = df.head(limit)
            
            # Generate column metadata
            columns = self._generate_column_metadata(df)
            
            # Generate quality metrics
            quality_metrics = self._calculate_quality_metrics(df)
            
            # Convert to records
            data = self._convert_to_records(df)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=data,
                columns=columns,
                quality_metrics=quality_metrics,
                source_file=str(file_path.name),
                processing_time_seconds=processing_time,
                warnings=warnings
            )
            
        except Exception as e:
            logger.exception(f"Processing failed: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e)
            )
    
    def _validate_file(self, file_path: Path) -> None:
        """Validate file exists and is accessible."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.config.MAX_FILE_SIZE_MB:
            raise ValidationError(
                f"File size ({size_mb:.1f}MB) exceeds limit "
                f"({self.config.MAX_FILE_SIZE_MB}MB)"
            )
        
        # Check extension
        valid_extensions = {'.csv', '.tsv', '.txt', '.xlsx', '.xls'}
        if file_path.suffix.lower() not in valid_extensions:
            raise ValidationError(
                f"Unsupported file type: {file_path.suffix}"
            )
    
    def _load_file(self, file_path: Path) -> pd.DataFrame:
        """Load file based on extension."""
        ext = file_path.suffix.lower()
        
        if ext in ('.csv', '.tsv', '.txt'):
            return self._load_csv(file_path)
        elif ext in ('.xlsx', '.xls'):
            return self._load_excel(file_path)
        else:
            raise ValidationError(f"Unsupported file type: {ext}")
    
    def _load_csv(self, file_path: Path) -> pd.DataFrame:
        """Load CSV file with intelligent encoding and delimiter detection."""
        detected_encoding = None
        detected_delimiter = None
        
        # Detect encoding
        for encoding in self.config.SUPPORTED_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    sample = f.read(8192)
                detected_encoding = encoding
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if detected_encoding is None:
            raise ProcessingError("Could not detect file encoding")
        
        # Detect delimiter using csv.Sniffer
        try:
            with open(file_path, 'r', encoding=detected_encoding) as f:
                sample = f.read(8192)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample, delimiters=',;\t|:')
                detected_delimiter = dialect.delimiter
        except csv.Error:
            # Fallback: count delimiters and use most common
            detected_delimiter = self._detect_delimiter_by_count(sample)
        
        logger.info(
            f"Detected encoding: {detected_encoding}, "
            f"delimiter: '{detected_delimiter}'"
        )
        
        # Load with pandas
        try:
            df = pd.read_csv(
                file_path,
                encoding=detected_encoding,
                delimiter=detected_delimiter,
                low_memory=False,
                on_bad_lines='warn'
            )
            
            # Check if loaded correctly (more than 1 column)
            if len(df.columns) == 1:
                # Try other delimiters
                for delim in self.config.SUPPORTED_DELIMITERS:
                    if delim == detected_delimiter:
                        continue
                    try:
                        test_df = pd.read_csv(
                            file_path,
                            encoding=detected_encoding,
                            delimiter=delim,
                            nrows=5
                        )
                        if len(test_df.columns) > 1:
                            df = pd.read_csv(
                                file_path,
                                encoding=detected_encoding,
                                delimiter=delim,
                                low_memory=False
                            )
                            break
                    except:
                        continue
            
            return df
            
        except Exception as e:
            raise ProcessingError(f"Failed to parse CSV: {e}")
    
    def _detect_delimiter_by_count(self, sample: str) -> str:
        """Detect delimiter by counting occurrences."""
        counts = {
            delim: sample.count(delim) 
            for delim in self.config.SUPPORTED_DELIMITERS
        }
        return max(counts, key=counts.get)
    
    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """Load Excel file."""
        try:
            # Try openpyxl engine first (for .xlsx)
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception:
            try:
                # Fallback to xlrd for older .xls files
                df = pd.read_excel(file_path, engine='xlrd')
            except Exception as e:
                raise ProcessingError(f"Failed to load Excel file: {e}")
        
        return df
    
    def _clean_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Clean and standardize DataFrame."""
        warnings = []
        original_rows = len(df)
        
        # Reset column name registry
        self._column_name_registry = {}
        
        # Clean column names
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        removed_rows = original_rows - len(df)
        if removed_rows > 0:
            warnings.append(f"Removed {removed_rows} empty rows")
        
        # Remove completely empty columns
        original_cols = len(df.columns)
        df = df.dropna(axis=1, how='all')
        removed_cols = original_cols - len(df.columns)
        if removed_cols > 0:
            warnings.append(f"Removed {removed_cols} empty columns")
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )
        
        return df, warnings
    
    def _clean_column_name(self, name: Any) -> str:
        """
        Clean and standardize column name.
        
        Handles:
        - Non-string values
        - Special characters
        - Whitespace
        - Name collisions
        """
        # Convert to string
        name = str(name).strip()
        
        if not name or name.lower() in ('unnamed', 'nan', 'none'):
            name = 'column'
        
        # Replace special characters with underscore
        name = re.sub(r'[^\w\s]', '_', name)
        
        # Replace whitespace with underscore
        name = re.sub(r'\s+', '_', name)
        
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = f'col_{name}'
        
        # Convert to lowercase
        name = name.lower()
        
        # Handle empty name
        if not name:
            name = 'column'
        
        # Handle duplicates
        base_name = name
        counter = self._column_name_registry.get(base_name, 0)
        if counter > 0:
            name = f"{base_name}_{counter}"
        self._column_name_registry[base_name] = counter + 1
        
        return name
    
    def _generate_column_metadata(
        self, 
        df: pd.DataFrame
    ) -> List[ColumnMetadata]:
        """Generate metadata for each column."""
        metadata = []
        
        for col in df.columns:
            series = df[col]
            non_null = series.dropna()
            total = len(series)
            
            # Basic counts
            null_count = int(series.isnull().sum())
            unique_count = int(series.nunique())
            
            # Infer type
            inferred_type = self.type_engine.infer_column_type(series)
            
            # Get sample values
            sample_values = non_null.head(5).tolist()
            sample_values = [
                self._serialize_for_json(v) for v in sample_values
            ]
            
            # Statistics for numeric types
            min_val = max_val = mean_val = None
            if inferred_type in ('integer', 'float'):
                try:
                    numeric_series = pd.to_numeric(series, errors='coerce')
                    min_val = float(numeric_series.min())
                    max_val = float(numeric_series.max())
                    mean_val = float(numeric_series.mean())
                except:
                    pass
            
            metadata.append(ColumnMetadata(
                name=col,
                original_name=col,  # Already cleaned
                inferred_type=inferred_type,
                null_count=null_count,
                null_percentage=(null_count / total * 100) if total > 0 else 0,
                unique_count=unique_count,
                unique_percentage=(unique_count / total * 100) if total > 0 else 0,
                sample_values=sample_values,
                min_value=min_val,
                max_value=max_val,
                mean_value=mean_val
            ))
        
        return metadata
    
    def _calculate_quality_metrics(self, df: pd.DataFrame) -> DataQualityMetrics:
        """Calculate data quality metrics."""
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols
        null_cells = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        
        completeness = ((total_cells - null_cells) / total_cells * 100) \
            if total_cells > 0 else 100
        
        uniqueness = ((total_rows - duplicate_rows) / total_rows * 100) \
            if total_rows > 0 else 100
        
        return DataQualityMetrics(
            total_rows=total_rows,
            total_columns=total_cols,
            total_cells=total_cells,
            null_cells=null_cells,
            completeness_score=completeness,
            duplicate_rows=duplicate_rows,
            uniqueness_score=uniqueness,
            memory_usage_bytes=int(df.memory_usage(deep=True).sum())
        )
    
    def _convert_to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of dictionaries with proper serialization."""
        records = []
        
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                value = row[col]
                record[col] = self._serialize_for_json(value)
            records.append(record)
        
        return records
    
    def _serialize_for_json(self, value: Any) -> Any:
        """Serialize value for JSON output."""
        if pd.isna(value):
            return None
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (int, float, str, bool)):
            return value
        if hasattr(value, 'item'):  # numpy types
            return value.item()
        return str(value)


# =============================================================================
# API GENERATOR
# =============================================================================

@dataclass
class APIStructure:
    """Generated API structure."""
    api_info: Dict[str, Any]
    metadata: Dict[str, Any]
    endpoints: Dict[str, str]
    data: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'api_info': self.api_info,
            'metadata': self.metadata,
            'endpoints': self.endpoints,
            'data': self.data
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class APIGenerator:
    """Generates structured API output from processing result."""
    
    def __init__(self, port: int = CONFIG.DEFAULT_PORT):
        self.port = port
        self.base_url = f"http://{CONFIG.DEFAULT_HOST}:{port}"
    
    def generate(self, result: ProcessingResult) -> APIStructure:
        """Generate API structure from processing result."""
        if not result.success:
            raise ValueError(f"Cannot generate API from failed result: {result.error_message}")
        
        api_info = {
            'version': CONFIG.VERSION,
            'title': f"{Path(result.source_file).stem} API",
            'description': f"Auto-generated JSON API from {result.source_file}",
            'generated_at': datetime.now().isoformat(),
            'source_file': result.source_file,
            'processing_time_seconds': round(result.processing_time_seconds, 3)
        }
        
        metadata = {
            'total_records': len(result.data),
            'total_fields': len(result.columns),
            'fields': [col.name for col in result.columns],
            'fields_info': {col.name: col.to_dict() for col in result.columns},
            'quality_metrics': result.quality_metrics.to_dict() if result.quality_metrics else None,
            'warnings': result.warnings
        }
        
        endpoints = {
            'health': f"{self.base_url}/api/health",
            'all_data': f"{self.base_url}/api/data",
            'single_record': f"{self.base_url}/api/data/{{id}}",
            'search': f"{self.base_url}/api/data/search?q={{query}}",
            'filter': f"{self.base_url}/api/data/filter?field={{field}}&value={{value}}",
            'paginate': f"{self.base_url}/api/data?page={{page}}&limit={{limit}}",
            'fields': f"{self.base_url}/api/fields",
            'stats': f"{self.base_url}/api/stats"
        }
        
        return APIStructure(
            api_info=api_info,
            metadata=metadata,
            endpoints=endpoints,
            data=result.data
        )


# =============================================================================
# FLASK REST API SERVER
# =============================================================================

class APIServer:
    """
    Lightweight Flask REST API server.
    
    Provides RESTful endpoints for accessing processed data.
    Supports pagination, filtering, and search.
    """
    
    def __init__(self, port: int = CONFIG.DEFAULT_PORT):
        self.port = port
        self.host = CONFIG.DEFAULT_HOST
        self.app = Flask(__name__)
        CORS(self.app)
        
        self._api_data: Optional[APIStructure] = None
        self._server_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        self._setup_routes()
    
    def load_data(self, api_structure: APIStructure) -> None:
        """Load API data structure."""
        self._api_data = api_structure
        logger.info(f"Loaded {len(api_structure.data)} records")
    
    def _setup_routes(self) -> None:
        """Configure all API routes."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'data_loaded': self._api_data is not None,
                'record_count': len(self._api_data.data) if self._api_data else 0,
                'timestamp': datetime.now().isoformat(),
                'version': CONFIG.VERSION
            })
        
        @self.app.route('/api/data', methods=['GET'])
        def get_data():
            """Get all data with pagination."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            try:
                page = request.args.get('page', 1, type=int)
                limit = request.args.get('limit', 100, type=int)
                
                # Validate parameters
                page = max(1, page)
                limit = max(1, min(limit, 1000))
                
                data = self._api_data.data
                total = len(data)
                total_pages = (total + limit - 1) // limit
                
                start = (page - 1) * limit
                end = start + limit
                
                return jsonify({
                    'success': True,
                    'data': data[start:end],
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total_records': total,
                        'total_pages': total_pages,
                        'has_next': page < total_pages,
                        'has_prev': page > 1
                    }
                })
                
            except Exception as e:
                logger.exception("Error in get_data")
                return jsonify({
                    'success': False, 
                    'error': str(e)
                }), HTTPStatus.INTERNAL_SERVER_ERROR
        
        @self.app.route('/api/data/<int:record_id>', methods=['GET'])
        def get_record(record_id: int):
            """Get single record by ID."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            data = self._api_data.data
            
            if 0 <= record_id < len(data):
                return jsonify({
                    'success': True,
                    'id': record_id,
                    'data': data[record_id]
                })
            
            return jsonify({
                'success': False,
                'error': f'Record {record_id} not found'
            }), HTTPStatus.NOT_FOUND
        
        @self.app.route('/api/data/search', methods=['GET'])
        def search_data():
            """Search data across all fields."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            query = request.args.get('q', '').lower().strip()
            
            if not query:
                return jsonify({
                    'success': False,
                    'error': 'Query parameter "q" is required'
                }), HTTPStatus.BAD_REQUEST
            
            results = []
            for idx, record in enumerate(self._api_data.data):
                for value in record.values():
                    if value is not None and query in str(value).lower():
                        results.append({'_id': idx, **record})
                        break
            
            return jsonify({
                'success': True,
                'query': query,
                'count': len(results),
                'results': results
            })
        
        @self.app.route('/api/data/filter', methods=['GET'])
        def filter_data():
            """Filter data by field and value."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            field = request.args.get('field', '').strip()
            value = request.args.get('value', '').strip()
            
            if not field:
                return jsonify({
                    'success': False,
                    'error': 'Parameter "field" is required'
                }), HTTPStatus.BAD_REQUEST
            
            # Check if field exists
            valid_fields = [col.name for col in self._api_data.metadata['fields_info'].values()]
            if field not in valid_fields:
                return jsonify({
                    'success': False,
                    'error': f'Unknown field: {field}'
                }), HTTPStatus.BAD_REQUEST
            
            results = []
            for idx, record in enumerate(self._api_data.data):
                record_value = record.get(field)
                if record_value is not None and str(record_value).lower() == value.lower():
                    results.append({'_id': idx, **record})
            
            return jsonify({
                'success': True,
                'field': field,
                'value': value,
                'count': len(results),
                'results': results
            })
        
        @self.app.route('/api/fields', methods=['GET'])
        def get_fields():
            """Get field information."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            return jsonify({
                'success': True,
                'fields': self._api_data.metadata['fields_info'],
                'field_names': self._api_data.metadata['fields']
            })
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get data statistics."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            return jsonify({
                'success': True,
                'api_info': self._api_data.api_info,
                'quality_metrics': self._api_data.metadata['quality_metrics'],
                'total_records': self._api_data.metadata['total_records'],
                'total_fields': self._api_data.metadata['total_fields']
            })
        
        @self.app.route('/api/export', methods=['GET'])
        def export_data():
            """Export all data as JSON."""
            if not self._api_data:
                return jsonify({'error': 'No data loaded'}), HTTPStatus.NOT_FOUND
            
            return Response(
                self._api_data.to_json(),
                mimetype='application/json',
                headers={
                    'Content-Disposition': 
                        f'attachment; filename={self._api_data.api_info["source_file"]}.json'
                }
            )
    
    def start(self, threaded: bool = True) -> None:
        """Start the API server."""
        if threaded:
            self._server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"API server started on http://{self.host}:{self.port}")
        else:
            self._run_server()
    
    def _run_server(self) -> None:
        """Run the Flask server."""
        from werkzeug.serving import make_server
        
        self._server = make_server(self.host, self.port, self.app)
        self._server.serve_forever()
    
    def stop(self) -> None:
        """Stop the API server."""
        if hasattr(self, '_server'):
            self._server.shutdown()
            logger.info("API server stopped")


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

class CLI:
    """Command line interface for the CSV to JSON API tool."""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.server: Optional[APIServer] = None
    
    def run(self, args: List[str] = None) -> int:
        """Run CLI with given arguments."""
        import argparse
        
        parser = argparse.ArgumentParser(
            description='CSV to JSON API Converter',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s data.csv                      Convert CSV and save as JSON
  %(prog)s data.xlsx -o api.json         Convert Excel to JSON
  %(prog)s data.csv --serve              Start API server
  %(prog)s data.csv --serve --port 8080  Start API server on port 8080
            """
        )
        
        parser.add_argument(
            'input_file',
            help='Input CSV or Excel file'
        )
        parser.add_argument(
            '-o', '--output',
            help='Output JSON file (default: <input>_api.json)'
        )
        parser.add_argument(
            '--serve',
            action='store_true',
            help='Start REST API server after processing'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=CONFIG.DEFAULT_PORT,
            help=f'API server port (default: {CONFIG.DEFAULT_PORT})'
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Process only first 100 rows'
        )
        parser.add_argument(
            '--preview-limit',
            type=int,
            default=CONFIG.PREVIEW_LIMIT,
            help='Number of rows for preview mode'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {CONFIG.VERSION}'
        )
        
        args = parser.parse_args(args)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            # Process file
            print(f"Processing: {args.input_file}")
            result = self.processor.process_file(
                args.input_file,
                preview_only=args.preview,
                preview_limit=args.preview_limit
            )
            
            if not result.success:
                print(f"Error: {result.error_message}")
                return 1
            
            # Generate API structure
            generator = APIGenerator(port=args.port)
            api_structure = generator.generate(result)
            
            # Print summary
            self._print_summary(result)
            
            # Save to file
            output_file = args.output or f"{Path(args.input_file).stem}_api.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(api_structure.to_json())
            print(f"Output saved to: {output_file}")
            
            # Start server if requested
            if args.serve:
                return self._start_server(api_structure, args.port)
            
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            logger.exception("CLI error")
            return 1
    
    def _print_summary(self, result: ProcessingResult) -> None:
        """Print processing summary."""
        print("\n" + "=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Source File: {result.source_file}")
        print(f"Records: {len(result.data)}")
        print(f"Columns: {len(result.columns)}")
        print(f"Processing Time: {result.processing_time_seconds:.3f}s")
        
        if result.quality_metrics:
            qm = result.quality_metrics
            print(f"\nData Quality:")
            print(f"  Completeness: {qm.completeness_score:.1f}%")
            print(f"  Uniqueness: {qm.uniqueness_score:.1f}%")
            print(f"  Null Cells: {qm.null_cells}")
            print(f"  Duplicate Rows: {qm.duplicate_rows}")
        
        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("\nColumn Info:")
        for col in result.columns[:10]:  # Show first 10
            print(f"  {col.name}: {col.inferred_type} "
                  f"({col.null_percentage:.1f}% null)")
        
        if len(result.columns) > 10:
            print(f"  ... and {len(result.columns) - 10} more columns")
        
        print("=" * 50 + "\n")
    
    def _start_server(self, api_structure: APIStructure, port: int) -> int:
        """Start the API server."""
        self.server = APIServer(port=port)
        self.server.load_data(api_structure)
        
        print(f"\nStarting API server on http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop\n")
        print("Available endpoints:")
        for name, url in api_structure.endpoints.items():
            print(f"  {name}: {url}")
        print()
        
        # Handle shutdown
        def signal_handler(signum, frame):
            print("\nShutting down server...")
            self.server.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start server (blocking)
        self.server.start(threaded=False)
        return 0


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
