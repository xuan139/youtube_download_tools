import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import yt_dlp
import threading
from threading import Thread, BoundedSemaphore
import time
import os
import subprocess
from datetime import datetime
import concurrent.futures
import common_functions
from threading import BoundedSemaphore

maxconnections = 2
# Initialize the semaphore
pool_sema = BoundedSemaphore(value=maxconnections)

current_time = datetime.now()
file_name = 'playlist'

def sort_column(col_name, reverse):
    populate_download_listbox()
    data = [(download_listbox.set(child, col_name), child) for child in download_listbox.get_children('')]
    data.sort(reverse=reverse)
    for i, item in enumerate(data):
        download_listbox.move(item[1], '', i)
    download_listbox.heading(col_name, command=lambda: sort_column(col_name, not reverse))
    

def on_item_selected(event):
    # populate_download_listbox()
    selected_item = download_listbox.selection()
    
    if selected_item:
        item = download_listbox.item(selected_item, "values")
        filename = item[0]  # Assuming the filename is in the first column
        
        print('video is ',filename)
        if filename:
            if filename.endswith(".webm") or filename.endswith(".mp4") or filename.endswith(".avi"):
                 subprocess.Popen(['open',  os.path.join(common_functions.get_default_downloads_directory(), "video_download")])

            elif filename.endswith(".vtt"):
                # 读取并显示 vtt 文件内容
                try:
                    with open(filename, 'r', encoding='utf-8') as vtt_file:
                        vtt_content = vtt_file.read()
                    common_functions.show_text_content(vtt_content)

                except FileNotFoundError:
                    simpledialog.messagebox.showinfo("File Not Found", f"File {filename} not found.")
                    subprocess.Popen(['open',  os.path.join(common_functions.get_default_downloads_directory(), "video_download")])

            else:

                subprocess.Popen(['open',  os.path.join(common_functions.get_default_downloads_directory(), "video_download")])
                populate_download_listbox()


def populate_download_listbox():
    download_directory = os.path.join(common_functions.get_default_downloads_directory(), "video_download")
    print('default dir ',download_directory)
    download_listbox.delete(*download_listbox.get_children())

    if os.path.exists(download_directory) and os.path.isdir(download_directory):
        files = os.listdir(download_directory)

        for filename in files:
            full_path = os.path.join(download_directory, filename)
            if os.path.isfile(full_path):
                # Get the creation time of the file
                ctime = os.path.getctime(full_path)
                create_time = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
                # Display the filename and create time in the download_listbox
                download_listbox.insert("", "end", values=(full_path, "Downloaded", create_time,common_functions.get_file_size(full_path)))

def update_info(info):
    download_percentage_label.config(text=info)
    root.update()
 
def download_video():
    url = url_entry.get()
    if common_functions.is_youtube_playlist(url):
        update_info("Getting playlist ...")
        download_playlist()
    elif common_functions.is_youtube_video(url):
        update_info("Getting batchlist ...")
        download_batch_videos()
    else:
        update_info("It's neither a playlist nor a video")

def download_batch_videos():
    print("It's a YouTube video.")
    update_info("It's a YouTube video")
    video_urls = url_entry.get()
    video_url_list = video_urls.split(',')
    # Create threads for each URL
    for video_url in video_url_list:
        video_thread = threading.Thread(target=download_video_thread, args=(video_url,))
        video_thread.start()


def download_playlist():
    playlist_url = url_entry.get()

    ydl_opts = {
        # 'quiet': True,  # Disable verbose output
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)

        if 'entries' in playlist_info:
            for entry in playlist_info['entries']:
                video_url = None
                if 'url' in entry:
                    video_url = entry['url']
                elif 'url_simple' in entry:
                    video_url = entry['url_simple']
                elif 'webpage_url' in entry:
                    video_url = entry['webpage_url']
                elif 'ie_key' in entry:
                    video_url = 'https://www.youtube.com/watch?v=' + entry['ie_key']
                
                if video_url:
                    # Get the current timestamp

                    # Format the timestamp as a string to use as the file name

                    # Open the file in write mode, creating it if it doesn't exist
                    # new_row = download_listbox.insert("", "end", values=(video_url, "0%", "Createtime", "Size"))
                    # print("Playable Video URL:", new_row + video_url)

                    video_thread = threading.Thread(target=download_video_thread, args=(video_url,))
                    video_thread.start()

                else:
                    print("No URL found for an entry in the playlist.")

        else:
            print("No video entries found in the playlist.")
        update_info("Begin download ...")


def download_video_thread(video_url):
    # with pool_sema:
    try:
        video_format = format_var.get()  # Get the selected video format
        print('video_format',video_format)
        downloads_dir = common_functions.get_default_downloads_directory()
        output_directory = os.path.join(downloads_dir, "video_download")
        new_row = download_listbox.insert("", "end", values=(video_url, "0%", "Createtime", "Size"))
        print('row is ',new_row)

        format_options = f"best[height<={video_format}][ext=mp4]/best[ext=mp4]"
            #  format_options = f"best[height<={video_format}][ext=mp4]/best[ext=mp4]"
        if video_format == 'MP3':
            format_options = "bestaudio[ext=mp3]/bestaudio"

        ydl_opts = {
            "progress_hooks": [lambda progress_dict: update_progress(new_row, progress_dict)],
            "format": format_options,
            'writesubtitles': True,
            'allsubtitles': True,
            'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print('downloading')
            ydl.download([video_url])
    except:
        print()


# Function to update the Progress column for a specific row
def update_progress(row_id,progress_dict):

    downloads_directory = common_functions.get_default_downloads_directory()  # Call the function to get the directory path
    full_path = os.path.join(downloads_directory, progress_dict['filename'])
    if progress_dict['status'] == 'finished':
        print()

    elif progress_dict['status'] == 'error':
        update_info("get error")

    else:
        try:
            total_bytes = progress_dict.get("total_bytes", 0)
            downloaded_bytes = progress_dict.get("downloaded_bytes", 0)
            if total_bytes is not None and total_bytes > 0:
                download_percentage = (downloaded_bytes / total_bytes) * 100
            else:
                download_percentage = 0

            download_listbox.item(row_id, values=(full_path, f"{download_percentage:.2f}%", "", ""))
            root.update_idletasks()
        except:
            print()
root = tk.Tk()
root.title("Video Download with Subtitles")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the window width and height
window_width = (5 * screen_width) // 6
window_height = (4 * screen_height) // 8

# Calculate the window's X and Y coordinates to position it in the bottom right corner
window_x = screen_width - window_width
window_y = screen_height - window_height-300

# Set the window's size and position
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")


# Create the frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Configure row and column weights for the frame
frame.grid_rowconfigure(0, weight=1)
# frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(0, weight=0)
frame.grid_columnconfigure(1, weight=12)
frame.grid_columnconfigure(2, weight=0)

url_label = tk.Label(frame, text="Video URL:")
url_label.grid(row=0, column=0, sticky="w", padx=2, pady=5)

url_entry = tk.Entry(frame)
url_entry.grid(row=0, column=1, sticky="ew", padx=2, pady=5)

download_button = tk.Button(frame, text="Download", command=download_video)
download_button.grid(row=0, column=2, sticky="e", padx=2, pady=5)

download_percentage_label = tk.Label(frame, text="info")
download_percentage_label.grid(row=1, columnspan=3,padx=5)


video_formats = ["480", "720","MP3"]
format_var = tk.StringVar()
format_var.set(video_formats[0])  # Set the default format

format_menu = ttk.OptionMenu(frame, format_var, video_formats[0], *video_formats)
format_menu.grid(row=1, column=1, padx=2, pady=5, sticky="w")


# Create a downframe below the frame
downframe = tk.Frame(root)
downframe.pack(padx=10, pady=10, fill="both", expand=True)



# Create the download_listbox
columns = ("Filename", "Progress", "Createtime", "Size")
download_listbox = ttk.Treeview(root, columns=columns, show="headings")
download_listbox.pack(padx=10, pady=10,fill="both", expand=True)
download_listbox.heading("Filename", text="Filename", command=lambda: sort_column("Filename", False))
download_listbox.heading("Progress", text="Progress")
download_listbox.heading("Createtime", text="Createtime", command=lambda: sort_column("Createtime", False))
download_listbox.heading("Size", text="Size", command=lambda: sort_column("Size", False))


# Set the width of the "Filename" column to 80% of the available space
# Update the window and calculate available width
root.update()
available_width = download_listbox.winfo_width()

# Set the width of the "Filename" column to 80% of the available space
download_listbox.column("Filename", width=int(available_width * 0.8))

# Bind the event handler to the download_listbox
download_listbox.bind("<Double-1>", on_item_selected)


donate_button = tk.Button(root, text="Donate", command=common_functions.show_donate_info)
donate_button.pack()
populate_download_listbox()
# Start the main loop
root.mainloop()

# https://www.youtube.com/watch?v=sLcoDLMVuBo&list=RDCMUCUW8CA9dN_y4SBU7I5txLsw&start_radio=1&rv=sLcoDLMVuBo

# In this code, we configure the row and column weights for the frame, which allows the widgets to expand and occupy the desired proportions of the frame. The sticky option is set to "ew" for the url_entry and "e" for the download_button to control the widget's placement and alignment.


# https://www.youtube.com/watch?v=sLcoDLMVuBo&list=RDCMUCUW8CA9dN_y4SBU7I5txLsw&start_radio=1&rv=sLcoDLMVuBo

# https://www.youtube.com/watch?v=ggGn8vgUbRw&list=RDCMUCDcugUbgNSHT0QQOkKeBGfw&start_radio=1&rv=ggGn8vgUbRw

# https://www.youtube.com/watch?v=c6RXqPDJdis&list=RDCMUCz4tgANd4yy8Oe0iXCdSWfA&start_radio=1&rv=c6RXqPDJdis

