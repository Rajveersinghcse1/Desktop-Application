"""
Splash Screen
Loading screen with progress bar
"""

import logging
from typing import Optional, Callable
try:
    import customtkinter as ctk
except ImportError:
    import tkinter as tk
    ctk = None

logger = logging.getLogger(__name__)


class SplashScreen:
    """Splash screen for application startup"""
    
    def __init__(self, title: str = "AI Avatar Studio", version: str = "1.0.0"):
        """Initialize splash screen"""
        self.title = title
        self.version = version
        self.window = None
        self.progress_bar = None
        self.status_label = None
        self.initialized = False
        
        if ctk:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
    
    def create(self) -> bool:
        """Create and show splash screen"""
        try:
            if ctk:
                self.window = ctk.CTk()
            else:
                self.window = tk.Tk()
            
            self.window.title(self.title)
            
            # Window size and position
            width = 500
            height = 350
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            self.window.geometry(f"{width}x{height}+{x}+{y}")
            self.window.resizable(False, False)
            self.window.overrideredirect(True)  # Remove window decorations
            
            # Main frame
            if ctk:
                main_frame = ctk.CTkFrame(self.window, corner_radius=15)
            else:
                main_frame = tk.Frame(self.window, bg='#1a1a1a')
            
            main_frame.pack(fill='both', expand=True, padx=2, pady=2)
            
            # Logo/Title
            if ctk:
                title_label = ctk.CTkLabel(
                    main_frame,
                    text="🎭 AI Avatar Studio",
                    font=ctk.CTkFont(size=32, weight="bold")
                )
            else:
                title_label = tk.Label(
                    main_frame,
                    text="🎭 AI Avatar Studio",
                    font=("Arial", 32, "bold"),
                    bg='#1a1a1a',
                    fg='white'
                )
            
            title_label.pack(pady=(40, 10))
            
            # Version
            if ctk:
                version_label = ctk.CTkLabel(
                    main_frame,
                    text=f"Version {self.version}",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
            else:
                version_label = tk.Label(
                    main_frame,
                    text=f"Version {self.version}",
                    font=("Arial", 14),
                    bg='#1a1a1a',
                    fg='gray'
                )
            
            version_label.pack(pady=(0, 30))
            
            # Description
            description = "Create AI-powered talking avatars\nwith synchronized lip movements"
            if ctk:
                desc_label = ctk.CTkLabel(
                    main_frame,
                    text=description,
                    font=ctk.CTkFont(size=13),
                    justify="center"
                )
            else:
                desc_label = tk.Label(
                    main_frame,
                    text=description,
                    font=("Arial", 13),
                    bg='#1a1a1a',
                    fg='white',
                    justify="center"
                )
            
            desc_label.pack(pady=(0, 30))
            
            # Progress bar
            if ctk:
                self.progress_bar = ctk.CTkProgressBar(
                    main_frame,
                    width=400,
                    height=20,
                    mode='determinate'
                )
                self.progress_bar.set(0)
            else:
                import tkinter.ttk as ttk
                self.progress_bar = ttk.Progressbar(
                    main_frame,
                    length=400,
                    mode='determinate'
                )
                self.progress_bar['value'] = 0
            
            self.progress_bar.pack(pady=(0, 15))
            
            # Status label
            if ctk:
                self.status_label = ctk.CTkLabel(
                    main_frame,
                    text="Initializing...",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
            else:
                self.status_label = tk.Label(
                    main_frame,
                    text="Initializing...",
                    font=("Arial", 12),
                    bg='#1a1a1a',
                    fg='gray'
                )
            
            self.status_label.pack(pady=(0, 20))
            
            # Footer
            if ctk:
                footer_label = ctk.CTkLabel(
                    main_frame,
                    text="Powered by Wav2Lip & MediaPipe",
                    font=ctk.CTkFont(size=10),
                    text_color="darkgray"
                )
            else:
                footer_label = tk.Label(
                    main_frame,
                    text="Powered by Wav2Lip & MediaPipe",
                    font=("Arial", 10),
                    bg='#1a1a1a',
                    fg='darkgray'
                )
            
            footer_label.pack(side='bottom', pady=(0, 20))
            
            self.initialized = True
            self.window.update()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to create splash screen: {e}")
            return False
    
    def update_progress(self, progress: float, status: str = ""):
        """
        Update progress bar
        
        Args:
            progress: Progress value (0-100)
            status: Status message
        """
        if not self.initialized or not self.window:
            return
        
        try:
            # Update progress bar
            if ctk:
                self.progress_bar.set(progress / 100)
            else:
                self.progress_bar['value'] = progress
            
            # Update status
            if status and self.status_label:
                if ctk:
                    self.status_label.configure(text=status)
                else:
                    self.status_label.config(text=status)
            
            self.window.update()
        
        except Exception as e:
            logger.error(f"Error updating splash screen: {e}")
    
    def close(self):
        """Close splash screen"""
        if self.window:
            try:
                self.window.destroy()
                self.initialized = False
            except Exception as e:
                logger.error(f"Error closing splash screen: {e}")


def show_splash_screen(
    init_callback: Callable,
    title: str = "AI Avatar Studio",
    version: str = "1.0.0"
) -> Optional[SplashScreen]:
    """
    Show splash screen during initialization
    
    Args:
        init_callback: Function to call for initialization
                      Should accept progress_callback(progress, status)
        title: Application title
        version: Version string
    
    Returns:
        SplashScreen instance or None if failed
    """
    splash = SplashScreen(title, version)
    
    if not splash.create():
        return None
    
    def progress_callback(progress: float, status: str):
        """Update splash screen progress"""
        splash.update_progress(progress, status)
    
    try:
        # Run initialization
        init_callback(progress_callback)
        
        # Keep splash visible for a moment
        import time
        time.sleep(0.5)
        
        return splash
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        splash.close()
        return None


if __name__ == '__main__':
    import time
    
    def test_init(progress_callback):
        """Test initialization"""
        steps = [
            (10, "Loading configuration..."),
            (25, "Initializing database..."),
            (40, "Checking system requirements..."),
            (55, "Loading AI models..."),
            (70, "Preparing workspace..."),
            (85, "Finalizing setup..."),
            (100, "Ready!")
        ]
        
        for progress, status in steps:
            progress_callback(progress, status)
            time.sleep(0.3)
    
    # Test splash screen
    splash = show_splash_screen(test_init)
    
    if splash:
        splash.close()
        print("Splash screen test completed")
