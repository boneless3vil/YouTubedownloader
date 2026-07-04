import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import json
import re
import threading
import sys
import logging
from datetime import datetime
import pyperclip
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more verbose logging
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

def get_base_path():
    """Get base path for resources, works both in development and when packaged"""
    try:
        if getattr(sys, 'frozen', False):
            # Running in a bundle (PyInstaller)
            base_path = os.path.dirname(sys.executable)
            # Check and set Tcl/Tk paths for frozen environment
            tcl_dir = os.path.join(sys._MEIPASS, "tcl")
            tk_dir = os.path.join(sys._MEIPASS, "tk")

            if os.path.exists(tcl_dir) and os.path.exists(tk_dir):
                vers = [d for d in os.listdir(tcl_dir) if d.startswith('tcl')]
                if vers:
                    tcl_vers = sorted(vers)[-1]
                    tk_vers = 'tk' + tcl_vers[3:]
                    os.environ['TCL_LIBRARY'] = os.path.join(tcl_dir, tcl_vers)
                    os.environ['TK_LIBRARY'] = os.path.join(tk_dir, tk_vers)
                    logger.debug(f"Set TCL_LIBRARY to {os.environ['TCL_LIBRARY']}")
                    logger.debug(f"Set TK_LIBRARY to {os.environ['TK_LIBRARY']}")
        else:
            # Running in a normal Python environment
            base_path = os.path.dirname(os.path.abspath(__file__))

        logger.debug(f"Base path set to: {base_path}")
        return base_path
    except Exception as e:
        logger.error(f"Error in get_base_path: {str(e)}", exc_info=True)
        raise

DEFAULT_SETTINGS = {
    # Final destination for finished downloads
    "download_path": os.path.join(os.path.expanduser("~"), "Downloads"),
    # Source/staging folder for in-progress downloads; "" = download
    # directly into the destination
    "temp_path": "",
    "default_download_type": "video+audio",
    "format": "mp4",
}


def load_settings(base_path):
    """Read settings.json, falling back to defaults for missing/invalid values.

    Shared by the GUI and the extension API so both honor the same folders.
    """
    settings = dict(DEFAULT_SETTINGS)
    try:
        settings_path = os.path.join(base_path, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings.update(json.load(f))
        # Fall back to defaults if saved paths don't exist (e.g. a settings
        # file created on another machine/OS)
        if not os.path.isdir(settings.get("download_path", "")):
            settings["download_path"] = DEFAULT_SETTINGS["download_path"]
        if settings.get("temp_path") and not os.path.isdir(settings["temp_path"]):
            settings["temp_path"] = ""
    except Exception:
        return dict(DEFAULT_SETTINGS)
    return settings


def build_download_paths(settings):
    """yt-dlp 'paths' dict: partial files go to temp, finished files to home."""
    paths = {"home": settings["download_path"]}
    if settings.get("temp_path"):
        paths["temp"] = settings["temp_path"]
    return paths


class FormatSelector(tk.Toplevel):
    def __init__(self, parent, formats):
        self.selected_format = None
        try:
            super().__init__(parent)
            self.title("Select Format")
            self.geometry("600x300")  
            self.resizable(False, False)  

            if not formats:
                ttk.Label(self, text="No suitable formats found for this download type.").pack(pady=20)
                ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)
                return

            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            self.tree = ttk.Treeview(main_frame, columns=("format_id", "ext", "resolution", "filesize", "tbr", "acodec"), show="headings")

            self.tree.heading("format_id", text="ID")
            self.tree.heading("ext", text="Format")
            self.tree.heading("resolution", text="Resolution")
            self.tree.heading("filesize", text="File Size")
            self.tree.heading("tbr", text="Bitrate")
            self.tree.heading("acodec", text="Audio")

            self.tree.column("format_id", width=40)
            self.tree.column("ext", width=50)
            self.tree.column("resolution", width=100)
            self.tree.column("filesize", width=80)
            self.tree.column("tbr", width=70)
            self.tree.column("acodec", width=80)

            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            for f in formats:
                try:
                    filesize = f.get('filesize', None)
                    if filesize and filesize > 0:
                        filesize = f"{filesize/1024/1024:.1f} MB"
                    else:
                        filesize = "N/A"

                    resolution = f.get('resolution', 'N/A')
                    if resolution == 'audio only':
                        resolution = f"Audio ({f.get('abr', 'N/A')}kbps)"
                    elif f.get('height'):
                        resolution = f"{f.get('height')}p"

                    self.tree.insert("", tk.END, values=(
                        str(f.get('format_id', 'N/A')),
                        str(f.get('ext', 'N/A')),
                        str(resolution),
                        str(filesize),
                        f"{str(f.get('tbr', 'N/A'))} kbps" if f.get('tbr') else 'N/A',
                        str(f.get('acodec', 'N/A'))
                    ))
                except Exception as e:
                    logger.error(f"Error processing format: {str(e)}")
                    continue

            self.tree.bind('<Double-1>', lambda e: self.select_format())

            self.grab_set()
        except Exception as e:
            logger.error(f"Error in FormatSelector initialization: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to initialize format selector: {str(e)}")
            self.destroy()

    def select_format(self):
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0])['values']
            self.selected_format = str(values[0])
            self.destroy()

class YouTubeDownloader:
    def __init__(self, root):
        try:
            logger.debug("Initializing YouTube Downloader GUI")
            self.root = root
            self.root.title("YouTube Downloader")
            self.root.geometry("500x300")
            self.root.resizable(True, True)

            # Initialize variables
            self.format_cache = {}
            self.setup_gui()
            logger.debug("GUI initialization completed")
        except Exception as e:
            logger.error(f"Failed to initialize GUI: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to initialize application: {str(e)}")
            raise

    def setup_gui(self):
        try:
            logger.debug("Setting up GUI components")
            # Settings are loaded first so widgets can pick up saved defaults
            self.base_path = get_base_path()
            self.settings = self.load_settings()
            self.set_window_icon()

            # Configure button style
            self.style = ttk.Style()
            self.style.configure("TButton", padding=5, width=10)
            self.style.configure("TLabel", padding=3)

            # Main frame setup
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create and pack all GUI elements
            self.create_menubar()
            self.create_url_frame()
            self.create_download_options()
            self.create_playlist_options()
            self.create_progress_frame()
            self.create_button_frame()
            logger.debug("GUI setup completed successfully")
        except Exception as e:
            logger.error(f"Error in setup_gui: {str(e)}", exc_info=True)
            raise

    def set_window_icon(self):
        # icon.ico sits next to the script in development; PyInstaller unpacks
        # bundled data files into sys._MEIPASS
        candidates = [os.path.join(self.base_path, "icon.ico")]
        if getattr(sys, 'frozen', False):
            candidates.insert(0, os.path.join(sys._MEIPASS, "icon.ico"))
        for icon_path in candidates:
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except tk.TclError:
                    logger.warning(f"Could not apply window icon {icon_path}")
                return

    def create_menubar(self):
        menubar = tk.Menu(self.root, tearoff=0)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings...", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def create_url_frame(self):
        # URL Frame with validation
        url_frame = ttk.Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.add_context_menu(self.url_entry)
        self.check_clipboard()

        # Enter in the URL field starts the format search
        self.url_entry.bind('<Return>', lambda e: self.prepare_download())

        # Auto-fetch formats when a complete YouTube URL lands in the field
        # (paste or typing). The trace is installed after check_clipboard so
        # a URL auto-filled from the clipboard at startup doesn't pop a
        # dialog before the user has done anything.
        self._auto_fetch_job = None
        self._last_fetched_url = self.url_var.get().strip()
        self.url_var.trace_add('write', self._schedule_auto_fetch)

    # Matches only complete video/shorts/playlist URLs so auto-fetch doesn't
    # fire on a half-typed address
    AUTO_FETCH_RE = re.compile(
        r'(youtube\.com/watch\?\S*v=[\w-]{11}'
        r'|youtu\.be/[\w-]{11}'
        r'|youtube\.com/shorts/[\w-]{11}'
        r'|youtube\.com/playlist\?\S*list=[\w-]+)'
    )

    def _schedule_auto_fetch(self, *_):
        if self._auto_fetch_job is not None:
            self.root.after_cancel(self._auto_fetch_job)
        self._auto_fetch_job = self.root.after(700, self._auto_fetch)

    def _auto_fetch(self):
        self._auto_fetch_job = None
        url = self.url_var.get().strip()
        if url and url != self._last_fetched_url and self.AUTO_FETCH_RE.search(url):
            self.prepare_download()

    def create_download_options(self):
        download_frame = ttk.LabelFrame(self.main_frame, text="Download Options", padding="10")
        download_frame.pack(fill=tk.X, pady=10)

        saved_type = self.settings.get("default_download_type", "video+audio")
        if saved_type not in ("video+audio", "video-only", "audio-only"):
            saved_type = "video+audio"
        self.download_type = tk.StringVar(value=saved_type)
        ttk.Radiobutton(download_frame, text="Video + Audio", value="video+audio", 
                       variable=self.download_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(download_frame, text="Video Only", value="video-only", 
                       variable=self.download_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(download_frame, text="Audio Only", value="audio-only", 
                       variable=self.download_type).pack(side=tk.LEFT, padx=10)

    def create_playlist_options(self):
        # Add playlist options frame
        playlist_frame = ttk.LabelFrame(self.main_frame, text="Playlist Options", padding="5")
        playlist_frame.pack(fill=tk.X, pady=5)

        self.is_playlist = tk.BooleanVar(value=False)
        self.playlist_info = None

        # Playlist checkboxes
        self.download_all = tk.BooleanVar(value=True)
        self.reverse_playlist = tk.BooleanVar(value=False)

        ttk.Checkbutton(playlist_frame, text="Download All Videos", 
                       variable=self.download_all).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(playlist_frame, text="Reverse Order", 
                       variable=self.reverse_playlist).pack(side=tk.LEFT, padx=5)

        # Add playlist range entries
        range_frame = ttk.Frame(playlist_frame)
        range_frame.pack(side=tk.LEFT, padx=5)

        self.start_index = tk.StringVar(value="")
        self.end_index = tk.StringVar(value="")

        ttk.Label(range_frame, text="Start:").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.start_index, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(range_frame, text="End:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(range_frame, textvariable=self.end_index, width=5).pack(side=tk.LEFT)

    def create_progress_frame(self):
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 0))  

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=(2, 0))  

    def create_button_frame(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        # Create buttons with explicit width and text configuration
        # Using regular tk.Button instead of ttk.Button for better text visibility
        download_btn = tk.Button(button_frame, text="Download", width=10, 
                               command=self.prepare_download, relief=tk.RAISED)
        download_btn.pack(side=tk.LEFT, padx=5)

        settings_btn = tk.Button(button_frame, text="Settings", width=10,
                               command=self.show_settings, relief=tk.RAISED)
        settings_btn.pack(side=tk.LEFT, padx=5)

        history_btn = tk.Button(button_frame, text="History", width=10,
                              command=self.show_history, relief=tk.RAISED)
        history_btn.pack(side=tk.LEFT, padx=5)

    def add_context_menu(self, entry):
        menu = tk.Menu(entry, tearoff=0)
        menu.add_command(label="Cut", command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        entry.bind("<Button-3>", show_menu)  
        entry.bind("<Control-Button-1>", show_menu)  

    def prepare_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        # Validate YouTube URL format
        if not ('youtube.com' in url or 'youtu.be' in url):
            messagebox.showerror("Error", "Invalid YouTube URL format")
            return

        # Remember what we fetched so the auto-fetch trace doesn't fire a
        # second search for the same URL
        self._last_fetched_url = url

        # Clean up playlist URL if present
        if 'playlist' in url:
            try:
                # Extract the playlist ID
                if 'list=' in url:
                    playlist_id = url.split('list=')[1].split('&')[0]
                    url = f"https://youtube.com/playlist?list={playlist_id}"
            except Exception as e:
                logger.error(f"Error formatting playlist URL: {str(e)}")

        if url in self.format_cache:
            self.show_format_selector(self.format_cache[url], url)
        else:
            self.status_var.set("Fetching available formats...")
            threading.Thread(target=self.fetch_formats, args=(url,), daemon=True).start()

    def fetch_formats(self, url):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)

                # Check if URL is a playlist
                is_playlist = 'entries' in info
                self.root.after(0, self.is_playlist.set, is_playlist)
                if is_playlist:
                    self.playlist_info = info
                    # For playlists, use the first video's formats
                    formats = info['entries'][0]['formats'] if info['entries'] else []

                    # Update status with playlist info
                    playlist_count = len(info['entries'])
                    self.root.after(0, self.status_var.set, f"Playlist detected: {playlist_count} videos")
                else:
                    self.playlist_info = None
                    formats = info['formats']

                # Filter and sort formats based on download type
                download_type = self.download_type.get()
                if download_type == "video+audio":
                    formats = [f for f in formats if 
                        f.get('vcodec') != 'none' and
                        f.get('acodec') != 'none' and
                        f.get('ext') in ['mp4', 'mkv', 'webm']
                    ]
                    formats.sort(key=lambda x: (
                        int(x.get('height', 0) or 0),
                        float(x.get('tbr', 0) or 0)
                    ), reverse=True)
                elif download_type == "video-only":
                    formats = [f for f in formats if 
                        f.get('vcodec') != 'none' and
                        f.get('acodec') == 'none' and
                        f.get('ext') in ['mp4', 'webm']
                    ]
                    formats.sort(key=lambda x: int(x.get('height', 0) or 0), reverse=True)
                else:  # audio-only
                    formats = [f for f in formats if 
                        f.get('acodec') != 'none' and
                        f.get('vcodec') == 'none' and
                        f.get('ext') in ['m4a', 'mp3', 'opus', 'webm']
                    ]
                    formats.sort(key=lambda x: float(x.get('abr', 0) or 0), reverse=True)

                # Cache the formats
                self.format_cache[url] = formats

                # Show format selector
                self.root.after(0, lambda: self.show_format_selector(formats, url))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch formats: {error_msg}"))
            self.root.after(0, self.status_var.set, "Ready")

    def show_format_selector(self, formats, url):
        selector = FormatSelector(self.root, formats)
        self.root.wait_window(selector)
        if selector.selected_format:
            self.start_download(url, selector.selected_format)
        else:
            self.status_var.set("Download cancelled")

    def start_download(self, url, format_id):
        format_id = str(format_id)
        download_type = self.download_type.get()
        is_playlist = self.is_playlist.get() and self.playlist_info

        # Only prefix filenames with the playlist index for playlist downloads;
        # for single videos %(playlist_index)s expands to "NA"
        outtmpl = '%(playlist_index)s-%(title)s.%(ext)s' if is_playlist else '%(title)s.%(ext)s'

        ydl_opts = {
            'outtmpl': outtmpl,
            'paths': build_download_paths(self.settings),
            'progress_hooks': [self.download_progress_hook],
            'ignoreerrors': True
        }

        if is_playlist:
            # Add playlist-specific options
            if not self.download_all.get():
                try:
                    start = int(self.start_index.get()) if self.start_index.get() else None
                    end = int(self.end_index.get()) if self.end_index.get() else None

                    if start is not None and start < 1:
                        raise ValueError("Start index must be 1 or greater")
                    if end is not None and start is not None and end < start:
                        raise ValueError("End index must be greater than start index")

                    if start is not None:
                        ydl_opts['playliststart'] = start
                    if end is not None:
                        ydl_opts['playlistend'] = end
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return

            ydl_opts['noplaylist'] = False
            ydl_opts['playlist_reverse'] = self.reverse_playlist.get()

        if download_type == "video+audio":
            ydl_opts.update({
                'format': f'{format_id}+bestaudio[ext=m4a]/best',
                'merge_output_format': self.settings['format']
            })
        elif download_type == "video-only":
            ydl_opts['format'] = format_id
        else:  
            ydl_opts.update({
                'format': format_id,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            })

        playlist_suffix = " (Playlist)" if is_playlist else ""

        def download_thread():
            try:
                self.root.after(0, self.status_var.set, "Downloading..." + playlist_suffix)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download([url])
                    if error_code != 0:
                        raise Exception("Download failed with non-zero exit code")

                self.root.after(0, self.status_var.set, "Download completed!")
                self.root.after(0, self.progress_var.set, 100)
                self.log_download(url, f"{download_type}:{format_id}", "Success" + playlist_suffix)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Download completed!"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, self.status_var.set, "Download failed!")
                self.log_download(url, f"{download_type}:{format_id}", f"Failed: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_msg}"))
            finally:
                self.root.after(0, self.progress_var.set, 0)

        threading.Thread(target=download_thread, daemon=True).start()

    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.root.after(0, self.progress_var.set, progress)
            except:
                pass

    def load_settings(self):
        return load_settings(self.base_path)

    def save_settings(self, source_var, dest_var, type_var, format_var, settings_window):
        source = source_var.get().strip()
        dest = dest_var.get().strip()
        if not os.path.isdir(dest):
            messagebox.showerror("Error", f"Destination folder does not exist:\n{dest}")
            return
        if source and not os.path.isdir(source):
            messagebox.showerror("Error", f"Source folder does not exist:\n{source}")
            return

        self.settings["temp_path"] = source
        self.settings["download_path"] = dest
        self.settings["default_download_type"] = type_var.get()
        self.settings["format"] = format_var.get()
        self.save_settings_file()
        # Apply the new default to the main window immediately
        self.download_type.set(type_var.get())
        settings_window.destroy()
        messagebox.showinfo("Success", "Settings saved!")

    def save_settings_file(self):
        settings_path = os.path.join(self.base_path, "settings.json")
        with open(settings_path, "w") as f:
            json.dump(self.settings, f)

    def check_clipboard(self):
        try:
            clipboard_content = pyperclip.paste()
            if "youtube.com" in clipboard_content or "youtu.be" in clipboard_content:
                self.url_var.set(clipboard_content)
        except:
            pass

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("520x230")
        settings_window.resizable(False, False)

        settings_frame = ttk.Frame(settings_window, padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        def folder_row(label, value):
            row = ttk.Frame(settings_frame)
            row.pack(fill=tk.X, pady=3)
            ttk.Label(row, text=label, width=22).pack(side=tk.LEFT)
            var = tk.StringVar(value=value)
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.add_context_menu(entry)
            ttk.Button(row, text="Browse",
                       command=lambda: self.browse_path(var)).pack(side=tk.RIGHT)
            return var

        # Source folder holds in-progress downloads; finished files are moved
        # to the destination. Leave source empty to download directly.
        source_var = folder_row("Source (in-progress):", self.settings.get("temp_path", ""))
        dest_var = folder_row("Destination (finished):", self.settings["download_path"])

        type_frame = ttk.Frame(settings_frame)
        type_frame.pack(fill=tk.X, pady=3)
        ttk.Label(type_frame, text="Default download:", width=22).pack(side=tk.LEFT)
        type_var = tk.StringVar(value=self.download_type.get())
        for text, value in (("Video + Audio", "video+audio"),
                            ("Video Only", "video-only"),
                            ("Audio Only", "audio-only")):
            ttk.Radiobutton(type_frame, text=text, value=value,
                            variable=type_var).pack(side=tk.LEFT, padx=4)

        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=3)
        ttk.Label(format_frame, text="Format:", width=22).pack(side=tk.LEFT)
        format_var = tk.StringVar(value=self.settings["format"])
        format_entry = ttk.Entry(format_frame, textvariable=format_var, width=10)
        format_entry.pack(side=tk.LEFT, padx=5)

        self.add_context_menu(format_entry)

        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=10)
        ttk.Button(save_frame, text="Save",
                   command=lambda: self.save_settings(source_var, dest_var, type_var,
                                                      format_var, settings_window)).pack()

    def browse_path(self, path_var):
        path = filedialog.askdirectory(
            initialdir=path_var.get() or self.settings["download_path"])
        if path:
            path_var.set(path)

    def log_download(self, url, download_type, status):
        try:
            log_path = os.path.join(self.base_path, "download_history.log")
            with open(log_path, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | {download_type} | {url} | {status}\n")
        except:
            pass

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Download History")
        history_window.geometry("600x400")
        history_window.resizable(False, False)  

        text_widget = tk.Text(history_window, wrap=tk.WORD, width=70, height=20)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        try:
            with open(os.path.join(self.base_path, "download_history.log"), "r") as f:
                history = f.read()
                text_widget.insert(tk.END, history)
        except:
            text_widget.insert(tk.END, "No download history available.")

        text_widget.configure(state=tk.DISABLED)


# Create Flask app instance
flask_app = Flask(__name__)
CORS(flask_app)  # Enable CORS for Chrome extension

@flask_app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'YouTube Downloader API is active'
    })

@flask_app.route('/api/download', methods=['POST'])
def api_download():
    try:
        data = request.json
        if not data or 'url' not in data or 'settings' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data. Required: url and settings'
            }), 400

        video_url = data['url']
        settings = data['settings']

        logger.info(f"Download request received for URL: {video_url}")
        logger.debug(f"Download settings: {settings}")

        # Initialize download with settings
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info['formats']

            # Filter formats based on settings
            download_type = settings.get('downloadType', 'video-audio')
            if download_type == 'video+audio':  # popup uses this spelling
                download_type = 'video-audio'
            quality = settings.get('quality', 'highest')

            if download_type == "video-audio":
                formats = [f for f in formats if 
                    f.get('vcodec') != 'none' and
                    f.get('acodec') != 'none'
                ]
            elif download_type == "video-only":
                formats = [f for f in formats if 
                    f.get('vcodec') != 'none' and
                    f.get('acodec') == 'none'
                ]
            else:  # audio-only
                formats = [f for f in formats if 
                    f.get('acodec') != 'none' and
                    f.get('vcodec') == 'none'
                ]

            if not formats:
                return jsonify({
                    'success': False,
                    'error': f'No formats found for type: {download_type}'
                }), 400

            # Sort formats by quality (audio formats have no height, use bitrate)
            if download_type == "audio-only":
                formats.sort(key=lambda x: float(x.get('abr', 0) or 0), reverse=True)
            else:
                formats.sort(key=lambda x: int(x.get('height', 0) or 0), reverse=True)

            # Select format based on quality preference
            if quality == 'highest':
                selected_format = formats[0]['format_id']
            elif quality == 'lowest':
                selected_format = formats[-1]['format_id']
            else:  # medium
                selected_format = formats[len(formats)//2]['format_id']

            logger.info(f"Selected format: {selected_format}")

            # Configure download options - honor the folders configured in
            # the desktop app's Settings
            app_settings = load_settings(get_base_path())
            ydl_opts = {
                'format': selected_format,
                'outtmpl': '%(title)s.%(ext)s',
                'paths': build_download_paths(app_settings),
            }

            # Start download in background thread
            def download_thread():
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    logger.info("Download completed successfully")
                except Exception as e:
                    logger.error(f"Download failed: {str(e)}")

            threading.Thread(target=download_thread, daemon=True).start()
            return jsonify({'success': True, 'message': 'Download started'})

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_flask():
    # Bind to localhost only: the API is meant for the local Chrome extension,
    # exposing it on all interfaces would let anyone on the network trigger downloads
    flask_app.run(host='127.0.0.1', port=5000)

def main():
    logger.info("Starting YouTube Downloader application")
    try:
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask server started")

        # Initialize Tk root with error handling
        try:
            root = tk.Tk()
            logger.debug("Created Tk root window")

            # Test Tk functionality
            test_label = ttk.Label(root, text="Initializing...")
            test_label.destroy()
            logger.debug("Successfully tested Tk widget creation")

        except tk.TclError as e:
            logger.error(f"Failed to initialize Tk: {str(e)}", exc_info=True)
            if "Can't find a usable init.tcl" in str(e):
                error_msg = (
                    "Error: Cannot initialize the graphical interface.\n\n"
                    "This might be caused by:\n"
                    "1. Missing Tcl/Tk libraries\n"
                    "2. Incorrect Tcl/Tk paths\n"
                    "3. Antivirus blocking the executable\n\n"
                    "Try:\n"
                    "1. Running as administrator\n"
                    "2. Temporarily disabling antivirus\n"
                    "3. Reinstalling the application"
                )
            else:
                error_msg = f"Failed to initialize graphical interface:\n{str(e)}"

            # Try to show error in GUI if possible, otherwise use console
            try:
                messagebox.showerror("Fatal Error", error_msg)
            except:
                print("FATAL ERROR:", error_msg)
            sys.exit(1)

        app = YouTubeDownloader(root)
        logger.debug("Created YouTubeDownloader instance")
        logger.info("Starting main event loop")
        root.mainloop()

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        if not isinstance(e, SystemExit):
            try:
                messagebox.showerror("Fatal Error", 
                                   f"Application failed to start: {str(e)}\n\n"
                                   "Please check the logs for more details.")
            except:
                print("FATAL ERROR:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()