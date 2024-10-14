from watchdog.events import FileSystemEventHandler
from lib.similarity import check
import time
import os
import pwd

class Handler(FileSystemEventHandler):
    def __init__(self):
        print("Handler initialized")
 
    def on_created(self, event):
        self.append_to_csv(event)
        print(f"{event.src_path} has been created")
 
    def on_modified(self, event):     
        self.append_to_csv(event)
        print(f"{event.src_path} has been modified")
        
    def on_deleted(self, event):
        self.append_to_csv(event)
        print(f"{event.src_path} has been deleted")

    def append_to_csv(self, event):
        absolute_path = os.path.abspath(event.src_path) if hasattr(event, 'src_path') else '-'
        file_name = event.src_path.split('/')[-1]
        event_type = event.event_type
        event_time = time.strftime('%Y-%m-%d %H:%M:%S')
        csv_file = 'events.csv'
        csv_file = os.path.abspath(csv_file)
        if absolute_path == csv_file or event.src_path == csv_file or absolute_path == os.path.abspath('.') or event.src_path == os.path.abspath('.'):
            return
        try:
            stat = os.stat(event.src_path) if os.path.exists(event.src_path) else None
            file_owner_id = stat.st_uid if stat else None
            file_owner = pwd.getpwuid(file_owner_id).pw_name if file_owner_id else None
            file_size = stat.st_size if stat else None
            highest_similarity_score = 0
            similar_with_file = None
            if os.path.exists(event.src_path):
                if not event.is_directory and event_type != 'deleted':
                    similarity = self.similarity_check(event)
                    highest_similarity_score = similarity[0]['score'] if similarity else 0
                    similar_with_file = similarity[0]['source'] if similarity else None
            with open(csv_file, 'a') as f:
                f.write(f"{file_name},{absolute_path},{event.is_directory},{file_size},{event_type},{event_time},{file_owner},{highest_similarity_score},{similar_with_file}\n")
        except Exception as e:
            print(f"Error writing to file: {e}")
            
    def similarity_check(self, event):
        file = open(event.src_path, 'r', encoding='utf-8', errors='ignore').read()
        return check(hypothesis=file)
