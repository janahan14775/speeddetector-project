from flask import Flask, request, jsonify
import cv2
import time
import numpy as np
from detector import YoloDetector
from tracker import CentroidTracker
from anpr import read_plate_from_vehicle
from storage import store_violation, list_violations
from config import SPEED_LIMIT_KMPH

app = Flask(__name__)

detector = YoloDetector()
tracker = CentroidTracker()

def process_frame(frame, timestamp=None):
    if timestamp is None:
        timestamp = time.time()
    detections = detector.detect(frame)
    tracked = tracker.update(detections, timestamp)
    results = []
    for det, trk in zip(detections, tracked):
        speed_kmph = trk['speed_m_s'] * 3.6 if trk['speed_m_s'] else 0
        plate = None
        if speed_kmph > SPEED_LIMIT_KMPH:
            plate = read_plate_from_vehicle(frame, det['bbox'])
            if plate:
                store_violation(plate, speed_kmph, timestamp, trk['id'])
        results.append({
            "track_id": trk['id'],
            "speed_m_s": trk['speed_m_s'],
            "speed_kmph": speed_kmph,
            "class_name": det['class_name'],
            "bbox": det['bbox'],
            "center": det['center'],
            "timestamp": timestamp,
            "plate": plate
        })
    return results

@app.route('/v1/process_frame', methods=['POST'])
def api_process_frame():
    if 'frame' not in request.files:
        return jsonify({'error':'frame missing'}), 400
    file = request.files['frame']
    file_bytes = file.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    results = process_frame(frame)
    return jsonify({'results': results})

@app.route('/v1/process_video', methods=['POST'])
def api_process_video():
    if 'video' not in request.files:
        return jsonify({'error': 'video file missing'}), 400

    file = request.files['video']
    frame_skip = int(request.form.get('frame_skip', 1))

    import tempfile
    temp_vid = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    file.save(temp_vid.name)

    cap = cv2.VideoCapture(temp_vid.name)
    if not cap.isOpened():
        return jsonify({'error': 'cannot open video'}), 400

    frame_count = 0
    violations_detected = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        results = process_frame(frame, timestamp=None)
        for r in results:
            if r.get('plate') and r.get('speed_kmph') and r['speed_kmph'] > SPEED_LIMIT_KMPH:
                violations_detected.append(r)

    cap.release()

    return jsonify({
        'video_name': file.filename,
        'frames_processed': frame_count,
        'violations_detected': violations_detected,
        'total_violations': len(violations_detected)
    })

@app.route('/v1/list_violations', methods=['GET'])
def api_list_violations():
    return jsonify(list_violations())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

