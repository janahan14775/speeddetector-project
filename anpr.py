import cv2
import pytesseract
import numpy as np
import os
from config import ANPR_DEBUG

def clean_text(text):
    import re
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def read_plate_from_vehicle(frame, bbox, save_debug=False):
    x1,y1,x2,y2 = map(int, bbox)
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w-1, x2), min(h-1, y2)
    crop = frame[y1:y2, x1:x2].copy()
    if crop.size == 0:
        return None

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    possible_regions = []
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.06 * peri, True)
        if len(approx) == 4:
            (x, y, w_r, h_r) = cv2.boundingRect(approx)
            aspect = w_r / float(h_r) if h_r>0 else 0
            area = w_r * h_r
            if area > 500 and 2 <= aspect <= 7:
                possible_regions.append((x,y,w_r,h_r,area,aspect))

    possible_regions = sorted(possible_regions, key=lambda r: r[4], reverse=True)
    plates = []
    candidates = possible_regions[:3]
    if len(candidates)==0:
        candidates = [(0,0,crop.shape[1], crop.shape[0], crop.shape[1]*crop.shape[0], 1.0)]

    for (x,y,w_r,h_r,_,_) in candidates:
        roi = crop[y:y+h_r, x:x+w_r]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_gray = cv2.resize(roi_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, roi_bin = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(roi_bin, config=config)
        cleaned = clean_text(text)
        if cleaned and len(cleaned) >= 4:
            plates.append(cleaned)
            if ANPR_DEBUG and save_debug:
                os.makedirs("anpr_debug", exist)

