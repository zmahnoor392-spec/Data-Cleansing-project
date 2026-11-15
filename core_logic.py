import pandas as pd
import numpy as np
import shutil
import os
import re

# File Paths
original_path = r'laptopDataset\laptopData.csv'
project_dir = os.path.dirname(os.path.abspath(__file__))
destination_path = os.path.join(project_dir, 'laptopData.csv')
cleaned_file_path = os.path.join(project_dir, 'laptop_cleaned_final.csv')

def move_file():
    """Copies/Moves the original CSV file to the project folder."""
    if os.path.exists(original_path):
        try:
            shutil.copy(original_path, destination_path)
            try:
                os.remove(original_path)
                return True, f"File successfully moved to project folder: {destination_path}"
            except Exception:
                return True, f"File copied successfully to project folder. (Original was locked and kept at source)."
        except Exception as e:
            return False, f"Error copying file: {e}"
    else:
        if os.path.exists(destination_path):
            return True, f"File already exists at {destination_path}"
        else:
            return False, f"Source file {original_path} not found."

def clean_data(df=None, options=None):
    """
    Performs data cleansing operations.
    If df is None, loads from destination_path.
    options is a dict of boolean flags for different operations.
    """
    if df is None:
        if not os.path.exists(destination_path):
            return None, "Error: Dataset not found for cleaning."
        df = pd.read_csv(destination_path)

    if options is None:
        # Default all to true
        options = {k: True for k in ['empty_rows', 'ram', 'weight', 'screen', 'cpu', 'memory', 'gpu_os', 'duplicates']}

    # 1. Empty rows & Unnamed index
    if options.get('empty_rows'):
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        df = df.dropna(how='all')

    # 2. Ram
    if options.get('ram') and 'Ram' in df.columns:
        df['Ram'] = df['Ram'].astype(str).str.replace('GB', '', regex=False)
        df['Ram'] = pd.to_numeric(df['Ram'], errors='coerce')
        df['Ram'] = df['Ram'].fillna(df['Ram'].median()).astype(int)

    # 3. Weight & Inches
    if options.get('weight'):
        if 'Weight' in df.columns:
            df['Weight'] = df['Weight'].astype(str).str.replace('kg', '', regex=False)
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
            df['Weight'] = df['Weight'].fillna(df['Weight'].median())
        if 'Inches' in df.columns:
            df['Inches'] = pd.to_numeric(df['Inches'], errors='coerce')
            df['Inches'] = df['Inches'].fillna(df['Inches'].median())

    # 4. Screen Resolution
    if options.get('screen') and 'ScreenResolution' in df.columns:
        df['Touchscreen'] = df['ScreenResolution'].apply(lambda x: 1 if 'Touchscreen' in str(x) else 0)
        df['Ips'] = df['ScreenResolution'].apply(lambda x: 1 if 'IPS' in str(x) else 0)

        def extract_res(res_str):
            matches = re.findall(r'(\d+)x(\d+)', str(res_str))
            if matches:
                return int(matches[0][0]), int(matches[0][1])
            return np.nan, np.nan

        df['X_res'], df['Y_res'] = zip(*df['ScreenResolution'].apply(extract_res))
        df['ppi'] = (((df['X_res']**2) + (df['Y_res']**2))**0.5 / df['Inches']).round(2)
        df = df.drop(columns=['ScreenResolution'])

    # 5. Cpu
    if options.get('cpu') and 'Cpu' in df.columns:
        def fetch_processor(text):
            text = str(text)
            brand = " ".join(text.split()[0:3])
            if brand in ['Intel Core i7', 'Intel Core i5', 'Intel Core i3']:
                return brand
            elif text.startswith('Intel'):
                return 'Other Intel Processor'
            else:
                return 'AMD Processor'

        df['Cpu Brand'] = df['Cpu'].apply(fetch_processor)
        df['Cpu_Speed_GHz'] = df['Cpu'].str.extract(r'(\d+\.?\d*)GHz').astype(float)
        df = df.drop(columns=['Cpu'])

    # 6. Memory
    if options.get('memory') and 'Memory' in df.columns:
        df['Memory'] = df['Memory'].astype(str).replace(r'\.0', '', regex=True)
        df['Memory'] = df['Memory'].str.replace('GB', '', regex=False)
        df['Memory'] = df['Memory'].str.replace('TB', '000', regex=False)

        new = df['Memory'].str.split("+", n=1, expand=True)
        df['first'] = new[0].str.strip()
        df['second'] = new[1].str.strip()

        df["Layer1HDD"] = df["first"].apply(lambda x: 1 if "HDD" in str(x) else 0)
        df["Layer1SSD"] = df["first"].apply(lambda x: 1 if "SSD" in str(x) else 0)
        df["Layer1Hybrid"] = df["first"].apply(lambda x: 1 if "Hybrid" in str(x) else 0)
        df["Layer1Flash"] = df["first"].apply(lambda x: 1 if "Flash" in str(x) else 0)
        df['first'] = df['first'].str.extract(r'(\d+)').astype(float).fillna(0)

        df['second'] = df['second'].fillna("0")
        df["Layer2HDD"] = df["second"].apply(lambda x: 1 if "HDD" in str(x) else 0)
        df["Layer2SSD"] = df["second"].apply(lambda x: 1 if "SSD" in str(x) else 0)
        df["Layer2Hybrid"] = df["second"].apply(lambda x: 1 if "Hybrid" in str(x) else 0)
        df["Layer2Flash"] = df["second"].apply(lambda x: 1 if "Flash" in str(x) else 0)
        df['second'] = df['second'].str.extract(r'(\d+)').astype(float).fillna(0)

        df["HDD"] = (df["first"] * df["Layer1HDD"] + df["second"] * df["Layer2HDD"])
        df["SSD"] = (df["first"] * df["Layer1SSD"] + df["second"] * df["Layer2SSD"])
        df["Hybrid"] = (df["first"] * df["Layer1Hybrid"] + df["second"] * df["Layer2Hybrid"])
        df["Flash_Storage"] = (df["first"] * df["Layer1Flash"] + df["second"] * df["Layer2Flash"])

        df = df.drop(columns=['first', 'second', 'Layer1HDD', 'Layer1SSD', 'Layer1Hybrid',
                            'Layer1Flash', 'Layer2HDD', 'Layer2SSD', 'Layer2Hybrid',
                            'Layer2Flash', 'Memory'])

    # 7. Gpu & OpSys
    if options.get('gpu_os'):
        if 'Gpu' in df.columns:
            df['Gpu Brand'] = df['Gpu'].apply(lambda x: str(x).split()[0])
            df = df[df['Gpu Brand'] != 'ARM']
            df = df.drop(columns=['Gpu'])

        if 'OpSys' in df.columns:
            def cat_os(inp):
                inp = str(inp)
                if 'Windows' in inp: return 'Windows'
                elif 'Mac' in inp or 'macOS' in inp: return 'Mac'
                else: return 'Others/No OS/Linux'
            df['os'] = df['OpSys'].apply(cat_os)
            df = df.drop(columns=['OpSys'])

    # 8. Duplicates
    if options.get('duplicates'):
        df = df.drop_duplicates()

    return df, "Successfully cleaned data."
