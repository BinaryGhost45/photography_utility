import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
from PIL import Image

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Image Resizer")
        self.root.geometry("550x450")
        self.root.resizable(False, False)

        # State variables
        self.input_paths = []
        self.output_dir = tk.StringVar()
        self.width_var = tk.StringVar(value="512")
        self.height_var = tk.StringVar(value="512")
        self.format_var = tk.StringVar(value="PNG")

        self.create_widgets()

    def create_widgets(self):
        # 1. Input File Selection
        file_frame = ttk.LabelFrame(self.root, text=" 1. Select Images ", padding=10)
        file_frame.pack(fill="x", padx=15, pady=10)

        self.file_label = ttk.Label(file_frame, text="No files selected (Supports multiple selection)", wraplength=400)
        self.file_label.pack(side="left", fill="x", expand=True)
        
        btn_browse_files = ttk.Button(file_frame, text="Browse Files", command=self.browse_files)
        btn_browse_files.pack(side="right", padx=5)

        # 2. Resizing Options
        size_frame = ttk.LabelFrame(self.root, text=" 2. Resize Dimensions (32 to 8192) ", padding=10)
        size_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(size_frame, text="Width:").pack(side="left", padx=5)
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(side="left", padx=5)

        ttk.Label(size_frame, text="x  Height:").pack(side="left", padx=5)
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(side="left", padx=5)

        # 3. Format Selection
        ttk.Label(size_frame, text="Format:").pack(side="left", padx=(20, 5))
        formats = ["PNG", "JPEG", "BMP", "WEBP"]
        format_menu = ttk.Combobox(size_frame, textvariable=self.format_var, values=formats, width=8, state="readonly")
        format_menu.pack(side="left", padx=5)

        # 4. Output Location
        out_frame = ttk.LabelFrame(self.root, text=" 3. Output Folder ", padding=10)
        out_frame.pack(fill="x", padx=15, pady=10)

        self.out_label = ttk.Label(out_frame, text="No output folder selected", wraplength=400)
        self.out_label.pack(side="left", fill="x", expand=True)

        btn_browse_out = ttk.Button(out_frame, text="Select Folder", command=self.browse_output)
        btn_browse_out.pack(side="right", padx=5)

        # 5. Progress and Status
        self.progress_frame = ttk.Frame(self.root, padding=10)
        self.progress_frame.pack(fill="x", padx=15, pady=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)

        self.status_label = ttk.Label(self.progress_frame, text="Ready to start.", font=("TkDefaultFont", 9, "italic"))
        self.status_label.pack(anchor="w")

        self.time_label = ttk.Label(self.progress_frame, text="Time Spent: 0s | Left: --")
        self.time_label.pack(anchor="w", pady=2)

        # 6. Action Button
        self.btn_start = ttk.Button(self.root, text="Start Processing", command=self.start_processing_thread, style="Accent.TButton")
        self.btn_start.pack(pady=10)

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images to Resize",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if files:
            self.input_paths = list(files)
            self.file_label.config(text=f"Selected {len(files)} image(s)")

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir.set(folder)
            self.out_label.config(text=folder)

    def validate_inputs(self):
        if not self.input_paths:
            messagebox.showerror("Error", "Please select at least one input image.")
            return False
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return False
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError:
            messagebox.showerror("Error", "Dimensions must be whole numbers.")
            return False

        if not (32 <= width <= 8192) or not (32 <= height <= 8192):
            messagebox.showerror("Error", "Dimensions must be between 32x32 and 8192x8192.")
            return False
            
        return width, height

    def start_processing_thread(self):
        # Run processing in a separate thread so the GUI doesn't freeze
        validation = self.validate_inputs()
        if not validation:
            return
        
        width, height = validation
        self.btn_start.config(state="disabled")
        
        thread = Thread(target=self.process_images, args=(width, height))
        thread.start()

    def process_images(self, width, height):
        total_files = len(self.input_paths)
        target_format = self.format_var.get().upper()
        ext = ".jpg" if target_format == "JPEG" else f".{target_format.lower()}"
        
        start_time = time.time()

        for index, file_path in enumerate(self.input_paths):
            try:
                # Update status
                base_name = os.path.basename(file_path)
                self.status_label.config(text=f"Processing: {base_name}")
                
                # Resize and save
                with Image.open(file_path) as img:
                    # RGB conversion is necessary if saving PNG/RGBA as JPEG
                    if target_format == "JPEG" and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                    
                    out_filename = os.path.splitext(base_name)[0] + ext
                    out_path = os.path.join(self.output_dir.get(), out_filename)
                    resized_img.save(out_path, format=target_format)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

            # Calculate time tracking
            processed = index + 1
            percent = (processed / total_files) * 100
            elapsed_time = time.time() - start_time
            
            # Simple linear extrapolation for ETA
            avg_time_per_file = elapsed_time / processed
            remaining_files = total_files - processed
            estimated_left = avg_time_per_file * remaining_files

            # Update UI elements safely from thread
            self.progress_bar['value'] = percent
            self.time_label.config(
                text=f"Time Spent: {int(elapsed_time)}s | Left: {int(estimated_left)}s"
            )
            self.root.update_idletasks()

        # Reset UI on completion
        self.status_label.config(text="Processing Complete!")
        self.time_label.config(text=f"Finished! Total time spent: {int(time.time() - start_time)}s")
        self.btn_start.config(state="normal")
        messagebox.showinfo("Success", f"Successfully resized {total_files} images!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()