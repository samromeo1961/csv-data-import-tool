#!/usr/bin/env python3
"""
zzTakeoff Items Import Converter
Converts estimating software exports (Databuild, PlanSwift, etc.) to zzTakeoff import format
Uses AI to intelligently map and generate required fields
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import os
import webbrowser
from typing import Dict, List, Optional
import anthropic

# Try to import API keys from config file, fallback to environment variables
try:
    from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY
except ImportError:
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Optional imports for different AI providers
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

class ToolTip:
    """Tooltip class for hover hints"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 9))
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class TakeoffConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("zzTakeoff Items Import Converter")
        self.root.geometry("1400x900")

        # Add close confirmation
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Data storage
        self.df = None
        self.mapped_df = None
        self.mapping_history = self.load_mapping_history()
        self.formula_templates = self.load_formula_templates()
        self.custom_property_mappings = {}  # Store custom property column mappings
        self.import_templates = self.load_import_templates()  # Store import format templates

        # AI Clients
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_AVAILABLE and OPENAI_API_KEY else None
        self.deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com") if OPENAI_AVAILABLE and DEEPSEEK_API_KEY else None

        if GOOGLE_AVAILABLE and GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)

        # Available AI providers and models
        self.ai_providers = {
            "Claude": {
                "available": self.anthropic_client is not None,
                "models": [
                    "claude-sonnet-4-20250514",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-opus-20241022",
                    "claude-3-5-haiku-20241022"
                ],
                "signup_url": "https://console.anthropic.com/settings/keys",
                "name": "Anthropic Claude"
            },
            "ChatGPT": {
                "available": self.openai_client is not None,
                "models": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo"
                ],
                "signup_url": "https://platform.openai.com/api-keys",
                "name": "OpenAI ChatGPT"
            },
            "Gemini": {
                "available": GOOGLE_AVAILABLE and GOOGLE_API_KEY is not None,
                "models": [
                    "gemini-2.0-flash-exp",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ],
                "signup_url": "https://aistudio.google.com/app/apikey",
                "name": "Google Gemini"
            },
            "DeepSeek": {
                "available": self.deepseek_client is not None,
                "models": [
                    "deepseek-chat",
                    "deepseek-reasoner"
                ],
                "signup_url": "https://platform.deepseek.com/api_keys",
                "name": "DeepSeek"
            }
        }

        self.selected_provider = tk.StringVar(value="Claude")
        self.selected_model = tk.StringVar(value="claude-sonnet-4-20250514")

        # Unit system selection
        self.unit_system = tk.StringVar(value="Metric")

        # Define math.js variable names based on unit system
        self.mathjs_variables = {
            "Metric": {
                "Area": {
                    "base": "[Area]",
                    "units": ["m2", "m²", "SM", "SQ M", "SQM", "cm2", "cm²", "mm2", "mm²", "km2", "km²"],
                    "description": "Area in square meters",
                    "special_vars": [
                        "[Wall Area:m2]", "[Wall Area:cm2]", "[Wall Area:mm2]", "[Wall Area:km2]",
                        "[Floor Area:m2]", "[Floor Area:cm2]", "[Floor Area:mm2]",
                        "[Ceiling Area:m2]", "[Ceiling Area:cm2]", "[Ceiling Area:mm2]",
                        "[Roof Area:m2]", "[Roof Area:cm2]", "[Roof Area:mm2]"
                    ]
                },
                "Linear": {
                    "base": "[Length]",
                    "units": ["M", "m", "LM", "metres", "meters", "cm", "mm", "km"],
                    "description": "Length in meters",
                    "special_vars": [
                        "[Linear:m]", "[Linear:cm]", "[Linear:mm]", "[Linear:km]",
                        "[Perimeter:m]", "[Perimeter:cm]", "[Perimeter:mm]"
                    ]
                },
                "Count": {
                    "base": "[Count]",
                    "units": ["EA", "Ea", "each", "EACH", "THOUS", "bag", "BAG", "TONNE", "PACKETS", "PACKET"],
                    "description": "Item count",
                    "special_vars": ["[Point Count]", "[Item Count]"]
                },
                "Volume": {
                    "base": "[Volume]",
                    "units": ["CU M", "m3", "m³", "cm3", "cm³", "mm3", "mm³"],
                    "description": "Volume in cubic meters",
                    "special_vars": [
                        "[Volume:m3]", "[Volume:cm3]", "[Volume:mm3]",
                        "[Concrete Volume:m3]", "[Concrete Volume:cm3]"
                    ]
                }
            },
            "Imperial": {
                "Area": {
                    "base": "[Area]",
                    "units": ["SF", "SQ FT", "ft2", "ft²", "FT2", "in2", "in²", "IN2", "yd2", "yd²", "YD2"],
                    "description": "Area in square feet",
                    "special_vars": [
                        "[Wall Area:FT2]", "[Wall Area:IN2]", "[Wall Area:YD2]",
                        "[Floor Area:FT2]", "[Floor Area:IN2]", "[Floor Area:YD2]",
                        "[Ceiling Area:FT2]", "[Ceiling Area:IN2]",
                        "[Roof Area:FT2]", "[Roof Area:IN2]", "[Roof Area:YD2]"
                    ]
                },
                "Linear": {
                    "base": "[Length]",
                    "units": ["FT", "ft", "feet", "LF", "in", "IN", "inch", "yd", "YD", "yard"],
                    "description": "Length in feet",
                    "special_vars": [
                        "[Linear:FT]", "[Linear:IN]", "[Linear:YD]",
                        "[Perimeter:FT]", "[Perimeter:IN]", "[Perimeter:YD]"
                    ]
                },
                "Count": {
                    "base": "[Count]",
                    "units": ["EA", "Ea", "each", "EACH", "bag", "BAG", "ton", "TON"],
                    "description": "Item count",
                    "special_vars": ["[Point Count]", "[Item Count]"]
                },
                "Volume": {
                    "base": "[Volume]",
                    "units": ["CF", "CU FT", "ft3", "ft³", "FT3", "in3", "in³", "IN3", "yd3", "yd³", "YD3"],
                    "description": "Volume in cubic feet",
                    "special_vars": [
                        "[Volume:FT3]", "[Volume:IN3]", "[Volume:YD3]",
                        "[Concrete Volume:FT3]", "[Concrete Volume:YD3]"
                    ]
                }
            }
        }

        self.setup_ui()
    
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header frame with logo and title
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        header_frame.columnconfigure(0, weight=1)

        # Try to load logo
        self.logo_image = None
        logo_files = ['zztakeoff_logo.png', 'zztakeoff-logo.png', 'logo.png', 'zzTakeoff_logo.png']
        for logo_file in logo_files:
            logo_path = os.path.join(os.path.dirname(__file__), logo_file)
            if os.path.exists(logo_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(logo_path)
                    # Resize to 20% of original size
                    new_width = int(img.width * 0.2)
                    new_height = int(img.height * 0.2)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)
                    break
                except Exception as e:
                    print(f"Could not load logo from {logo_file}: {e}")

        # Create header layout
        if self.logo_image:
            # Logo on left
            logo_label = ttk.Label(header_frame, image=self.logo_image)
            logo_label.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)

            # Title next to logo
            title_label = ttk.Label(header_frame, text="Items Import Converter",
                                   font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=1, sticky=tk.W)
        else:
            # No logo - just title (centered)
            title_label = ttk.Label(header_frame, text="zzTakeoff Items Import Converter",
                                   font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=0, columnspan=2)
        
        # Control panel - reorganized into logical groups
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # === SETTINGS GROUP (Collapsible) ===
        self.settings_visible = tk.BooleanVar(value=True)
        settings_header = ttk.Frame(control_frame)
        settings_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        self.settings_toggle_btn = ttk.Button(settings_header, text="▼ Settings",
                                              command=self.toggle_settings, width=15)
        self.settings_toggle_btn.grid(row=0, column=0, sticky=tk.W)
        self.create_tooltip(self.settings_toggle_btn, "Click to show/hide settings panel")

        ttk.Label(settings_header, text="(Configure AI provider and units - usually set once)",
                 foreground="gray", font=('Arial', 8, 'italic')).grid(row=0, column=1, padx=10, sticky=tk.W)

        settings_frame = ttk.Frame(control_frame, padding="10", relief="sunken", borderwidth=1)
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.settings_content_frame = settings_frame

        # Unit System
        ttk.Label(settings_frame, text="Unit System:").grid(row=0, column=0, padx=5, pady=3, sticky=tk.W)
        unit_combo = ttk.Combobox(settings_frame, textvariable=self.unit_system,
                                  values=["Metric", "Imperial"],
                                  state='readonly', width=12)
        unit_combo.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
        self.create_tooltip(unit_combo, "Select Metric (m, m², m³) or Imperial (ft, ft², ft³) units for measurements")

        # AI Provider
        ttk.Label(settings_frame, text="AI Provider:").grid(row=0, column=2, padx=(15, 5), pady=3, sticky=tk.W)
        self.provider_combo = ttk.Combobox(settings_frame, textvariable=self.selected_provider,
                                           values=list(self.ai_providers.keys()),
                                           state='readonly', width=12)
        self.provider_combo.grid(row=0, column=3, padx=5, pady=3, sticky=tk.W)
        self.provider_combo.bind('<<ComboboxSelected>>', self.on_provider_change)
        self.create_tooltip(self.provider_combo, "Choose AI provider: Claude (Anthropic), ChatGPT (OpenAI), Gemini (Google), or DeepSeek")

        # API Status
        self.api_status_label = ttk.Label(settings_frame, text="", foreground="green")
        self.api_status_label.grid(row=0, column=4, padx=5, pady=3, sticky=tk.W)

        # Configure API Key Button
        self.get_key_btn = ttk.Button(settings_frame, text="Configure API Key",
                                      command=self.open_api_key_page)
        self.get_key_btn.grid(row=0, column=5, padx=5, pady=3, sticky=tk.W)
        self.create_tooltip(self.get_key_btn, "Set up or change API key for selected AI provider")

        # Model Selection
        ttk.Label(settings_frame, text="Model:").grid(row=1, column=0, padx=5, pady=3, sticky=tk.W)
        self.model_combo = ttk.Combobox(settings_frame, textvariable=self.selected_model,
                                        state='readonly', width=30)
        self.model_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=3, sticky=tk.W)
        self.update_model_list()
        self.update_api_status()
        self.create_tooltip(self.model_combo, "Select AI model - larger models are more accurate but slower/costlier")

        # === FILE OPERATIONS GROUP (Collapsible) ===
        self.file_ops_visible = tk.BooleanVar(value=True)
        file_ops_header = ttk.Frame(control_frame)
        file_ops_header.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        self.file_ops_toggle_btn = ttk.Button(file_ops_header, text="▼ File Operations",
                                              command=self.toggle_file_ops, width=20)
        self.file_ops_toggle_btn.grid(row=0, column=0, sticky=tk.W)
        self.create_tooltip(self.file_ops_toggle_btn, "Click to show/hide file operations")

        file_ops_frame = ttk.Frame(control_frame, padding="10", relief="sunken", borderwidth=1)
        file_ops_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.file_ops_content_frame = file_ops_frame

        load_btn = ttk.Button(file_ops_frame, text="Load CSV/Excel",
                  command=self.load_file, width=18)
        load_btn.grid(row=0, column=0, padx=5, pady=3)
        self.create_tooltip(load_btn, "Load data from CSV or Excel file exported from your estimating software")

        self.save_progress_btn = ttk.Button(file_ops_frame, text="Save Progress",
                                            command=self.save_progress, state='disabled', width=18)
        self.save_progress_btn.grid(row=0, column=1, padx=5, pady=3)
        self.create_tooltip(self.save_progress_btn, "Save your current work to resume later without re-running AI")

        load_progress_btn = ttk.Button(file_ops_frame, text="Load Progress",
                  command=self.load_progress, width=18)
        load_progress_btn.grid(row=0, column=2, padx=5, pady=3)
        self.create_tooltip(load_progress_btn, "Load previously saved work-in-progress file")

        # === DATA MAPPING GROUP (Collapsible) ===
        self.mapping_visible = tk.BooleanVar(value=True)
        mapping_header = ttk.Frame(control_frame)
        mapping_header.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        self.mapping_toggle_btn = ttk.Button(mapping_header, text="▼ Data Mapping & Templates",
                                             command=self.toggle_mapping, width=25)
        self.mapping_toggle_btn.grid(row=0, column=0, sticky=tk.W)
        self.create_tooltip(self.mapping_toggle_btn, "Click to show/hide data mapping tools")

        mapping_frame = ttk.Frame(control_frame, padding="10", relief="sunken", borderwidth=1)
        mapping_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.mapping_content_frame = mapping_frame

        import_tpl_btn = ttk.Button(mapping_frame, text="Import Templates",
                  command=self.show_import_templates, width=18)
        import_tpl_btn.grid(row=0, column=0, padx=5, pady=3)
        self.create_tooltip(import_tpl_btn, "Manage column mapping templates for different estimating software formats")

        self.custom_props_btn = ttk.Button(mapping_frame, text="Custom Properties",
                                           command=self.show_custom_properties, state='disabled', width=18)
        self.custom_props_btn.grid(row=0, column=1, padx=5, pady=3)
        self.create_tooltip(self.custom_props_btn, "Map additional columns as custom properties (preserves leading zeros)")

        formula_tpl_btn = ttk.Button(mapping_frame, text="Formula Templates",
                  command=self.show_formula_templates, width=18)
        formula_tpl_btn.grid(row=0, column=2, padx=5, pady=3)
        self.create_tooltip(formula_tpl_btn, "Save and reuse common formulas for quantity calculations")

        # Markup section in mapping group
        markup_subframe = ttk.Frame(mapping_frame)
        markup_subframe.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(markup_subframe, text="Markup %:").pack(side=tk.LEFT, padx=(0, 5))
        self.markup_var = tk.StringVar(value="0")
        markup_entry = ttk.Entry(markup_subframe, textvariable=self.markup_var, width=8)
        markup_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(markup_entry, "Enter markup percentage to apply to all items (e.g., 15 for 15%)")

        self.apply_markup_btn = ttk.Button(markup_subframe, text="Apply",
                                           command=self.apply_markup, state='disabled')
        self.apply_markup_btn.pack(side=tk.LEFT)
        self.create_tooltip(self.apply_markup_btn, "Apply markup percentage to all items in the dataset")

        # === AI PROCESSING WORKFLOW (Collapsible) ===
        self.ai_workflow_visible = tk.BooleanVar(value=True)
        ai_header = ttk.Frame(control_frame)
        ai_header.grid(row=6, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        self.ai_workflow_toggle_btn = ttk.Button(ai_header, text="▼ AI Processing Workflow",
                                                 command=self.toggle_ai_workflow, width=25)
        self.ai_workflow_toggle_btn.grid(row=0, column=0, sticky=tk.W)
        self.create_tooltip(self.ai_workflow_toggle_btn, "Click to show/hide AI workflow steps")

        ai_frame = ttk.Frame(control_frame, padding="10", relief="sunken", borderwidth=1)
        ai_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.ai_workflow_content_frame = ai_frame

        # Workflow steps with arrows
        ttk.Label(ai_frame, text="Step 1:", font=('Arial', 8, 'bold')).grid(row=0, column=0, padx=5, pady=3, sticky=tk.W)
        self.cost_type_btn = ttk.Button(ai_frame, text="Generate Cost Types",
                                        command=self.generate_cost_types, state='disabled', width=20)
        self.cost_type_btn.grid(row=0, column=1, padx=5, pady=3)
        self.create_tooltip(self.cost_type_btn, "AI classifies items as Material, Labor, Equipment, Subcontract, or Other")

        ttk.Label(ai_frame, text="→", font=('Arial', 12)).grid(row=0, column=2, padx=2)

        ttk.Label(ai_frame, text="Step 2:", font=('Arial', 8, 'bold')).grid(row=0, column=3, padx=5, pady=3, sticky=tk.W)
        self.takeoff_type_btn = ttk.Button(ai_frame, text="Generate Takeoff Types",
                                           command=self.generate_takeoff_types, state='disabled', width=20)
        self.takeoff_type_btn.grid(row=0, column=4, padx=5, pady=3)
        self.create_tooltip(self.takeoff_type_btn, "AI determines measurement type: Area, Linear, Count, or Volume")

        ttk.Label(ai_frame, text="→", font=('Arial', 12)).grid(row=0, column=5, padx=2)

        ttk.Label(ai_frame, text="Step 3:", font=('Arial', 8, 'bold')).grid(row=0, column=6, padx=5, pady=3, sticky=tk.W)
        self.formula_btn = ttk.Button(ai_frame, text="Generate Formulas",
                                      command=self.generate_formulas, state='disabled', width=20)
        self.formula_btn.grid(row=0, column=7, padx=5, pady=3)
        self.create_tooltip(self.formula_btn, "AI creates math.js formulas for quantity calculations (e.g., [Area] * 50)")

        # === EXPORT SECTION (Final step) ===
        export_frame = ttk.Frame(control_frame, padding="10")
        export_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.export_btn = ttk.Button(export_frame, text="📤 Export to zzTakeoff",
                                     command=self.export_file, state='disabled', width=25)
        self.export_btn.grid(row=0, column=0, padx=5, pady=3)
        self.create_tooltip(self.export_btn, "Export final mapped data to CSV/Excel format for zzTakeoff import")

        # Progress label below everything
        self.progress_label = ttk.Label(control_frame, text="", foreground="blue", font=('Arial', 9))
        self.progress_label.grid(row=9, column=0, pady=5, sticky=tk.W, padx=10)
        
        # Data display
        data_frame = ttk.LabelFrame(main_frame, text="Data Preview", padding="10")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Treeview for data display
        self.tree = ttk.Treeview(data_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Bind double-click to edit formulas
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)

        # Scrollbars
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=hsb.set)

        # Label to show editing instructions
        edit_hint = ttk.Label(data_frame, text="Double-click on Formula field to edit",
                             foreground="gray", font=('Arial', 8, 'italic'))
        edit_hint.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready to load file", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def on_provider_change(self, event=None):
        """Update available models when provider changes"""
        self.update_model_list()
        self.update_api_status()

    def update_model_list(self):
        """Update model dropdown based on selected provider"""
        provider = self.selected_provider.get()
        if provider in self.ai_providers:
            models = self.ai_providers[provider]["models"]
            self.model_combo['values'] = models
            if models:
                self.selected_model.set(models[0])

    def open_api_key_page(self):
        """Open API key configuration dialog"""
        provider = self.selected_provider.get()
        if provider in self.ai_providers:
            url = self.ai_providers[provider]["signup_url"]
            provider_name = self.ai_providers[provider]["name"]

            # Open configuration dialog
            self.show_api_key_dialog(provider, provider_name, url)

    def show_api_key_dialog(self, provider, provider_name, signup_url):
        """Show dialog to configure API key"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configure {provider_name} API Key")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Instructions
        instructions_frame = ttk.Frame(dialog, padding="10")
        instructions_frame.pack(fill=tk.BOTH, expand=False)

        instructions = f"""Configure your {provider_name} API Key:

1. Click 'Open API Key Page' to get your API key
2. Sign up or log in to your {provider_name} account
3. Create a new API key
4. Copy the API key and paste it below
5. Click 'Save' to update your configuration"""

        ttk.Label(instructions_frame, text=instructions, justify=tk.LEFT).pack(anchor=tk.W)

        # Button to open API page
        ttk.Button(instructions_frame, text="Open API Key Page",
                  command=lambda: webbrowser.open(signup_url)).pack(pady=10)

        # API Key Entry
        entry_frame = ttk.Frame(dialog, padding="10")
        entry_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(entry_frame, text=f"{provider_name} API Key:").pack(anchor=tk.W)

        # Text box for API key
        api_key_text = tk.Text(entry_frame, height=4, wrap=tk.WORD)
        api_key_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Load existing key if available
        existing_key = self.get_existing_api_key(provider)
        if existing_key and existing_key != "None":
            api_key_text.insert(1.0, existing_key)

        # Status label
        status_label = ttk.Label(entry_frame, text="", foreground="blue")
        status_label.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)

        def save_and_close():
            api_key = api_key_text.get(1.0, tk.END).strip()
            if api_key:
                if self.save_api_key_to_config(provider, api_key):
                    messagebox.showinfo("Success",
                        f"{provider_name} API key saved!\n\nPlease restart the application for changes to take effect.")
                    dialog.destroy()
                    # Update status and auto-collapse settings
                    self.update_api_status()
                else:
                    messagebox.showerror("Error", "Failed to save API key to config.py")
            else:
                messagebox.showwarning("Warning", "Please enter an API key")

        ttk.Button(button_frame, text="Save", command=save_and_close).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def get_existing_api_key(self, provider):
        """Get existing API key for provider"""
        key_map = {
            "Claude": ANTHROPIC_API_KEY,
            "ChatGPT": OPENAI_API_KEY,
            "Gemini": GOOGLE_API_KEY,
            "DeepSeek": DEEPSEEK_API_KEY
        }
        key = key_map.get(provider)
        return str(key) if key else None

    def save_api_key_to_config(self, provider, api_key):
        """Save API key to config.py file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.py')

            # Read current config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []

            # Map provider to config variable name
            key_var_map = {
                "Claude": "ANTHROPIC_API_KEY",
                "ChatGPT": "OPENAI_API_KEY",
                "Gemini": "GOOGLE_API_KEY",
                "DeepSeek": "DEEPSEEK_API_KEY"
            }

            var_name = key_var_map.get(provider)
            if not var_name:
                return False

            # Update or add the API key
            key_line = f'{var_name} = "{api_key}"\n'
            found = False

            for i, line in enumerate(lines):
                if line.strip().startswith(f'{var_name} ='):
                    lines[i] = key_line
                    found = True
                    break

            if not found:
                # Add the key if not found
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                lines.append(f'\n# {provider} API Key\n')
                lines.append(key_line)

            # Write back to file
            with open(config_path, 'w') as f:
                f.writelines(lines)

            return True

        except Exception as e:
            print(f"Error saving API key: {e}")
            return False

    def load_mapping_history(self) -> Dict:
        """Load previous mapping patterns from file"""
        history_file = 'mapping_history.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_mapping_history(self):
        """Save mapping patterns for future use"""
        with open('mapping_history.json', 'w') as f:
            json.dump(self.mapping_history, f, indent=2)

    def load_formula_templates(self) -> List[Dict]:
        """Load saved formula templates from file"""
        templates_file = 'formula_templates.json'
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_formula_templates(self):
        """Save formula templates to file"""
        templates_file = 'formula_templates.json'
        with open(templates_file, 'w') as f:
            json.dump(self.formula_templates, f, indent=2)

    def load_import_templates(self) -> List[Dict]:
        """Load saved import templates from file"""
        templates_file = 'import_templates.json'
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_import_templates(self):
        """Save import templates to file"""
        templates_file = 'import_templates.json'
        with open(templates_file, 'w') as f:
            json.dump(self.import_templates, f, indent=2)
    
    def load_file(self):
        """Load CSV or Excel file"""
        filename = filedialog.askopenfilename(
            title="Select estimating export file",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            # Load file based on extension
            if filename.endswith('.csv'):
                self.df = pd.read_csv(filename)
            else:
                self.df = pd.read_excel(filename)

            # Clean column names
            self.df.columns = self.df.columns.str.strip()

            # Store original filename
            self.original_filename = os.path.basename(filename)

            # Initialize mapped dataframe
            self.initialize_mapped_df()

            # Display data
            self.display_data()

            # Enable buttons
            self.cost_type_btn.config(state='normal')
            self.apply_markup_btn.config(state='normal')
            self.custom_props_btn.config(state='normal')
            self.save_progress_btn.config(state='normal')

            self.status_label.config(text=f"Loaded {len(self.df)} rows from {os.path.basename(filename)}")
            self.progress_label.config(text="✓ File loaded. Click 'Custom Properties' to map additional columns or 'Generate Cost Types' to start AI mapping.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def initialize_mapped_df(self):
        """Initialize the mapped dataframe with required zzTakeoff columns"""
        self.mapped_df = pd.DataFrame()
        
        # Map obvious fields from source
        # Cost Type - will be generated by AI
        self.mapped_df['Cost Type'] = ''
        
        # Name - map from 'Name' column
        if 'Name' in self.df.columns:
            self.mapped_df['Name'] = self.df['Name']
        else:
            self.mapped_df['Name'] = self.df.iloc[:, 0]  # Use first column as fallback
        
        # Usage - optional
        self.mapped_df['Usage'] = ''
        
        # Takeoff Type - will be generated by AI
        self.mapped_df['Takeoff Type'] = ''
        
        # Formula - will be generated by AI
        self.mapped_df['Formula'] = ''
        
        # Waste % - optional
        self.mapped_df['Waste %'] = ''
        
        # Round Up to Nearest - optional
        self.mapped_df['Round Up to Nearest'] = ''
        
        # SKU - map from Databuild Code if available
        if 'Databuild Code' in self.df.columns:
            self.mapped_df['SKU'] = self.df['Databuild Code']
        else:
            self.mapped_df['SKU'] = ''
        
        # Description - use Name as description
        self.mapped_df['Description'] = self.mapped_df['Name']
        
        # Cost Each - map from Unit Price
        if 'Unit Price' in self.df.columns:
            self.mapped_df['Cost Each'] = self.df['Unit Price']
        else:
            self.mapped_df['Cost Each'] = ''
        
        # Markup % - optional
        self.mapped_df['Markup %'] = ''
        
        # Units - map from Units column
        if 'Units' in self.df.columns:
            self.mapped_df['Units'] = self.df['Units']
        else:
            self.mapped_df['Units'] = ''
    
    def display_data(self):
        """Display current data in the treeview"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.mapped_df is None:
            return
        
        # Configure columns
        self.tree['columns'] = list(self.mapped_df.columns)
        
        for col in self.mapped_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Insert data (first 100 rows for performance)
        for idx, row in self.mapped_df.head(100).iterrows():
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.tree.insert('', 'end', values=values)
    
    def call_ai_api(self, prompt: str, system_prompt: str = "") -> str:
        """Call selected AI API for assistance"""
        provider = self.selected_provider.get()
        model = self.selected_model.get()

        try:
            if provider == "Claude":
                if not self.anthropic_client:
                    raise Exception("Claude API key not configured")

                message = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text

            elif provider == "ChatGPT":
                if not self.openai_client:
                    raise Exception("OpenAI API key not configured")

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4000
                )
                return response.choices[0].message.content

            elif provider == "Gemini":
                if not GOOGLE_AVAILABLE or not GOOGLE_API_KEY:
                    raise Exception("Google Gemini API not configured")

                gemini_model = genai.GenerativeModel(model)
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = gemini_model.generate_content(full_prompt)
                return response.text

            elif provider == "DeepSeek":
                if not self.deepseek_client:
                    raise Exception("DeepSeek API key not configured")

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.deepseek_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4000
                )
                return response.choices[0].message.content

            else:
                raise Exception(f"Unknown AI provider: {provider}")

        except Exception as e:
            raise Exception(f"AI API Error ({provider}): {str(e)}")
    
    def generate_cost_types(self):
        """Use AI to generate Cost Type classifications"""
        if self.df is None or self.mapped_df is None:
            return

        self.progress_label.config(text="⏳ Generating Cost Types with AI... Please wait.")
        self.root.update()

        try:
            # Prepare ALL data for batch processing
            all_data = []
            for idx, row in self.df.iterrows():
                item = {
                    'name': row.get('Name', ''),
                    'supplier': row.get('Supplier Reference', ''),
                    'code': row.get('Databuild Code', ''),
                    'unit': row.get('Units', '')
                }
                all_data.append(item)

            # Process using batch function
            def process_batch(batch_data):
                system_prompt = """You are a JSON generator. You MUST respond with ONLY valid JSON arrays.
Rules:
1. Start with [ and end with ]
2. Each item must be in double quotes: "Material"
3. Separate items with commas
4. No explanations, no markdown, no extra text"""

                prompt = f"""Classify each construction item into ONE of these Cost Types: Material, Labor, Equipment, Subcontract, Other

Items:
{json.dumps(batch_data, indent=2)}

Return format (EXACT JSON ARRAY):
["Material", "Labor", "Material", "Equipment", "Other"]

Your response (only the JSON array):"""

                response = self.call_ai_api(prompt, system_prompt)

                # Robust parsing - handle any malformed JSON
                import re

                # Clean response
                response = response.strip()

                # Remove markdown
                if '```' in response:
                    response = re.sub(r'```[\w]*\n?', '', response).strip()

                # Find anything that looks like an array
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
                elif '"' in response or "'" in response:
                    # Add brackets if missing
                    response = '[' + response.rstrip(',').strip() + ']'

                # Normalize quotes - replace single quotes with double
                response = response.replace("'", '"')

                # Fix missing quotes: Word, -> "Word",
                response = re.sub(r'(?<=[,\[\s])([A-Z][a-z]+)(?=[,\]\s])', r'"\1"', response)

                # Remove trailing commas before ]
                response = re.sub(r',\s*\]', ']', response)

                # Try standard JSON parse
                try:
                    result = json.loads(response)
                    if isinstance(result, list):
                        return result
                except:
                    pass

                # Fallback: Extract category words from comma-separated list
                valid_categories = ['Material', 'Labor', 'Equipment', 'Subcontract', 'Other']
                items = []

                # Split by comma and extract each item
                # Remove brackets first
                clean_response = response.strip('[]')

                # Split by comma
                parts = clean_response.split(',')

                for part in parts:
                    # Clean the part - remove quotes, whitespace, extra characters
                    cleaned = re.sub(r'["\'\[\]\s]+', '', part.strip())

                    if not cleaned:
                        continue

                    # Match to valid category (case-insensitive)
                    matched = False
                    for cat in valid_categories:
                        if cleaned.lower() == cat.lower():
                            items.append(cat)
                            matched = True
                            break

                    # If we have enough items, stop
                    if len(items) == len(batch_data):
                        break

                if len(items) == len(batch_data):
                    return items

                raise Exception(f"Could not parse {len(items)} items from response (expected {len(batch_data)}). Response: {response[:200]}...")

            cost_types = self.process_in_batches(all_data, process_batch, "Generating Cost Types")

            # Apply directly to mapped dataframe
            for idx, cost_type in enumerate(cost_types):
                if idx < len(self.mapped_df):
                    self.mapped_df.at[idx, 'Cost Type'] = cost_type

            # Update display
            self.display_data()

            # Enable next button
            self.takeoff_type_btn.config(state='normal')

            self.progress_label.config(text="✓ Cost Types generated! Click 'Generate Takeoff Types' to continue.")
            self.status_label.config(text=f"Cost Types assigned to {len(self.mapped_df)} items")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Cost Types:\n{str(e)}")
            self.progress_label.config(text="❌ Error generating Cost Types")
    
    def apply_cost_types_to_all(self, sample_cost_types: List[str], sample_data: List[Dict]):
        """Apply learned patterns from sample to all rows"""
        # Create pattern dictionary based on sample
        patterns = {}
        for i, cost_type in enumerate(sample_cost_types):
            if i < len(sample_data):
                item = sample_data[i]
                # Create patterns based on name keywords
                name_lower = item['name'].lower()
                for word in name_lower.split():
                    if len(word) > 3:  # Ignore short words
                        if word not in patterns:
                            patterns[word] = {}
                        patterns[word][cost_type] = patterns[word].get(cost_type, 0) + 1
        
        # Apply to all rows
        for idx, row in self.df.iterrows():
            name = str(row.get('Name', '')).lower()
            supplier = str(row.get('Supplier Reference', ''))
            
            # Scoring system
            scores = {'Material': 0, 'Labor': 0, 'Equipment': 0, 'Subcontract': 0, 'Other': 0}
            
            # Check supplier reference
            if supplier and supplier.strip():
                scores['Subcontract'] += 3
                scores['Labor'] += 2
            
            # Check keywords in name
            if 'supply' in name:
                scores['Material'] += 3
            if any(word in name for word in ['fix', 'install', 'paint', 'render', 'laying']):
                scores['Labor'] += 3
            if any(word in name for word in ['hire', 'rental', 'equipment']):
                scores['Equipment'] += 3
            
            # Check learned patterns
            for word in name.split():
                if word in patterns:
                    for cost_type, count in patterns[word].items():
                        scores[cost_type] += count
            
            # Assign highest scoring type
            best_type = max(scores.items(), key=lambda x: x[1])[0]
            self.mapped_df.at[idx, 'Cost Type'] = best_type
    
    def generate_takeoff_types(self):
        """Use AI to generate Takeoff Type classifications"""
        if self.mapped_df is None:
            return

        self.progress_label.config(text="⏳ Generating Takeoff Types with AI... Please wait.")
        self.root.update()

        try:
            # Prepare ALL data for batch processing
            all_data = []
            for idx, row in self.df.iterrows():
                item = {
                    'name': row.get('Name', ''),
                    'unit': row.get('Units', ''),
                    'quantity': row.get('Quantity', '')
                }
                all_data.append(item)

            # Process using batch function
            def process_batch(batch_data):
                prompt = f"""Analyze these construction items and classify each Takeoff Type as one of:
- Area (for items measured in square units: SM, Sm, m2, SQ M, etc.)
- Linear (for items measured in linear units: M, Lm, LM, meters, etc.)
- Count (for items counted as whole units: EA, Ea, each, etc.)
- Segment (for segmented linear items)

Items to classify:
{json.dumps(batch_data, indent=2)}

Rules:
1. Look at the Units column primarily
2. SM, Sm, m2, SQ M, SQUARE → Area
3. M, Lm, LM, meters, metres → Linear
4. EA, Ea, each, THOUS, bag, TONNE, PACKETS → Count
5. When unit is ambiguous, look at the item name/description

CRITICAL: Return ONLY a valid JSON array with takeoff types in the same order as input.
No explanations, no markdown, no extra text - just the JSON array.

Format:
["Area", "Count", "Linear", ...]"""

                response = self.call_ai_api(prompt)

                # Parse response - extract JSON from potential markdown or text
                response = response.strip()

                # Remove markdown code blocks if present
                if response.startswith('```'):
                    lines = response.split('\n')
                    response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
                    response = response.replace('```json', '').replace('```', '').strip()

                # Try to find JSON array in response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
                else:
                    # No brackets found, try to add them if we have quoted items
                    if '"' in response or "'" in response:
                        response = '[' + response.rstrip(',') + ']'

                try:
                    return json.loads(response)
                except json.JSONDecodeError as e:
                    # Try to fix common JSON issues
                    # Replace unquoted values with quoted ones
                    fixed_response = re.sub(r'(?<=[,\[])\s*([A-Za-z]+)\s*(?=[,\]])', r'"\1"', response)
                    try:
                        return json.loads(fixed_response)
                    except json.JSONDecodeError:
                        # Last resort: extract all category words and create valid array
                        valid_categories = ['Area', 'Linear', 'Count', 'Segment']
                        items = re.findall(r'\b(' + '|'.join(valid_categories) + r')\b', response, re.IGNORECASE)
                        # Capitalize properly
                        items = [cat.capitalize() for cat in items]
                        if items and len(items) == len(batch_data):
                            return items
                        raise Exception(f"Invalid JSON response from AI. Response: {response[:200]}...")

            takeoff_types = self.process_in_batches(all_data, process_batch, "Generating Takeoff Types")

            # Apply directly to mapped dataframe
            for idx, takeoff_type in enumerate(takeoff_types):
                if idx < len(self.mapped_df):
                    self.mapped_df.at[idx, 'Takeoff Type'] = takeoff_type

            # Update display
            self.display_data()

            # Enable next button
            self.formula_btn.config(state='normal')

            self.progress_label.config(text="✓ Takeoff Types generated! Click 'Generate Formulas' to continue.")
            self.status_label.config(text=f"Takeoff Types assigned to {len(self.mapped_df)} items")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Takeoff Types:\n{str(e)}")
            self.progress_label.config(text="❌ Error generating Takeoff Types")
    
    def apply_takeoff_types_to_all(self, sample_takeoff_types: List[str], sample_data: List[Dict]):
        """Apply takeoff type patterns to all rows"""
        # Create unit mapping
        unit_mapping = {}
        for i, takeoff_type in enumerate(sample_takeoff_types):
            if i < len(sample_data):
                unit = str(sample_data[i]['unit']).strip().upper()
                if unit:
                    unit_mapping[unit] = takeoff_type
        
        # Apply to all rows
        for idx, row in self.df.iterrows():
            unit = str(row.get('Units', '')).strip().upper()
            
            # Try exact match first
            if unit in unit_mapping:
                self.mapped_df.at[idx, 'Takeoff Type'] = unit_mapping[unit]
            else:
                # Pattern matching
                if unit in ['SM', 'SQ M', 'M2', 'SQM']:
                    self.mapped_df.at[idx, 'Takeoff Type'] = 'Area'
                elif unit in ['M', 'LM', 'METRES', 'METERS']:
                    self.mapped_df.at[idx, 'Takeoff Type'] = 'Linear'
                elif unit in ['EA', 'EACH', 'THOUS', 'BAG', 'TONNE', 'PACKETS', 'PACKET', 'CU M']:
                    self.mapped_df.at[idx, 'Takeoff Type'] = 'Count'
                else:
                    self.mapped_df.at[idx, 'Takeoff Type'] = 'Count'  # Default
    
    def generate_formulas(self):
        """Use AI to generate Formula field"""
        if self.mapped_df is None:
            return

        self.progress_label.config(text="⏳ Generating Formulas with AI... Please wait.")
        self.root.update()

        try:
            # Get current unit system
            unit_system = self.unit_system.get()
            variables = self.mathjs_variables[unit_system]

            # Prepare ALL data with takeoff types for batch processing
            all_data = []
            for idx in range(len(self.df)):
                row = self.df.iloc[idx]
                mapped_row = self.mapped_df.iloc[idx]
                item = {
                    'name': row.get('Name', ''),
                    'unit': row.get('Units', ''),
                    'quantity': row.get('Quantity', ''),
                    'takeoff_type': mapped_row['Takeoff Type']
                }
                all_data.append(item)

            # Create variable reference for AI
            var_reference = []
            special_vars_list = []

            for var_type, var_info in variables.items():
                var_reference.append(f"- {var_type}: Use {var_info['base']} ({var_info['description']})")
                # Add special variables for this type
                if 'special_vars' in var_info and var_info['special_vars']:
                    special_vars_list.extend(var_info['special_vars'])

            # Format saved formula templates for AI
            template_examples = ""
            if self.formula_templates:
                template_examples = "\n\nUser's Saved Formula Templates (USE THESE AS REFERENCE):\n"
                for template in self.formula_templates:
                    desc = f" - {template.get('description', '')}" if template.get('description') else ""
                    category = f"[{template.get('category', 'General')}]"
                    template_examples += f"{category} {template['name']}: {template['formula']}{desc}\n"
                template_examples += "\nIMPORTANT: When an item matches or is similar to one of these templates, use the template formula or adapt it accordingly.\n"

            # Process using batch function
            def process_batch(batch_data):
                prompt = f"""Generate math.js formulas for zzTakeoff import based on item details.

IMPORTANT: All formulas MUST use math.js syntax with variables in square brackets: [Variable Name]

Unit System: {unit_system}

Basic Variables:
{chr(10).join(var_reference)}

Special Unit-Specific Variables (use when specific measurements are needed):
{chr(10).join('- ' + var for var in special_vars_list)}

Additional General Variables:
- [Width] - Width measurement
- [Height] - Height measurement
- [Depth] - Depth measurement
- [Count] - Count or quantity
- [Point Count] - Point count for counted items
- [Waste] - Waste percentage
- [Thickness] - Thickness measurement
{template_examples}
Items with their Takeoff Types:
{json.dumps(batch_data, indent=2)}

Formula Rules:
1. ALL variables MUST be enclosed in square brackets: [Variable]
2. For unit-specific measurements, use the format [Variable:unit] (e.g., [Wall Area:m2], [Linear:cm])
3. For Area types:
   - Simple: "[Area]"
   - Wall specific: "[Wall Area:m2]" or "[Wall Area:ft2]"
   - Complex: "[Length] * [Width]"
   - With waste: "[Area] * (1 + [Waste]/100)"
4. For Linear types:
   - Simple: "[Length]"
   - Unit specific: "[Linear:m]", "[Linear:cm]", "[Linear:ft]"
   - Multiple: "[Point Count] * [Length]"
5. For Count types:
   - Simple: "[Point Count]" (PRIMARY - use this for Count type)
   - Complex calculations: Example for "50 bricks per m2" use "[Area] * 50"
6. For Volume types:
   - Simple: "[Volume]"
   - Unit specific: "[Volume:m3]", "[Volume:cm3]", "[Volume:ft3]"
   - Complex: "[Length] * [Width] * [Height]"

Examples of CORRECT formulas:
- "[Area]"
- "[Wall Area:m2]" (for wall-specific area in metric)
- "[Wall Area:FT2]" (for wall-specific area in imperial - USE CAPITALS)
- "[Linear:m]" (for linear measurement in meters)
- "[Linear:FT]" (for linear measurement in feet - USE CAPITALS)
- "[Volume:m3]" (for volume in cubic meters)
- "[Volume:FT3]" (for volume in cubic feet - USE CAPITALS)
- "[Length] * [Width]"
- "[Point Count]" (PRIMARY for Count type items)
- "[Area] * 50" (for 50 items per square unit)
- "([Length] * [Width]) * [Point Count]"
- "[Length] * (1 + [Waste]/100)"
- "[Wall Area:m2] * 0.05" (for 5cm thick wall coverage)
- "[Wall Area:FT2] * 6.5" (for imperial measurements - ALWAYS USE CAPITALS FOR IMPERIAL UNITS)

CRITICAL: Return ONLY a valid JSON array of formula strings in the same order as input.
No explanations, no markdown, no extra text - just the JSON array.
Every variable MUST have square brackets!

Format:
["[Area]", "[Count]", "[Length] * [Width]", "[Point Count]", ...]"""

                response = self.call_ai_api(prompt)

                # Parse response - extract JSON from potential markdown or text
                response = response.strip()

                # Remove markdown code blocks if present
                if response.startswith('```'):
                    lines = response.split('\n')
                    response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
                    response = response.replace('```json', '').replace('```', '').strip()

                # Try to find JSON array in response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
                else:
                    # No brackets found, try to add them if we have quoted items
                    if '"' in response or "'" in response:
                        response = '[' + response.rstrip(',') + ']'

                try:
                    return json.loads(response)
                except json.JSONDecodeError as e:
                    # Try to fix common JSON issues
                    # First attempt: fix unquoted strings (but preserve formulas in quotes)
                    fixed_response = response
                    # Replace patterns like: Other, with "Other",
                    fixed_response = re.sub(r'(?<=[,\[])\s*([A-Za-z][A-Za-z\s]*)\s*(?=,)', r'"\1"', fixed_response)
                    # Replace patterns like: Other] with "Other"]
                    fixed_response = re.sub(r'(?<=[,\[])\s*([A-Za-z][A-Za-z\s]*)\s*(?=\])', r'"\1"', fixed_response)
                    try:
                        return json.loads(fixed_response)
                    except json.JSONDecodeError:
                        # Last resort: extract quoted strings and bracket expressions
                        items = re.findall(r'"([^"]+)"|\[([^\]]+)\]', response)
                        # Flatten and filter
                        items = [item[0] if item[0] else f'[{item[1]}]' for item in items if any(item)]
                        if items and len(items) == len(batch_data):
                            return items
                        raise Exception(f"Invalid JSON response from AI. Response: {response[:200]}...")

            formulas = self.process_in_batches(all_data, process_batch, "Generating Formulas")

            # Apply directly to mapped dataframe
            for idx, formula in enumerate(formulas):
                if idx < len(self.mapped_df):
                    self.mapped_df.at[idx, 'Formula'] = formula

            # Update display
            self.display_data()

            # Enable export button
            self.export_btn.config(state='normal')

            self.progress_label.config(text="✓ Formulas generated! Click 'Export to zzTakeoff' to save.")
            self.status_label.config(text=f"All fields mapped for {len(self.mapped_df)} items. Ready to export!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Formulas:\n{str(e)}")
            self.progress_label.config(text="❌ Error generating Formulas")
    
    def apply_formulas_to_all(self, sample_formulas: List[str]):
        """Apply formula patterns to all rows based on takeoff type"""
        # Create takeoff type to formula mapping
        formula_mapping = {}
        for i, formula in enumerate(sample_formulas):
            if i < len(self.mapped_df):
                takeoff_type = self.mapped_df.iloc[i]['Takeoff Type']
                if takeoff_type not in formula_mapping:
                    formula_mapping[takeoff_type] = {}
                formula_mapping[takeoff_type][formula] = formula_mapping[takeoff_type].get(formula, 0) + 1

        # Get most common formula for each takeoff type
        default_formulas = {}
        for takeoff_type, formulas in formula_mapping.items():
            if formulas:
                default_formulas[takeoff_type] = max(formulas.items(), key=lambda x: x[1])[0]

        # Apply to all rows
        for idx, row in self.mapped_df.iterrows():
            takeoff_type = row['Takeoff Type']

            # Use learned pattern or default
            if takeoff_type in default_formulas:
                formula = default_formulas[takeoff_type]
            else:
                # Fallback based on type - use math.js syntax
                if takeoff_type == 'Area':
                    formula = '[Area]'
                elif takeoff_type == 'Linear':
                    formula = '[Length]'
                elif takeoff_type == 'Count':
                    formula = '[Point Count]'
                elif takeoff_type == 'Volume':
                    formula = '[Volume]'
                else:
                    formula = '[Point Count]'

            self.mapped_df.at[idx, 'Formula'] = formula
    
    def export_file(self):
        """Export mapped data to zzTakeoff format"""
        if self.mapped_df is None:
            return

        filename = filedialog.asksaveasfilename(
            title="Save zzTakeoff import file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )

        if not filename:
            return

        try:
            # Prepare final export with required columns in correct order
            export_columns = [
                'Cost Type', 'Name', 'Usage', 'Takeoff Type', 'Formula',
                'Waste %', 'Round Up to Nearest', 'SKU', 'Description',
                'Cost Each', 'Markup %', 'Units'
            ]

            # Add custom property columns
            custom_columns = [col for col in self.mapped_df.columns if col not in export_columns]
            export_columns.extend(custom_columns)

            export_df = self.mapped_df[export_columns].copy()

            # Convert custom property columns to string to preserve leading zeros
            custom_columns_in_export = [col for col in custom_columns if col in export_df.columns]
            for col in custom_columns_in_export:
                export_df[col] = export_df[col].astype(str).replace('nan', '')

            # Save file
            if filename.endswith('.csv'):
                export_df.to_csv(filename, index=False)
            else:
                # For Excel, use ExcelWriter to preserve text format
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Sheet1')
                    # Get the worksheet
                    worksheet = writer.sheets['Sheet1']
                    # Format custom property columns as text
                    from openpyxl.styles import Alignment
                    for col_idx, col_name in enumerate(export_df.columns, start=1):
                        if col_name in custom_columns_in_export:
                            col_letter = chr(64 + col_idx)  # A, B, C, etc.
                            for row in range(2, len(export_df) + 2):  # Start at row 2 (after header)
                                cell = worksheet[f'{col_letter}{row}']
                                cell.number_format = '@'  # Text format
                                cell.alignment = Alignment(horizontal='left')

            custom_props_msg = f" (including {len(custom_columns)} custom properties)" if custom_columns else ""
            messagebox.showinfo("Success",
                              f"Exported {len(export_df)} items{custom_props_msg} to:\n{os.path.basename(filename)}")

            self.status_label.config(text=f"Exported to {os.path.basename(filename)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")

    def apply_markup(self):
        """Apply markup percentage to all items"""
        if self.mapped_df is None:
            return

        try:
            markup_value = self.markup_var.get().strip()
            if not markup_value:
                messagebox.showwarning("Warning", "Please enter a markup percentage")
                return

            markup = float(markup_value)

            if markup < 0:
                messagebox.showwarning("Warning", "Markup percentage cannot be negative")
                return

            # Apply markup to all rows
            self.mapped_df['Markup %'] = markup

            # Update display
            self.display_data()

            messagebox.showinfo("Success", f"Applied {markup}% markup to all {len(self.mapped_df)} items")
            self.status_label.config(text=f"Markup {markup}% applied to all items")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for markup percentage")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply markup:\n{str(e)}")

    def on_tree_double_click(self, event):
        """Handle double-click on treeview to edit formulas"""
        if self.mapped_df is None:
            return

        # Get the clicked item and column
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)

        if not item or not column:
            return

        # Get column name
        col_index = int(column[1:]) - 1  # column is like '#1', '#2', etc.
        if col_index < 0 or col_index >= len(self.mapped_df.columns):
            return

        col_name = self.mapped_df.columns[col_index]

        # Only allow editing of Formula column
        if col_name != 'Formula':
            messagebox.showinfo("Info", "Only the Formula field is editable. Double-click on a Formula cell to edit it.")
            return

        # Get row index
        item_values = self.tree.item(item, 'values')
        if not item_values:
            return

        # Find the actual row index in the dataframe
        row_index = self.tree.index(item)

        # Get current value
        current_value = str(item_values[col_index])

        # Show edit dialog
        self.show_formula_edit_dialog(row_index, current_value)

    def show_formula_edit_dialog(self, row_index, current_formula):
        """Show dialog to edit a formula"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Formula - Row {row_index + 1}")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Item info
        info_frame = ttk.Frame(dialog, padding="10")
        info_frame.pack(fill=tk.X)

        item_name = self.mapped_df.iloc[row_index]['Name']
        takeoff_type = self.mapped_df.iloc[row_index]['Takeoff Type']

        ttk.Label(info_frame, text=f"Item: {item_name}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Takeoff Type: {takeoff_type}").pack(anchor=tk.W)

        # Help text
        help_frame = ttk.LabelFrame(dialog, text="Available Variables", padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        help_text = tk.Text(help_frame, height=12, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)

        # Get unit system and variables
        unit_system = self.unit_system.get()
        variables = self.mathjs_variables[unit_system]

        help_content = f"Unit System: {unit_system}\n\n"
        help_content += "Basic Variables:\n"
        for var_type, var_info in variables.items():
            help_content += f"  {var_info['base']} - {var_info['description']}\n"

        help_content += "\nSpecial Variables:\n"
        for var_type, var_info in variables.items():
            if 'special_vars' in var_info:
                for special_var in var_info['special_vars'][:3]:  # Show first 3
                    help_content += f"  {special_var}\n"

        help_content += "\nGeneral Variables:\n"
        help_content += "  [Width], [Height], [Depth], [Count], [Point Count], [Waste], [Thickness]\n"
        help_content += "\nExamples:\n"
        help_content += "  [Area] * 50 (50 items per square unit)\n"
        help_content += "  [Length] * [Width]\n"
        help_content += "  [Wall Area:m2] * 0.05\n"

        help_text.insert(1.0, help_content)
        help_text.config(state='disabled')

        # Formula entry
        entry_frame = ttk.Frame(dialog, padding="10")
        entry_frame.pack(fill=tk.X, padx=10)

        ttk.Label(entry_frame, text="Formula:").pack(anchor=tk.W)
        formula_entry = ttk.Entry(entry_frame, width=80)
        formula_entry.pack(fill=tk.X, pady=5)
        formula_entry.insert(0, current_formula)
        formula_entry.select_range(0, tk.END)
        formula_entry.focus()

        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)

        def save_formula():
            new_formula = formula_entry.get().strip()
            if new_formula:
                self.mapped_df.at[row_index, 'Formula'] = new_formula
                self.display_data()
                self.status_label.config(text=f"Formula updated for row {row_index + 1}")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Formula cannot be empty")

        def cancel():
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_formula).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)

        # Bind Enter key to save
        formula_entry.bind('<Return>', lambda e: save_formula())
        formula_entry.bind('<Escape>', lambda e: cancel())

    def show_formula_templates(self):
        """Show formula templates management dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Formula Templates Library")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Instructions
        instructions = ttk.Label(dialog, text="Save and reuse common formulas from your estimates",
                                font=('Arial', 10))
        instructions.pack(pady=10)

        # Main frame with two columns
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Template list
        left_frame = ttk.LabelFrame(main_frame, text="Saved Templates", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        template_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Courier', 9))
        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=template_listbox.yview)

        # Populate listbox
        def refresh_list():
            template_listbox.delete(0, tk.END)
            for template in self.formula_templates:
                display = f"{template['name']}: {template['formula']}"
                template_listbox.insert(tk.END, display)

        refresh_list()

        # Right side - Add/Edit template
        right_frame = ttk.LabelFrame(main_frame, text="Add/Edit Template", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Template name
        ttk.Label(right_frame, text="Template Name:").pack(anchor=tk.W)
        name_entry = ttk.Entry(right_frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 10))

        # Formula
        ttk.Label(right_frame, text="Formula:").pack(anchor=tk.W)
        formula_entry = ttk.Entry(right_frame, width=40)
        formula_entry.pack(fill=tk.X, pady=(0, 10))

        # Description
        ttk.Label(right_frame, text="Description (optional):").pack(anchor=tk.W)
        desc_text = tk.Text(right_frame, height=3, wrap=tk.WORD)
        desc_text.pack(fill=tk.X, pady=(0, 10))

        # Category/Type
        ttk.Label(right_frame, text="Category:").pack(anchor=tk.W)
        category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(right_frame, textvariable=category_var,
                                      values=["General", "Area", "Linear", "Count", "Volume", "Complex"],
                                      state='readonly', width=37)
        category_combo.pack(fill=tk.X, pady=(0, 10))

        # Example formulas section
        examples_frame = ttk.LabelFrame(right_frame, text="Common Examples", padding="5")
        examples_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        examples_text = tk.Text(examples_frame, height=8, wrap=tk.WORD, font=('Courier', 8))
        examples_text.pack(fill=tk.BOTH, expand=True)

        examples_content = """Bricks per m²: [Area] * 50
Paint coverage: [Wall Area:m2] / 10
Concrete volume: [Length] * [Width] * 0.1
Tiles with waste: [Area] * (1 + [Waste]/100)
Linear multiply: [Linear:m] * 2.5
Count items: [Point Count]
Perimeter calc: ([Length] + [Width]) * 2"""

        examples_text.insert(1.0, examples_content)
        examples_text.config(state='disabled')

        # Buttons for template management
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        def add_template():
            name = name_entry.get().strip()
            formula = formula_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            category = category_var.get()

            if not name or not formula:
                messagebox.showwarning("Warning", "Please enter both name and formula")
                return

            # Check if template name already exists
            for template in self.formula_templates:
                if template['name'] == name:
                    if messagebox.askyesno("Duplicate", f"Template '{name}' already exists. Replace it?"):
                        self.formula_templates.remove(template)
                        break
                    else:
                        return

            # Add new template
            self.formula_templates.append({
                'name': name,
                'formula': formula,
                'description': description,
                'category': category
            })

            self.save_formula_templates()
            refresh_list()

            # Clear fields
            name_entry.delete(0, tk.END)
            formula_entry.delete(0, tk.END)
            desc_text.delete(1.0, tk.END)

            messagebox.showinfo("Success", f"Template '{name}' saved!")

        def delete_template():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template to delete")
                return

            idx = selection[0]
            template_name = self.formula_templates[idx]['name']

            if messagebox.askyesno("Confirm Delete", f"Delete template '{template_name}'?"):
                del self.formula_templates[idx]
                self.save_formula_templates()
                refresh_list()
                messagebox.showinfo("Deleted", f"Template '{template_name}' deleted")

        def load_to_fields():
            selection = template_listbox.curselection()
            if not selection:
                return

            idx = selection[0]
            template = self.formula_templates[idx]

            name_entry.delete(0, tk.END)
            name_entry.insert(0, template['name'])

            formula_entry.delete(0, tk.END)
            formula_entry.insert(0, template['formula'])

            desc_text.delete(1.0, tk.END)
            desc_text.insert(1.0, template.get('description', ''))

            category_var.set(template.get('category', 'General'))

        def apply_to_selected():
            """Apply template formula to selected items in main view"""
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template to apply")
                return

            if self.mapped_df is None:
                messagebox.showwarning("Warning", "Please load data first")
                return

            idx = selection[0]
            template = self.formula_templates[idx]
            formula = template['formula']

            # Ask which items to apply to
            apply_dialog = tk.Toplevel(dialog)
            apply_dialog.title("Apply Template")
            apply_dialog.geometry("400x200")
            apply_dialog.transient(dialog)
            apply_dialog.grab_set()

            ttk.Label(apply_dialog, text=f"Apply formula: {formula}",
                     font=('Arial', 10, 'bold')).pack(pady=10)

            ttk.Label(apply_dialog, text="Apply to:").pack(pady=5)

            apply_var = tk.StringVar(value="all")
            ttk.Radiobutton(apply_dialog, text="All items", variable=apply_var,
                           value="all").pack(anchor=tk.W, padx=20)
            ttk.Radiobutton(apply_dialog, text="Items with empty formulas only",
                           variable=apply_var, value="empty").pack(anchor=tk.W, padx=20)

            def do_apply():
                choice = apply_var.get()
                count = 0

                for idx, row in self.mapped_df.iterrows():
                    if choice == "all" or (choice == "empty" and not row['Formula']):
                        self.mapped_df.at[idx, 'Formula'] = formula
                        count += 1

                self.display_data()
                apply_dialog.destroy()
                dialog.destroy()
                messagebox.showinfo("Success", f"Applied formula to {count} items")

            btn_frame = ttk.Frame(apply_dialog)
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="Apply", command=do_apply).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancel", command=apply_dialog.destroy).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Save Template", command=add_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=delete_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load", command=load_to_fields).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Apply to Data", command=apply_to_selected).pack(side=tk.LEFT, padx=2)

        # Double-click to load
        template_listbox.bind('<Double-Button-1>', lambda e: load_to_fields())

        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def show_custom_properties(self):
        """Show custom properties column mapping dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a file first")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Property Column Mapping")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Instructions
        instructions = ttk.Label(dialog, text="Map additional columns from your CSV to zzTakeoff custom properties",
                                font=('Arial', 10))
        instructions.pack(pady=10)

        # Main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Get available columns (exclude already mapped ones)
        standard_columns = ['Name', 'Unit Price', 'Units', 'Databuild Code', 'Supplier Reference', 'Quantity']
        available_columns = [col for col in self.df.columns if col not in standard_columns]

        # Scrollable frame for mappings
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        ttk.Label(scrollable_frame, text="Source Column", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(scrollable_frame, text="→", font=('Arial', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Custom Property Name", font=('Arial', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Label(scrollable_frame, text="Include?", font=('Arial', 9, 'bold')).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Sample Value", font=('Arial', 9, 'bold')).grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        mapping_widgets = []

        # Create mapping row for each available column
        for idx, col in enumerate(available_columns, start=1):
            # Source column label
            ttk.Label(scrollable_frame, text=col).grid(row=idx, column=0, padx=5, pady=2, sticky=tk.W)

            # Arrow
            ttk.Label(scrollable_frame, text="→").grid(row=idx, column=1, padx=5, pady=2)

            # Custom property name entry (default to column name)
            custom_name_var = tk.StringVar(value=self.custom_property_mappings.get(col, col))
            custom_name_entry = ttk.Entry(scrollable_frame, textvariable=custom_name_var, width=30)
            custom_name_entry.grid(row=idx, column=2, padx=5, pady=2, sticky=tk.W)

            # Include checkbox
            include_var = tk.BooleanVar(value=col in self.custom_property_mappings)
            include_check = ttk.Checkbutton(scrollable_frame, variable=include_var)
            include_check.grid(row=idx, column=3, padx=5, pady=2)

            # Sample value (first non-null value from column)
            sample_value = ""
            for val in self.df[col]:
                if pd.notna(val) and str(val).strip():
                    sample_value = str(val)[:30]
                    break
            ttk.Label(scrollable_frame, text=sample_value, foreground="gray").grid(row=idx, column=4, padx=5, pady=2, sticky=tk.W)

            mapping_widgets.append({
                'source': col,
                'custom_name': custom_name_var,
                'include': include_var
            })

        # Button frame
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)

        def save_mappings():
            # Clear existing mappings
            self.custom_property_mappings = {}

            # Add selected mappings
            for widget in mapping_widgets:
                if widget['include'].get():
                    source_col = widget['source']
                    custom_name = widget['custom_name'].get().strip()
                    if custom_name:
                        self.custom_property_mappings[source_col] = custom_name

            # Update mapped dataframe
            self.apply_custom_properties()
            self.display_data()

            dialog.destroy()
            messagebox.showinfo("Success", f"Added {len(self.custom_property_mappings)} custom properties")

        ttk.Button(button_frame, text="Save Mappings", command=save_mappings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def apply_custom_properties(self):
        """Apply custom property mappings to the mapped dataframe"""
        if not self.custom_property_mappings:
            return

        # Remove existing custom property columns
        existing_custom_cols = [col for col in self.mapped_df.columns if col not in [
            'Cost Type', 'Name', 'Usage', 'Takeoff Type', 'Formula',
            'Waste %', 'Round Up to Nearest', 'SKU', 'Description',
            'Cost Each', 'Markup %', 'Units'
        ]]
        self.mapped_df = self.mapped_df.drop(columns=existing_custom_cols)

        # Add custom property columns at the end - convert to string to preserve leading zeros
        for source_col, custom_name in self.custom_property_mappings.items():
            if source_col in self.df.columns:
                # Convert to string and preserve formatting (including leading zeros)
                self.mapped_df[custom_name] = self.df[source_col].astype(str)
                # Replace 'nan' string with empty string
                self.mapped_df[custom_name] = self.mapped_df[custom_name].replace('nan', '')

    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for text (rough estimate: ~4 chars per token)"""
        return len(text) // 4

    def calculate_batch_size(self, sample_size: int = 50) -> int:
        """Calculate optimal batch size based on model context window"""
        provider = self.selected_provider.get()
        model = self.selected_model.get()

        # Model context windows (in tokens)
        context_windows = {
            "claude-sonnet-4-20250514": 200000,
            "claude-3-5-sonnet-20241022": 200000,
            "claude-3-5-opus-20241022": 200000,
            "claude-3-5-haiku-20241022": 200000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16000,
            "gemini-2.0-flash-exp": 1000000,
            "gemini-1.5-pro": 2000000,
            "gemini-1.5-flash": 1000000,
            "deepseek-chat": 64000,
            "deepseek-reasoner": 64000
        }

        max_tokens = context_windows.get(model, 50000)

        # Reserve tokens for prompt structure and response
        reserved_tokens = 5000
        available_tokens = max_tokens - reserved_tokens

        # Estimate tokens per row
        if self.df is not None and len(self.df) > 0:
            sample = self.df.head(min(sample_size, len(self.df)))
            sample_text = sample.to_json()
            tokens_per_row = self.estimate_token_count(sample_text) / len(sample)

            # Calculate safe batch size (use 60% of available tokens for safety, lower for reliability)
            safe_batch_size = int((available_tokens * 0.6) / tokens_per_row)
            # Cap at 100 items per batch for JSON formatting reliability
            return max(10, min(safe_batch_size, 100))

        return 50  # Default

    def process_in_batches(self, data: List[Dict], process_func, description: str) -> List:
        """Process data in batches with progress updates"""
        batch_size = self.calculate_batch_size()
        total_items = len(data)
        results = []

        if total_items <= batch_size:
            # No batching needed
            return process_func(data)

        # Process in batches
        num_batches = (total_items + batch_size - 1) // batch_size

        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_items)
            batch_data = data[start_idx:end_idx]

            self.progress_label.config(
                text=f"⏳ {description} - Batch {batch_num + 1}/{num_batches} ({start_idx + 1}-{end_idx} of {total_items})..."
            )
            self.root.update()

            batch_results = process_func(batch_data)
            results.extend(batch_results)

        return results

    def save_progress(self):
        """Save work-in-progress to a file"""
        if self.df is None or self.mapped_df is None:
            messagebox.showwarning("Warning", "No data to save")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Work in Progress",
            defaultextension=".zztakeoff_progress",
            filetypes=[("zzTakeoff Progress", "*.zztakeoff_progress"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            import pickle

            # Create progress data structure
            progress_data = {
                'version': '1.0',
                'original_df': self.df,
                'mapped_df': self.mapped_df,
                'custom_property_mappings': self.custom_property_mappings,
                'unit_system': self.unit_system.get(),
                'original_filename': getattr(self, 'original_filename', 'unknown')
            }

            # Save to file
            with open(filename, 'wb') as f:
                pickle.dump(progress_data, f)

            messagebox.showinfo("Success", f"Progress saved to:\n{os.path.basename(filename)}")
            self.status_label.config(text=f"Progress saved to {os.path.basename(filename)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save progress:\n{str(e)}")

    def load_progress(self):
        """Load work-in-progress from a file"""
        filename = filedialog.askopenfilename(
            title="Load Work in Progress",
            filetypes=[("zzTakeoff Progress", "*.zztakeoff_progress"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            import pickle

            # Load from file
            with open(filename, 'rb') as f:
                progress_data = pickle.load(f)

            # Restore data
            self.df = progress_data['original_df']
            self.mapped_df = progress_data['mapped_df']
            self.custom_property_mappings = progress_data.get('custom_property_mappings', {})
            self.unit_system.set(progress_data.get('unit_system', 'Metric'))
            self.original_filename = progress_data.get('original_filename', 'loaded_progress')

            # Display data
            self.display_data()

            # Determine what stage we're at and enable appropriate buttons
            has_cost_types = not self.mapped_df['Cost Type'].isna().all() and (self.mapped_df['Cost Type'] != '').any()
            has_takeoff_types = not self.mapped_df['Takeoff Type'].isna().all() and (self.mapped_df['Takeoff Type'] != '').any()
            has_formulas = not self.mapped_df['Formula'].isna().all() and (self.mapped_df['Formula'] != '').any()

            # Enable buttons based on progress
            self.cost_type_btn.config(state='normal')
            self.apply_markup_btn.config(state='normal')
            self.custom_props_btn.config(state='normal')
            self.save_progress_btn.config(state='normal')

            if has_cost_types:
                self.takeoff_type_btn.config(state='normal')
                progress_msg = "✓ Cost Types loaded."

            if has_takeoff_types:
                self.formula_btn.config(state='normal')
                progress_msg = "✓ Cost Types and Takeoff Types loaded."

            if has_formulas:
                self.export_btn.config(state='normal')
                progress_msg = "✓ All fields loaded. Ready to export!"

            if not has_cost_types:
                progress_msg = "✓ Data loaded. Click 'Generate Cost Types' to continue."

            messagebox.showinfo("Success", f"Progress loaded from:\n{os.path.basename(filename)}")
            self.status_label.config(text=f"Loaded {len(self.df)} rows from progress file")
            self.progress_label.config(text=progress_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load progress:\n{str(e)}")

    def show_import_templates(self):
        """Show import templates management dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Format Templates")
        dialog.geometry("1000x700")
        dialog.transient(self.root)
        dialog.grab_set()

        # Instructions
        instructions = ttk.Label(dialog,
            text="Save and reuse column mappings for different estimating software formats (Databuild, PlanSwift, etc.)",
            font=('Arial', 10))
        instructions.pack(pady=10)

        # Main frame with two columns
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Template list
        left_frame = ttk.LabelFrame(main_frame, text="Saved Templates", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        template_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Arial', 10))
        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=template_listbox.yview)

        # Populate listbox
        def refresh_list():
            template_listbox.delete(0, tk.END)
            for template in self.import_templates:
                display = f"{template['name']} ({template.get('software', 'Unknown')})"
                template_listbox.insert(tk.END, display)

        refresh_list()

        # Right side - Template details
        right_frame = ttk.LabelFrame(main_frame, text="Template Details", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Template name
        ttk.Label(right_frame, text="Template Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(right_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Software name
        ttk.Label(right_frame, text="Estimating Software:").grid(row=1, column=0, sticky=tk.W, pady=5)
        software_var = tk.StringVar(value="")
        software_combo = ttk.Combobox(right_frame, textvariable=software_var, width=37,
                                      values=["Databuild", "PlanSwift", "Bluebeam", "CostX", "Cubit", "Other"])
        software_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Column mappings frame
        mappings_frame = ttk.LabelFrame(right_frame, text="Column Mappings", padding="10")
        mappings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        right_frame.rowconfigure(2, weight=1)
        right_frame.columnconfigure(1, weight=1)

        # Scrollable mappings
        canvas = tk.Canvas(mappings_frame)
        map_scrollbar = ttk.Scrollbar(mappings_frame, orient="vertical", command=canvas.yview)
        scrollable_map = ttk.Frame(canvas)

        scrollable_map.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_map, anchor="nw")
        canvas.configure(yscrollcommand=map_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        map_scrollbar.pack(side="right", fill="y")

        # Standard zzTakeoff fields
        zztakeoff_fields = [
            'Cost Type', 'Name', 'Usage', 'Takeoff Type', 'Formula',
            'Waste %', 'Round Up to Nearest', 'SKU', 'Description',
            'Cost Each', 'Markup %', 'Units'
        ]

        mapping_widgets = {}

        # Create mapping rows
        ttk.Label(scrollable_map, text="zzTakeoff Field", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(scrollable_map, text="→", font=('Arial', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_map, text="Source Column Name", font=('Arial', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        # Get available columns from loaded file
        available_columns = [''] + list(self.df.columns) if self.df is not None else ['(Load a file first)']

        for idx, field in enumerate(zztakeoff_fields, start=1):
            ttk.Label(scrollable_map, text=field).grid(row=idx, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(scrollable_map, text="→").grid(row=idx, column=1, padx=5, pady=2)

            source_var = tk.StringVar(value="")

            # Use Combobox if file is loaded, otherwise Entry
            if self.df is not None:
                source_combo = ttk.Combobox(scrollable_map, textvariable=source_var, width=32, values=available_columns)
                source_combo.grid(row=idx, column=2, padx=5, pady=2, sticky=tk.W)
            else:
                source_entry = ttk.Entry(scrollable_map, textvariable=source_var, width=35)
                source_entry.grid(row=idx, column=2, padx=5, pady=2, sticky=tk.W)

            mapping_widgets[field] = source_var

        # Notes section
        ttk.Label(right_frame, text="Notes (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(right_frame, height=3, width=40, wrap=tk.WORD)
        notes_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Button frame
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def save_template():
            name = name_entry.get().strip()
            software = software_var.get().strip()

            if not name:
                messagebox.showwarning("Warning", "Please enter a template name")
                return

            # Collect mappings
            field_mappings = {}
            for field, var in mapping_widgets.items():
                source_col = var.get().strip()
                if source_col and source_col != '(Load a file first)':
                    field_mappings[field] = source_col

            if not field_mappings:
                messagebox.showwarning("Warning", "Please map at least one field")
                return

            # Check if template exists
            template_exists = False
            for i, template in enumerate(self.import_templates):
                if template['name'] == name:
                    template_exists = True
                    if messagebox.askyesno("Update Template",
                        f"Template '{name}' already exists.\n\n" +
                        "Click YES to UPDATE the existing template\n" +
                        "Click NO to cancel"):
                        # Update existing template
                        self.import_templates[i] = {
                            'name': name,
                            'software': software,
                            'field_mappings': field_mappings,
                            'notes': notes_text.get(1.0, tk.END).strip()
                        }
                        self.save_import_templates()
                        refresh_list()
                        messagebox.showinfo("Success", f"Template '{name}' updated!")
                        return
                    else:
                        return

            # Create new template
            new_template = {
                'name': name,
                'software': software,
                'field_mappings': field_mappings,
                'notes': notes_text.get(1.0, tk.END).strip()
            }

            self.import_templates.append(new_template)
            self.save_import_templates()
            refresh_list()

            messagebox.showinfo("Success", f"Template '{name}' saved!")

        def delete_template():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template to delete")
                return

            idx = selection[0]
            template_name = self.import_templates[idx]['name']

            if messagebox.askyesno("Confirm Delete", f"Delete template '{template_name}'?"):
                del self.import_templates[idx]
                self.save_import_templates()
                refresh_list()
                messagebox.showinfo("Deleted", f"Template '{template_name}' deleted")

        def load_template_to_fields():
            selection = template_listbox.curselection()
            if not selection:
                return

            idx = selection[0]
            template = self.import_templates[idx]

            name_entry.delete(0, tk.END)
            name_entry.insert(0, template['name'])

            software_var.set(template.get('software', ''))

            # Clear existing mappings
            for var in mapping_widgets.values():
                var.set('')

            # Load mappings
            for field, source_col in template.get('field_mappings', {}).items():
                if field in mapping_widgets:
                    mapping_widgets[field].set(source_col)

            notes_text.delete(1.0, tk.END)
            notes_text.insert(1.0, template.get('notes', ''))

        def apply_template():
            """Apply template to current loaded data"""
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template to apply")
                return

            if self.df is None:
                messagebox.showwarning("Warning", "Please load a data file first")
                return

            idx = selection[0]
            template = self.import_templates[idx]

            # Apply mappings
            applied_count = 0
            skipped_fields = []

            for zz_field, source_col in template.get('field_mappings', {}).items():
                if source_col in self.df.columns:
                    if zz_field == 'Name':
                        self.mapped_df['Name'] = self.df[source_col]
                    elif zz_field == 'SKU':
                        self.mapped_df['SKU'] = self.df[source_col]
                    elif zz_field == 'Description':
                        self.mapped_df['Description'] = self.df[source_col]
                    elif zz_field == 'Cost Each':
                        self.mapped_df['Cost Each'] = self.df[source_col]
                    elif zz_field == 'Units':
                        self.mapped_df['Units'] = self.df[source_col]
                    applied_count += 1
                else:
                    skipped_fields.append(f"{zz_field} ← {source_col}")

            self.display_data()
            dialog.destroy()

            msg = f"Applied {applied_count} field mappings from template '{template['name']}'"
            if skipped_fields:
                msg += f"\n\nSkipped (column not found):\n" + "\n".join(skipped_fields)

            messagebox.showinfo("Template Applied", msg)

        def save_from_current():
            """Save template from current file's columns"""
            if self.df is None:
                messagebox.showwarning("Warning", "Please load a file first to detect columns")
                return

            # Auto-populate mappings based on current file
            detected = 0
            for field in mapping_widgets.keys():
                # Try to find matching column
                for col in self.df.columns:
                    if field.lower() in col.lower() or col.lower() in field.lower():
                        mapping_widgets[field].set(col)
                        detected += 1
                        break

            if detected > 0:
                messagebox.showinfo("Auto-Detect", f"Auto-detected {detected} field mappings.\nPlease review and adjust as needed.")

        def clone_template():
            """Clone selected template with new name"""
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template to clone")
                return

            idx = selection[0]
            template = self.import_templates[idx]

            # Ask for new name
            new_name = tk.simpledialog.askstring("Clone Template",
                f"Enter new name for cloned template:\n(Original: {template['name']})",
                initialvalue=f"{template['name']} - Copy")

            if not new_name or not new_name.strip():
                return

            new_name = new_name.strip()

            # Check if name exists
            for t in self.import_templates:
                if t['name'] == new_name:
                    messagebox.showerror("Error", f"Template '{new_name}' already exists")
                    return

            # Create cloned template
            cloned_template = {
                'name': new_name,
                'software': template.get('software', ''),
                'field_mappings': template.get('field_mappings', {}).copy(),
                'notes': template.get('notes', '') + "\n(Cloned from: " + template['name'] + ")"
            }

            self.import_templates.append(cloned_template)
            self.save_import_templates()
            refresh_list()

            messagebox.showinfo("Success", f"Template cloned as '{new_name}'")

        ttk.Button(button_frame, text="Save Template", command=save_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=delete_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clone", command=clone_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load to Fields", command=load_template_to_fields).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Apply to Data", command=apply_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Auto-Detect from File", command=save_from_current).pack(side=tk.LEFT, padx=2)

        # Double-click to load
        template_listbox.bind('<Double-Button-1>', lambda e: load_template_to_fields())

        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def create_tooltip(self, widget, text):
        """Create tooltip for a widget"""
        ToolTip(widget, text)

    def toggle_settings(self):
        """Toggle settings panel visibility"""
        if self.settings_visible.get():
            # Hide settings
            self.settings_content_frame.grid_remove()
            self.settings_toggle_btn.config(text="▶ Settings")
            self.settings_visible.set(False)
        else:
            # Show settings
            self.settings_content_frame.grid()
            self.settings_toggle_btn.config(text="▼ Settings")
            self.settings_visible.set(True)

    def toggle_file_ops(self):
        """Toggle file operations panel visibility"""
        if self.file_ops_visible.get():
            self.file_ops_content_frame.grid_remove()
            self.file_ops_toggle_btn.config(text="▶ File Operations")
            self.file_ops_visible.set(False)
        else:
            self.file_ops_content_frame.grid()
            self.file_ops_toggle_btn.config(text="▼ File Operations")
            self.file_ops_visible.set(True)

    def toggle_mapping(self):
        """Toggle data mapping panel visibility"""
        if self.mapping_visible.get():
            self.mapping_content_frame.grid_remove()
            self.mapping_toggle_btn.config(text="▶ Data Mapping & Templates")
            self.mapping_visible.set(False)
        else:
            self.mapping_content_frame.grid()
            self.mapping_toggle_btn.config(text="▼ Data Mapping & Templates")
            self.mapping_visible.set(True)

    def toggle_ai_workflow(self):
        """Toggle AI workflow panel visibility"""
        if self.ai_workflow_visible.get():
            self.ai_workflow_content_frame.grid_remove()
            self.ai_workflow_toggle_btn.config(text="▶ AI Processing Workflow")
            self.ai_workflow_visible.set(False)
        else:
            self.ai_workflow_content_frame.grid()
            self.ai_workflow_toggle_btn.config(text="▼ AI Processing Workflow")
            self.ai_workflow_visible.set(True)

    def update_api_status(self):
        """Update API key status indicator"""
        provider = self.selected_provider.get()
        if provider in self.ai_providers:
            is_available = self.ai_providers[provider]["available"]
            provider_name = self.ai_providers[provider]["name"]

            if is_available:
                self.api_status_label.config(text="✓ API Key Configured", foreground="green")
                # Auto-collapse settings after successful configuration
                if self.settings_visible.get():
                    self.root.after(1000, self.toggle_settings)  # Collapse after 1 second
            else:
                self.api_status_label.config(text="✗ API Key Not Found", foreground="red")

    def on_closing(self):
        """Handle window close event with confirmation"""
        if self.df is not None:
            if messagebox.askokcancel("Quit", "Are you sure you want to exit? Any unsaved work will be lost."):
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = TakeoffConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
