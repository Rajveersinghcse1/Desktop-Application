"""
Main Application Window
Primary GUI for AI Avatar Studio
"""

import logging
from pathlib import Path
from typing import Optional
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    ctk = None

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window"""
    
    def __init__(self, database_manager, model_manager, pipeline):
        """
        Initialize main window
        
        Args:
            database_manager: Database manager instance
            model_manager: Model manager instance
            pipeline: Generation pipeline instance
        """
        self.db = database_manager
        self.model_manager = model_manager
        self.pipeline = pipeline
        
        self.window = None
        self.current_project_id = None
        self.input_image_path = None
        
        # GUI elements
        self.image_preview = None
        self.text_input = None
        self.voice_dropdown = None
        self.quality_dropdown = None
        self.resolution_dropdown = None
        self.speed_slider = None
        self.generate_button = None
        
        if ctk:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
    
    def create(self) -> bool:
        """Create main window"""
        try:
            if ctk:
                self.window = ctk.CTk()
            else:
                self.window = tk.Tk()
            
            self.window.title("AI Avatar Studio")
            self.window.geometry("1200x800")
            
            # Create UI layout
            self._create_menu_bar()
            self._create_main_layout()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            return False
    
    def _create_menu_bar(self):
        """Create menu bar"""
        import tkinter as tk
        
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Download Models", command=self._download_models)
        tools_menu.add_command(label="Settings", command=self._open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create main UI layout"""
        # Left panel - Image input
        if ctk:
            left_panel = ctk.CTkFrame(self.window)
        else:
            left_panel = tk.Frame(self.window, bg='#1a1a1a')
        
        left_panel.pack(side='left', fill='both', expand=False, padx=10, pady=10)
        
        # Image preview
        if ctk:
            image_label = ctk.CTkLabel(left_panel, text="Input Image", font=ctk.CTkFont(size=16, weight="bold"))
        else:
            image_label = tk.Label(left_panel, text="Input Image", font=("Arial", 16, "bold"), bg='#1a1a1a', fg='white')
        
        image_label.pack(pady=(0, 10))
        
        # Image frame
        if ctk:
            image_frame = ctk.CTkFrame(left_panel, width=400, height=400)
        else:
            image_frame = tk.Frame(left_panel, width=400, height=400, bg='#2a2a2a')
        
        image_frame.pack(pady=(0, 10))
        image_frame.pack_propagate(False)
        
        # Placeholder
        if ctk:
            self.image_preview = ctk.CTkLabel(
                image_frame,
                text="No image selected\nClick 'Select Image' to choose",
                font=ctk.CTkFont(size=14)
            )
        else:
            self.image_preview = tk.Label(
                image_frame,
                text="No image selected\nClick 'Select Image' to choose",
                font=("Arial", 14),
                bg='#2a2a2a',
                fg='gray'
            )
        
        self.image_preview.pack(expand=True)
        
        # Select image button
        if ctk:
            select_image_btn = ctk.CTkButton(
                left_panel,
                text="Select Image",
                command=self._select_image,
                width=200,
                height=40
            )
        else:
            select_image_btn = tk.Button(
                left_panel,
                text="Select Image",
                command=self._select_image,
                width=20,
                height=2
            )
        
        select_image_btn.pack(pady=(0, 10))
        
        # Right panel - Settings and text
        if ctk:
            right_panel = ctk.CTkFrame(self.window)
        else:
            right_panel = tk.Frame(self.window, bg='#1a1a1a')
        
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Text input section
        if ctk:
            text_label = ctk.CTkLabel(right_panel, text="Script Text", font=ctk.CTkFont(size=16, weight="bold"))
        else:
            text_label = tk.Label(right_panel, text="Script Text", font=("Arial", 16, "bold"), bg='#1a1a1a', fg='white')
        
        text_label.pack(pady=(0, 10))
        
        if ctk:
            self.text_input = ctk.CTkTextbox(right_panel, height=200, width=600)
        else:
            self.text_input = tk.Text(right_panel, height=12, width=70, bg='#2a2a2a', fg='white')
        
        self.text_input.pack(pady=(0, 20))
        
        # Settings section
        if ctk:
            settings_frame = ctk.CTkFrame(right_panel)
        else:
            settings_frame = tk.Frame(right_panel, bg='#1a1a1a')
        
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # Voice selection
        if ctk:
            voice_label = ctk.CTkLabel(settings_frame, text="Voice:", font=ctk.CTkFont(size=14))
            voice_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            
            self.voice_dropdown = ctk.CTkComboBox(
                settings_frame,
                values=["Default", "Male", "Female"],
                width=200
            )
            self.voice_dropdown.grid(row=0, column=1, padx=10, pady=10)
        else:
            voice_label = tk.Label(settings_frame, text="Voice:", font=("Arial", 14), bg='#1a1a1a', fg='white')
            voice_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            
            import tkinter.ttk as ttk
            self.voice_dropdown = ttk.Combobox(settings_frame, values=["Default", "Male", "Female"], width=30)
            self.voice_dropdown.grid(row=0, column=1, padx=10, pady=10)
            self.voice_dropdown.current(0)
        
        # Quality selection
        if ctk:
            quality_label = ctk.CTkLabel(settings_frame, text="Quality:", font=ctk.CTkFont(size=14))
            quality_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
            
            self.quality_dropdown = ctk.CTkComboBox(
                settings_frame,
                values=["Fast", "Balanced", "High"],
                width=200
            )
            self.quality_dropdown.set("Balanced")
            self.quality_dropdown.grid(row=1, column=1, padx=10, pady=10)
        else:
            quality_label = tk.Label(settings_frame, text="Quality:", font=("Arial", 14), bg='#1a1a1a', fg='white')
            quality_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
            
            self.quality_dropdown = ttk.Combobox(settings_frame, values=["Fast", "Balanced", "High"], width=30)
            self.quality_dropdown.grid(row=1, column=1, padx=10, pady=10)
            self.quality_dropdown.current(1)
        
        # Resolution selection
        if ctk:
            res_label = ctk.CTkLabel(settings_frame, text="Resolution:", font=ctk.CTkFont(size=14))
            res_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
            
            self.resolution_dropdown = ctk.CTkComboBox(
                settings_frame,
                values=["480p", "720p", "1080p"],
                width=200
            )
            self.resolution_dropdown.set("720p")
            self.resolution_dropdown.grid(row=2, column=1, padx=10, pady=10)
        else:
            res_label = tk.Label(settings_frame, text="Resolution:", font=("Arial", 14), bg='#1a1a1a', fg='white')
            res_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
            
            self.resolution_dropdown = ttk.Combobox(settings_frame, values=["480p", "720p", "1080p"], width=30)
            self.resolution_dropdown.grid(row=2, column=1, padx=10, pady=10)
            self.resolution_dropdown.current(1)
        
        # Speed slider
        if ctk:
            speed_label = ctk.CTkLabel(settings_frame, text="Speed:", font=ctk.CTkFont(size=14))
            speed_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
            
            self.speed_slider = ctk.CTkSlider(
                settings_frame,
                from_=0.5,
                to=2.0,
                number_of_steps=30,
                width=200
            )
            self.speed_slider.set(1.0)
            self.speed_slider.grid(row=3, column=1, padx=10, pady=10)
        else:
            speed_label = tk.Label(settings_frame, text="Speed:", font=("Arial", 14), bg='#1a1a1a', fg='white')
            speed_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
            
            self.speed_slider = tk.Scale(
                settings_frame,
                from_=0.5,
                to=2.0,
                resolution=0.1,
                orient='horizontal',
                length=200
            )
            self.speed_slider.set(1.0)
            self.speed_slider.grid(row=3, column=1, padx=10, pady=10)
        
        # Generate button
        if ctk:
            self.generate_button = ctk.CTkButton(
                right_panel,
                text="🎬 Generate Avatar Video",
                command=self._generate_avatar,
                width=300,
                height=50,
                font=ctk.CTkFont(size=16, weight="bold")
            )
        else:
            self.generate_button = tk.Button(
                right_panel,
                text="🎬 Generate Avatar Video",
                command=self._generate_avatar,
                width=30,
                height=2,
                font=("Arial", 16, "bold")
            )
        
        self.generate_button.pack(pady=20)
    
    def _select_image(self):
        """Select input image"""
        file_path = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.input_image_path = file_path
            logger.info(f"Selected image: {file_path}")
            
            # Load and display image
            try:
                from PIL import Image, ImageTk
                
                img = Image.open(file_path)
                img.thumbnail((380, 380))
                
                if ctk:
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=(380, 380))
                    self.image_preview.configure(image=photo, text="")
                    self.image_preview.image = photo
                else:
                    photo = ImageTk.PhotoImage(img)
                    self.image_preview.config(image=photo, text="")
                    self.image_preview.image = photo
            
            except Exception as e:
                logger.error(f"Error loading image: {e}")
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def _generate_avatar(self):
        """Start avatar generation"""
        # Validate inputs
        if not self.input_image_path:
            messagebox.showwarning("Missing Input", "Please select an input image")
            return
        
        if ctk:
            text = self.text_input.get("1.0", "end-1c")
        else:
            text = self.text_input.get("1.0", tk.END)
        
        if not text.strip():
            messagebox.showwarning("Missing Input", "Please enter script text")
            return
        
        # Get settings
        voice = self.voice_dropdown.get().lower() if hasattr(self.voice_dropdown, 'get') else 'default'
        quality = self.quality_dropdown.get().lower() if hasattr(self.quality_dropdown, 'get') else 'balanced'
        resolution = self.resolution_dropdown.get() if hasattr(self.resolution_dropdown, 'get') else '720p'
        speed = self.speed_slider.get()
        
        # Create project if needed
        if not self.current_project_id:
            self.current_project_id = self.db.create_project(
                name=f"Avatar_{Path(self.input_image_path).stem}",
                description=text[:100]
            )
        
        # Output path
        from config import paths
        output_path = str(paths.output_dir / f"avatar_{self.current_project_id}.mp4")
        
        # Start generation
        logger.info("Starting generation...")
        
        try:
            # Disable button
            if ctk:
                self.generate_button.configure(state="disabled", text="Generating...")
            else:
                self.generate_button.config(state="disabled", text="Generating...")
            
            # Run pipeline
            result = self.pipeline.generate(
                project_id=self.current_project_id,
                input_image=self.input_image_path,
                text=text,
                output_path=output_path,
                voice=voice,
                quality=quality,
                resolution=resolution,
                speed=speed
            )
            
            # Re-enable button
            if ctk:
                self.generate_button.configure(state="normal", text="🎬 Generate Avatar Video")
            else:
                self.generate_button.config(state="normal", text="🎬 Generate Avatar Video")
            
            if result['success']:
                messagebox.showinfo("Success", f"Avatar video generated!\n\n{result['output_path']}")
            else:
                messagebox.showerror("Error", f"Generation failed:\n{result['error']}")
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            messagebox.showerror("Error", f"Generation failed: {e}")
            
            if ctk:
                self.generate_button.configure(state="normal", text="🎬 Generate Avatar Video")
            else:
                self.generate_button.config(state="normal", text="🎬 Generate Avatar Video")
    
    def _new_project(self):
        """Create new project"""
        self.current_project_id = None
        self.input_image_path = None
        if ctk:
            self.text_input.delete("1.0", "end")
            self.image_preview.configure(image=None, text="No image selected\nClick 'Select Image' to choose")
        else:
            self.text_input.delete("1.0", tk.END)
            self.image_preview.config(image=None, text="No image selected\nClick 'Select Image' to choose")
    
    def _open_project(self):
        """Open existing project"""
        messagebox.showinfo("Coming Soon", "Project management coming in next update!")
    
    def _download_models(self):
        """Download AI models"""
        response = messagebox.askyesno(
            "Download Models",
            "This will download required AI models (~400 MB).\nContinue?"
        )
        
        if response:
            logger.info("Starting model download...")
            success = self.model_manager.download_all_models()
            
            if success:
                messagebox.showinfo("Success", "Models downloaded successfully!")
            else:
                messagebox.showerror("Error", "Some models failed to download")
    
    def _open_settings(self):
        """Open settings"""
        messagebox.showinfo("Coming Soon", "Settings panel coming in next update!")
    
    def _show_help(self):
        """Show help"""
        messagebox.showinfo(
            "Help",
            "AI Avatar Studio\n\n"
            "1. Select an input image with a face\n"
            "2. Enter the script text\n"
            "3. Adjust settings (voice, quality, resolution)\n"
            "4. Click 'Generate Avatar Video'\n\n"
            "For more information, see README.md"
        )
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "AI Avatar Studio v1.0.0\n\n"
            "Create AI-powered talking avatars\n"
            "with synchronized lip movements\n\n"
            "Powered by:\n"
            "- Wav2Lip\n"
            "- MediaPipe\n"
            "- FFmpeg"
        )
    
    def run(self):
        """Run the main window"""
        if self.window:
            self.window.mainloop()


if __name__ == '__main__':
    print("Main Window")
    print("=" * 60)
    print("This module creates the main GUI interface")
    print("Run main.py to start the application")
