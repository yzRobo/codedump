# codedump_gui.py

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Make sure codedump.py sits alongside this file
import codedump

class CodeDumpGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CodeDump GUI")
        self.geometry("700x500")

        # Source directory
        tk.Label(self, text="Source Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.src_var = tk.StringVar(value=os.getcwd())
        tk.Entry(self, textvariable=self.src_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(self, text="Browse…", command=self.browse_src).grid(row=0, column=2, padx=5)

        # List-only checkbox
        self.list_only_var = tk.BooleanVar()
        tk.Checkbutton(self, text="List only", variable=self.list_only_var).grid(row=1, column=1, sticky="w", padx=5)

        # Split-files checkbox
        self.split_var = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="Split files",
            variable=self.split_var,
            command=self.toggle_output_dir
        ).grid(row=2, column=1, sticky="w", padx=5)

        # Output directory (only enabled when split is checked)
        tk.Label(self, text="Output Directory:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.out_var = tk.StringVar(value=os.path.join(os.getcwd(), "extracted"))
        self.out_entry = tk.Entry(self, textvariable=self.out_var, width=60, state="disabled")
        self.out_entry.grid(row=3, column=1, padx=5)
        self.out_btn = tk.Button(self, text="Browse…", command=self.browse_out, state="disabled")
        self.out_btn.grid(row=3, column=2, padx=5)

        # Run button
        tk.Button(self, text="Run", command=self.run).grid(row=4, column=1, pady=10)

        # Scrollable text output
        self.log = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        # Let the text area expand
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def browse_src(self):
        d = filedialog.askdirectory(initialdir=self.src_var.get())
        if d:
            self.src_var.set(d)

    def browse_out(self):
        d = filedialog.askdirectory(initialdir=self.out_var.get())
        if d:
            self.out_var.set(d)

    def toggle_output_dir(self):
        st = "normal" if self.split_var.get() else "disabled"
        self.out_entry.config(state=st)
        self.out_btn.config(state=st)

    def run(self):
        # clear previous output
        self.log.delete(1.0, tk.END)

        src = self.src_var.get()
        list_only = self.list_only_var.get()
        do_split = self.split_var.get()
        outdir = self.out_var.get()

        # run in background
        threading.Thread(
            target=self._do_run,
            args=(src, list_only, do_split, outdir),
            daemon=True
        ).start()

    def _do_run(self, src, list_only, do_split, outdir):
        try:
            if do_split:
                # call your exact split logic
                codedump.split_files(src, outdir)
                # mirror the CLI message
                self._append(f"\nAll files have been split into '{outdir}/'.\n")
            else:
                # call your exact concatenate logic
                result = codedump.concatenate_files(src, list_only)
                self._append(result + "\n")
                # copy to clipboard exactly as before
                try:
                    self.clipboard_clear()
                    self.clipboard_append(result)
                    self._append("[Copied to clipboard]\n")
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _append(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)


if __name__ == "__main__":
    app = CodeDumpGUI()
    app.mainloop()
