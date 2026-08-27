#!/usr/bin/env python3
"""
st_mod_manager_gui.py – Tkinter GUI for Stardew Valley mod manager.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the core module
sys.path.insert(0, str(Path(__file__).parent))
from st_mod_manager_core import (
    create_profile, install_mod, check_profile, use_profile,
    list_profiles, list_mods, remove_mod, default_steam_dir
)

class StardewModManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stardew Valley Mod Manager")
        self.root.geometry("800x600")

        self.game_dir = default_steam_dir()

        self.create_widgets()

    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Profiles Tab
        self.profiles_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profiles_tab, text="Profiles")

        self.setup_profiles_tab()

        # Mods Tab
        self.mods_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mods_tab, text="Mods")

        self.setup_mods_tab()

        # Check Tab
        self.check_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.check_tab, text="Check")

        self.setup_check_tab()

        # Use Profile Tab
        self.use_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.use_tab, text="Use Profile")

        self.setup_use_tab()

    def setup_profiles_tab(self):
        # Create Profile
        ttk.Label(self.profiles_tab, text="Create New Profile:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_name_entry = ttk.Entry(self.profiles_tab)
        self.profile_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.profiles_tab, text="Create", command=self.create_profile_gui).grid(row=0, column=2, padx=5, pady=5)

        # List Profiles
        ttk.Label(self.profiles_tab, text="Existing Profiles:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.profiles_listbox = tk.Listbox(self.profiles_tab)
        self.profiles_listbox.grid(row=2, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.profiles_tab, text="Refresh", command=self.refresh_profiles_list).grid(row=3, column=0, padx=5, pady=5)

        # Configure grid
        self.profiles_tab.columnconfigure(1, weight=1)

        self.refresh_profiles_list()

    def setup_mods_tab(self):
        # Profile Selection
        ttk.Label(self.mods_tab, text="Select Profile:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.mods_profile_combobox = ttk.Combobox(self.mods_tab)
        self.mods_profile_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # Install Mod
        ttk.Label(self.mods_tab, text="Install Mod:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mod_path_entry = ttk.Entry(self.mods_tab)
        self.mod_path_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.mods_tab, text="Browse", command=self.browse_mod).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.mods_tab, text="Install", command=self.install_mod_gui).grid(row=2, column=0, columnspan=3, pady=5)

        # List Mods
        ttk.Label(self.mods_tab, text="Installed Mods:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.mods_listbox = tk.Listbox(self.mods_tab)
        self.mods_listbox.grid(row=4, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        # Remove Mod
        ttk.Label(self.mods_tab, text="Remove Mod:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.remove_mod_entry = ttk.Entry(self.mods_tab)
        self.remove_mod_entry.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.mods_tab, text="Remove", command=self.remove_mod_gui).grid(row=5, column=2, padx=5, pady=5)

        # Configure grid
        self.mods_tab.columnconfigure(1, weight=1)

        self.refresh_profiles_combobox()
        self.mods_profile_combobox.bind("<<ComboboxSelected>>", self.on_profile_select)

    def setup_check_tab(self):
        ttk.Label(self.check_tab, text="Select Profile to Check:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.check_profile_combobox = ttk.Combobox(self.check_tab)
        self.check_profile_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.check_tab, text="Check", command=self.check_profile_gui).grid(row=0, column=2, padx=5, pady=5)

        self.check_output = scrolledtext.ScrolledText(self.check_tab, wrap=tk.WORD, width=80, height=20)
        self.check_output.grid(row=1, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.check_tab.columnconfigure(1, weight=1)
        self.refresh_profiles_combobox_check()

    def setup_use_tab(self):
        ttk.Label(self.use_tab, text="Select Profile to Use:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.use_profile_combobox = ttk.Combobox(self.use_tab)
        self.use_profile_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(self.use_tab, text="Use Profile", command=self.use_profile_gui).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.use_tab, text="Game Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.game_dir_entry = ttk.Entry(self.use_tab)
        self.game_dir_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.game_dir_entry.insert(0, str(default_steam_dir()))
        ttk.Button(self.use_tab, text="Browse", command=self.browse_game_dir).grid(row=1, column=2, padx=5, pady=5)

        self.use_output = scrolledtext.ScrolledText(self.use_tab, wrap=tk.WORD, width=80, height=10)
        self.use_output.grid(row=2, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.use_tab.columnconfigure(1, weight=1)
        self.refresh_profiles_combobox_use()

    # --- GUI Actions ---

    def refresh_profiles_list(self):
        self.profiles_listbox.delete(0, tk.END)
        profiles = list_profiles()
        if profiles.startswith("📂 Existing profiles:"):
            for profile in profiles.split("\n")[1:]:
                if profile.strip().startswith("-"):
                    self.profiles_listbox.insert(tk.END, profile.strip()[2:])

    def refresh_profiles_combobox(self):
        profiles = list_profiles()
        if profiles.startswith("📂 Existing profiles:"):
            profile_list = [p.strip()[2:] for p in profiles.split("\n")[1:] if p.strip().startswith("-")]
            self.mods_profile_combobox["values"] = profile_list

    def refresh_profiles_combobox_check(self):
        profiles = list_profiles()
        if profiles.startswith("📂 Existing profiles:"):
            profile_list = [p.strip()[2:] for p in profiles.split("\n")[1:] if p.strip().startswith("-")]
            self.check_profile_combobox["values"] = profile_list

    def refresh_profiles_combobox_use(self):
        profiles = list_profiles()
        if profiles.startswith("📂 Existing profiles:"):
            profile_list = [p.strip()[2:] for p in profiles.split("\n")[1:] if p.strip().startswith("-")]
            self.use_profile_combobox["values"] = profile_list

    def on_profile_select(self, event):
        profile = self.mods_profile_combobox.get()
        mods = list_mods(profile)
        self.mods_listbox.delete(0, tk.END)
        if mods.startswith("📦 Mods installed in profile"):
            for line in mods.split("\n")[1:]:
                if line.strip().startswith("*"):
                    self.mods_listbox.insert(tk.END, line.strip()[2:])

    def browse_mod(self):
        path = filedialog.askopenfilename(title="Select Mod File", filetypes=[("Zip Files", "*.zip"), ("All Files", "*.*")])
        if path:
            self.mod_path_entry.delete(0, tk.END)
            self.mod_path_entry.insert(0, path)

    def browse_game_dir(self):
        path = filedialog.askdirectory(title="Select Stardew Valley Directory")
        if path:
            self.game_dir_entry.delete(0, tk.END)
            self.game_dir_entry.insert(0, path)

    def create_profile_gui(self):
        name = self.profile_name_entry.get()
        if not name:
            messagebox.showerror("Error", "Please enter a profile name.")
            return
        result = create_profile(name)
        messagebox.showinfo("Info", result)
        self.refresh_profiles_list()
        self.refresh_profiles_combobox()
        self.refresh_profiles_combobox_check()
        self.refresh_profiles_combobox_use()
        self.profile_name_entry.delete(0, tk.END)

    def install_mod_gui(self):
        profile = self.mods_profile_combobox.get()
        mod_path = self.mod_path_entry.get()
        if not profile or not mod_path:
            messagebox.showerror("Error", "Please select a profile and a mod path.")
            return
        result = install_mod(profile, mod_path)
        messagebox.showinfo("Info", result)
        self.on_profile_select(None)

    def remove_mod_gui(self):
        profile = self.mods_profile_combobox.get()
        mod_name = self.remove_mod_entry.get()
        if not profile:
            messagebox.showerror("Error", "Please select a profile.")
            return
        result = remove_mod(profile, mod_name)
        messagebox.showinfo("Info", result)
        self.on_profile_select(None)
        self.remove_mod_entry.delete(0, tk.END)

    def check_profile_gui(self):
        profile = self.check_profile_combobox.get()
        if not profile:
            messagebox.showerror("Error", "Please select a profile.")
            return
        result = check_profile(profile)
        self.check_output.delete(1.0, tk.END)
        self.check_output.insert(tk.END, result)

    def use_profile_gui(self):
        profile = self.use_profile_combobox.get()
        game_dir = self.game_dir_entry.get()
        if not profile:
            messagebox.showerror("Error", "Please select a profile.")
            return
        result = use_profile(profile, Path(game_dir))
        self.use_output.delete(1.0, tk.END)
        self.use_output.insert(tk.END, result)

def main():
    root = tk.Tk()
    app = StardewModManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
