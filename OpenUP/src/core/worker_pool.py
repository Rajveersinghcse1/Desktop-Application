"""Background worker pool for async file processing."""

import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    """Signals for worker results."""
    finished = pyqtSignal(object)  # Result data
    error = pyqtSignal(Exception)  # Error occurred
    progress = pyqtSignal(int)  # Progress percentage (0-100)


class WorkerPool:
    """
    Manages background workers for heavy file processing tasks.
    
    Provides thread pool for CPU-intensive operations like:
    - Metadata extraction
    - Thumbnail generation
    - Point cloud downsampling
    - Large file parsing
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize worker pool.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_tasks = {}
        self.logger.info(f"WorkerPool initialized with {max_workers} workers")
        
    def submit_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> WorkerSignals:
        """
        Submit a task to the worker pool.
        
        Args:
            task_id: Unique identifier for this task
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            WorkerSignals instance for connecting to results
        """
        signals = WorkerSignals()
        
        def wrapped_task():
            try:
                result = func(*args, **kwargs)
                signals.finished.emit(result)
                return result
            except Exception as e:
                self.logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                signals.error.emit(e)
                raise
            finally:
                if task_id in self._active_tasks:
                    del self._active_tasks[task_id]
                    
        future = self._executor.submit(wrapped_task)
        self._active_tasks[task_id] = {
            'future': future,
            'signals': signals,
            'func': func.__name__
        }
        
        self.logger.debug(f"Submitted task {task_id}: {func.__name__}")
        return signals
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Attempt to cancel a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was cancelled, False otherwise
        """
        if task_id in self._active_tasks:
            future = self._active_tasks[task_id]['future']
            cancelled = future.cancel()
            if cancelled:
                del self._active_tasks[task_id]
                self.logger.info(f"Cancelled task {task_id}")
            return cancelled
        return False
        
    def is_task_running(self, task_id: str) -> bool:
        """Check if task is currently running."""
        return task_id in self._active_tasks
        
    def get_active_task_count(self) -> int:
        """Get number of active tasks."""
        return len(self._active_tasks)
        
    def shutdown(self, wait: bool = True):
        """
        Shutdown worker pool.
        
        Args:
            wait: If True, wait for all tasks to complete
        """
        self.logger.info("Shutting down worker pool...")
        self._executor.shutdown(wait=wait)
        self._active_tasks.clear()
        self.logger.info("Worker pool shutdown complete")
