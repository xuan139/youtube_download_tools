import tkinter as tk
from tkinter import ttk
import yt_dlp
import threading
import os
import subprocess
from datetime import datetime
import common_functions
import re
import shutil

# author lixuan2001@gmail.com

def sort_column(col_name, reverse):
    try:
        populate_download_listbox()
        data = [(download_listbox.set(child, col_name), child) for child in download_listbox.get_children('')]
        data.sort(reverse=reverse)
        for i, item in enumerate(data):
            download_listbox.move(item[1], '', i)
        download_listbox.heading(col_name, command=lambda: sort_column(col_name, not reverse))
    except:
        update_info('Some error happened')
    

def on_item_selected(event):
    try:
        selected_item = download_listbox.selection()
        if selected_item:
            item = download_listbox.item(selected_item, "values")
            filename = item[0]
            
            if filename:
                show_popup(filename)       
    except:
        update_info('Some error happened')
         


def populate_download_listbox():
    try:
        download_directory = common_functions.get_default_downloads_directory()
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
    except:
        update_info('Some error happened')

def update_info(info):
    download_percentage_label.config(text=info)
    root.update()
 
def download_video():
    try:
        url = url_entry.get()
        if common_functions.is_youtube_playlist(url):
            update_info("Getting playlist ...")
            download_playlist()
        elif common_functions.is_youtube_video(url):
            update_info("Getting video ...")
            download_batch_videos()
        else:
            update_info("It's neither a playlist nor a video")
    except:
        update_info('Some error happened at download_video')

def download_batch_videos():
    print("It's a YouTube video.")
    update_info("It's a YouTube video")
    try:
        video_urls = url_entry.get()
        video_url_list = video_urls.split(',')
        # Create threads for each URL
        for video_url in video_url_list:
            video_thread = threading.Thread(target=download_video_thread, args=(video_url,))
            video_thread.start()
    except:
        update_info('Some error happened at download_video')



def download_playlist():
    try:
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
                        video_thread = threading.Thread(target=download_video_thread, args=(video_url,))
                        video_thread.start()

                    else:
                        print("No URL found for an entry in the playlist.")

            else:
                print("No video entries found in the playlist.")
            update_info("Begin download ...")
            
    except:
        update_info("error happened ...")       


def download_video_thread(video_url):
    # with pool_sema:
    try:
        video_format = format_var.get()  # Get the selected video format
        # print('video_format',video_format)
        output_directory = common_functions.get_default_downloads_directory()
        # print('output_directory',output_directory)
        new_row = download_listbox.insert("", "0", values=(video_url, "0%", "Createtime", "Size",video_url))
        # print('row is ',new_row)

        format_options = f"best[height<={video_format}][ext=mp4]/best[ext=mp4]"
            #  format_options = f"best[height<={video_format}][ext=mp4]/best[ext=mp4]"
        if video_format == 'Audio':
            # format_options = "bestaudio[ext=mp3]/bestaudio"
            format_options = "bestaudio[ext=m4a]/bestaudio"

        elif video_format == 'Best':

            format_options = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        # update_info(video_format + ',' + output_directory + ',' + format_options)

        ydl_opts = {
            "progress_hooks": [lambda progress_dict: update_progress(new_row, progress_dict)],
            "format": format_options,
            'writesubtitles': True,
            'allsubtitles': True,
            'writethumbnail': True ,
            # 'writesubtitles': 'en,zh',  # 明确指定英语（en）和中文（zh）字幕
            'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print('downloading')
            ydl.download([video_url])
            
    except:
        print()


# Function to update the Progress column for a specific row
def update_progress(row_id,progress_dict):

    downloads_directory = common_functions.get_default_directory()  # Call the function to get the directory path
    full_path = os.path.join(downloads_directory, progress_dict['filename'])

    print("full_path is " ,full_path)
    if progress_dict['status'] == 'finished':
        update_info("finished")
        ctime = os.path.getctime(full_path)
        create_time = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
             
        download_listbox.item(row_id, values=(full_path, "Downloaded", create_time, common_functions.get_file_size(full_path)))
        download_listbox.update_idletasks()


    elif progress_dict['status'] == 'error':
        update_info("get error")
        download_listbox.item(row_id, values=(full_path, "Error", "", ""))
        download_listbox.update_idletasks()


    else:
        try:
            update_info("downloading")
            total_bytes = progress_dict.get("total_bytes", 0)
            downloaded_bytes = progress_dict.get("downloaded_bytes", 0)
            if total_bytes is not None and total_bytes > 0:
                download_percentage = (downloaded_bytes / total_bytes) * 100
            else:
                download_percentage = 0

            download_listbox.item(row_id, values=(full_path, f"{download_percentage:.2f}%", "", ""))
            download_listbox.update_idletasks()

        except:
            print()



def find_files_with_same_basename(file_path):
    # 获取文件名（不包括扩展名）
    # base_name = os.path.splitext(os.path.basename(file_path))[0]

        # 获取文件名（包括扩展名）
    full_name = os.path.basename(file_path)
    print('full_name',full_name)
    # 提取文件名（不包括扩展名）
    base_name = full_name.split(".")[0]
 
    print('base_name',base_name)

    # 获取文件所在目录
    directory_path = os.path.dirname(file_path)
    print('directory_path',directory_path)
    all_files = os.listdir(directory_path)

    ext_pattern =  r'.*'  # 此处使用正则表达式匹配包含两个点的扩展名
    ext_regex = re.compile(ext_pattern)
     # 找到与输入文件名相同的文件，且扩展名匹配指定的正则表达式
    matching_files = [os.path.join(directory_path, file) for file in all_files if file.split(".")[0] == base_name and ext_regex.match(os.path.splitext(file)[1])]
    return matching_files


def on_double_click(event, listbox):
    # 获取双击的项的索引
    selected_index = listbox.nearest(event.y)

    if selected_index is not None:
        # 获取双击的项的文本
        selected_item = listbox.get(selected_index)
        common_functions.openselectedfile(selected_item)

def show_popup(filename):
    try:
        print('popup filename',filename)
        matching_files = find_files_with_same_basename(filename)

        for file in matching_files:
            print("File with the same basename:", file)

        popup = tk.Toplevel(root)
        popup.title("File Details")

        # Calculate the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the width to 1/6 of the screen width and the height to 1/2 of the screen height
        width = screen_width // 2
        height = screen_height // 2

        # Calculate the X and Y coordinates to center the popup
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        popup.geometry(f"{width}x{height}+{x}+{y}")

        # text = tk.Text(popup, wrap="word", height=10, width=40)
        # text.insert("1.0", f"Filename: {filename}")
        # text.pack(fill="both", expand=True)  # Expand both horizontally and vertically

        # 创建一个Listbox
        listbox = tk.Listbox(popup)
        listbox.pack(fill=tk.BOTH, expand=True)

        # 将匹配的文件添加到Listbox中
        for file in matching_files:
            listbox.insert(tk.END, file)

        # listbox.bind("<Double-1>", on_double_click)
        # 绑定双击事件处理函数，并传递listbox作为参数
        listbox.bind("<Double-1>", lambda event, lb=listbox: on_double_click(event, lb))

        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", expand=True)  # Expand horizontally

        open_button = tk.Button(button_frame, text="Archive", command=archive_file(listbox))
        open_button.pack(side="left", fill="x", expand=True)

        # play_button = tk.Button(button_frame, text="Open", command=lambda: common_functions.play_video(filename))
        # play_button.pack(side="left", fill="x", expand=True)

        close_button = tk.Button(button_frame, text="Close", command=lambda: custom_close_function(popup))
        close_button.pack(side="left", fill="x", expand=True)

        root.mainloop()
    except:
        pass



def archive_file(listbox):
    try:
        output_directory =  listbox.get(0).split(".")[0]
        print('output_directory',output_directory)

        os.makedirs(output_directory, exist_ok=True)

        for i in range(listbox.size()):
            item = listbox.get(i)
            if os.path.isfile(item):
                try:
                    # 直接复制文件到目录
                    shutil.copy(item, output_directory)
                    # os.remove(item)
                except Exception as e:
                    print(f"Error copying {item} to {output_directory}: {str(e)}")
            else:
                print(f"Skipping {item} as it's not a file.")


    except:
        pass
        


def custom_close_function(popup):
    # 在这里执行你的自定义关闭操作
    print("Custom close function called")
    populate_download_listbox()
    # 这里可以添加你的其他操作
    # 最后关闭窗口
    
    popup.destroy()


def show_filename(event):
    try:
        item = download_listbox.identify_row(event.y)
        filename = download_listbox.item(item, "values")[0]
        # Get the first 100 characters and the last 30 characters
        if len(filename) > 48 + 30:
            shortened_filename = filename[:48] + "..." + filename[-30:]
        else:
            shortened_filename = filename  # If the filename is shorter than 100+30 characters

        update_info(shortened_filename)
    except:
        pass


if __name__ == "__main__":

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


    video_formats = ["480", "720","1440","Best","Audio"]
    format_var = tk.StringVar()
    format_var.set(video_formats[0])  # Set the default format

    format_menu = ttk.OptionMenu(frame, format_var, video_formats[0], *video_formats)
    format_menu.grid(row=1, column=1, padx=2, pady=5, sticky="w")


    # Create a downframe below the frame
    downframe = tk.Frame(root)
    downframe.pack(padx=10, pady=10, fill="both", expand=True)

    # 创建一个滚动条
    scrollbar = ttk.Scrollbar(root, orient="vertical")


    # Create the download_listbox
    columns = ("Filename", "Progress", "Createtime", "Size","Url")
    download_listbox = ttk.Treeview(root, columns=columns, show="headings")
    download_listbox.pack(padx=10, pady=10,fill="both", expand=True)
    download_listbox.heading("Filename", text="Filename", command=lambda: sort_column("Filename", False))
    download_listbox.heading("Progress", text="Progress")
    download_listbox.heading("Createtime", text="Createtime", command=lambda: sort_column("Createtime", False))
    download_listbox.heading("Size", text="Size", command=lambda: sort_column("Size", False))
    download_listbox.heading("Url", text="Url", command=lambda: sort_column("Url", False))
    scrollbar.config(command=download_listbox.yview)
    download_listbox.config(yscrollcommand=scrollbar.set)

# Bind the mouse event to the "Filename" column
    # download_listbox.tag_bind("column", "#1", "<Enter>", show_filename)
    download_listbox.bind("<Motion>", show_filename)

    # Automatically scroll to the last row
    download_listbox.yview_scroll(1, "units")


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

