import os
import sys
import tkinter as tk
import core_logic
from gui_app import DataCleansingGUI

def run_console():
    """Runs the data cleansing project in console mode."""
    print("--- Laptop Data Cleansing (Console Mode) ---")

    # 1. Move file if needed
    success, msg = core_logic.move_file()
    print(f"> {msg}")

    # 2. Run Cleaning
    df, msg = core_logic.clean_data()
    if df is not None:
        print(f"> {msg}")
        # Save output
        output_path = core_logic.cleaned_file_path
        df.to_csv(output_path, index=False)
        print(f"> Cleaned dataset saved to: {output_path}")
        print(f"> Final Shape: {df.shape}")
    else:
        print(f"❌ Error: {msg}")

def run_gui():
    """Runs the data cleansing project in GUI mode (Default)."""
    print("Launching Laptop Data Cleansing GUI...")
    root = tk.Tk()
    app = DataCleansingGUI(root)
    root.mainloop()

def main():
    # Default to GUI unless --cli flag is provided
    if "--cli" in sys.argv:
        run_console()
    else:
        run_gui()

if __name__ == "__main__":
    main()
