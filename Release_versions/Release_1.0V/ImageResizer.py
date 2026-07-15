import os
import time
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class ImageResizer(ttk.Frame):
    def __init__(self, parent):
       
        super().__init__(parent, style="Card.TFrame")
        self.parent = parent
        
        # Variables to store paths and user inputs 
        self.input_paths = []
        self.output_dir = tk.StringVar()
        self.width_var = tk.StringVar(value="512")
        self.height_var = tk.StringVar(value="512")
        self.format_var = tk.StringVar(value="PNG")

        self.create_widgets()

    def create_widgets(self):
        # Configure grid expansion 
        self.columnconfigure(0, weight=1)

        # --- SECTION 1: Folder/File Selection ---
        file_frame = ttk.LabelFrame(self, text=" 1. Select Images ")
        file_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(file_frame, text="Browse Files", command=self.browse_files).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.file_label = ttk.Label(file_frame, text="No files selected (Supports multi-selection)", wraplength=350)
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # --- SECTION 2: Resizing Options ---
        size_frame = ttk.LabelFrame(self, text=" 2. Resize Options ")
        size_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        size_frame.columnconfigure(1, weight=1)
        size_frame.columnconfigure(3, weight=1)
        size_frame.columnconfigure(5, weight=1)

        # Width Entry
        ttk.Label(size_frame, text="Width (px):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Height Entry
        ttk.Label(size_frame, text="Height (px):").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Format Menu
        ttk.Label(size_frame, text="Format:").grid(row=0, column=4, padx=10, pady=10, sticky="e")
        formats = ["PNG", "JPEG", "BMP", "WEBP"]
        self.format_menu = ttk.Combobox(size_frame, textvariable=self.format_var, values=formats, width=8, state="readonly")
        self.format_menu.grid(row=0, column=5, padx=10, pady=10, sticky="w")

        # --- SECTION 3: Output Folder ---
        out_frame = ttk.LabelFrame(self, text=" 3. Output Folder ")
        out_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        out_frame.columnconfigure(1, weight=1)

        ttk.Button(out_frame, text="Select Folder", command=self.browse_output).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.out_label = ttk.Label(out_frame, text="No output folder selected", wraplength=350)
        self.out_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # --- SECTION 4: Status & Execution ---
        action_frame = ttk.LabelFrame(self, text=" 4. Status & Execution ")
        action_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew")
        action_frame.columnconfigure(0, weight=1)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(action_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Status Label
        self.status_label = ttk.Label(action_frame, text="Ready to process.", anchor="center")
        self.status_label.grid(row=1, column=0, padx=10, pady=2, sticky="ew")
        
        # Time Tracker Label
        self.time_label = ttk.Label(action_frame, text="Time Spent: 0s | Time Left: --", anchor="center")
        self.time_label.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

        # Start Button
        self.btn_start = ttk.Button(action_frame, text="Start Processing", command=self.start_processing_thread)
        self.btn_start.grid(row=3, column=0, padx=10, pady=10)

    # --- File/Folder Dialogs  ---
    def browse_files(self):
        files = filedialog.askopenfilenames(title="Select Images to Resize", filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if files:
            self.input_paths = list(files)
            self.file_label.config(text=f"Selected {len(files)} image(s)")

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir.set(folder)
            self.out_label.config(text=os.path.basename(folder) if len(folder) > 40 else folder)

    # --- Verification & Execution ---
    def validate_inputs(self):
        if not self.input_paths or not self.output_dir.get():
            messagebox.showerror("Error", "Please select input files and an output folder.")
            return False
        try:
            w, h = int(self.width_var.get()), int(self.height_var.get())
            if not (32 <= w <= 8192) or not (32 <= h <= 8192):
                raise ValueError
            return w, h
        except ValueError:
            messagebox.showerror("Error", "Dimensions must be integers between 32 and 8192.")
            return False

    def start_processing_thread(self):
        validation = self.validate_inputs()
        if validation:
            self.btn_start.config(state="disabled")
            w, h = validation
            t = Thread(target=self.process_images, args=(w, h))
            t.daemon = True
            t.start()

    # --- Core Resizing Logic  ---
    def process_images(self, width, height):
        try:
            total = len(self.input_paths)
            fmt = self.format_var.get().upper()
            ext = ".jpg" if fmt == "JPEG" else f".{fmt.lower()}"
            start_time = time.time()

            for idx, file_path in enumerate(self.input_paths):
                base = os.path.basename(file_path)
                self.status_label.config(text=f"Processing image {idx + 1}/{total}: {base}")
                
                with Image.open(file_path) as img:
                    # Converts transparent background vectors/images to clean RGB if converting to standard JPEG
                    if fmt == "JPEG" and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    resized = img.resize((width, height), Image.Resampling.LANCZOS)
                    out_path = os.path.join(self.output_dir.get(), os.path.splitext(base)[0] + ext)
                    resized.save(out_path, format=fmt)

                # Metrics update calculations
                processed = idx + 1
                pct = (processed / total) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / processed) * (total - processed)
                
                self.progress_bar['value'] = pct
                self.time_label.config(text=f"Spent: {int(elapsed)}s | Est. Left: {int(eta)}s")
                self.root_update()

            self.status_label.config(text="Processing Complete!")
            self.time_label.config(text=f"Completed in {int(time.time() - start_time)}s!")
            messagebox.showinfo("Success", f"Successfully resized {total} images!")
        except Exception as e:
            messagebox.showerror("Error", f"An execution error occurred: {str(e)}")
        finally:
            self.btn_start.config(state="normal")

    def root_update(self):
        try:
            self.update_idletasks()
        except Exception:
            pass

# Standalone engine execution theme wrapper 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Multi-Tool Suite: Image Resizer (Standalone Preview)")
    root.geometry("500x520")
    root.resizable(False, False)
    
   
    BG_DARK = "#1E1E24"
    BG_CARD = "#2A2A32"
    FG_LIGHT = "#F5F5FA"
    ACCENT_BLUE = "#4A90E2"
    
    root.configure(bg=BG_DARK)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background=BG_DARK, foreground=FG_LIGHT, font=("Segoe UI", 10))
    style.configure("Card.TFrame", background=BG_DARK)
    style.configure("TLabelframe", background=BG_DARK, bordercolor=BG_CARD, borderwidth=1)
    style.configure("TLabelframe.Label", background=BG_DARK, foreground=ACCENT_BLUE, font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", background=BG_DARK, foreground=FG_LIGHT)
    style.configure("TEntry", fieldbackground=BG_CARD, background=BG_CARD, foreground=FG_LIGHT, borderwidth=0)
    style.configure("TCombobox", fieldbackground=BG_CARD, background=BG_CARD, foreground=FG_LIGHT, borderwidth=0)
    style.configure("TProgressbar", thickness=8, troughcolor=BG_CARD, background=ACCENT_BLUE)
    style.configure("TButton", font=("Segoe UI", 10, "bold"), background=ACCENT_BLUE, foreground=FG_LIGHT, borderwidth=0, padding=8)
    style.map("TButton", background=[("active", "#357ABD")])
    
    app = ImageResizer(root)
    app.pack(fill="both", expand=True)
    root.mainloop()