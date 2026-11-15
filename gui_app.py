import os
import shutil
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import core_logic

class DataCleansingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Dataset Data Cleansing Tool")
        self.root.geometry("1150x750")
        self.root.minsize(950, 650)
        self.center_window(1150, 750)

        # UI Colors & Styles
        self.bg_color = "#f4f6f9"
        self.primary_color = "#2b5c8f"
        self.accent_color = "#27ae60"
        self.card_bg = "#ffffff"
        self.root.configure(bg=self.bg_color)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', font=('Segoe UI', 10))
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 6])
        self.style.map('TNotebook.Tab', background=[('selected', self.primary_color)], foreground=[('selected', 'white')])

        # Data variables
        self.raw_df = None
        self.cleaned_df = None
        self.current_file_path = ""

        self.create_widgets()

        # Auto-load default dataset if exists
        default_file = core_logic.destination_path
        if os.path.exists(default_file):
            self.load_dataset(default_file)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg=self.primary_color, height=60)
        header.pack(fill='x', side='top')
        tk.Label(header, text="💻 Laptop Dataset Data Cleansing Application", font=('Segoe UI', 16, 'bold'), bg=self.primary_color, fg='white', padx=20, pady=12).pack(side='left')

        # File Selector
        file_frame = tk.Frame(self.root, bg=self.card_bg, relief='ridge', bd=1, pady=8, padx=15)
        file_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(file_frame, text="Dataset File:", font=('Segoe UI', 10, 'bold'), bg=self.card_bg).pack(side='left', padx=(0, 10))
        self.file_path_var = tk.StringVar(value="No file loaded")
        tk.Entry(file_frame, textvariable=self.file_path_var, font=('Segoe UI', 9), width=70, state='readonly').pack(side='left', padx=(0, 10), fill='x', expand=True)
        ttk.Button(file_frame, text="📁 Browse CSV...", command=self.browse_file).pack(side='left', padx=5)
        ttk.Button(file_frame, text="📦 Load Project File", command=self.load_default).pack(side='left', padx=5)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        self.tab_ops = ttk.Frame(self.notebook)
        self.tab_raw = ttk.Frame(self.notebook)
        self.tab_clean = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_ops, text=" 🛠️ Cleansing Control ")
        self.notebook.add(self.tab_raw, text=" 📊 Raw Preview ")
        self.notebook.add(self.tab_clean, text=" ✨ Cleaned Result ")

        self.setup_ops_tab()
        self.setup_raw_tab()
        self.setup_clean_tab()

    def setup_ops_tab(self):
        container = tk.Frame(self.tab_ops, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Left: Options
        left = tk.Frame(container, bg=self.card_bg, relief='ridge', bd=1, padx=20, pady=20, width=400)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left, text="Operations", font=('Segoe UI', 12, 'bold'), bg=self.card_bg, fg=self.primary_color).pack(anchor='w', pady=(0, 15))

        self.vars = {
            'empty_rows': tk.BooleanVar(value=True),
            'ram': tk.BooleanVar(value=True),
            'weight': tk.BooleanVar(value=True),
            'screen': tk.BooleanVar(value=True),
            'cpu': tk.BooleanVar(value=True),
            'memory': tk.BooleanVar(value=True),
            'gpu_os': tk.BooleanVar(value=True),
            'duplicates': tk.BooleanVar(value=True)
        }

        labels = {
            'empty_rows': "Remove Empty Rows & Index",
            'ram': "Clean 'Ram' Column",
            'weight': "Clean 'Weight' & 'Inches'",
            'screen': "Parse 'ScreenResolution'",
            'cpu': "Parse 'Cpu' (Brand/Speed)",
            'memory': "Parse 'Memory' (SSD/HDD)",
            'gpu_os': "Categorize 'Gpu' & 'OpSys'",
            'duplicates': "Remove Duplicates"
        }

        for key, text in labels.items():
            tk.Checkbutton(left, text=text, variable=self.vars[key], font=('Segoe UI', 10), bg=self.card_bg, anchor='w').pack(fill='x', pady=3)

        tk.Button(left, text="🚀 Run Cleansing", command=self.run_process, font=('Segoe UI', 12, 'bold'), bg=self.accent_color, fg='white', bd=0, pady=12, cursor='hand2').pack(fill='x', pady=(30, 0))

        # Right: Log & Stats
        right = tk.Frame(container, bg=self.bg_color)
        right.pack(side='right', fill='both', expand=True)

        stats = tk.Frame(right, bg=self.bg_color)
        stats.pack(fill='x', pady=(0, 10))

        self.raw_stat = self.create_stat(stats, "Raw Records", "0 x 0")
        self.raw_stat.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.clean_stat = self.create_stat(stats, "Cleaned Records", "N/A")
        self.clean_stat.pack(side='left', fill='x', expand=True, padx=5)

        log_frame = tk.Frame(right, bg=self.card_bg, relief='ridge', bd=1, padx=10, pady=10)
        log_frame.pack(fill='both', expand=True)
        self.log_area = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9), bg='#1e272c', fg='#2ec4b6')
        self.log_area.pack(fill='both', expand=True)

    def create_stat(self, parent, title, val):
        f = tk.Frame(parent, bg=self.card_bg, relief='ridge', bd=1, padx=15, pady=10)
        tk.Label(f, text=title, font=('Segoe UI', 9), bg=self.card_bg, fg="#7f8c8d").pack(anchor='w')
        v = tk.Label(f, text=val, font=('Segoe UI', 14, 'bold'), bg=self.card_bg, fg=self.primary_color)
        v.pack(anchor='w')
        f.v_lbl = v
        return f

    def setup_raw_tab(self):
        f = tk.Frame(self.tab_raw, bg=self.card_bg, padx=10, pady=10)
        f.pack(fill='both', expand=True, padx=10, pady=10)
        self.raw_tree = self.create_tree(f)

    def setup_clean_tab(self):
        f = tk.Frame(self.tab_clean, bg=self.card_bg, padx=10, pady=10)
        f.pack(fill='both', expand=True, padx=10, pady=10)
        bar = tk.Frame(f, bg=self.card_bg)
        bar.pack(fill='x', pady=(0, 10))
        tk.Button(bar, text="💾 Export Cleaned CSV...", command=self.export, font=('Segoe UI', 10, 'bold'), bg=self.accent_color, fg='white', bd=0, padx=15, pady=5).pack(side='right')
        self.clean_tree = self.create_tree(f)

    def create_tree(self, parent):
        tf = tk.Frame(parent)
        tf.pack(fill='both', expand=True)
        sy = ttk.Scrollbar(tf, orient='vertical')
        sx = ttk.Scrollbar(tf, orient='horizontal')
        t = ttk.Treeview(tf, yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.config(command=t.yview); sx.config(command=t.xview)
        sy.pack(side='right', fill='y'); sx.pack(side='bottom', fill='x'); t.pack(fill='both', expand=True)
        return t

    def log(self, msg):
        self.log_area.insert(tk.END, f"> {msg}\n"); self.log_area.see(tk.END)

    def load_dataset(self, path):
        try:
            self.raw_df = pd.read_csv(path)
            self.current_file_path = path
            self.file_path_var.set(path)
            r, c = self.raw_df.shape
            self.raw_stat.v_lbl.config(text=f"{r} Rows x {c} Cols")
            self.fill_tree(self.raw_tree, self.raw_df)
            self.log(f"Loaded {os.path.basename(path)}: {r} rows")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fill_tree(self, tree, df):
        tree.delete(*tree.get_children())
        tree['columns'] = list(df.columns); tree['show'] = 'headings'
        for c in df.columns:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        for _, row in df.head(50).iterrows():
            tree.insert('', 'end', values=[str(v) if pd.notnull(v) else "" for v in row])

    def browse_file(self):
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if p: self.load_dataset(p)

    def load_default(self):
        if os.path.exists(core_logic.destination_path):
            self.load_dataset(core_logic.destination_path)
        else:
            messagebox.showinfo("Info", "Project file not found. Use 'Browse' to select one.")

    def run_process(self):
        if self.raw_df is None: return messagebox.showwarning("Warning", "Load data first!")
        self.log("Starting cleansing...")
        opts = {k: v.get() for k, v in self.vars.items()}
        res_df, msg = core_logic.clean_data(self.raw_df.copy(), opts)
        if res_df is not None:
            self.cleaned_df = res_df
            self.log(msg)
            r, c = res_df.shape
            self.clean_stat.v_lbl.config(text=f"{r} Rows x {c} Cols")
            self.fill_tree(self.clean_tree, res_df)
            self.notebook.select(self.tab_clean)
            messagebox.showinfo("Success", "Cleansing complete!")
        else:
            self.log(f"Error: {msg}")

    def export(self):
        if self.cleaned_df is None: return
        p = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="laptop_cleaned_final.csv")
        if p:
            self.cleaned_df.to_csv(p, index=False)
            messagebox.showinfo("Saved", f"Exported to {p}")

if __name__ == "__main__":
    root = tk.Tk()
    DataCleansingGUI(root)
    root.mainloop()
