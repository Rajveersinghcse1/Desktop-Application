import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import threading
from utils import load_excel
from ai_engine import generate_code
from executor import run_generated_code

class ExcelAssistantApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("💡 AI Excel Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f5f7fa")
        
        # Define common prompts
        self.predefined_prompts = [
            "show data",
            "plot all graphs",
            "show [one, two , three, four] which is [column names] where [column] condition",
            "Column condition like Hole Depth >5.8",
            "plot graph between blastcode vs ppv where ppv is not zero",
            "plot graph for ppv and airblast",
            "Generate a correlation matrix between all numeric columns",
            "plot a graph for fragmenatation",
            "Compare different groups in the data and show differences",
            "Clean this data by removing duplicates and handling missing values",
            "Create a forecast for the next 3 periods based on historical data"
        ]
        
        # Apply modern styling
        self._apply_styling()
        
        # Create main container with padding
        main_container = ttk.Frame(root, padding="12 12 12 12")
        main_container.pack(fill="both", expand=True)
        
        # File selector bar with improved layout
        file_frame = ttk.Frame(main_container)
        file_frame.pack(fill="x", pady=(0, 10))
        
        file_label = ttk.Label(file_frame, text="Excel File:")
        file_label.pack(side="left", padx=(0, 8))

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=70, state="readonly")
        self.file_entry.pack(side="left", padx=(0, 8), expand=True, fill="x")

        self.browse_button = ttk.Button(file_frame, text="📂 Browse", command=self.browse_file, style="Accent.TButton")
        self.browse_button.pack(side="left", padx=(0, 5))
        
        self.load_button = ttk.Button(file_frame, text="📤 Load", command=self.load_file_threaded, style="Accent.TButton")
        self.load_button.pack(side="left")

        # Status area with progress indicator and user prompts button
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill="x", pady=(0, 8))
        
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side="left", anchor="w")
        
        # User Prompts button
        self.prompt_button = ttk.Button(status_frame, text="📋 User Prompts", 
                                      command=self.show_user_prompts, style="Accent.TButton")
        self.prompt_button.pack(side="right")
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=200, 
                                       mode="indeterminate", variable=self.progress_var)
        self.progress.pack(side="right", padx=(10, 10))
        self.progress.pack_forget()  # Hidden initially

        # Chat area with improved visuals
        chat_frame = ttk.LabelFrame(main_container, text="Conversation", padding="8")
        chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_area = ScrolledText(chat_frame, wrap=tk.WORD, height=20, 
                                     font=("Segoe UI", 11), bg="#ffffff", fg="#333333",
                                     insertbackground="#333333", borderwidth=0,
                                     padx=10, pady=10)
        self.chat_area.configure(state="disabled")
        self.chat_area.pack(fill="both", expand=True)

        # Prompt row with improved layout and button styling
        prompt_frame = ttk.Frame(main_container)
        prompt_frame.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(prompt_frame, textvariable=self.input_var, 
                                   font=("Segoe UI", 11), style="Prompt.TEntry")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_entry.focus_set()

        self.send_button = ttk.Button(prompt_frame, text="🚀 Send", command=self.send_prompt_threaded, 
                                    style="Primary.TButton")
        self.send_button.pack(side="left")

        # Key bindings
        self.root.bind("<Return>", self.send_prompt_threaded)
        self.root.bind("<Control-l>", lambda e: self.browse_file())
        self.root.bind("<Control-p>", lambda e: self.show_user_prompts())
        
        # State variables
        self.df = None
        self.processing = False
        
        # Welcome message
        self.append_chat("📘 AI Excel Assistant Ready! Please load an Excel file to begin.")

    def _apply_styling(self):
        """Apply custom styling to the application."""
        style = ttk.Style()
        style.theme_use("clam")  # Base theme
        
        # Define colors
        bg_color = "#f5f7fa"
        fg_color = "#333333"
        accent_color = "#4361ee"
        accent_hover = "#3a56d4"
        button_bg = "#ffffff"
        button_hover = "#f0f0f0"
        
        # Configure base styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color, font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        
        # Entry styling
        style.configure("TEntry", padding=8, relief="flat", fieldbackground="#ffffff")
        style.configure("Prompt.TEntry", padding=10, relief="flat", fieldbackground="#ffffff")
        
        # Button styling
        style.configure("TButton", font=("Segoe UI", 10), padding=8, relief="flat", 
                      background=button_bg, foreground=fg_color)
        style.map("TButton", 
                background=[("active", button_hover), ("pressed", button_hover)],
                relief=[("pressed", "flat")])
        
        # Accent button
        style.configure("Accent.TButton", background=accent_color, foreground="#ffffff")
        style.map("Accent.TButton", 
                background=[("active", accent_hover), ("pressed", accent_hover)])
        
        # Primary button
        style.configure("Primary.TButton", background=accent_color, foreground="#ffffff", 
                      padding=10, font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", 
                background=[("active", accent_hover), ("pressed", accent_hover)])
        
        # Treeview styling for result viewer
        style.configure("Treeview", 
                      background="#ffffff", 
                      foreground="#333333", 
                      fieldbackground="#ffffff",
                      rowheight=30, 
                      font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                      background="#f0f0f0", foreground="#333333", padding=5)
        style.map("Treeview", background=[("selected", accent_color)])

    def append_chat(self, message: str):
        """Add message to chat area with improved formatting."""
        self.chat_area.configure(state="normal")
        if message.startswith(">>>"):
            # User message formatting
            self.chat_area.insert(tk.END, message + "\n", "user_message")
            self.chat_area.tag_configure("user_message", foreground="#333333", font=("Segoe UI", 11, "bold"))
        elif message.startswith("❌"):
            # Error message formatting
            self.chat_area.insert(tk.END, message + "\n", "error_message")
            self.chat_area.tag_configure("error_message", foreground="#e63946")
        elif message.startswith("✅") or message.startswith("📊") or message.startswith("💬"):
            # Success message formatting
            self.chat_area.insert(tk.END, message + "\n", "success_message")
            self.chat_area.tag_configure("success_message", foreground="#2a9d8f")
        else:
            # Regular message
            self.chat_area.insert(tk.END, message + "\n")
        
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)

    def browse_file(self):
        """Open file dialog to select Excel file."""
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xls *.xlsx")],
            title="Select Excel File"
        )
        if path:
            self.file_path_var.set(path)

    def set_processing_state(self, is_processing: bool):
        """Update UI elements based on processing state."""
        self.processing = is_processing
        if is_processing:
            self.progress.pack(side="right", padx=(10, 0))
            self.progress.start(10)
            self.load_button.state(["disabled"])
            self.send_button.state(["disabled"])
        else:
            self.progress.stop()
            self.progress.pack_forget()
            self.load_button.state(["!disabled"])
            self.send_button.state(["!disabled"])
            self.input_entry.focus_set()

    def load_file_threaded(self):
        """Load file in a separate thread to keep UI responsive."""
        if self.processing:
            return
            
        path = self.file_path_var.get()
        if not path:
            messagebox.showwarning("No File", "Please choose a file.")
            return
            
        # Start loading thread
        self.set_processing_state(True)
        threading.Thread(target=self._load_file_task, daemon=True).start()

    def _load_file_task(self):
        """Background task to load Excel file."""
        path = self.file_path_var.get()
        try:
            self.df = load_excel(path)
            self.root.after(0, lambda: self._update_after_load("✅ Excel file loaded successfully.", True))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._update_after_load(f"❌ Load error: {error_msg}", False))

    def _update_after_load(self, message, success):
        """Update UI after file loading completes."""
        self.append_chat(message)
        if success:
            self.status_label.config(text=f"✅ Loaded: {self.file_path_var.get()}")
        else:
            self.status_label.config(text="")
            self.df = None
        self.set_processing_state(False)

    def send_prompt_threaded(self, event=None):
        """Process user prompt in a separate thread."""
        if self.processing:
            return
            
        prompt = self.input_var.get().strip()
        if not prompt:
            return
            
        self.append_chat(f">>> {prompt}")
        self.input_var.set("")

        if prompt.lower() in {"exit", "quit"}:
            self.append_chat("👋 Exiting...")
            self.root.quit()
            return

        if self.df is None:
            self.append_chat("⚠️  Load an Excel file first.")
            return
            
        # Start processing thread
        self.set_processing_state(True)
        threading.Thread(target=self._process_prompt_task, args=(prompt,), daemon=True).start()

    def _process_prompt_task(self, prompt):
        """Background task to process user prompt."""
        try:
            code = generate_code(prompt, self.df.columns)
            result = run_generated_code(self.df, code)
            
            if isinstance(result, pd.DataFrame):
                self.root.after(0, lambda: self._show_dataframe_result(result))
            else:
                response = str(result)
                self.root.after(0, lambda: self._update_after_processing(f"💬 Gemini says:\n{response}"))
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._update_after_processing(f"❌ Error: {error_msg}"))

    def _update_after_processing(self, message):
        """Update UI after prompt processing completes."""
        self.append_chat(message)
        self.set_processing_state(False)

    def _show_dataframe_result(self, df):
        """Display DataFrame result and update UI."""
        self.append_chat("📊 Gemini returned a DataFrame (opened in new window).")
        self.show_dataframe(df)
        self.set_processing_state(False)

    def show_user_prompts(self):
        """Show dialog with predefined user prompts."""
        prompt_dialog = tk.Toplevel(self.root)
        prompt_dialog.title("📋 User Prompts")
        prompt_dialog.geometry("600x400")
        prompt_dialog.minsize(500, 300)
        prompt_dialog.configure(bg="#f5f7fa")
        prompt_dialog.transient(self.root)  # Set as transient to main window
        prompt_dialog.grab_set()  # Make dialog modal
        
        # Make dialog position centered on main window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        prompt_dialog.geometry(f"+{x}+{y}")
        
        # Create prompt selection area
        ttk.Label(prompt_dialog, text="Select a predefined prompt:", 
                 font=("Segoe UI", 11, "bold")).pack(pady=(15, 10), padx=20, anchor="w")
        
        # Create frame for prompts with scrollbar
        prompt_frame = ttk.Frame(prompt_dialog)
        prompt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(prompt_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create listbox for prompts
        prompt_listbox = tk.Listbox(prompt_frame, selectmode=tk.SINGLE, 
                                  font=("Segoe UI", 10), bg="white", fg="#333333",
                                  selectbackground="#4361ee", selectforeground="white",
                                  activestyle="none", relief="flat", bd=1,
                                  highlightthickness=2, highlightcolor="#4361ee")
        prompt_listbox.pack(side="left", fill="both", expand=True)
        
        # Connect scrollbar to listbox
        scrollbar.config(command=prompt_listbox.yview)
        prompt_listbox.config(yscrollcommand=scrollbar.set)
        
        # Add predefined prompts to listbox
        for prompt in self.predefined_prompts:
            prompt_listbox.insert(tk.END, prompt)
            
        # Buttons frame
        button_frame = ttk.Frame(prompt_dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Add buttons
        ttk.Button(button_frame, text="Cancel", 
                 command=prompt_dialog.destroy).pack(side="right", padx=(5, 0))
        
        # Select button
        def on_select():
            selection = prompt_listbox.curselection()
            if selection:
                selected_prompt = self.predefined_prompts[selection[0]]
                self.input_var.set(selected_prompt)
                prompt_dialog.destroy()
        
        ttk.Button(button_frame, text="Use Selected Prompt", 
                 command=on_select, style="Primary.TButton").pack(side="right")
        
        # Double click to select
        prompt_listbox.bind("<Double-1>", lambda event: on_select())
        
        # Handle Enter key
        prompt_dialog.bind("<Return>", lambda event: on_select())
        
        # Focus on listbox
        prompt_listbox.focus_set()
        
        # Wait for dialog to close
        self.root.wait_window(prompt_dialog)

    def show_dataframe(self, df: pd.DataFrame):
        """Show DataFrame in a separate window with enhanced styling."""
        win = tk.Toplevel(self.root)
        win.title("Result Viewer")
        win.geometry("1100x700")
        win.minsize(800, 600)
        win.configure(bg="#f5f7fa")
        
        # Add toolbar frame
        toolbar = ttk.Frame(win)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        # Add title
        title_label = ttk.Label(toolbar, text="Data Analysis Results", 
                              font=("Segoe UI", 12, "bold"))
        title_label.pack(side="left")
        
        # Add export button
        export_btn = ttk.Button(toolbar, text="Export to Excel", 
                              command=lambda: self._export_dataframe(df),
                              style="Accent.TButton")
        export_btn.pack(side="right")
        
        # Add search functionality
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="right", padx=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=20)
        search_entry.pack(side="left")
        
        # Create container for treeview and scrollbars
        container = ttk.Frame(win)
        container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical")
        hsb = ttk.Scrollbar(container, orient="horizontal")

        # Create treeview with performance optimizations
        tree = ttk.Treeview(container, columns=list(df.columns), show="headings",
                          yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        # Configure column headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120, minwidth=80)
            
            # Add sorting functionality
            tree.heading(col, text=col, command=lambda c=col: self._sort_treeview(tree, c, False))

        # Optimize rendering by batching updates
        # Only load visible rows initially, with lazy loading for better performance
        self._populate_treeview(tree, df)
        
        # Set up search functionality
        def filter_treeview(*args):
            search_term = search_var.get().lower()
            for item in tree.get_children():
                tree.delete(item)
            
            if search_term:
                filtered_df = df[df.astype(str).apply(lambda row: row.str.lower().str.contains(search_term).any(), axis=1)]
                self._populate_treeview(tree, filtered_df)
            else:
                self._populate_treeview(tree, df)
                
        search_var.trace("w", filter_treeview)

    def _populate_treeview(self, tree, df, batch_size=1000):
        """Populate treeview efficiently with batching for better performance."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        # Convert to list of tuples for faster insertion
        rows = [tuple(row) for _, row in df.iterrows()]
        
        # Insert in batches for better performance
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            for row in batch:
                tree.insert("", "end", values=row)
                
            # Update UI to maintain responsiveness
            self.root.update_idletasks()

    def _sort_treeview(self, tree, col, reverse):
        """Sort treeview column when header is clicked."""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Try to convert to numeric for proper sorting
        try:
            data = [(float(item[0]), item[1]) for item in data]
        except ValueError:
            pass
            
        # Sort the data
        data.sort(reverse=reverse)
        
        # Rearrange items in sorted orderc
        for index, (_, child) in enumerate(data):
            tree.move(child, '', index)
            
        # Switch sort direction next time
        tree.heading(col, command=lambda: self._sort_treeview(tree, col, not reverse))

    def _export_dataframe(self, df):
        """Export DataFrame to Excel file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Export DataFrame to Excel"
        )
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Export Successful", 
                                   f"Data successfully exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))


# ----------------------- main ------------------------- #
if __name__ == "__main__":
    # Set DPI awareness for better display on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    root = tk.Tk()
    app = ExcelAssistantApp(root)
    root.mainloop()