import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ExcelHandler(FileSystemEventHandler):

    def on_modified(self, event):
        # Only react to xlsx files, ignore temp files
        if event.src_path.endswith(".xlsx") and "_temp" not in event.src_path:
            print(f"Excel updated: {os.path.basename(event.src_path)}")

if __name__ == "__main__":

    event_handler = ExcelHandler()
    observer = Observer()

    observer.schedule(event_handler, path=os.path.join(BASE_DIR, "data"), recursive=False)
    observer.start()

    print("Watching Excel files for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
