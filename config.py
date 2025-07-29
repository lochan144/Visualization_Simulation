# Configuration settings for NavIC + LoRa monitoring system

# Base coordinates (Bangalore, India)
BASE_COORDS = (12.9716, 77.5946)

# Timing settings
UPDATE_INTERVAL = 120  # Update frequency in seconds (2 minutes)
RECONNECT_TIMEOUT = 30  # Client reconnection timeout
MAX_RETRY_ATTEMPTS = 5  # Connection retry limit

# Distance parameters
DISTANCE_THRESHOLD = 100  # Alert distance in meters
RSSI_REFERENCE = -40  # RSSI at 1 meter (dBm)
PATH_LOSS_EXPONENT = 2.7  # Signal propagation factor

# Visualization settings
MAP_ZOOM_LEVEL = 15  # Initial map zoom
MARKER_SIZES = {
    'human': 8,
    'cow_safe': 6,
    'cow_alert': 6
}

COLORS = {
    'human': 'blue',
    'safe': 'blue',
    'alert': 'red'
}

# Movement simulation parameters
HUMAN_MOVEMENT_RANGE = 0.001  # Degrees of movement variation
COW_MOVEMENT_RANGE = 0.002  # Degrees of movement variation for cows

# RSSI simulation range
RSSI_MIN = -120  # Minimum RSSI value (dBm)
RSSI_MAX = -30   # Maximum RSSI value (dBm)

# Web server settings
HOST = 'localhost'
PORT = 5000
DEBUG = True

# Fixed position mode
FIXED_POSITION_MODE = True  # Set to True to keep human at fixed location
FIXED_HUMAN_COORDS = (12.9183899, 77.5917152)  # Fixed coordinates when in fixed mode
