"""
Plugin Validation System for OpenUP
====================================
Comprehensive validation for plugins to ensure stability and compatibility.
"""

from __future__ import annotations

import inspect
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity level for validation issues."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a plugin."""
    code: str
    message: str
    severity: ValidationSeverity
    plugin_name: str
    location: str = ""
    suggestion: str = ""
    
    def __str__(self) -> str:
        severity_str = self.severity.name
        return f"[{severity_str}] {self.plugin_name}: {self.message}"


@dataclass
class ValidationResult:
    """Result of plugin validation."""
    plugin_name: str
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues 
                   if i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL))
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)
    
    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)
        if issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL):
            self.is_valid = False
    
    def get_summary(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"{self.plugin_name}: {status} ({self.error_count} errors, {self.warning_count} warnings)"


class PluginValidator(ABC):
    """Abstract base class for plugin validators."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name."""
        pass
    
    @abstractmethod
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate a plugin.
        
        Args:
            plugin_class: The plugin class to validate
            plugin_info: Additional plugin information
            
        Returns:
            List of validation issues found
        """
        pass


class InterfaceValidator(PluginValidator):
    """Validates that plugin implements required interface."""
    
    def __init__(self, required_methods: Dict[str, Dict[str, Any]]):
        """
        Args:
            required_methods: Dict mapping method names to their expected signatures
                              e.g., {'can_preview': {'args': ['path'], 'returns': bool}}
        """
        self.required_methods = required_methods
    
    @property
    def name(self) -> str:
        return "InterfaceValidator"
    
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        issues = []
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        
        for method_name, spec in self.required_methods.items():
            # Check method exists
            if not hasattr(plugin_class, method_name):
                issues.append(ValidationIssue(
                    code="MISSING_METHOD",
                    message=f"Missing required method: {method_name}",
                    severity=ValidationSeverity.ERROR,
                    plugin_name=plugin_name,
                    location=f"{plugin_class.__name__}",
                    suggestion=f"Implement {method_name} method"
                ))
                continue
            
            method = getattr(plugin_class, method_name)
            
            # Check it's callable
            if not callable(method):
                issues.append(ValidationIssue(
                    code="NOT_CALLABLE",
                    message=f"{method_name} is not callable",
                    severity=ValidationSeverity.ERROR,
                    plugin_name=plugin_name
                ))
                continue
            
            # Check signature if specified
            if 'args' in spec:
                try:
                    sig = inspect.signature(method)
                    params = [p for p in sig.parameters.keys() if p != 'self']
                    expected_args = spec['args']
                    
                    if len(params) < len(expected_args):
                        issues.append(ValidationIssue(
                            code="SIGNATURE_MISMATCH",
                            message=f"{method_name} has fewer parameters than expected",
                            severity=ValidationSeverity.WARNING,
                            plugin_name=plugin_name,
                            suggestion=f"Expected parameters: {expected_args}"
                        ))
                except Exception:
                    pass  # Can't inspect signature, skip
        
        return issues


class MetadataValidator(PluginValidator):
    """Validates plugin metadata completeness."""
    
    REQUIRED_FIELDS = ['name', 'version']
    OPTIONAL_FIELDS = ['description', 'author', 'license', 'supported_extensions']
    
    @property
    def name(self) -> str:
        return "MetadataValidator"
    
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        issues = []
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in plugin_info or not plugin_info[field]:
                issues.append(ValidationIssue(
                    code="MISSING_METADATA",
                    message=f"Missing required metadata: {field}",
                    severity=ValidationSeverity.ERROR,
                    plugin_name=plugin_name,
                    suggestion=f"Add '{field}' to plugin metadata"
                ))
        
        # Check optional fields
        for field in self.OPTIONAL_FIELDS:
            if field not in plugin_info:
                issues.append(ValidationIssue(
                    code="MISSING_OPTIONAL",
                    message=f"Missing optional metadata: {field}",
                    severity=ValidationSeverity.INFO,
                    plugin_name=plugin_name,
                    suggestion=f"Consider adding '{field}' for better discoverability"
                ))
        
        # Validate version format
        if 'version' in plugin_info:
            version = plugin_info['version']
            if not self._is_valid_version(version):
                issues.append(ValidationIssue(
                    code="INVALID_VERSION",
                    message=f"Invalid version format: {version}",
                    severity=ValidationSeverity.WARNING,
                    plugin_name=plugin_name,
                    suggestion="Use semantic versioning (e.g., 1.0.0)"
                ))
        
        return issues
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semantic versioning."""
        parts = version.split('.')
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        for part in parts:
            # Allow numeric parts and pre-release suffixes like 'beta1'
            clean = ''.join(c for c in part if c.isdigit())
            if not clean:
                return False
        
        return True


class DependencyValidator(PluginValidator):
    """Validates plugin dependencies are available."""
    
    @property
    def name(self) -> str:
        return "DependencyValidator"
    
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        issues = []
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        
        dependencies = plugin_info.get('dependencies', [])
        
        for dep in dependencies:
            # Parse dependency spec (e.g., "numpy>=1.20")
            dep_name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('<')[0].split('>')[0]
            dep_name = dep_name.strip()
            
            # Check if module is importable
            try:
                __import__(dep_name)
            except ImportError:
                issues.append(ValidationIssue(
                    code="MISSING_DEPENDENCY",
                    message=f"Missing dependency: {dep}",
                    severity=ValidationSeverity.ERROR,
                    plugin_name=plugin_name,
                    suggestion=f"Install with: pip install {dep}"
                ))
        
        return issues


class ResourceValidator(PluginValidator):
    """Validates plugin resource files exist."""
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
    
    @property
    def name(self) -> str:
        return "ResourceValidator"
    
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        issues = []
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        
        resources = plugin_info.get('resources', [])
        
        for resource in resources:
            resource_path = self.plugin_dir / resource
            
            if not resource_path.exists():
                issues.append(ValidationIssue(
                    code="MISSING_RESOURCE",
                    message=f"Missing resource file: {resource}",
                    severity=ValidationSeverity.WARNING,
                    plugin_name=plugin_name,
                    suggestion=f"Create the file at: {resource_path}"
                ))
        
        return issues


class SecurityValidator(PluginValidator):
    """Basic security validation for plugins."""
    
    DANGEROUS_PATTERNS = [
        ('eval(', "Use of eval() is dangerous"),
        ('exec(', "Use of exec() is dangerous"),
        ('__import__', "Dynamic imports can be risky"),
        ('subprocess.call(', "Shell command execution detected"),
        ('os.system(', "Shell command execution detected"),
        ('pickle.loads(', "Unpickling arbitrary data is dangerous"),
    ]
    
    @property
    def name(self) -> str:
        return "SecurityValidator"
    
    def validate(self, plugin_class: Type, plugin_info: Dict[str, Any]) -> List[ValidationIssue]:
        issues = []
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        
        # Get source code if available
        try:
            source = inspect.getsource(plugin_class)
        except (OSError, TypeError):
            # Can't get source, skip security validation
            return issues
        
        for pattern, description in self.DANGEROUS_PATTERNS:
            if pattern in source:
                issues.append(ValidationIssue(
                    code="SECURITY_WARNING",
                    message=f"Potential security issue: {description}",
                    severity=ValidationSeverity.WARNING,
                    plugin_name=plugin_name,
                    suggestion="Review this usage for security implications"
                ))
        
        return issues


class PluginValidationSystem:
    """
    Complete plugin validation system.
    
    Aggregates multiple validators and provides comprehensive validation.
    """
    
    def __init__(self, plugin_base_class: Optional[Type] = None):
        """
        Initialize validation system.
        
        Args:
            plugin_base_class: Base class plugins should inherit from
        """
        self.plugin_base_class = plugin_base_class
        self.validators: List[PluginValidator] = []
        
        # Add default validators
        self._add_default_validators()
    
    def _add_default_validators(self):
        """Add default validators."""
        # Metadata validator
        self.validators.append(MetadataValidator())
        
        # Security validator
        self.validators.append(SecurityValidator())
        
        # Dependency validator
        self.validators.append(DependencyValidator())
    
    def add_validator(self, validator: PluginValidator):
        """Add a custom validator."""
        self.validators.append(validator)
    
    def validate(
        self,
        plugin_class: Type,
        plugin_info: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a plugin class.
        
        Args:
            plugin_class: Plugin class to validate
            plugin_info: Plugin metadata dict
            
        Returns:
            ValidationResult with all issues found
        """
        if plugin_info is None:
            plugin_info = self._extract_plugin_info(plugin_class)
        
        plugin_name = plugin_info.get('name', plugin_class.__name__)
        result = ValidationResult(plugin_name=plugin_name, is_valid=True)
        
        # Check base class inheritance
        if self.plugin_base_class is not None:
            if not issubclass(plugin_class, self.plugin_base_class):
                result.add_issue(ValidationIssue(
                    code="INVALID_BASE",
                    message=f"Plugin does not inherit from {self.plugin_base_class.__name__}",
                    severity=ValidationSeverity.ERROR,
                    plugin_name=plugin_name,
                    suggestion=f"Make {plugin_class.__name__} inherit from {self.plugin_base_class.__name__}"
                ))
        
        # Run all validators
        for validator in self.validators:
            try:
                issues = validator.validate(plugin_class, plugin_info)
                for issue in issues:
                    result.add_issue(issue)
            except Exception as e:
                logger.error(f"Validator {validator.name} failed: {e}")
                result.add_issue(ValidationIssue(
                    code="VALIDATOR_ERROR",
                    message=f"Validation failed: {e}",
                    severity=ValidationSeverity.WARNING,
                    plugin_name=plugin_name
                ))
        
        # Extract metadata
        result.metadata = plugin_info
        
        return result
    
    def validate_all(
        self,
        plugins: Dict[str, Type],
        plugin_infos: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple plugins.
        
        Args:
            plugins: Dict mapping plugin names to classes
            plugin_infos: Optional dict mapping plugin names to metadata
            
        Returns:
            Dict mapping plugin names to validation results
        """
        results = {}
        
        for name, plugin_class in plugins.items():
            info = plugin_infos.get(name, {}) if plugin_infos else {}
            info.setdefault('name', name)
            results[name] = self.validate(plugin_class, info)
        
        return results
    
    def _extract_plugin_info(self, plugin_class: Type) -> Dict[str, Any]:
        """Extract metadata from plugin class attributes."""
        info = {}
        
        # Standard metadata attributes
        for attr in ['name', 'version', 'description', 'author', 'license',
                     'supported_extensions', 'dependencies', 'resources']:
            if hasattr(plugin_class, attr):
                info[attr] = getattr(plugin_class, attr)
        
        # Try PLUGIN_INFO dict
        if hasattr(plugin_class, 'PLUGIN_INFO'):
            info.update(plugin_class.PLUGIN_INFO)
        
        # Default name from class
        if 'name' not in info:
            info['name'] = plugin_class.__name__
        
        return info
    
    def generate_report(self, results: Dict[str, ValidationResult]) -> str:
        """Generate a validation report."""
        lines = ["=" * 60, "Plugin Validation Report", "=" * 60, ""]
        
        # Summary
        valid_count = sum(1 for r in results.values() if r.is_valid)
        total_count = len(results)
        
        lines.append(f"Plugins validated: {total_count}")
        lines.append(f"Valid: {valid_count}")
        lines.append(f"Invalid: {total_count - valid_count}")
        lines.append("")
        
        # Details per plugin
        for name, result in sorted(results.items()):
            lines.append("-" * 40)
            lines.append(result.get_summary())
            
            if result.issues:
                for issue in result.issues:
                    prefix = "  "
                    if issue.severity == ValidationSeverity.ERROR:
                        prefix = "  ❌ "
                    elif issue.severity == ValidationSeverity.WARNING:
                        prefix = "  ⚠️ "
                    elif issue.severity == ValidationSeverity.INFO:
                        prefix = "  ℹ️ "
                    
                    lines.append(f"{prefix}{issue.message}")
                    if issue.suggestion:
                        lines.append(f"      → {issue.suggestion}")
            
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


# Factory function for common plugin types
def create_preview_plugin_validator() -> PluginValidationSystem:
    """Create a validator for preview plugins (OpenUP specific)."""
    system = PluginValidationSystem()
    
    # Add interface validator for preview plugins
    system.add_validator(InterfaceValidator({
        'can_preview': {'args': ['path'], 'returns': bool},
        'get_preview_widget': {'args': ['path'], 'returns': 'QWidget'},
        'get_supported_extensions': {'args': [], 'returns': list}
    }))
    
    return system
