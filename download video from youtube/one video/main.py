from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import yt_dlp
import threading
import os

def fetch_formats(url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            all_formats = []
            if 'entries' in info:
                for entry in info['entries']:
                    formats = entry.get('formats', [])
                    if not all_formats:
                        all_formats = formats
                    else:
                        all_formats = [fmt for fmt in all_formats if fmt in formats]
            else:
                all_formats = info.get('formats', [])
            return all_formats
    except Exception as e:
        error_label.config(text=f"Error: {e}")
        return []

def update_formats(*args):
    url = Link.get().strip()
    if not url:
        error_label.config(text="Please enter a valid URL")
        return
    formats = fetch_formats(url)
    quality_var.set('')
    quality_menu['menu'].delete(0, 'end')
    extension_var.set('mp4')
    extension_menu['menu'].delete(0, 'end')
    extensions = set()
    quality_dict = {}
    if formats:
        for f in formats:
            ext = f['ext']
            format_note = f.get('format_note', None)
            if format_note:
                format_note = f"{format_note} ({ext})"
                format_id = f['format_id']
                extensions.add(ext)
                if ext not in quality_dict:
                    quality_dict[ext] = []
                if (format_note, format_id) not in quality_dict[ext]:
                    quality_dict[ext].append((format_note, format_id))
        for ext in extensions:
            extension_menu['menu'].add_command(label=ext, command=lambda e=ext: update_quality_menu(e, quality_dict))
        error_label.config(text="")
    else:
        error_label.config(text="No available formats")

def update_quality_menu(selected_ext, quality_dict):
    quality_var.set('')
    quality_menu['menu'].delete(0, 'end')
    if selected_ext in quality_dict:
        for quality, format_id in quality_dict[selected_ext]:
            quality_menu['menu'].add_command(label=quality, command=lambda q=format_id: quality_var.set(q))
        error_label.config(text="")
    else:
        error_label.config(text="No available qualities for the selected extension")

def update_progress(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str'].strip()
        progress_label.config(text=f"Download Progress: {percent}")
        progress_bar['value'] = d['_percent_str'].strip('%')
        progress_bar.update()

def Downloader():
    url = Link.get().strip()
    selected_format = quality_var.get()
    file_extension = extension_var.get()
    output_dir = output_directory.get()
    if not url:
        error_label.config(text="Please enter a valid URL")
        return
    if not selected_format:
        error_label.config(text="Please select a quality")
        return
    if not file_extension:
        error_label.config(text="Please select a file extension")
        return
    if not output_dir:
        error_label.config(text="Please select an output directory")
        return
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            playlist_title = info.get('title', 'Playlist')
            playlist_dir = os.path.join(output_dir, playlist_title)
            if not os.path.exists(playlist_dir):
                os.makedirs(playlist_dir)
            ydl_opts = {
                'format': selected_format,
                'outtmpl': f"{playlist_dir}/%(playlist_index)03d_%(title)s.%(ext)s",
                'merge_output_format': file_extension,
                'progress_hooks': [update_progress],
                'noplaylist': False,
                'yes_playlist': True
            }
            ydl.download([url])
            error_label.config(text="Finished Downloading", fg="green")
    except Exception as e:
        error_label.config(text=f"Error: {e}", fg="red")

def start_download_thread():
    threading.Thread(target=Downloader).start()

def select_output_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_directory.set(directory)

# Main application window
root = Tk()
root.geometry("600x650")
root.resizable(0, 0)
root.title("YouTube Video Downloader")
root.config(bg="#f0f0f0")

# Main frame
main_frame = Frame(root, bg="#f0f0f0", bd=2, relief=SOLID)
main_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

# Header
header_frame = Frame(main_frame, bg="#4CAF50", bd=2, relief=RIDGE)
header_frame.pack(fill=X)
Label(header_frame, text="Download YouTube Video", font="Helvetica 20 bold", bg="#4CAF50", fg="white").pack(pady=10)

# Content frame
content_frame = Frame(main_frame, bg="#f0f0f0")
content_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

# URL Entry
Label(content_frame, text="Paste Link:", font="Helvetica 12 bold", bg="#f0f0f0", fg="#555555").pack(anchor="w")
Link = StringVar()
Link.trace_add("write", update_formats)
link_entry = Entry(content_frame, width=55, textvariable=Link, font="Helvetica 10", bd=2, relief=SUNKEN)
link_entry.pack(pady=5)

# Quality selection
Label(content_frame, text="Select Quality:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")
quality_var = StringVar()
quality_menu = OptionMenu(content_frame, quality_var, '')
quality_menu.config(width=20, font="Helvetica 10")
quality_menu.pack(pady=5)

# File extension selection
Label(content_frame, text="Select File Extension:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")
extension_var = StringVar(value="mp4")
extension_menu = OptionMenu(content_frame, extension_var, "mp4", "mkv", "webm")
extension_menu.config(width=10, font="Helvetica 10")
extension_menu.pack(pady=5)

# Output directory selection
Label(content_frame, text="Select Output Directory:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")
output_directory = StringVar()
output_dir_entry = Entry(content_frame, textvariable=output_directory, font="Helvetica 10", state='readonly')
output_dir_entry.pack(pady=5)
Button(content_frame, text="Browse", command=select_output_directory, font="Helvetica 10").pack(pady=5)

# Error label
error_label = Label(content_frame, text="", font="Helvetica 10", fg="red", bg="#f0f0f0")
error_label.pack(pady=5)

# Progress label
progress_label = Label(content_frame, text="Download Progress: 0%", font="Helvetica 12", bg="#f0f0f0", fg="blue")
progress_label.pack(pady=5)

# Progress bar
progress_bar = ttk.Progressbar(content_frame, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Download button
Button(content_frame, text="Download Video", font="Helvetica 14 bold", bg="#4CAF50", fg="white", command=start_download_thread).pack(pady=20)

root.mainloop()
