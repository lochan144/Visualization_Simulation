"""
Distance calculation module for NavIC + LoRa monitoring system
Handles geodesic distance calculations and RSSI-based positioning
"""

import math
from geopy.distance import geodesic
import config


def calculate_cow_distances(human_pos, cow_data):
    """
    Calculate distances from human to each cow
    
    Args:
        human_pos: Tuple of (latitude, longitude) for human position
        cow_data: List of dictionaries containing cow position and RSSI data
    
    Returns:
        List of distances in meters for each cow
    """
    distances = []
    
    for cow in cow_data:
        cow_pos = (cow['lat'], cow['lon'])
        distance = geodesic(human_pos, cow_pos).meters
        distances.append(distance)
    
    return distances


def rssi_to_estimated_distance(rssi, rssi0=None, n=None):
    """
    Convert RSSI to approximate distance using path-loss formula
    
    Args:
        rssi: Received Signal Strength Indicator (dBm)
        rssi0: Reference RSSI at 1 meter (default from config)
        n: Path-loss exponent (default from config)
    
    Returns:
        Estimated distance in meters
    """
    if rssi0 is None:
        rssi0 = config.RSSI_REFERENCE
    if n is None:
        n = config.PATH_LOSS_EXPONENT
    
    # Path-loss formula: RSSI = RSSI0 - 10*n*log10(d)
    # Solving for d: d = 10^((RSSI0 - RSSI) / (10*n))
    distance = 10 ** ((rssi0 - rssi) / (10 * n))
    return distance


def determine_alert_status(distance, threshold=None):
    """
    Check if cow is within safe distance
    
    Args:
        distance: Distance in meters
        threshold: Safety threshold in meters (default from config)
    
    Returns:
        String: 'safe' or 'alert'
    """
    if threshold is None:
        threshold = config.DISTANCE_THRESHOLD
    
    return 'safe' if distance <= threshold else 'alert'


def calculate_position_from_rssi(human_pos, rssi, angle_offset=0):
    """
    Estimate cow position based on RSSI and a simulated angle
    
    Args:
        human_pos: Tuple of (latitude, longitude) for human position
        rssi: RSSI value in dBm
        angle_offset: Angle offset in degrees for positioning
    
    Returns:
        Tuple of estimated (latitude, longitude)
    """
    # Convert RSSI to distance
    estimated_distance = rssi_to_estimated_distance(rssi)
    
    # Add some variation to make it realistic (within 50-200 meters typically)
    estimated_distance = max(50, min(200, estimated_distance))
    
    # Convert distance to approximate coordinate offset
    # 1 degree ≈ 111,000 meters at equator
    lat_offset = (estimated_distance * math.cos(math.radians(angle_offset))) / 111000
    lon_offset = (estimated_distance * math.sin(math.radians(angle_offset))) / (111000 * math.cos(math.radians(human_pos[0])))
    
    estimated_lat = human_pos[0] + lat_offset
    estimated_lon = human_pos[1] + lon_offset
    
    return (estimated_lat, estimated_lon)


def get_distance_status_summary(human_pos, cow_data):
    """
    Get comprehensive distance and status information for all cows
    
    Args:
        human_pos: Tuple of (latitude, longitude) for human position
        cow_data: List of dictionaries containing cow data
    
    Returns:
        Dictionary with distance analysis and alert summary
    """
    distances = calculate_cow_distances(human_pos, cow_data)
    alert_count = 0
    safe_count = 0
    
    summary = {
        'human_position': human_pos,
        'cow_details': [],
        'total_cows': len(cow_data),
        'alerts_active': 0,
        'cows_safe': 0,
        'max_distance': 0,
        'min_distance': float('inf')
    }
    
    for i, (cow, distance) in enumerate(zip(cow_data, distances)):
        status = determine_alert_status(distance)
        
        if status == 'alert':
            alert_count += 1
        else:
            safe_count += 1
        
        cow_detail = {
            'id': i + 1,
            'position': (cow['lat'], cow['lon']),
            'rssi': cow['rssi'],
            'distance': round(distance, 2),
            'status': status
        }
        
        summary['cow_details'].append(cow_detail)
        summary['max_distance'] = max(summary['max_distance'], distance)
        summary['min_distance'] = min(summary['min_distance'], distance)
    
    summary['alerts_active'] = alert_count
    summary['cows_safe'] = safe_count
    summary['min_distance'] = round(summary['min_distance'], 2)
    summary['max_distance'] = round(summary['max_distance'], 2)
    
    return summary


def validate_coordinates(lat, lon):
    """
    Validate latitude and longitude coordinates
    
    Args:
        lat: Latitude value
        lon: Longitude value
    
    Returns:
        Boolean: True if coordinates are valid
    """
    return (-90 <= lat <= 90) and (-180 <= lon <= 180)


def calculate_bearing(pos1, pos2):
    """
    Calculate the bearing between two positions
    
    Args:
        pos1: Tuple of (latitude, longitude) for first position
        pos2: Tuple of (latitude, longitude) for second position
    
    Returns:
        Bearing in degrees (0-360)
    """
    lat1, lon1 = math.radians(pos1[0]), math.radians(pos1[1])
    lat2, lon2 = math.radians(pos2[0]), math.radians(pos2[1])
    
    dlon = lon2 - lon1
    
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing
