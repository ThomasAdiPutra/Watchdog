import requests
import os

class Store:
    def __init__(self):
        print("Store initialized")
        
    def upload_to_server(self, filename, path, event_type, event_time):
        try:
            file = {
                'file': open(path, 'rb'),
                'path': path,
                'filename': filename,
                'event_type': event_type,
                'event_time': event_time,
            }
            url = "http://172.16.40.117:5000"
            r = requests.post(url, file=file)
        except Exception as e:
            print(f"Error uploading file: {e}")
            