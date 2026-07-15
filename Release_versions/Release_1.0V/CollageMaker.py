import os
import time
import math
import gc
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class CollageMaker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")
        self.parent = parent
        
        # Variables to store paths and user inputs 
        self.input_folder = ""
        self.output_folder = ""
        self.image_files = []
        
        # Tkinter variables for automatic UI updating
        self.spacing_var = tk.StringVar(value="10")  # Default pixel spacing
        self.ram_limit_var = tk.StringVar(value="1024")  # Default RAM limit in MB
        
        self.create_widgets()

    def create_widgets(self):
        # Configure grid expansion so things scale nicely
        self.columnconfigure(0, weight=1)
        
        # --- SECTION 1: Folder Selection ---
        folder_frame = ttk.LabelFrame(self, text=" 1. Folder Locations ")
        folder_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        folder_frame.columnconfigure(1, weight=1)
        
        # Input Folder
        ttk.Button(folder_frame, text="Select Source Folder", command=self.browse_input).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_label = ttk.Label(folder_frame, text="No folder selected", wraplength=350)
        self.input_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Output Folder
        ttk.Button(folder_frame, text="Select Output Folder", command=self.browse_output).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_label = ttk.Label(folder_frame, text="No folder selected", wraplength=350)
        self.output_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # --- SECTION 2: Configuration Settings ---
        config_frame = ttk.LabelFrame(self, text=" 2. Collage Configuration ")
        config_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Spacing Entry
        ttk.Label(config_frame, text="Spacing (pixels):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(config_frame, textvariable=self.spacing_var, width=10).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # RAM Entry
        ttk.Label(config_frame, text="RAM Limit (MB):").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Entry(config_frame, textvariable=self.ram_limit_var, width=10).grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # --- SECTION 3: Progress & Action ---
        action_frame = ttk.LabelFrame(self, text=" 3. Status & Execution ")
        action_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(action_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Status Label
        self.status_label = ttk.Label(action_frame, text="Ready", anchor="center")
        self.status_label.grid(row=1, column=0, padx=10, pady=2, sticky="ew")
        
        # Time Tracker Label
        self.time_label = ttk.Label(action_frame, text="Time Spent: 0s | Time Left: --", anchor="center")
        self.time_label.grid(row=2, column=0, padx=10, pady=2, sticky="ew")
        
        # Start Button
        self.btn_start = ttk.Button(action_frame, text="Generate Collage", command=self.start_collage_thread)
        self.btn_start.grid(row=3, column=0, padx=10, pady=10)

    # --- Folder Dialogs (Original Logic Retained) ---
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            self.input_folder = folder
            self.input_label.config(text=os.path.basename(folder) if len(folder) > 40 else folder)

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Save Location")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=os.path.basename(folder) if len(folder) > 40 else folder)

    # --- Verification & Execution ---
    def validate_inputs(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both source and output folders.")
            return False
            
        try:
            spacing = int(self.spacing_var.get())
            if spacing < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Spacing must be a positive integer.")
            return False
            
        try:
            ram = int(self.ram_limit_var.get())
            if ram < 128:
                messagebox.showerror("Error", "Please allocate at least 128 MB of RAM.")
                return False
        except ValueError:
            messagebox.showerror("Error", "RAM limit must be a valid integer in Megabytes.")
            return False

        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        self.image_files = [
            os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder)
            if f.lower().endswith(supported_extensions)
        ]
        
        num_files = len(self.image_files)
        if num_files == 0:
            messagebox.showerror("Error", f"No valid images found.\nSupported: {', '.join(supported_extensions)}")
            return False
        elif num_files > 200:
            messagebox.showerror("Error", f"Hard Cap Exceeded! Found {num_files} images. The absolute maximum limit is 200 images.")
            return False
            
        return True

    def start_collage_thread(self):
        if self.validate_inputs():
            self.btn_start.config(state="disabled")
            thread = Thread(target=self.generate_collage)
            thread.daemon = True
            thread.start()

    # --- Core Generation Logic (Original & Debugged Ratios Retained) ---
    def generate_collage(self):
        processed_images = []
        try:
            spacing = int(self.spacing_var.get())
            ram_limit_mb = int(self.ram_limit_var.get())
            
            max_pixels_allowed = (ram_limit_mb * 1024 * 1024) // 3
            num_images = len(self.image_files)
            
            self.status_label.config(text=f"Initializing {num_images} images...")
            self.progress_bar['value'] = 0
            self.root_update()
            
            start_time = time.time()
            
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            max_pixels_per_tile = max_pixels_allowed // num_images
            
            with Image.open(self.image_files[0]) as first_img:
                aspect_ratio = first_img.width / first_img.height
            
            max_tile_h = math.sqrt(max_pixels_per_tile / aspect_ratio)
            max_tile_w = max_tile_h * aspect_ratio
            
            tile_w = min(400, int(max_tile_w))
            tile_h = min(int(400 / aspect_ratio), int(max_tile_h))
            
            tile_w, tile_h = max(16, tile_w), max(16, tile_h)

            # Step 1: Resizing Phase
            for index, file_path in enumerate(self.image_files):
                self.status_label.config(text=f"Processing image {index + 1}/{num_images}...")
                
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    resized_tile = img.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
                    processed_images.append(resized_tile)
                
                percent = int(((index + 1) / (num_images * 2)) * 100)
                self.progress_bar['value'] = percent
                
                elapsed = time.time() - start_time
                avg_time = elapsed / (index + 1)
                eta = avg_time * ((num_images * 2) - (index + 1))
                
                self.time_label.config(text=f"Spent: {int(elapsed)}s | Est. Left: {int(eta)}s")
                self.root_update()

            # Step 2: Stitching Phase
            self.status_label.config(text="Stitching collage canvas...")
            
            collage_width = (cols * tile_w) + ((cols + 1) * spacing)
            collage_height = (rows * tile_h) + ((rows + 1) * spacing)
            
            collage_canvas = Image.new("RGB", (collage_width, collage_height), color=(255, 255, 255))
            
            for index, img in enumerate(processed_images):
                row = index // cols
                col = index % cols
                
                x = (col * tile_w) + ((col + 1) * spacing)
                y = (row * tile_h) + ((row + 1) * spacing)
                
                collage_canvas.paste(img, (x, y))
                img.close()  
                
                curr_step = num_images + index + 1
                percent = int((curr_step / (num_images * 2)) * 100)
                self.progress_bar['value'] = percent
                
                elapsed = time.time() - start_time
                avg_time = elapsed / curr_step
                eta = avg_time * ((num_images * 2) - curr_step)
                
                self.time_label.config(text=f"Spent: {int(elapsed)}s | Est. Left: {int(eta)}s")
                self.root_update()

            # Step 3: Export Output File
            self.status_label.config(text="Saving output collage...")
            output_path = os.path.join(self.output_folder, f"collage_{int(time.time())}.jpg")
            collage_canvas.save(output_path, "JPEG", quality=90)
            collage_canvas.close()
            
            self.progress_bar['value'] = 100
            self.status_label.config(text="Done!")
            self.time_label.config(text=f"Completed in {int(time.time() - start_time)}s!")
            
            messagebox.showinfo("Success", f"Collage successfully compiled!\nSaved to: {output_path}")

        except Exception as e:
            messagebox.showerror("Runtime Error", f"An unexpected error occurred: {str(e)}")
        finally:
            for img in processed_images:
                try:
                    img.close()
                except Exception:
                    pass
            del processed_images
            gc.collect()
            self.btn_start.config(state="normal")

    def root_update(self):
        try:
            self.update_idletasks()
        except Exception:
            pass

# Standalone engine execution theme wrapper 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Multi-Tool Suite: Collage Maker (Standalone Preview)")
    root.geometry("500x450")
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
    style.configure("TProgressbar", thickness=8, troughcolor=self.BG_CARD if 'self' in locals() else BG_CARD, background=ACCENT_BLUE)
    style.configure("TButton", font=("Segoe UI", 10, "bold"), background=ACCENT_BLUE, foreground=FG_LIGHT, borderwidth=0, padding=8)
    style.map("TButton", background=[("active", "#357ABD")])
    
    app = CollageMaker(root)
    app.pack(fill="both", expand=True)
    root.mainloop()