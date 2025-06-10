import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"Created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"Deleted: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            print(f"Modified: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            print(f"Moved/Renamed: From '{event.src_path}' to '{event.dest_path}'")

def start_monitoring(path):
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    print(f"Monitoring directory: {path}")
    print("Press Ctrl+C to stop monitoring.")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped.")
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory_to_monitor = sys.argv[1]
    else:
        # Default directory to monitor if no argument is provided
        # Set to C:\ for Windows, or adjust for other OS if needed
        directory_to_monitor = "C:\\" # Or "C:/" or "/mnt/c" for WSL or equivalent root for Linux/macOS
        print(f"No directory specified. Monitoring the default drive: {directory_to_monitor}")
        print("To monitor a specific directory, run the script like: python your_script_name.py /path/to/directory")

    if not os.path.isdir(directory_to_monitor):
        print(f"Error: The specified directory '{directory_to_monitor}' does not exist.")
        sys.exit(1)

    start_monitoring(directory_to_monitor)
