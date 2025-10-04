import math
from collections import OrderedDict

class Track:
    def __init__(self, track_id, centroid, timestamp):
        self.id = track_id
        self.centroid = centroid
        self.last_timestamp = timestamp
        self.history = [(timestamp, centroid)]
        self.lost = 0

class CentroidTracker:
    def __init__(self, max_lost=5, meters_per_pixel=0.02):
        self.next_object_id = 1
        self.tracks = OrderedDict()
        self.max_lost = max_lost
        self.meters_per_pixel = meters_per_pixel

    def _euclid(self, a, b):
        return math.hypot(a[0]-b[0], a[1]-b[1])

    def update(self, detections, timestamp):
        centers = [d['center'] for d in detections]
        if len(self.tracks) == 0:
            for c in centers:
                t = Track(self.next_object_id, c, timestamp)
                self.tracks[self.next_object_id] = t
                self.next_object_id += 1
        else:
            track_ids = list(self.tracks.keys())
            track_centroids = [self.tracks[tid].centroid for tid in track_ids]
            if len(centers) == 0:
                for tid in list(self.tracks.keys()):
                    self.tracks[tid].lost += 1
            else:
                D = [[self._euclid(tc, cc) for cc in centers] for tc in track_centroids]
                matched_tracks, matched_dets = set(), set()
                while True:
                    min_val = float('inf')
                    min_i = min_j = -1
                    for i in range(len(D)):
                        for j in range(len(D[i])):
                            if D[i][j] < min_val:
                                min_val = D[i][j]
                                min_i, min_j = i, j
                    if min_val == float('inf'):
                        break
                    tid = track_ids[min_i]
                    self.tracks[tid].centroid = centers[min_j]
                    self.tracks[tid].last_timestamp = timestamp
                    self.tracks[tid].history.append((timestamp, centers[min_j]))
                    self.tracks[tid].lost = 0
                    matched_tracks.add(min_i)
                    matched_dets.add(min_j)
                    for k in range(len(D)):
                        D[k][min_j] = float('inf')
                    D[min_i] = [float('inf')] * len(D[min_i])
                for j, c in enumerate(centers):
                    if j not in matched_dets:
                        t = Track(self.next_object_id, c, timestamp)
                        self.tracks[self.next_object_id] = t
                        self.next_object_id += 1
                for i, tid in enumerate(track_ids):
                    if i not in matched_tracks:
                        self.tracks[tid].lost += 1
                to_delete = [tid for tid, tr in self.tracks.items() if tr.lost > self.max_lost]
                for tid in to_delete:
                    del self.tracks[tid]

        results = []
        for tid, tr in self.tracks.items():
            speed_m_s = None
            if len(tr.history) >= 2:
                (t1, p1), (t2, p2) = tr.history[-2], tr.history[-1]
                dt = t2 - t1
                if dt > 0:
                    pixel_dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                    meters = pixel_dist * self.meters_per_pixel
                    speed_m_s = meters / dt
            results.append({
                'id': tid,
                'center': tr.centroid,
                'speed_m_s': speed_m_s,
                'timestamp': tr.last_timestamp
            })
        return results

