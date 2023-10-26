"""
Author: XUAN LI
Date: 
Email: lixuan2001@gmail.com
"""
import tkinter as tk
from tkinter import ttk
import os
import common_functions
import ytdtkinter
import ytd
  

def on_item_selected(event):
    try:
        selected_item = download_listbox.selection()
        print(f"selected_item,{selected_item}")

        if selected_item:
            item = download_listbox.item(selected_item, "values")
            filename = item[0]
            
            if filename:
                print(f"filename,{filename}")
                show_popup(filename)       
    except:
        update_info('Some error happened')
         


def update_info(info):
    download_percentage_label.config(text=info)
    root.update()
 
def on_double_click(event, listbox):
    # 获取双击的项的索引
    selected_index = listbox.nearest(event.y)

    if selected_index is not None:
        # 获取双击的项的文本
        selected_item = listbox.get(selected_index)
        common_functions.openselectedfile(selected_item)

def show_popup(filename):
    try:
        # update_info(filename)
        # Calculate the screen width and height
        print(f"show popup {filename}")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the width to 1/6 of the screen width and the height to 1/2 of the screen height
        width = screen_width // 2
        height = screen_height // 4

        # Calculate the X and Y coordinates to center the popup
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        if os.path.isdir(filename):
            common_functions.open_directory(filename)

        elif os.path.isfile(filename):
            # 处理文件
            popup = tk.Toplevel(root)
            popup.title("File Details")
            popup.geometry(f"{width}x{height}+{x}+{y}")
            listbox = tk.Listbox(popup)
            listbox.pack(fill=tk.BOTH, expand=True)

            matching_files = common_functions.find_files_with_same_basename(filename)

            for file in matching_files:
                listbox.insert(tk.END, file)
                listbox.bind("<Double-1>", lambda event, lb=listbox: on_double_click(event, lb))

        else:
            # 其他情况，可能是不存在的路径
            print("Path does not exist or is not a file or directory")
        


        # 将匹配的文件添加到Listbox中
        infolabel = tk.Label(popup, text="info")
        infolabel.pack()

        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", expand=True)  # Expand horizontally

        open_button = tk.Button(button_frame, text="Archive", command=lambda:common_functions.archive_file(listbox,infolabel))
        open_button.pack(side="left", fill="x", expand=True)

        # play_button = tk.Button(button_frame, text="Open", command=lambda: common_functions.play_video(filename))
        # play_button.pack(side="left", fill="x", expand=True)

        close_button = tk.Button(button_frame, text="Close", command=lambda: custom_close_function(popup))
        close_button.pack(side="left", fill="x", expand=True)

        root.mainloop()
    except:
        pass


def custom_close_function(popup):
    print("Custom close function called")
    ytdtkinter.populate_download_listbox(download_listbox)
    
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
    download_listbox.heading("Filename", text="Filename", command=lambda: ytdtkinter.sort_column(download_listbox,"Filename", False))
    download_listbox.heading("Progress", text="Progress")
    download_listbox.heading("Createtime", text="Createtime", command=lambda: ytdtkinter.sort_column(download_listbox,"Createtime", False))
    download_listbox.heading("Size", text="Size", command=lambda: ytdtkinter.sort_column(download_listbox,"Size", False))
    download_listbox.heading("Url", text="Url", command=lambda: ytdtkinter.sort_column(download_listbox,"Url", False))
    scrollbar.config(command=download_listbox.yview)
    download_listbox.config(yscrollcommand=scrollbar.set)

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

    download_button = tk.Button(frame, text="Download", command=lambda:ytd.download_video(url_entry.get(),format_var.get(),download_listbox,download_percentage_label))
    download_button.grid(row=0, column=2, sticky="e", padx=2, pady=5)

    donate_button = tk.Button(root, text="Donate", command=common_functions.show_donate_info)
    donate_button.pack()
    ytdtkinter.populate_download_listbox(download_listbox)
    # Start the main loop
    root.mainloop()

