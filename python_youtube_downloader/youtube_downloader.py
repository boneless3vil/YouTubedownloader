import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import json
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

class FormatSelector(tk.Toplevel):
    def __init__(self, parent, formats):
        try:
            super().__init__(parent)
            self.title("Select Format")
            self.geometry("600x300")  
            self.resizable(False, False)  

            if not formats:
                ttk.Label(self, text="No suitable formats found for this download type.").pack(pady=20)
                ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)
                self.selected_format = None
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

            self.selected_format = None
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
            # Configure button style
            self.style = ttk.Style()
            self.style.configure("TButton", padding=5, width=10)
            self.style.configure("TLabel", padding=3)

            # Main frame setup
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create and pack all GUI elements
            self.create_url_frame()
            self.create_download_options()
            self.create_playlist_options()
            self.create_progress_frame()
            self.create_button_frame()

            # Base path for resources
            self.base_path = get_base_path()
            self.settings = self.load_settings()
            logger.debug("GUI setup completed successfully")
        except Exception as e:
            logger.error(f"Error in setup_gui: {str(e)}", exc_info=True)
            raise

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

    def create_download_options(self):
        download_frame = ttk.LabelFrame(self.main_frame, text="Download Options", padding="10")
        download_frame.pack(fill=tk.X, pady=10)

        self.download_type = tk.StringVar(value="video+audio")
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
                self.is_playlist.set('entries' in info)
                if self.is_playlist.get():
                    self.playlist_info = info
                    # For playlists, use the first video's formats
                    formats = info['entries'][0]['formats'] if info['entries'] else []

                    # Update status with playlist info
                    playlist_count = len(info['entries'])
                    self.status_var.set(f"Playlist detected: {playlist_count} videos")
                else:
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
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch formats: {str(e)}"))
            self.status_var.set("Ready")

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

        ydl_opts = {
            'outtmpl': os.path.join(self.settings['download_path'], '%(playlist_index)s-%(title)s.%(ext)s'),
            'progress_hooks': [self.download_progress_hook],
            'ignoreerrors': True  
        }

        if self.is_playlist.get() and self.playlist_info:
            # Add playlist-specific options
            if not self.download_all.get():
                try:
                    start = int(self.start_index.get()) if self.start_index.get() else None
                    end = int(self.end_index.get()) if self.end_index.get() else None

                    if start is not None and start < 1:
                        raise ValueError("Start index must be 1 or greater")
                    if end is not None and start is not None and end < start:
                        raise ValueError("End index must be greater than start index")

                    ydl_opts['playliststart'] = start
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

        def download_thread():
            try:
                self.status_var.set("Downloading..." + (" (Playlist)" if self.is_playlist.get() else ""))
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download([url])
                    if error_code != 0:
                        raise Exception("Download failed with non-zero exit code")

                self.status_var.set("Download completed!")
                self.progress_var.set(100)
                self.log_download(url, f"{download_type}:{format_id}", "Success" + (" (Playlist)" if self.is_playlist.get() else ""))
                messagebox.showinfo("Success", "Download completed!")
            except Exception as e:
                self.status_var.set("Download failed!")
                error_msg = str(e)
                self.log_download(url, f"{download_type}:{format_id}", f"Failed: {error_msg}")
                messagebox.showerror("Error", f"Download failed: {error_msg}")
            finally:
                self.progress_var.set(0)

        threading.Thread(target=download_thread, daemon=True).start()

    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()
            except:
                pass

    def load_settings(self):
        default_settings = {
            "download_path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "format": "mp4"
        }
        try:
            settings_path = os.path.join(self.base_path, "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    return {**default_settings, **json.load(f)}
            return default_settings
        except:
            return default_settings

    def save_settings(self, path_var, format_var, settings_window):
        self.settings["download_path"] = path_var.get()
        self.settings["format"] = format_var.get()
        self.save_settings_file()
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
        settings_window.geometry("400x120")  
        settings_window.resizable(False, False)  

        settings_frame = ttk.Frame(settings_window, padding="3")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        path_frame = ttk.Frame(settings_frame)
        path_frame.pack(fill=tk.X, pady=2)
        ttk.Label(path_frame, text="Download Path:").pack(side=tk.LEFT)
        path_var = tk.StringVar(value=self.settings["download_path"])
        path_entry = ttk.Entry(path_frame, textvariable=path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.add_context_menu(path_entry)

        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_path(path_var)).pack(side=tk.RIGHT)

        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        format_var = tk.StringVar(value=self.settings["format"])
        format_entry = ttk.Entry(format_frame, textvariable=format_var, width=10)
        format_entry.pack(side=tk.LEFT, padx=5)

        self.add_context_menu(format_entry)

        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=5)
        ttk.Button(save_frame, text="Save", command=lambda: self.save_settings(path_var, format_var, settings_window)).pack()

    def browse_path(self, path_var):
        path = filedialog.askdirectory(initialdir=self.settings["download_path"])
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

    def __call__(self):
        self.settings = self.load_settings()


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

            # Sort formats by quality
            formats.sort(key=lambda x: int(x.get('height', 0) or 0), reverse=True)

            # Select format based on quality preference
            if quality == 'highest':
                selected_format = formats[0]['format_id']
            elif quality == 'lowest':
                selected_format = formats[-1]['format_id']
            else:  # medium
                selected_format = formats[len(formats)//2]['format_id']

            logger.info(f"Selected format: {selected_format}")

            # Configure download options
            ydl_opts = {
                'format': selected_format,
                'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")
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
    flask_app.run(host='0.0.0.0', port=5000)

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
        app()
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