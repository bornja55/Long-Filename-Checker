import os
import zipfile
import json
from datetime import datetime
from tkinter import Tk, filedialog, messagebox, Button, Label, StringVar, IntVar, Entry, Checkbutton, BooleanVar
from tkinter.ttk import Progressbar

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"length_limit": 200}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def collect_files(folder_path):
    all_files = []
    try:
        for root_dir, dirs, files in os.walk(folder_path):
            for file in files:
                all_files.append(os.path.join(root_dir, file))
    except PermissionError:
        messagebox.showerror("Error", "Permission denied. Please check your folder permissions.")
    return all_files

def save_results(long_filenames, short_filenames, folder_path):
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save long filenames
    long_file_output = os.path.join(folder_path, f"long_filenames_{timestamp}.txt")
    with open(long_file_output, "w", encoding="utf-8") as f:
        for filename in long_filenames:
            f.write(filename + "\n")

    # Save short filenames
    short_file_output = os.path.join(folder_path, f"short_filenames_{timestamp}.txt")
    with open(short_file_output, "w", encoding="utf-8") as f:
        for filename in short_filenames:
            f.write(filename + "\n")

    return long_file_output, short_file_output

def check_long_filenames():
    folder_path = folder_var.get()
    max_length = length_var.get()

    if not folder_path:
        messagebox.showerror("Error", "Please select a folder first!")
        return

    if max_length <= 0:
        messagebox.showerror("Error", "Please enter a valid length greater than 0!")
        return

    progress_bar["value"] = 0
    root.update_idletasks()

    all_files = collect_files(folder_path)
    total_files = len(all_files)
    if total_files == 0:
        messagebox.showinfo("No Files", "No files found in the selected folder.")
        return

    long_filenames = []
    short_filenames = []
    for index, full_path in enumerate(all_files):
        if len(full_path) > max_length:  # Check if the full path exceeds the specified length
            long_filenames.append(full_path)
        else:
            short_filenames.append(full_path)

        # Update progress bar and label
        progress = int((index + 1) / total_files * 100)
        progress_bar["value"] = progress
        progress_label.config(text=f"{index + 1}/{total_files} files checked")
        root.update_idletasks()

    if long_filenames or short_filenames:
        long_file_output, short_file_output = save_results(long_filenames, short_filenames, folder_path)
        if zip_var.get():
            zip_file = os.path.join(folder_path, f"long_filenames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for filename in long_filenames:
                    arcname = os.path.relpath(filename, folder_path)
                    zipf.write(filename, arcname)
            messagebox.showinfo("Success", f"Results saved to:\n{long_file_output}\n{short_file_output}\nFiles zipped to:\n{zip_file}")
        else:
            messagebox.showinfo("Success", f"Results saved to:\n{long_file_output}\n{short_file_output}")
    else:
        messagebox.showinfo("No Long Filenames", f"No filenames longer than {max_length} characters were found.")

    progress_bar["value"] = 0
    progress_label.config(text="0/0 files checked")
    root.update_idletasks()

root = Tk()
root.title("Long Filename Checker")

folder_var = StringVar()
length_var = IntVar()
zip_var = BooleanVar(value=True)

settings = load_settings()
length_var.set(settings["length_limit"])

Label(root, text="Select Folder:").grid(row=0, column=0, padx=10, pady=10)
Button(root, text="Browse", command=browse_folder).grid(row=0, column=2, padx=10, pady=10)
Label(root, textvariable=folder_var, wraplength=400, anchor="w", justify="left").grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Max Filename Length:").grid(row=1, column=0, padx=10, pady=10)
Entry(root, textvariable=length_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")

Label(root, text="Progress:").grid(row=2, column=0, padx=10, pady=10)
progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

progress_label = Label(root, text="0/0 files checked")
progress_label.grid(row=3, column=0, columnspan=3, pady=5)

Checkbutton(root, text="Zip long filenames", variable=zip_var).grid(row=4, column=0, columnspan=3, pady=5)

Button(root, text="Check Long Filenames", command=check_long_filenames).grid(row=5, column=0, columnspan=3, pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings({"length_limit": length_var.get()}), root.destroy()))
root.mainloop()
