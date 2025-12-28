"""
Memory Manager for OpenUP
=========================
Intelligent memory monitoring and management for preview operations.
"""

from __future__ import annotations

import gc
import logging
import os
import sys
import threading
import time
import weakref
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def get_process_memory_mb() -> float:
    """Get current process memory usage in MB."""
    try:
        if sys.platform == 'win32':
            import ctypes
            from ctypes import wintypes
            
            kernel32 = ctypes.windll.kernel32
            
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]
            
            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            
            psapi = ctypes.windll.psapi
            handle = kernel32.GetCurrentProcess()
            
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
                return pmc.WorkingSetSize / (1024 * 1024)
        else:
            # Unix-based systems
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return usage.ru_maxrss / 1024  # Convert KB to MB
            
    except Exception as e:
        logger.debug(f"Could not get memory info: {e}")
    
    return 0.0


def get_system_memory_info() -> Dict[str, float]:
    """Get system memory information."""
    try:
        if sys.platform == 'win32':
            import ctypes
            
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            
            return {
                'total_mb': stat.ullTotalPhys / (1024 * 1024),
                'available_mb': stat.ullAvailPhys / (1024 * 1024),
                'percent_used': stat.dwMemoryLoad
            }
        else:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            info = {}
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = int(parts[1].strip().split()[0])  # KB
                    info[key] = value
            
            total = info.get('MemTotal', 0) / 1024
            available = info.get('MemAvailable', info.get('MemFree', 0)) / 1024
            
            return {
                'total_mb': total,
                'available_mb': available,
                'percent_used': ((total - available) / total * 100) if total > 0 else 0
            }
            
    except Exception as e:
        logger.debug(f"Could not get system memory info: {e}")
    
    return {'total_mb': 0, 'available_mb': 0, 'percent_used': 0}


@dataclass
class MemoryPressureLevel:
    """Memory pressure level thresholds."""
    LOW = 'low'      # < 50% usage
    MEDIUM = 'medium' # 50-75% usage
    HIGH = 'high'    # 75-90% usage  
    CRITICAL = 'critical'  # > 90% usage


@dataclass
class TrackedResource:
    """Metadata for a tracked memory resource."""
    name: str
    ref: weakref.ref
    estimated_size_mb: float
    created_at: float = field(default_factory=time.time)
    category: str = 'general'


class MemoryManager:
    """
    Intelligent memory manager for OpenUP.
    
    Features:
    - Memory pressure monitoring
    - Automatic cleanup triggers
    - Resource tracking with weak references
    - Memory budget enforcement
    - Garbage collection optimization
    """
    
    def __init__(
        self,
        max_memory_mb: Optional[float] = None,
        warning_threshold: float = 0.75,
        critical_threshold: float = 0.90,
        auto_cleanup: bool = True,
        check_interval_seconds: float = 5.0
    ):
        """
        Initialize memory manager.
        
        Args:
            max_memory_mb: Maximum memory budget (None = auto-detect)
            warning_threshold: Threshold for warning level
            critical_threshold: Threshold for critical level
            auto_cleanup: Enable automatic cleanup on high pressure
            check_interval_seconds: Interval for memory checks
        """
        system_info = get_system_memory_info()
        
        if max_memory_mb is None:
            # Use 50% of available system memory as default
            max_memory_mb = system_info['available_mb'] * 0.5
        
        self.max_memory_mb = max_memory_mb
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.auto_cleanup = auto_cleanup
        self.check_interval = check_interval_seconds
        
        # Resource tracking
        self._tracked_resources: Dict[str, TrackedResource] = {}
        self._lock = threading.RLock()
        
        # Cleanup callbacks
        self._cleanup_callbacks: List[Callable[[str], None]] = []
        
        # Monitoring thread
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Statistics
        self._peak_usage_mb = 0.0
        self._cleanups_triggered = 0
        
        logger.info(f"Memory manager initialized: max {max_memory_mb:.1f}MB")
    
    def start_monitoring(self):
        """Start background memory monitoring."""
        if self._monitor_thread is not None:
            return
        
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MemoryMonitor"
        )
        self._monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring."""
        if self._monitor_thread is None:
            return
        
        self._stop_monitoring.set()
        self._monitor_thread.join(timeout=2.0)
        self._monitor_thread = None
        logger.info("Memory monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while not self._stop_monitoring.wait(self.check_interval):
            try:
                self._check_memory_pressure()
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
    
    def _check_memory_pressure(self):
        """Check memory pressure and trigger cleanup if needed."""
        current = get_process_memory_mb()
        self._peak_usage_mb = max(self._peak_usage_mb, current)
        
        usage_ratio = current / self.max_memory_mb if self.max_memory_mb > 0 else 0
        
        if usage_ratio >= self.critical_threshold:
            level = MemoryPressureLevel.CRITICAL
            if self.auto_cleanup:
                self.force_cleanup()
        elif usage_ratio >= self.warning_threshold:
            level = MemoryPressureLevel.HIGH
            if self.auto_cleanup:
                self.soft_cleanup()
        elif usage_ratio >= 0.5:
            level = MemoryPressureLevel.MEDIUM
        else:
            level = MemoryPressureLevel.LOW
        
        return level
    
    def track_resource(
        self,
        name: str,
        resource: Any,
        estimated_size_mb: float = 0.0,
        category: str = 'general'
    ):
        """
        Track a resource for memory management.
        
        Uses weak references so resources can be garbage collected.
        
        Args:
            name: Unique identifier for resource
            resource: Object to track
            estimated_size_mb: Estimated memory usage
            category: Category for grouped cleanup
        """
        with self._lock:
            # Create weak reference
            try:
                ref = weakref.ref(resource)
            except TypeError:
                # Object doesn't support weak references
                logger.debug(f"Cannot create weak ref for {name}")
                return
            
            self._tracked_resources[name] = TrackedResource(
                name=name,
                ref=ref,
                estimated_size_mb=estimated_size_mb,
                category=category
            )
    
    def untrack_resource(self, name: str):
        """Remove resource from tracking."""
        with self._lock:
            self._tracked_resources.pop(name, None)
    
    def get_tracked_resources(self, category: Optional[str] = None) -> List[TrackedResource]:
        """Get list of tracked resources, optionally filtered by category."""
        with self._lock:
            # Clean up dead references
            dead_keys = [
                key for key, res in self._tracked_resources.items()
                if res.ref() is None
            ]
            for key in dead_keys:
                del self._tracked_resources[key]
            
            resources = list(self._tracked_resources.values())
            
            if category:
                resources = [r for r in resources if r.category == category]
            
            return resources
    
    def register_cleanup_callback(self, callback: Callable[[str], None]):
        """
        Register a callback for cleanup events.
        
        Args:
            callback: Function called with pressure level on cleanup
        """
        self._cleanup_callbacks.append(callback)
    
    def soft_cleanup(self):
        """Perform soft cleanup (generation 0 GC)."""
        gc.collect(0)
        
        # Notify callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback('soft')
            except Exception as e:
                logger.error(f"Cleanup callback error: {e}")
    
    def force_cleanup(self):
        """Perform aggressive cleanup (full GC)."""
        self._cleanups_triggered += 1
        
        # Full garbage collection
        gc.collect()
        gc.collect()
        gc.collect()
        
        # Notify callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback('force')
            except Exception as e:
                logger.error(f"Cleanup callback error: {e}")
        
        logger.info(f"Force cleanup completed. Memory: {get_process_memory_mb():.1f}MB")
    
    def can_allocate(self, size_mb: float) -> bool:
        """Check if allocation of given size is safe."""
        current = get_process_memory_mb()
        projected = current + size_mb
        return projected < self.max_memory_mb * self.warning_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        current = get_process_memory_mb()
        system = get_system_memory_info()
        tracked = self.get_tracked_resources()
        
        return {
            'current_mb': round(current, 2),
            'peak_mb': round(self._peak_usage_mb, 2),
            'max_budget_mb': round(self.max_memory_mb, 2),
            'usage_percent': round(current / self.max_memory_mb * 100, 2) if self.max_memory_mb > 0 else 0,
            'system_total_mb': round(system['total_mb'], 2),
            'system_available_mb': round(system['available_mb'], 2),
            'tracked_resources': len(tracked),
            'tracked_estimated_mb': round(sum(r.estimated_size_mb for r in tracked), 2),
            'cleanups_triggered': self._cleanups_triggered
        }
    
    def __enter__(self):
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring()
        return False


class MemoryBudget:
    """
    Context manager for memory-budgeted operations.
    
    Usage:
        with MemoryBudget(manager, 100) as budget:
            # Operations limited to 100MB additional memory
            large_data = load_large_file()
            budget.check()  # Raises if exceeded
    """
    
    def __init__(self, manager: MemoryManager, budget_mb: float):
        self.manager = manager
        self.budget_mb = budget_mb
        self.start_mb = 0.0
    
    def __enter__(self):
        self.start_mb = get_process_memory_mb()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def check(self):
        """Check if within budget, raise if exceeded."""
        current = get_process_memory_mb()
        used = current - self.start_mb
        
        if used > self.budget_mb:
            raise MemoryError(
                f"Memory budget exceeded: {used:.1f}MB used, {self.budget_mb:.1f}MB allowed"
            )
    
    def remaining(self) -> float:
        """Get remaining budget in MB."""
        current = get_process_memory_mb()
        used = current - self.start_mb
        return max(0, self.budget_mb - used)


# Singleton instance
_global_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = MemoryManager()
    return _global_manager
