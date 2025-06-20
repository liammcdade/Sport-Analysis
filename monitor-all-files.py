import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyEventHandler(FileSystemEventHandler):
    """Handles file system events and prints them to the console."""

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            print(f"Created: {event.src_path}")

    def on_deleted(self, event):
        """Called when a file or directory is deleted."""
        if not event.is_directory:
            print(f"Deleted: {event.src_path}")

    def on_modified(self, event):
        """Called when a file or directory is modified."""
        if not event.is_directory:
            print(f"Modified: {event.src_path}")

    def on_moved(self, event):
        """Called when a file or directory is moved or renamed."""
        if not event.is_directory:
            print(f"Moved/Renamed: From '{event.src_path}' to '{event.dest_path}'")


def start_monitoring(path_to_monitor):
    """
    Starts monitoring the specified path for file system events.

    Args:
        path_to_monitor (str): The directory path to monitor.
    """
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_monitor, recursive=True)

    print(f"Monitoring directory: {path_to_monitor}")
    print("Press Ctrl+C to stop monitoring.")

    observer.start()
    try:
        while True:
            # Keep the script running until interrupted
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped by user.")
    except Exception as e:
        observer.stop()
        print(f"\nAn unexpected error occurred: {e}")
        print("Monitoring stopped.")
    finally:
        observer.join()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the directory provided as a command-line argument
        directory_to_monitor = sys.argv[1]
    else:
        # Default to the user's home directory if no argument is provided
        default_path = os.path.expanduser("~")
        print(f"No directory specified. Defaulting to home directory: {default_path}")
        print(
            "To monitor a specific directory, run the script like: "
            "python monitor-all-files.py /path/to/your/directory"
        )
        directory_to_monitor = default_path

    if not os.path.isdir(directory_to_monitor):
        print(
            f"Error: The specified directory '{directory_to_monitor}' does not exist or is not a directory."
        )
        sys.exit(1)

    if not os.access(directory_to_monitor, os.R_OK):
        print(
            f"Error: The specified directory '{directory_to_monitor}' is not readable."
        )
        sys.exit(1)

    print("Starting file system monitor...")
    start_monitoring(directory_to_monitor)
