import tkinter as tk
from tkinter import ttk

# Import modular user tools 
from ImageResizer import ImageResizer
from CollageMaker import CollageMaker

class ModernDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Media Utility Workspace Suite")
        self.geometry("850x580")
        self.minimum_size = (800, 550)
        self.resizable(True, True)
        
        # Configure global modern system colors 
        self.BG_DARK = "#1E1E24"
        self.BG_SIDEBAR = "#141419"
        self.BG_CARD = "#2A2A32"
        self.FG_LIGHT = "#F5F5FA"
        self.ACCENT_BLUE = "#4A90E2"
        
        self.configure(bg=self.BG_DARK)
        self.setup_styles()
        
        # Core Active Panel View State Container
        self.active_frame = None
        
        self.build_layout()
        self.show_welcome_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Base Layout Theme mappings
        style.configure(".", background=self.BG_DARK, foreground=self.FG_LIGHT, font=("Segoe UI", 10))
        style.configure("Card.TFrame", background=self.BG_DARK)
        
        # Label Frame configurations
        style.configure("TLabelframe", background=self.BG_DARK, bordercolor=self.BG_CARD, borderwidth=1)
        style.configure("TLabelframe.Label", background=self.BG_DARK, foreground=self.ACCENT_BLUE, font=("Segoe UI", 10, "bold"))
        
        # Interactive standard widget custom properties
        style.configure("TLabel", background=self.BG_DARK, foreground=self.FG_LIGHT)
        style.configure("TEntry", fieldbackground=self.BG_CARD, background=self.BG_CARD, foreground=self.FG_LIGHT, borderwidth=0)
        style.configure("TCombobox", fieldbackground=self.BG_CARD, background=self.BG_CARD, foreground=self.FG_LIGHT, borderwidth=0)
        
        # Progressbar overrides
        style.configure("TProgressbar", thickness=8, troughcolor=self.BG_CARD, background=self.ACCENT_BLUE)
        
        # Custom Navigational Button styling
        style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), background=self.BG_CARD, foreground=self.FG_LIGHT, borderwidth=0, padding=12)
        style.map("Nav.TButton", background=[("active", self.ACCENT_BLUE)])
        
        # Main Process Action Button layout rules
        style.configure("TButton", font=("Segoe UI", 10, "bold"), background=self.ACCENT_BLUE, foreground=self.FG_LIGHT, borderwidth=0, padding=8)
        style.map("TButton", background=[("active", "#357ABD")])

    def build_layout(self):
        # Configure overall window grid layout
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # 1. Left Navigation Panel
        sidebar = tk.Frame(self, bg=self.BG_SIDEBAR, width=220)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        lbl_brand = tk.Label(sidebar, text=" UTILITY WORKSPACE ", bg=self.BG_SIDEBAR, fg=self.ACCENT_BLUE, font=("Segoe UI", 12, "bold"))
        lbl_brand.pack(pady=30, padx=10)

        # Dynamic Content Navigation Button hooks
        btn_resize = ttk.Button(sidebar, text="Image Resizer", style="Nav.TButton", command=lambda: self.switch_view(ImageResizer))
        btn_resize.pack(fill="x", padx=15, pady=6)

        btn_collage = ttk.Button(sidebar, text="Collage Maker", style="Nav.TButton", command=lambda: self.switch_view(CollageMaker))
        btn_collage.pack(fill="x", padx=15, pady=6)
        
        # =========================================================================
        # FUTURE EXTENSION HOOK: (I will add more)
        # e.g., btn_tool3 = ttk.Button(sidebar, text="New Tool", style="Nav.TButton", command=lambda: self.switch_view(NewToolClass))
        # =========================================================================

        lbl_footer = tk.Label(sidebar, text="v1.1.0 Ready", bg=self.BG_SIDEBAR, fg=self.BG_CARD, font=("Segoe UI", 8))
        lbl_footer.pack(side="bottom", pady=20)

        # 2. Central Component Display Viewport Frame 
        self.content_viewport = tk.Frame(self, bg=self.BG_DARK)
        self.content_viewport.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.content_viewport.columnconfigure(0, weight=1)
        self.content_viewport.rowconfigure(0, weight=1)

    def show_welcome_screen(self):
        self.clear_viewport()
        welcome_frame = tk.Frame(self.content_viewport, bg=self.BG_DARK)
        welcome_frame.grid(row=0, column=0, sticky="nsew")
        
        lbl_title = tk.Label(welcome_frame, text="Welcome to your Media Workspace", bg=self.BG_DARK, fg=self.FG_LIGHT, font=("Segoe UI", 16, "bold"))
        lbl_title.pack(expand=True, anchor="s", pady=10)
        
        lbl_sub = tk.Label(welcome_frame, text="Select a tool module from the left dashboard options to get started.", bg=self.BG_DARK, fg=self.BG_CARD, font=("Segoe UI", 11))
        lbl_sub.pack(expand=True, anchor="n", pady=10)
        
        self.active_frame = welcome_frame

    def switch_view(self, frame_class):
        """ Clears out current active component framework and swaps viewport canvas configurations """
        self.clear_viewport()
        
        # Instantiate the newly selected panel structure context into the workspace grid viewport
        self.active_frame = frame_class(self.content_viewport)
        self.active_frame.grid(row=0, column=0, sticky="nsew")

    def clear_viewport(self):
        if self.active_frame:
            self.active_frame.destroy()

if __name__ == "__main__":
    app = ModernDashboard()
    app.mainloop()