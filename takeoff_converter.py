#!/usr/bin/env python3
"""
zzTakeoff Import Converter
Converts estimating software exports (Databuild, PlanSwift, etc.) to zzTakeoff import format
Uses AI to intelligently map and generate required fields
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import os
from typing import Dict, List, Optional
import anthropic

class TakeoffConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("zzTakeoff Import Converter")
        self.root.geometry("1400x900")
        
        # Data storage
        self.df = None
        self.mapped_df = None
        self.mapping_history = self.load_mapping_history()
        
        # AI Client - using direct API call
        self.client = anthropic.Anthropic()
        
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
        
        # Title
        title_label = ttk.Label(main_frame, text="zzTakeoff Import Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="Load CSV/Excel", 
                  command=self.load_file).grid(row=0, column=0, padx=5)
        
        ttk.Button(control_frame, text="Generate Cost Types (AI)", 
                  command=self.generate_cost_types,
                  state='disabled').grid(row=0, column=1, padx=5)
        self.cost_type_btn = control_frame.winfo_children()[-1]
        
        ttk.Button(control_frame, text="Generate Takeoff Types (AI)", 
                  command=self.generate_takeoff_types,
                  state='disabled').grid(row=0, column=2, padx=5)
        self.takeoff_type_btn = control_frame.winfo_children()[-1]
        
        ttk.Button(control_frame, text="Generate Formulas (AI)", 
                  command=self.generate_formulas,
                  state='disabled').grid(row=0, column=3, padx=5)
        self.formula_btn = control_frame.winfo_children()[-1]
        
        ttk.Button(control_frame, text="Export to zzTakeoff", 
                  command=self.export_file,
                  state='disabled').grid(row=0, column=4, padx=5)
        self.export_btn = control_frame.winfo_children()[-1]
        
        # Progress label
        self.progress_label = ttk.Label(control_frame, text="", foreground="blue")
        self.progress_label.grid(row=1, column=0, columnspan=5, pady=5)
        
        # Data display
        data_frame = ttk.LabelFrame(main_frame, text="Data Preview", padding="10")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Treeview for data display
        self.tree = ttk.Treeview(data_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready to load file", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
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
            
            # Initialize mapped dataframe
            self.initialize_mapped_df()
            
            # Display data
            self.display_data()
            
            # Enable buttons
            self.cost_type_btn.config(state='normal')
            
            self.status_label.config(text=f"Loaded {len(self.df)} rows from {os.path.basename(filename)}")
            self.progress_label.config(text="✓ File loaded. Click 'Generate Cost Types' to start AI mapping.")
            
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
    
    def call_claude_api(self, prompt: str, system_prompt: str = "") -> str:
        """Call Claude API for AI assistance"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"AI API Error: {str(e)}")
    
    def generate_cost_types(self):
        """Use AI to generate Cost Type classifications"""
        if self.df is None or self.mapped_df is None:
            return
        
        self.progress_label.config(text="⏳ Generating Cost Types with AI... Please wait.")
        self.root.update()
        
        try:
            # Prepare sample data for AI
            sample_data = []
            for idx, row in self.df.head(50).iterrows():
                item = {
                    'name': row.get('Name', ''),
                    'supplier': row.get('Supplier Reference', ''),
                    'code': row.get('Databuild Code', ''),
                    'unit': row.get('Units', '')
                }
                sample_data.append(item)
            
            # Create prompt for AI
            prompt = f"""Analyze these construction items and classify each into one of these Cost Types:
- Material
- Labor
- Equipment
- Subcontract
- Other

Items to classify:
{json.dumps(sample_data, indent=2)}

Classification rules:
1. If Supplier Reference contains names like plumber/carpenter/installer names → Labor or Subcontract
2. If description mentions "Supply" or "Fix" → Material or Labor respectively
3. If description is about rental/hire → Equipment
4. Fixtures, fittings, raw materials → Material
5. Installation, fixing, painting work → Labor

Return ONLY a JSON array with cost types in the same order as input. Format:
["Material", "Labor", "Material", ...]

Be consistent and use exact category names."""

            response = self.call_claude_api(prompt)
            
            # Parse response
            cost_types = json.loads(response.strip())
            
            # Apply to full dataset using pattern matching
            self.apply_cost_types_to_all(cost_types, sample_data)
            
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
            # Prepare sample data
            sample_data = []
            for idx, row in self.df.head(50).iterrows():
                item = {
                    'name': row.get('Name', ''),
                    'unit': row.get('Units', ''),
                    'quantity': row.get('Quantity', '')
                }
                sample_data.append(item)
            
            prompt = f"""Analyze these construction items and classify each Takeoff Type as one of:
- Area (for items measured in square units: SM, Sm, m2, SQ M, etc.)
- Linear (for items measured in linear units: M, Lm, LM, meters, etc.)
- Count (for items counted as whole units: EA, Ea, each, etc.)
- Segment (for segmented linear items)

Items to classify:
{json.dumps(sample_data, indent=2)}

Rules:
1. Look at the Units column primarily
2. SM, Sm, m2, SQ M, SQUARE → Area
3. M, Lm, LM, meters, metres → Linear
4. EA, Ea, each, THOUS, bag, TONNE, PACKETS → Count
5. When unit is ambiguous, look at the item name/description

Return ONLY a JSON array with takeoff types in order. Format:
["Area", "Count", "Linear", ...]

Use exact category names."""

            response = self.call_claude_api(prompt)
            
            # Parse response
            takeoff_types = json.loads(response.strip())
            
            # Apply to full dataset
            self.apply_takeoff_types_to_all(takeoff_types, sample_data)
            
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
            # Prepare sample data with takeoff types
            sample_data = []
            for idx in range(min(30, len(self.df))):
                row = self.df.iloc[idx]
                mapped_row = self.mapped_df.iloc[idx]
                item = {
                    'name': row.get('Name', ''),
                    'unit': row.get('Units', ''),
                    'quantity': row.get('Quantity', ''),
                    'takeoff_type': mapped_row['Takeoff Type']
                }
                sample_data.append(item)
            
            prompt = f"""Generate formulas for zzTakeoff import based on item details.

Items with their Takeoff Types:
{json.dumps(sample_data, indent=2)}

Formula Rules:
1. For Area types: Usually "Length * Width" or just "Area" if single measurement
2. For Linear types: Usually "Length" or "Count * Length"
3. For Count types: Usually "Count" or just the quantity itself
4. Keep formulas simple and use standard field names

Common formula patterns:
- Area items: "Length * Width" or "Area"
- Linear items: "Length" or "Quantity * Length"  
- Count items: "Count" or "Quantity"
- Some may need: "(Length * Width) * (1 + Waste/100)" if waste is a factor

Return ONLY a JSON array of formula strings in the same order. Format:
["Area", "Count", "Length * Width", "Count", ...]

Keep it simple and practical."""

            response = self.call_claude_api(prompt)
            
            # Parse response
            formulas = json.loads(response.strip())
            
            # Apply to full dataset
            self.apply_formulas_to_all(formulas)
            
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
                # Fallback based on type
                if takeoff_type == 'Area':
                    formula = 'Area'
                elif takeoff_type == 'Linear':
                    formula = 'Length'
                elif takeoff_type == 'Count':
                    formula = 'Count'
                else:
                    formula = 'Quantity'
            
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
            
            export_df = self.mapped_df[export_columns].copy()
            
            # Save file
            if filename.endswith('.csv'):
                export_df.to_csv(filename, index=False)
            else:
                export_df.to_excel(filename, index=False)
            
            messagebox.showinfo("Success", 
                              f"Exported {len(export_df)} items to:\n{os.path.basename(filename)}")
            
            self.status_label.config(text=f"Exported to {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")

def main():
    root = tk.Tk()
    app = TakeoffConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
