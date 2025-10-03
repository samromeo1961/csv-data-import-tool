#!/usr/bin/env python3
"""
Test script for zzTakeoff Converter
Verifies installation and processes sample data
"""

import pandas as pd
import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        print("✗ pandas not found - run: pip install pandas")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl installed")
    except ImportError:
        print("✗ openpyxl not found - run: pip install openpyxl")
        return False
    
    try:
        import anthropic
        print("✓ anthropic installed")
    except ImportError:
        print("✗ anthropic not found - run: pip install anthropic")
        return False
    
    try:
        import tkinter
        print("✓ tkinter available")
    except ImportError:
        print("✗ tkinter not found - install python3-tk package")
        return False
    
    return True

def test_api_key():
    """Test if API key is configured"""
    print("\nTesting API key...")
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✓ API key found (starts with: {api_key[:10]}...)")
        return True
    else:
        print("✗ ANTHROPIC_API_KEY not set in environment")
        print("  Set it with: export ANTHROPIC_API_KEY=your_key")
        return False

def create_sample_data():
    """Create a sample CSV file for testing"""
    print("\nCreating sample test data...")
    
    sample_data = {
        'Databuild Code': ['130 010', '180 030', '360004', '2205', '100001'],
        'Quantity': [15, 10, 188.64, 2, 6.8],
        'Cost Centre': [130, 180, 400, 410, 430],
        'Name': [
            'Internal Drainage Points',
            'Supply 32MPA Concrete',
            'Supply & install R3.0 batts to ceiling',
            'Rough-In Shower',
            'Supply Face Bricks'
        ],
        'Unit Price': [70, 237, 5.25, 97.5, 784.5],
        'Units': ['EA', 'CU M', 'Sm', 'EA', 'THOUS'],
        'Supplier Reference': ['RAVPLUMB', '', 'PATNICAR', 'RAVPLUMB', '']
    }
    
    df = pd.DataFrame(sample_data)
    filename = 'sample_export.csv'
    df.to_csv(filename, index=False)
    print(f"✓ Created {filename}")
    print(f"  Contains {len(df)} sample items")
    return filename

def test_data_loading(filename):
    """Test loading the sample data"""
    print(f"\nTesting data loading from {filename}...")
    try:
        df = pd.read_csv(filename)
        print(f"✓ Loaded {len(df)} rows")
        print(f"✓ Columns: {', '.join(df.columns)}")
        return True
    except Exception as e:
        print(f"✗ Failed to load: {e}")
        return False

def main():
    print("=" * 60)
    print("zzTakeoff Converter - Installation Test")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some packages are missing. Please install them first.")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Test API key
    api_configured = test_api_key()
    if not api_configured:
        print("\n⚠️  API key not configured. AI features will not work.")
        print("   The GUI will launch but AI classification will fail.")
    
    # Create and test sample data
    sample_file = create_sample_data()
    if not test_data_loading(sample_file):
        return False
    
    print("\n" + "=" * 60)
    if api_configured:
        print("✅ All tests passed! You can now run:")
        print("   python takeoff_converter.py")
    else:
        print("⚠️  Setup incomplete - configure API key:")
        print("   export ANTHROPIC_API_KEY=your_key")
        print("   python takeoff_converter.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
