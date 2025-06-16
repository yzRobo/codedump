#!/usr/bin/env python3
"""
codedump_gui.py – Tk front-end for codedump.py

Changes (2025-06-16)
────────────────────────────────────────────────────────────
• Output-directory entry & Browse… button are always active.
• Concatenate mode now also writes the full output to a text file inside
  the selected output directory.  File name example:
      code_dump_20250616_161530.txt
"""
import os
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import codedump  # codedump.py must be importable


class CodeDumpGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CodeDump GUI")
        self.geometry("760x520")

        # ─── Source directory ────────────────────────────────────────────────
        tk.Label(self, text="Source Directory:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.src_var = tk.StringVar(value=os.getcwd())
        tk.Entry(self, textvariable=self.src_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(self, text="Browse…", command=self.browse_src).grid(row=0, column=2)

        # ─── Options ─────────────────────────────────────────────────────────
        self.list_only_var = tk.BooleanVar()
        tk.Checkbutton(
            self, text="List only", variable=self.list_only_var
        ).grid(row=1, column=1, sticky="w", padx=5)

        self.split_var = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="Split files",
            variable=self.split_var,
            command=self.toggle_flatten_state,
        ).grid(row=2, column=1, sticky="w", padx=5)

        self.flatten_var = tk.BooleanVar()
        self.flatten_chk = tk.Checkbutton(
            self,
            text="Flatten output (no sub-folders)",
            variable=self.flatten_var,
            state="disabled",
        )
        self.flatten_chk.grid(row=3, column=1, sticky="w", padx=25)

        # ─── Output directory (always enabled) ───────────────────────────────
        tk.Label(self, text="Output Directory:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.out_var = tk.StringVar(
            value=os.path.join(os.getcwd(), "extracted")
        )
        self.out_entry = tk.Entry(self, textvariable=self.out_var, width=60)
        self.out_entry.grid(row=4, column=1, padx=5)
        tk.Button(self, text="Browse…", command=self.browse_out).grid(row=4, column=2)

        # ─── Run button ──────────────────────────────────────────────────────
        tk.Button(self, text="Run", command=self.run).grid(row=5, column=1, pady=10)

        # ─── Log area ────────────────────────────────────────────────────────
        self.log = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # ─── Helper UI callbacks ────────────────────────────────────────────────
    def browse_src(self):
        d = filedialog.askdirectory(initialdir=self.src_var.get())
        if d:
            self.src_var.set(d)

    def browse_out(self):
        d = filedialog.askdirectory(initialdir=self.out_var.get())
        if d:
            self.out_var.set(d)

    def toggle_flatten_state(self):
        """Enable/disable the Flatten checkbox based on Split option."""
        self.flatten_chk.config(
            state=("normal" if self.split_var.get() else "disabled")
        )

    # ─── Threaded run logic ─────────────────────────────────────────────────
    def run(self):
        self.log.delete(1.0, tk.END)  # clear log
        threading.Thread(
            target=self._do_run,
            args=(
                self.src_var.get(),
                self.list_only_var.get(),
                self.split_var.get(),
                self.out_var.get(),
                self.flatten_var.get(),
            ),
            daemon=True,
        ).start()

    def _do_run(self, src, list_only, do_split, outdir, flatten):
        try:
            if do_split:
                codedump.split_files(src, outdir, flatten=flatten)
                msg = f"\nAll files have been split into '{outdir}/'."
                if flatten:
                    msg += " (flattened)"
                self._append(msg + "\n")
            else:
                result = codedump.concatenate_files(src, list_only)
                self._append(result + "\n")

                # ─ Save to TXT file ─────────────────────────────────────────
                os.makedirs(outdir, exist_ok=True)
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"code_dump_{ts}.txt"
                fpath = os.path.join(outdir, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(result)
                self._append(f"[Saved to {fpath}]\n")

                # ─ Copy to clipboard ───────────────────────────────────────
                try:
                    self.clipboard_clear()
                    self.clipboard_append(result)
                    self._append("[Copied to clipboard]\n")
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ─── Convenience ────────────────────────────────────────────────────────
    def _append(self, text: str):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)


if __name__ == "__main__":
    CodeDumpGUI().mainloop()
