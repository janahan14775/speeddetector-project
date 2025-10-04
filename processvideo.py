import requests

VIDEO_PATH = "test_video.mp4"
API_URL = "http://localhost:5000/v1/process_video"

with open(VIDEO_PATH, "rb") as f:
    files = {'video': f}
    data = {'frame_skip': 5}  # optional, process every 5th frame
    response = requests.post(API_URL, files=files, data=data)

if response.status_code == 200:
    print("Violations detected:")
    print(response.json())
else:
    print("Error:", response.status_code, response.text)

