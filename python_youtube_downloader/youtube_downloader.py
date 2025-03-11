import os
import sys
import logging
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app instance
flask_app = Flask(__name__)
CORS(flask_app, resources={
    r"/*": {
        "origins": ["chrome-extension://*", "moz-extension://*", "http://localhost:5000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept", "Origin"],
        "expose_headers": ["Content-Type", "Content-Length"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

@flask_app.route('/')
def index():
    """Health check endpoint"""
    logger.info(f"Health check request received from: {request.headers.get('Origin')}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Client IP: {request.remote_addr}")

    response = jsonify({
        "status": "ok",
        "message": "YouTube Downloader API is running"
    })

    # Ensure CORS headers are set correctly for the specific origin
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    if origin != '*':
        response.headers['Vary'] = 'Origin'

    return response

@flask_app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        logger.info(f"Received request from: {request.headers.get('Origin')}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Client IP: {request.remote_addr}")

        data = request.get_json()
        logger.info(f"Received download request: {data}")

        url = data.get('url')
        options = data.get('options', {
            'quality': 'highest',
            'format': 'mp4'
        })

        if not url:
            logger.error("No URL provided in request")
            return jsonify({'success': False, 'error': 'No URL provided'}), 400

        downloader = YouTubeDownloader()
        result = downloader.download_video(url, options)
        logger.info(f"Download result: {result}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Download API error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

class YouTubeDownloader:
    def __init__(self, root=None):
        self.root = root
        self.setup_gui() if root else None
        self.base_path = self.get_base_path()
        self.settings = self.load_settings()

    def get_base_path(self):
        """Get the base path for downloads"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Base path set to: {base_path}")
        return base_path

    def setup_gui(self):
        """Initialize the GUI components"""
        logger.debug("Initializing YouTube Downloader GUI")
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL Entry
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

        # Quality Selection
        ttk.Label(main_frame, text="Quality:").grid(row=1, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="highest")
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var)
        quality_combo['values'] = ('highest', '1080p', '720p', '480p', '360p')
        quality_combo.grid(row=1, column=1, padx=5, pady=5)

        # Format Selection
        ttk.Label(main_frame, text="Format:").grid(row=2, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var)
        format_combo['values'] = ('mp4', 'webm')
        format_combo.grid(row=2, column=1, padx=5, pady=5)

        # Download Button
        self.download_btn = ttk.Button(main_frame, text="Download", command=self.download_video)
        self.download_btn.grid(row=3, column=1, pady=20)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3)

        logger.debug("GUI setup completed successfully")

    def load_settings(self):
        """Load application settings"""
        settings_path = os.path.join(self.base_path, 'settings.json')
        try:
            import json
            with open(settings_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
            return {
                'download_path': os.path.join(self.base_path, 'downloads'),
                'default_format': 'mp4',
                'default_quality': 'highest'
            }

    def save_settings(self):
        """Save application settings"""
        settings_path = os.path.join(self.base_path, 'settings.json')
        try:
            import json
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Could not save settings: {e}")

    def download_video(self, url=None, options=None):
        """Download a video with the specified options"""
        if self.root:  # GUI Mode
            url = self.url_var.get()
            options = {
                'quality': self.quality_var.get(),
                'format': self.format_var.get()
            }

        if not url:
            return {'success': False, 'error': 'No URL provided'}

        try:
            ydl_opts = {
                'format': f'bestvideo[height<={options["quality"]}]+bestaudio/best'
                if options["quality"] != "highest" else 'bestvideo+bestaudio/best',
                'merge_output_format': options['format'],
                'progress_hooks': [self.progress_hook] if self.root else None,
                'outtmpl': os.path.join(self.settings['download_path'], '%(title)s.%(ext)s')
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return {'success': True}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Download error: {error_msg}")
            if self.root:
                self.status_var.set(f"Error: {error_msg}")
            return {'success': False, 'error': error_msg}

    def progress_hook(self, d):
        """Update download progress"""
        if d['status'] == 'downloading':
            try:
                percent = d['_percent_str'].replace('%','')
                self.progress_var.set(float(percent))
                self.status_var.set(f"Downloading... {d['_percent_str']}")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_var.set("Download completed!")
            self.progress_var.set(100)

    def __call__(self):
        """Make the class callable for easier instantiation"""
        logger.debug("GUI initialization completed")


# Start Flask server in a separate thread
def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"Flask server failed to start: {str(e)}")
        raise

def main():
    logger.info("Starting YouTube Downloader application")
    try:
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask server thread started")

        # Wait for Flask to initialize
        import time
        import socket
        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                # Try to connect to the server
                with socket.create_connection(('localhost', 5000), timeout=1.0):
                    logger.info("Flask server is ready")
                    break
            except (socket.error, socket.timeout):
                retries += 1
                time.sleep(1)
                logger.debug(f"Waiting for Flask server, attempt {retries}/{max_retries}")

        if retries >= max_retries:
            logger.error("Flask server failed to start within timeout")
            raise Exception("Flask server failed to start")

        # Try to initialize the Tk GUI; if not possible, run in headless mode
        headless = False
        try:
            root = tk.Tk()
            logger.debug("Created Tk root window")
            # Test Tk functionality
            test_label = ttk.Label(root, text="Initializing...")
            test_label.destroy()
            logger.debug("Successfully tested Tk widget creation")
        except tk.TclError as e:
            logger.warning(f"GUI not available: {str(e)}. Running in headless mode.")
            headless = True

        if headless:
            logger.info("Running in headless mode; Flask server is active on port 5000")
            # In headless mode, simply block indefinitely
            while True:
                time.sleep(10)
        else:
            app = YouTubeDownloader(root)
            logger.debug("Created YouTubeDownloader instance")
            app()
            logger.info("Starting GUI main event loop")
            root.mainloop()

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        if not isinstance(e, SystemExit):
            try:
                if not headless:
                    messagebox.showerror("Fatal Error",
                                         f"Application failed to start: {str(e)}\n\n"
                                         "Please check the logs for more details.")
            except:
                print("FATAL ERROR:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()