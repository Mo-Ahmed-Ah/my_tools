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
                # Iterate through all entries to get available formats
                for entry in info['entries']:
                    formats = entry.get('formats', [])
                    if not all_formats:
                        all_formats = formats
                    else:
                        # Keep only formats that are common in all videos
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
            format_note = f.get('format_note', None) # Check if format_note is available
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
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                available_formats = info.get('formats', [])
                # Find the best matching format
                if selected_format not in [fmt['format_id'] for fmt in available_formats]:
                    available_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
                    best_format = available_formats[0] if available_formats else None
                    ydl_opts['format'] = best_format['format_id'] if best_format else 'best'
                else:
                    ydl_opts['format'] = selected_format
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

def clear_input():
    Link.set("")

root = Tk()
root.geometry("600x650")
root.resizable(0, 0)
root.title("YouTube Playlist Downloader")

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10), padding=10, background="#4CAF50", foreground="white")
style.map('TButton', background=[('active', '#45a049')])
style.configure('TLabel', font=('Helvetica', 12), padding=5)
style.configure('TEntry', font=('Helvetica', 10))

main_frame = Frame(root, bg="#f0f0f0", bd=2, relief=SOLID)
main_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

header_frame = Frame(main_frame, bg="#5f9ea0", bd=2, relief=RIDGE)
header_frame.pack(fill=X)
Label(header_frame, text="Download YouTube Playlist", font="Helvetica 20 bold", bg="#5f9ea0", fg="white").pack(pady=10)

content_frame = Frame(main_frame, bg="#f0f0f0")
content_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

Label(content_frame, text="Paste Link:", font="Helvetica 12 bold", bg="#f0f0f0", fg="#555555").pack(anchor="w")
Link = StringVar()
Link.trace_add("write", update_formats)
link_entry = Entry(content_frame, width=55, textvariable=Link, font="Helvetica 10", bd=2, relief=SUNKEN)
link_entry.pack(pady=5)

Label(content_frame, text="Select quality:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")
quality_var = StringVar()
quality_menu = ttk.OptionMenu(content_frame, quality_var, '', style='TMenubutton')
quality_menu.config(width=20)
quality_menu.pack(pady=5)

Label(content_frame, text="Select file extension:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")
extension_var = StringVar(value="mp4")
extension_menu = ttk.OptionMenu(content_frame, extension_var, "mp4", "mkv", "webm", style='TMenubutton')
extension_menu.config(width=10)
extension_menu.pack(pady=5)

Label(content_frame, text="Select Output Directory:", font="Helvetica 12", bg="#f0f0f0", fg="#555555").pack(anchor="w")

# تغيير من Entry إلى Label لعرض مسار التحميل
output_directory = StringVar()
output_dir_label = Label(content_frame, textvariable=output_directory, font="Helvetica 10", bg="#f0f0f0", bd=2, relief=SUNKEN, width=55)
output_dir_label.pack(pady=5)

# تعديل الزر ليقوم باختيار الدليل
ttk.Button(content_frame, text="Browse", command=select_output_directory).pack(pady=5)

ttk.Button(content_frame, text="Clear", command=clear_input).pack(pady=5)

error_label = Label(content_frame, text="", font="Helvetica 10", fg="red", bg="#f0f0f0")
error_label.pack(pady=5)

progress_label = Label(content_frame, text="Download Progress: 0%", font="Helvetica 12", bg="#f0f0f0", fg="#5f9ea0")
progress_label.pack(pady=5)
progress_bar = ttk.Progressbar(content_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

ttk.Button(content_frame, text="Download Playlist", command=start_download_thread).pack(pady=20)

root.mainloop()
