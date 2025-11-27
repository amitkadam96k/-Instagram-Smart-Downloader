import instaloader
import threading
import os
import re
import time
import webbrowser  # <--- NEW (needed for GitHub button)
import tkinter as tk
from tkinter import ttk, messagebox
from moviepy.video.io.VideoFileClip import VideoFileClip


# ================= UI COLORS =================
BG="#0d0f1a"; ACCENT="#00e0ff"; TEXT="#d9f7ff"


# ================= HELPERS ======================
def extract_username(link):
    m=re.search(r"instagram\.com/([^/?#&]+)",link)
    return m.group(1) if m else link.strip()


# ===== ONE FOLDER MODE =====
def folders(username):
    base=f"downloads/{username}"
    os.makedirs(base,exist_ok=True)
    return {"root":base}


# ===== DELETE .json/.txt/.xz =====
def clean_meta(path):
    time.sleep(0.4)
    for root,_,files in os.walk(path):
        for f in files:
            if f.endswith((".json",".txt",".xz",".json.xz")):
                try: os.remove(os.path.join(root,f))
                except:
                    time.sleep(0.2)
                    try: os.remove(os.path.join(root,f))
                    except: pass


# ===== MP3 inside same folder =====
def extract_audio(video,out):
    try:
        name=os.path.splitext(os.path.basename(video))[0]+".mp3"
        VideoFileClip(video).audio.write_audiofile(os.path.join(out,name))
    except: pass


# ================= POST/REEL ==================
def download_post(link,progress,status):
    sc=re.search(r"(?:reel|p|tv)/([^/?#]+)",link)
    if not sc: status.config(text="Invalid Link",fg="red"); return

    code=sc.group(1)
    L=instaloader.Instaloader(download_videos=True,download_pictures=True)

    try: post=instaloader.Post.from_shortcode(L.context,code)
    except:
        messagebox.showerror("Error","Post not found"); return

    user=post.owner_username
    p=folders(user); dest=p["root"]

    L.download_post(post,target=dest)
    clean_meta(dest)

    for f in os.listdir(dest):
        if code in f and f.endswith(".mp4"):
            extract_audio(os.path.join(dest,f),dest)

    progress["value"]=100
    status.config(text="Downloaded ✔",fg="#00ff95")
    messagebox.showinfo("Done",f"Saved → downloads/{user}")
    root.after(1500,UI_MAIN)


# ================= FULL PROFILE ==================
def download_profile(link,progress,status):
    username=extract_username(link)
    p=folders(username); dest=p["root"]

    L=instaloader.Instaloader(download_videos=True,download_pictures=True)

    try: profile=instaloader.Profile.from_username(L.context,username)
    except:
        messagebox.showerror("Error","User not found"); return

    posts=list(profile.get_posts())
    total=len(posts)

    for i,post in enumerate(posts,1):
        progress["value"]=(i/total)*100
        status.config(text=f"{i}/{total} downloading...")

        L.download_post(post,target=dest)
        clean_meta(dest)

        if post.is_video:
            for f in os.listdir(dest):
                if post.shortcode in f and f.endswith(".mp4"):
                    extract_audio(os.path.join(dest,f),dest)

    clean_meta(dest)
    status.config(text="Profile Downloaded ✔",fg="#00ff95")
    messagebox.showinfo("Done",f"Saved → downloads/{username}")
    root.after(2000,UI_MAIN)


# ================= GUI ==================
root=tk.Tk()
root.title("Instagram Downloader – Single Folder Mode")
root.geometry("520x520")
root.config(bg=BG)

tk.Label(root,text="Instagram Downloader",fg=ACCENT,bg=BG,
         font=("Segoe UI",18,"bold")).pack(pady=15)

progress=ttk.Progressbar(root,length=350,mode="determinate")
status=tk.Label(root,text="Ready",bg=BG,fg="#8aa6b3",font=("Segoe UI",11))
screen=tk.Frame(root,bg=BG); screen.pack()


def load_ui(f):
    for w in screen.winfo_children(): w.destroy()
    f()


# ================= PROFILE UI ==================
def UI_PROFILE():
    load_ui(lambda:None)
    tk.Label(screen,text="Enter Profile Link:",bg=BG,fg=TEXT,font=("Segoe UI",13)).pack(pady=7)

    e=tk.Entry(screen,width=38,bg="#11182d",fg=TEXT,font=("Segoe UI",12))
    e.insert(0,"https://instagram.com/username")
    e.pack(pady=5)

    progress.pack(pady=15); status.pack()

    tk.Button(screen,text="DOWNLOAD FULL PROFILE",bg=ACCENT,fg="black",
              font=("Segoe UI",12,"bold"),
              command=lambda:threading.Thread(
                  target=download_profile,args=(e.get(),progress,status),daemon=True
              ).start()).pack(pady=10)


# ================= POST UI ==================
def UI_POST():
    load_ui(lambda:None)
    tk.Label(screen,text="Paste Reel/Post Link:",bg=BG,fg=TEXT,font=("Segoe UI",13)).pack(pady=7)

    e=tk.Entry(screen,width=38,bg="#11182d",fg=TEXT,font=("Segoe UI",12))
    e.insert(0,"add link")
    e.pack(pady=5)

    progress.pack(pady=15); status.pack()

    tk.Button(screen,text="DOWNLOAD POST/REEL",bg=ACCENT,fg="black",
              font=("Segoe UI",12,"bold"),
              command=lambda:threading.Thread(
                  target=download_post,args=(e.get(),progress,status),daemon=True
              ).start()).pack(pady=10)


# ================= MAIN MENU + GITHUB BUTTON ==================
def UI_MAIN():
    load_ui(lambda:None)
    tk.Label(screen,text="What do you want to download?",
             fg=ACCENT,bg=BG,font=("Segoe UI",15,"bold")).pack(pady=15)

    tk.Button(screen,text="FULL PROFILE",width=22,bg="#00b4cc",fg="black",
              font=("Segoe UI",12,"bold"),command=UI_PROFILE).pack(pady=8)

    tk.Button(screen,text="REEL / POST",width=22,bg="#00ff95",fg="black",
              font=("Segoe UI",12,"bold"),command=UI_POST).pack(pady=8)

    # -------------- GitHub Follow Button --------------
    tk.Button(screen,text="⭐ Follow me on GitHub ⭐",width=22,bg="#222",fg="#00e0ff",
              font=("Segoe UI",11,"bold"),
              command=lambda:webbrowser.open("https://github.com/amitkadam96k")).pack(pady=25)


UI_MAIN()
root.mainloop()
