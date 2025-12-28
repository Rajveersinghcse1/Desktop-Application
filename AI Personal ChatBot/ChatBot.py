import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import json
import re
import threading
import time
import google.generativeai as genai
import os
import sys
from datetime import datetime

# Optional imports - will be checked at runtime
# Optional imports - will be checked at runtime
try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = None

# Try to import google.generativeai
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Constants for API endpoints
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Gemini API key - consider using environment variables for production use
GEMINI_API_KEY = "AIzaSyAeXNQ8-VuXgDF6hN-cEghhBUZogs4ZQpw"


class OllamaChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set app icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Variables
        self.conversation_history = []
        self.current_model = tk.StringVar(value="llama3:8b")
        self.available_models = []
        self.is_sending = False
        self.temperature = tk.DoubleVar(value=0.7)
        self.max_tokens = tk.IntVar(value=2048)
        self.thinking_animation = None
        self.chat_file_path = None
        self.dark_mode = tk.BooleanVar(value=True)
        self.api_provider = tk.StringVar(value="ollama")  # Added API provider selection
        #Initialize Gemini if available
        if genai and self.api_provider.get()=="gemini":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
            except Exception as e:
                messagebox.showwarning("Gemini API Warnning",f"Could not initialize Gemini API:{str(e)}")

        # Configure colors based on theme
        self.update_colors()
        
        # Create main frames
        self.create_ui_components()
        
        # Fetch available models
        threading.Thread(target=self.fetch_available_models, daemon=True).start()
        
        # Set up key bindings
        self.setup_bindings()
        
        # Apply initial theme
        self.toggle_theme()

    def update_colors(self):
        if self.dark_mode.get():
            self.bg_color = "#1E1E1E"
            self.text_bg = "#2D2D2D"
            self.text_fg = "#E0E0E0"
            self.accent_color = "#0078D7"
            self.user_bubble_bg = "#0078D7"
            self.user_bubble_fg = "#FFFFFF"
            self.bot_bubble_bg = "#3E3E3E"
            self.bot_bubble_fg = "#E0E0E0"
            self.input_bg = "#3E3E3E"
            self.input_fg = "#FFFFFF"
        else:
            self.bg_color = "#F0F0F0"
            self.text_bg = "#FFFFFF"
            self.text_fg = "#333333"
            self.accent_color = "#0078D7"
            self.user_bubble_bg = "#0078D7"
            self.user_bubble_fg = "#FFFFFF"
            self.bot_bubble_bg = "#E6E6E6"
            self.bot_bubble_fg = "#333333"
            self.input_bg = "#FFFFFF"
            self.input_fg = "#333333"

    def create_ui_components(self):
        # Create main paned window
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left sidebar (model selection, settings)
        self.sidebar_frame = ttk.Frame(self.main_pane, width=200)
        self.main_pane.add(self.sidebar_frame, weight=1)
        
        # Chat area frame
        self.chat_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.chat_frame, weight=5)
        
        # Populate sidebar
        self.create_sidebar()
        
        # Populate chat area
        self.create_chat_area()

    def create_sidebar(self):
        # Sidebar header
        header_frame = ttk.Frame(self.sidebar_frame)
        header_frame.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        ttk.Label(header_frame, text="AI Chat", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        
        # New chat button
        new_chat_btn = ttk.Button(self.sidebar_frame, text="New Chat", command=self.new_chat)
        new_chat_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # API Provider selection
        provider_frame = ttk.LabelFrame(self.sidebar_frame, text="API Provider")
        provider_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Radio buttons for API selection
        ttk.Radiobutton(provider_frame, text="Ollama", variable=self.api_provider, 
                       value="ollama", command=self.on_provider_change).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(provider_frame, text="Gemini 1.5", variable=self.api_provider, 
                       value="gemini", command=self.on_provider_change).pack(anchor=tk.W, padx=5, pady=2)
        
        # Model selection
        model_frame = ttk.LabelFrame(self.sidebar_frame, text="Model")
        model_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.current_model, state="readonly")
        self.model_dropdown.pack(fill=tk.X, padx=5, pady=5)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # Refresh models button
        refresh_btn = ttk.Button(model_frame, text="⟳ Refresh", command=self.refresh_models)
        refresh_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Settings section
        settings_frame = ttk.LabelFrame(self.sidebar_frame, text="Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Temperature slider
        ttk.Label(settings_frame, text=f"Temperature: {self.temperature.get():.1f}").pack(anchor=tk.W, padx=5, pady=(5, 0))
        temp_slider = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=self.temperature, command=self.update_temp_label)
        temp_slider.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.temp_label = ttk.Label(settings_frame, text=f"{self.temperature.get():.1f}")
        self.temp_label.pack(anchor=tk.E, padx=5)
        
        # Max tokens slider
        ttk.Label(settings_frame, text=f"Max Tokens: {self.max_tokens.get()}").pack(anchor=tk.W, padx=5, pady=(5, 0))
        tokens_slider = ttk.Scale(settings_frame, from_=256, to=4096, variable=self.max_tokens, command=self.update_tokens_label)
        tokens_slider.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.tokens_label = ttk.Label(settings_frame, text=str(self.max_tokens.get()))
        self.tokens_label.pack(anchor=tk.E, padx=5)
        
        # Theme toggle
        theme_btn = ttk.Checkbutton(
            settings_frame, 
            text="Dark Mode", 
            variable=self.dark_mode, 
            command=self.toggle_theme
        )
        theme_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # File options
        file_frame = ttk.LabelFrame(self.sidebar_frame, text="File")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(file_frame, text="Save Chat", command=self.save_chat).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="Load Chat", command=self.load_chat).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="Export as Text", command=self.export_as_text).pack(fill=tk.X, padx=5, pady=2)
        
        # App version at bottom
        version_frame = ttk.Frame(self.sidebar_frame)
        version_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        ttk.Label(version_frame, text="Version 2.1.0", font=("Segoe UI", 8)).pack(side=tk.RIGHT)

    def create_chat_area(self):
        # Chat display area with custom styling
        self.chat_display_frame = ttk.Frame(self.chat_frame)
        self.chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Use Canvas with a Frame inside for custom styling and better scrolling
        self.chat_canvas = tk.Canvas(self.chat_display_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_display_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas to hold messages - use tk.Frame instead of ttk.Frame for background support
        self.messages_frame = tk.Frame(self.chat_canvas)
        self.canvas_frame = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        
        # Make the inner frame expand to fill canvas width
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bottom input area
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Text input instead of Entry for multi-line support
        self.user_input = tk.Text(input_frame, height=3, font=("Segoe UI", 11), wrap=tk.WORD)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Send button frame with icon
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        self.send_button = ttk.Button(btn_frame, text="Send", command=self.on_send)
        self.send_button.pack(side=tk.TOP, pady=(0, 5))
        
        # Cancel button (hidden initially)
        self.cancel_button = ttk.Button(btn_frame, text="Cancel", command=self.cancel_request, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.BOTTOM)
        
        # Status bar
        self.status_bar = ttk.Label(self.chat_frame, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=(0, 5))

    def setup_bindings(self):
        # Set up key bindings
        self.user_input.bind("<Control-Return>", self.on_send)
        self.user_input.bind("<Control-KeyRelease-Return>", lambda e: "break")  # Prevent double line
        
        # Allow Tab to work properly in the text widget
        self.user_input.bind("<Tab>", lambda e: self.user_input.insert(tk.INSERT, "    ") or "break")
        
        # Handle scrolling
        self.chat_canvas.bind("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_frame_configure(self, event=None):
        # Update scrollregion when the inner frame changes size
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def on_canvas_configure(self, event=None):
        # Update the width of the inner frame to fill the canvas
        self.chat_canvas.itemconfig(self.canvas_frame, width=event.width)

    def toggle_theme(self):
        self.update_colors()
        
        # Update UI elements with new colors
        self.root.configure(bg=self.bg_color)
        self.chat_canvas.config(bg=self.bg_color)
        
        # Note: ttk.Frame doesn't support background color directly
        # We need to use style configuration instead
        self.user_input.config(bg=self.input_bg, fg=self.input_fg, insertbackground=self.input_fg)
        
        # Redraw all messages with new theme colors
        self.redraw_messages()

    def redraw_messages(self):
        # Clear and redraw all messages with current theme
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        for entry in self.conversation_history:
            self.display_message(entry["role"], entry["content"], redraw=True)
        
        # Scroll to bottom
        self.scroll_to_bottom()

    def on_provider_change(self, event=None):
        api_provider = self.api_provider.get()
        if api_provider == "ollama":
            self.update_status("API provider changed to Ollama")
            threading.Thread(target=self.fetch_available_models, daemon=True).start()
        elif api_provider == "gemini":
            self.update_status("API provider changed to Gemini")

        # Check if google-generativeai package is installed
            try:
                import google.generativeai as genai
                self.available_models = ["gemini-1.5-flash"]
                self.model_dropdown['values'] = self.available_models
                self.current_model.set("gemini-1.5-flash")

                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.update_status("Gemini API configured successfully")
                except Exception as e:
                    messagebox.showwarning("Gemini API Warning", f"Could not initialize Gemini API: {str(e)}")
            except ImportError:
                messagebox.showwarning("Missing Package", 
                                      "The google-generativeai package is required for Gemini support.\n"
                                      "You can install it with: pip install google-generativeai")
                self.api_provider.set("ollama")
                return    

                
    def fetch_available_models(self):
        if self.api_provider.get() == "ollama":
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    self.available_models = [model['name'] for model in data['models']]
                    self.model_dropdown['values'] = self.available_models
                    
                    # Set current model if it exists in available models
                    if self.current_model.get() in self.available_models:
                        self.model_dropdown.set(self.current_model.get())
                    elif self.available_models:
                        self.current_model.set(self.available_models[0])
                        
                    self.update_status(f"Found {len(self.available_models)} models")
                else:
                    self.update_status("Failed to fetch models")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                self.available_models = ["llama3:8b", "llama3:8b", "mistral:7b", "phi3:mini"]
                self.model_dropdown['values'] = self.available_models

    def refresh_models(self):
        threading.Thread(target=self.fetch_available_models, daemon=True).start()
        self.update_status("Refreshing model list...")

    def update_temp_label(self, value):
        # Update the temperature value display
        temp_value = float(value)
        self.temp_label.config(text=f"{temp_value:.1f}")

    def update_tokens_label(self, value):
        # Update the max tokens value display
        token_value = int(float(value))
        self.tokens_label.config(text=str(token_value))

    def on_model_change(self, event=None):
        self.update_status(f"Model changed to {self.current_model.get()}")

    def update_status(self, message):
        self.status_bar.config(text=message)

    def clean_response(self, text):
        # Clean thinking text
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        # Clean other tags
        cleaned = re.sub(r"<[^>]*>", "", cleaned, flags=re.DOTALL)
        # Remove specific characters/patterns
        cleaned = re.sub(r'```', "", cleaned)
        cleaned = re.sub(r'\'\'\'', "", cleaned)
        cleaned = re.sub(r'###', "", cleaned)
        cleaned = re.sub(r'\*\*', "", cleaned)
        cleaned = re.sub(r'#', "", cleaned)
        return cleaned.strip()

    def display_message(self, sender, message, redraw=False):
        # Create message frame - use tk.Frame instead of ttk.Frame for background color support
        msg_frame = tk.Frame(self.messages_frame, bg=self.bg_color)
        msg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if sender == "user":
            # User message (right-aligned)
            spacer = tk.Frame(msg_frame, bg=self.bg_color)
            spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            msg_content = tk.Text(msg_frame, wrap=tk.WORD, width=50, height=1, 
                               font=("Segoe UI", 11),
                               bg=self.user_bubble_bg, fg=self.user_bubble_fg,
                               relief=tk.FLAT, padx=10, pady=8)
            msg_content.pack(side=tk.RIGHT, anchor=tk.E)
            
            # Insert user icon
            user_icon = tk.Label(msg_frame, text="👤", bg=self.bg_color, fg=self.text_fg)
            user_icon.pack(side=tk.RIGHT, padx=(0, 5))
            
        else:
            # Bot message (left-aligned)
            bot_icon = tk.Label(msg_frame, text="🤖", bg=self.bg_color, fg=self.text_fg)
            bot_icon.pack(side=tk.LEFT, padx=(0, 5))
            
            msg_bubble = tk.Frame(msg_frame, bg=self.bg_color)
            msg_bubble.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, expand=True)
            
            msg_content = tk.Text(msg_bubble, wrap=tk.WORD, width=65, height=1,
                               font=("Segoe UI", 11), 
                               bg=self.bot_bubble_bg, fg=self.bot_bubble_fg,
                               relief=tk.FLAT, padx=10, pady=8)
            msg_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Add copy button - use tk.Button instead of ttk.Button for better styling
            copy_btn = tk.Button(msg_bubble, text="📋", width=3, bg=self.bot_bubble_bg, fg=self.bot_bubble_fg,
                              command=lambda text=message: self.copy_to_clipboard(text))
            copy_btn.pack(side=tk.RIGHT, padx=5, anchor=tk.NE)
        
        # Insert message
        msg_content.insert(tk.END, message)
        msg_content.config(state=tk.DISABLED)
        
        # Calculate required height based on content
        line_count = int(msg_content.index('end-1c').split('.')[0])
        msg_content.config(height=min(max(line_count, 1), 20))
        
        if not redraw:
            # Add to conversation history
            self.conversation_history.append({"role": sender, "content": message})
        
        # Scroll to see the new message
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def on_send(self, event=None):
        prompt = self.user_input.get("1.0", tk.END).strip()
        if not prompt:
            return "break"
        
        # Clear input
        self.user_input.delete("1.0", tk.END)
        
        # Display user message
        self.display_message("user", prompt)
        
        # Special commands
        if prompt.lower() == "clear":
            self.new_chat()
            return "break"
        
        if prompt.lower() == "exit" or prompt.lower() == "quit":
            self.root.destroy()
            return "break"
        
        # Disable send button and enable cancel
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.is_sending = True
        
        # Start thinking animation
        self.start_thinking_animation()
        
        # Start API call in a thread
        threading.Thread(target=self.get_and_display_response, args=(prompt,), daemon=True).start()
        
        return "break"  # Prevent default Enter behavior

    def start_thinking_animation(self):
        # Create a temporary thinking message
        thinking_frame = tk.Frame(self.messages_frame, bg=self.bg_color)
        thinking_frame.pack(fill=tk.X, padx=10, pady=5)
        
        bot_icon = tk.Label(thinking_frame, text="🤖", bg=self.bg_color, fg=self.text_fg)
        bot_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.thinking_label = tk.Label(thinking_frame, text="Thinking...", bg=self.bg_color, fg=self.text_fg)
        self.thinking_label.pack(side=tk.LEFT)
        
        self.thinking_animation = thinking_frame
        self.thinking_dots = 0
        
        # Animate the dots
        self.animate_thinking()
        
        # Scroll to bottom
        self.scroll_to_bottom()

    def animate_thinking(self):
        if not self.thinking_animation or not self.is_sending:
            return
            
        dots = "." * ((self.thinking_dots % 3) + 1)
        self.thinking_label.config(text=f"Thinking{dots}")
        self.thinking_dots += 1
        
        # Schedule next animation frame
        self.root.after(500, self.animate_thinking)

    def stop_thinking_animation(self):
        if self.thinking_animation:
            self.thinking_animation.destroy()
            self.thinking_animation = None

    def get_and_display_response(self, prompt):
        try:
            self.update_status("Requesting response...")
            
            api_provider = self.api_provider.get()
            response_text = None
            
            if api_provider == "ollama":
                response_text = self.call_ollama_api(prompt)
            elif api_provider == "gemini":
                response_text = self.call_gemini_api(prompt)
                    
            # Stop thinking animation
            self.stop_thinking_animation()
                    
            if response_text:
                cleaned_text = self.clean_response(response_text)
                self.display_message("bot", cleaned_text)
                self.update_status("Response received")
            else:
                self.display_message("bot", f"Sorry, I couldn't reach the {api_provider.capitalize()} server or no response was received.")
                self.update_status(f"Error: No response from {api_provider} server")
                
        except Exception as e:
            self.stop_thinking_animation()
            self.display_message("bot", f"An error occurred: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            
        finally:
            # Re-enable send button and disable cancel
            self.send_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.is_sending = False
            
    def call_ollama_api(self, prompt):
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.current_model.get(),
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature.get(),
            "max_tokens": self.max_tokens.get(),
        }
        
        try:
            response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            self.update_status(f"Ollama API error: {str(e)}")
            
        return None
        
    def call_gemini_api(self, prompt):
        try:
            if not genai:
                self.update_status("Gemini API error: google.generativeai package not available")
                return "Error: The google-generativeai package is not installed. Please install it to use Gemini."
        
        # First, make sure the API key is configured
            try:
                genai.configure(api_key=GEMINI_API_KEY)
            except Exception as e:
                self.update_status(f"Gemini API configuration error: {str(e)}")
                return f"Error configuring Gemini API: {str(e)}"
        
             # For proper chat history handling with Gemini
            try:
                # Create a new chat session
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "temperature": self.temperature.get(),
                        "max_output_tokens": self.max_tokens.get(),
                        "top_p": 0.95,
                        "top_k": 64
                }
            )
            
                # Create a chat session
                chat = model.start_chat(history=[])
            
                # Add previous messages to chat context
                for entry in self.conversation_history:
                    if entry["role"] == "user":
                        chat.send_message(entry["content"], stream=False)
                        # Skip adding assistant responses to avoid duplicate responses
            
                # Send the current prompt and get response
                response = chat.send_message(prompt, stream=False)
                if response and hasattr(response, 'text'):
                    return response.text
                else:
                    self.update_status("Empty response from Gemini API")
                    return "Sorry, I received an empty response from the Gemini API."
                
            except Exception as e:
                self.update_status(f"Gemini API error: {str(e)}")
                return f"Error calling Gemini API: {str(e)}"
            
        except Exception as e:
            self.update_status(f"Gemini setup error: {str(e)}")
            return f"Error setting up Gemini: {str(e)}"

    def cancel_request(self):
        if self.is_sending:
            self.is_sending = False
            self.stop_thinking_animation()
            self.display_message("bot", "Request cancelled by user.")
            self.send_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.update_status("Request cancelled")

    def copy_to_clipboard(self, text):
        if pyperclip:
            pyperclip.copy(text)
            self.update_status("Copied to clipboard")
        else:
            self.update_status("pyperclip module not installed - clipboard feature unavailable")
            messagebox.showinfo("Missing Package", "The pyperclip module is not installed. Install it to enable clipboard functionality.")

    def new_chat(self):
        # Clear conversation history
        self.conversation_history = []
        
        # Clear chat display
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
            
        # Reset file path
        self.chat_file_path = None
        
        self.update_status("New chat started")

    def save_chat(self):
        # Convert conversation history to dict with metadata
        chat_data = {
            "metadata": {
                "model": self.current_model.get(),
                "provider":self.api_provider.get(),
                "timestamp": datetime.now().isoformat(),
                "app_version": "2.0.0"
            },
            "conversation": self.conversation_history
        }
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
                
            self.chat_file_path = file_path
            self.update_status(f"Chat saved to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chat: {str(e)}")

    def load_chat(self):
        # Ask for file to load
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                
            # Check if it's a valid chat file
            if "conversation" not in chat_data:
                raise ValueError("Invalid chat file format")
                
            # Clear current chat
            self.new_chat()
            
            # Set model if available
            if "metadata" in chat_data and "model" in chat_data["metadata"]:
                model = chat_data["metadata"]["model"]
                if model in self.available_models:
                    self.current_model.set(model)
            
            # Load conversation
            self.conversation_history = chat_data["conversation"]
            
            # Display messages
            for entry in self.conversation_history:
                role = entry.get("role", "bot")
                content = entry.get("content", "")
                self.display_message(role, content, redraw=True)
                
            self.chat_file_path = file_path
            self.update_status(f"Chat loaded from {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chat: {str(e)}")

    def export_as_text(self):
        if not self.conversation_history:
            messagebox.showinfo("Info", "No conversation to export")
            return
            
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Ollama Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model: {self.current_model.get()}\n\n")
                
                for entry in self.conversation_history:
                    role = "You" if entry["role"] == "user" else "Bot"
                    f.write(f"{role}: {entry['content']}\n\n")
                    
            self.update_status(f"Chat exported to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export chat: {str(e)}")

def main():
    # Check for required packages
    missing_packages = []
    
    if not pyperclip:
        missing_packages.append("pyperclip")
    
    # Check for google-generativeai
    try:
        import google.generativeai as genai
    except ImportError:
        missing_packages.append("google-generativeai")
    
    if ThemedTk:
        root = ThemedTk(theme="arc")
    else:
        missing_packages.append("ttkthemes")
        root = tk.Tk()
    
    if missing_packages:
        if messagebox.askyesno("Missing Packages", 
                             f"The following packages are recommended but not installed: {', '.join(missing_packages)}\n\n"
                             f"Would you like to install them now? (The app will work without them, but with reduced functionality)"):
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                messagebox.showinfo("Success", "Packages installed successfully. Please restart the application.")
                sys.exit(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install packages: {str(e)}")
    
    app = OllamaChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()