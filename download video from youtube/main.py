from tkinter import *
import yt_dlp

def Downloader():
    url = Link.get().strip()
    if not url:
        Label(root, text="Please enter a valid URL", font="arial 12", fg="red").place(x=150, y=210)
        return

    try:
        # إعدادات التنزيل الخاصة بـ yt-dlp
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # تحميل أفضل جودة للفيديو والصوت معًا أو أفضل صيغة متاحة
            'outtmpl': '%(title)s.%(ext)s',  # تسمية ملف التنزيل
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        Label(root, text="Finished Downloading", font="arial 15").place(x=150, y=210)
    
    except Exception as e:
        Label(root, text=f"Error: {e}", font="arial 12", fg="red").place(x=150, y=210)

root = Tk()
root.geometry("500x300")
root.resizable(0, 0)
root.title("YouTube Video Downloader")

Label(root, text="Download YouTube Video", font="arial 20 bold").pack()

Link = StringVar()
Label(root, text="Paste Link", font="arial 15 bold").place(x=200, y=60)
link_enter = Entry(root, width=70, textvariable=Link)
link_enter.place(x=32, y=90)

Button(root, 
       text="Download Video", 
       font="arial 15 bold", 
       bg="pale violet red", 
       padx=2, 
       command=Downloader).place(x=180, y=150)

root.mainloop()
