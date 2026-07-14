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
        super().__init__(parent)
        self.parent = parent
        
        # Variables to store paths and user inputs
        self.input_folder = ""
        self.output_folder = ""
        
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
        self.spacing_entry = ttk.Entry(config_frame, textvariable=self.spacing_var, width=10)
        self.spacing_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # RAM Entry
        ttk.Label(config_frame, text="RAM Limit (MB):").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.ram_entry = ttk.Entry(config_frame, textvariable=self.ram_limit_var, width=10)
        self.ram_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

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

    # --- Folder Dialogs ---
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
        # 1. Path check
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both source and output folders.")
            return False
            
        # 2. Spacing sanity check
        try:
            spacing = int(self.spacing_var.get())
            if spacing < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Spacing must be a positive integer (e.g., 0, 10, 20).")
            return False
            
        # 3. RAM Limit sanity check
        try:
            ram = int(self.ram_limit_var.get())
            if ram < 128:  # Minimum safety baseline for Python PIL
                messagebox.showerror("Error", "Please allocate at least 128 MB of RAM.")
                return False
        except ValueError:
            messagebox.showerror("Error", "RAM limit must be a valid integer in Megabytes.")
            return False

        # 4. Input File Checks & Image Hard-caps (1 to 200)
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        self.image_files = [
            os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder)
            if f.lower().endswith(supported_extensions)
        ]
        
        num_files = len(self.image_files)
        if num_files == 0:
            messagebox.showerror("Error", f"No valid images found in the selected folder.\nSupported: {', '.join(supported_extensions)}")
            return False
        elif num_files > 200:
            messagebox.showerror("Error", f"Hard Cap Exceeded! Found {num_files} images. The absolute maximum limit is 200 images.")
            return False
            
        return True

    def start_collage_thread(self):
        if self.validate_inputs():
            # Disable button to prevent double-clicks
            self.btn_start.config(state="disabled")
            
            # Offload processing to a secondary thread so the Tkinter UI doesn't freeze
            thread = Thread(target=self.generate_collage)
            thread.daemon = True
            thread.start()

    # --- Core Generation Logic ---
    def generate_collage(self):
        try:
            spacing = int(self.spacing_var.get())
            ram_limit_mb = int(self.ram_limit_var.get())
            
            # Approximate max pixels we can safely hold in RAM (using a conservative 3 bytes per pixel)
            # Max Pixels = (RAM in MB * 1024 * 1024) / 3
            max_pixels_allowed = (ram_limit_mb * 1024 * 1024) // 3
            
            num_images = len(self.image_files)
            self.status_label.config(text=f"Initializing {num_images} images...")
            self.progress_bar['value'] = 0
            self.root_update()
            
            start_time = time.time()
            
            # Grid calculation 
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            
            max_pixels_per_tile = max_pixels_allowed // num_images
            max_tile_dimension = int(math.sqrt(max_pixels_per_tile))
            
            # Target width/height 
            with Image.open(self.image_files[0]) as first_img:
                aspect_ratio = first_img.width / first_img.height
                
            if aspect_ratio >= 1:
                tile_w = min(400, max_tile_dimension) 
                tile_h = int(tile_w / aspect_ratio)
            else:
                tile_h = min(400, max_tile_dimension)
                tile_w = int(tile_h * aspect_ratio)

            processed_images = []
            
            for index, file_path in enumerate(self.image_files):
                # UI status updates
                self.status_label.config(text=f"Processing image {index + 1}/{num_images}...")
                
                # Load and instantly downscale image to stay under RAM limit safely
                with Image.open(file_path) as img:
                    # Drop alpha channels to maintain uniform RGB color models
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    resized_tile = img.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
                    processed_images.append(resized_tile)
                
                # Math for live ETA / Elapsed tracking
                percent = int(((index + 1) / (num_images * 2)) * 100) # Pre-processing is first 50% of task
                self.progress_bar['value'] = percent
                
                elapsed = time.time() - start_time
                avg_time = elapsed / (index + 1)
                eta = avg_time * ((num_images * 2) - (index + 1))
                
                self.time_label.config(text=f"Spent: {int(elapsed)}s | Est. Left: {int(eta)}s")
                self.root_update()

            # Step 2: Assemble the Collage Canvas
            self.status_label.config(text="Stitching collage canvas...")
            
            collage_width = (cols * tile_w) + ((cols + 1) * spacing)
            collage_height = (rows * tile_h) + ((rows + 1) * spacing)
            
            # Create the master blank canvas
            collage_canvas = Image.new("RGB", (collage_width, collage_height), color=(255, 255, 255))
            
            for index, img in enumerate(processed_images):
                row = index // cols
                col = index % cols
                
                x = (col * tile_w) + ((col + 1) * spacing)
                y = (row * tile_h) + ((row + 1) * spacing)
                
                collage_canvas.paste(img, (x, y))
                
                # Close the tile to free memory
                img.close()
                
                # Progress math for final half of compilation
                curr_step = num_images + index + 1
                percent = int((curr_step / (num_images * 2)) * 100)
                self.progress_bar['value'] = percent
                
                elapsed = time.time() - start_time
                avg_time = elapsed / curr_step
                eta = avg_time * ((num_images * 2) - curr_step)
                
                self.time_label.config(text=f"Spent: {int(elapsed)}s | Est. Left: {int(eta)}s")
                self.root_update()

            # Save Output
            self.status_label.config(text="Saving output collage...")
            output_path = os.path.join(self.output_folder, f"collage_{int(time.time())}.jpg")
            collage_canvas.save(output_path, "JPEG", quality=90)
            
            # Memory Cleanup
            collage_canvas.close()
            del processed_images
            gc.collect()
            
            # Finished state
            self.progress_bar['value'] = 100
            self.status_label.config(text="Done!")
            total_elapsed = time.time() - start_time
            self.time_label.config(text=f"Completed in {int(total_elapsed)}s!")
            
            messagebox.showinfo("Success", f"Collage successfully compiled!\nSaved to: {output_path}")

        except Exception as e:
            messagebox.showerror("Runtime Error", f"An unexpected error occurred: {str(e)}")
        finally:
           
            self.btn_start.config(state="normal")

    def root_update(self):
       
        try:
            self.update_idletasks()
        except Exception:
            pass


# Standalone runner
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Multi-Tool Suite: Collage Maker")
    root.geometry("500x450")
    root.resizable(False, False)
    
   
    app = CollageMaker(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()