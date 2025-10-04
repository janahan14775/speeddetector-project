# config.py

# MongoDB
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "speed_db"
VEHICLE_COLLECTION = "vehicles"
VIOLATIONS_COLLECTION = "violations"

# Calibration & detection
METERS_PER_PIXEL = 0.02
DETECT_CONFIDENCE = 0.35
DEFAULT_FPS = 30.0
SPEED_LIMIT_KMPH = 100.0

# Twilio (optional)
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_FROM_NUMBER = None

# Misc
ANPR_DEBUG = False

