"""
Position simulation module for NavIC + LoRa monitoring system
Generates realistic positioning data when hardware is unavailable
"""

import random
import time
import math
from datetime import datetime
import config
from distance import calculate_position_from_rssi


class PositionSimulator:
    """Handles simulation of NavIC and LoRa positioning data"""
    
    def __init__(self):
        self.base_lat, self.base_lon = config.BASE_COORDS
        self.human_pos = (self.base_lat, self.base_lon)
        self.cow_positions = [
            (self.base_lat + 0.001, self.base_lon + 0.001),  # Cow 1
            (self.base_lat - 0.001, self.base_lon + 0.002)   # Cow 2
        ]
        self.simulation_start_time = time.time()
    
    def simulate_navic_position(self, base_lat=None, base_lon=None):
        """
        Simulate realistic human movement using NavIC positioning
        
        Args:
            base_lat: Base latitude (optional, uses config default)
            base_lon: Base longitude (optional, uses config default)
        
        Returns:
            Tuple of (latitude, longitude) for current human position
        """
        if base_lat is None:
            base_lat = self.base_lat
        if base_lon is None:
            base_lon = self.base_lon
        
        # Create realistic movement pattern
        elapsed_time = time.time() - self.simulation_start_time
        
        # Slow walking pattern with some randomness
        movement_scale = config.HUMAN_MOVEMENT_RANGE
        
        # Use sine wave for smooth movement with random component
        lat_variation = movement_scale * (
            0.5 * math.sin(elapsed_time / 60) +  # 1-minute cycle
            0.3 * random.uniform(-1, 1)         # Random component
        )
        
        lon_variation = movement_scale * (
            0.5 * math.cos(elapsed_time / 80) +  # Slightly different cycle
            0.3 * random.uniform(-1, 1)         # Random component
        )
        
        new_lat = base_lat + lat_variation
        new_lon = base_lon + lon_variation
        
        # Update internal position
        self.human_pos = (new_lat, new_lon)
        
        return self.human_pos
    
    def simulate_lora_signals(self, human_pos, num_cows=2):
        """
        Generate RSSI values and estimate cow positions based on signal strength
        
        Args:
            human_pos: Tuple of (latitude, longitude) for human position
            num_cows: Number of cows to simulate (default: 2)
        
        Returns:
            List of dictionaries containing cow data with positions and RSSI
        """
        cow_data = []
        
        for i in range(num_cows):
            # Simulate RSSI with realistic values
            # Closer cows have stronger signals (less negative RSSI)
            base_rssi = random.uniform(config.RSSI_MIN, config.RSSI_MAX)
            
            # Add some time-based variation to simulate movement
            elapsed_time = time.time() - self.simulation_start_time
            rssi_variation = 5 * math.sin(elapsed_time / (30 + i * 10))  # Different periods for each cow
            current_rssi = base_rssi + rssi_variation
            
            # Ensure RSSI stays within realistic bounds
            current_rssi = max(config.RSSI_MIN, min(config.RSSI_MAX, current_rssi))
            
            # Calculate estimated position based on RSSI
            # Use different angle offsets for each cow
            angle_offset = i * 120 + (elapsed_time / 10) % 360  # Rotating positions
            estimated_pos = calculate_position_from_rssi(human_pos, current_rssi, angle_offset)
            
            # Add some random movement to cow positions
            movement_scale = config.COW_MOVEMENT_RANGE
            lat_noise = movement_scale * random.uniform(-0.5, 0.5)
            lon_noise = movement_scale * random.uniform(-0.5, 0.5)
            
            final_lat = estimated_pos[0] + lat_noise
            final_lon = estimated_pos[1] + lon_noise
            
            cow_info = {
                'id': i + 1,
                'lat': final_lat,
                'lon': final_lon,
                'rssi': round(current_rssi, 1),
                'timestamp': datetime.now().isoformat(),
                'signal_quality': self._assess_signal_quality(current_rssi)
            }
            
            cow_data.append(cow_info)
            
            # Update internal cow positions
            if i < len(self.cow_positions):
                self.cow_positions[i] = (final_lat, final_lon)
        
        return cow_data
    
    def _assess_signal_quality(self, rssi):
        """
        Assess LoRa signal quality based on RSSI value
        
        Args:
            rssi: RSSI value in dBm
        
        Returns:
            String describing signal quality
        """
        if rssi > -70:
            return 'Excellent'
        elif rssi > -85:
            return 'Good'
        elif rssi > -100:
            return 'Fair'
        else:
            return 'Poor'
    
    def get_current_positions(self):
        """
        Get current positions for human and all cows
        
        Returns:
            Dictionary with human coordinates and cow data
        """
        # Update human position with NavIC simulation
        human_coords = self.simulate_navic_position()
        
        # Generate cow positions with LoRa simulation
        cow_data = self.simulate_lora_signals(human_coords)
        
        return {
            'human': {
                'lat': human_coords[0],
                'lon': human_coords[1],
                'timestamp': datetime.now().isoformat(),
                'positioning_system': 'NavIC'
            },
            'cows': cow_data,
            'system_time': datetime.now().isoformat(),
            'update_interval': config.UPDATE_INTERVAL
        }
    
    def generate_test_scenario(self, scenario_type='normal'):
        """
        Generate specific test scenarios for system validation
        
        Args:
            scenario_type: Type of scenario ('normal', 'alert', 'mixed')
        
        Returns:
            Position data for the specified scenario
        """
        human_pos = self.simulate_navic_position()
        
        if scenario_type == 'alert':
            # Force cows to be beyond alert threshold
            cow_data = []
            for i in range(2):
                # Place cows at distances > 100m
                distance = random.uniform(120, 200)
                angle = random.uniform(0, 360)
                
                lat_offset = (distance * math.cos(math.radians(angle))) / 111000
                lon_offset = (distance * math.sin(math.radians(angle))) / (111000 * math.cos(math.radians(human_pos[0])))
                
                cow_lat = human_pos[0] + lat_offset
                cow_lon = human_pos[1] + lon_offset
                
                # Generate corresponding RSSI for this distance
                rssi = config.RSSI_REFERENCE - 10 * config.PATH_LOSS_EXPONENT * math.log10(distance)
                rssi = max(config.RSSI_MIN, min(config.RSSI_MAX, rssi))
                
                cow_data.append({
                    'id': i + 1,
                    'lat': cow_lat,
                    'lon': cow_lon,
                    'rssi': round(rssi, 1),
                    'timestamp': datetime.now().isoformat(),
                    'signal_quality': self._assess_signal_quality(rssi)
                })
        
        elif scenario_type == 'normal':
            # Keep cows within safe distance
            cow_data = self.simulate_lora_signals(human_pos)
            
        else:  # mixed scenario
            cow_data = self.simulate_lora_signals(human_pos)
            
        return {
            'human': {
                'lat': human_pos[0],
                'lon': human_pos[1],
                'timestamp': datetime.now().isoformat(),
                'positioning_system': 'NavIC'
            },
            'cows': cow_data,
            'system_time': datetime.now().isoformat(),
            'scenario_type': scenario_type
        }
    
    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.human_pos = (self.base_lat, self.base_lon)
        self.cow_positions = [
            (self.base_lat + 0.001, self.base_lon + 0.001),
            (self.base_lat - 0.001, self.base_lon + 0.002)
        ]
        self.simulation_start_time = time.time()


# Global simulator instance
simulator = PositionSimulator()


def get_current_positions():
    """
    Convenience function to get current positions
    
    Returns:
        Current position data for human and cows
    """
    return simulator.get_current_positions()


def simulate_navic_position(base_lat=None, base_lon=None):
    """
    Convenience function for NavIC position simulation
    
    Args:
        base_lat: Base latitude
        base_lon: Base longitude
    
    Returns:
        Tuple of (latitude, longitude) for human position
    """
    return simulator.simulate_navic_position(base_lat, base_lon)


def simulate_lora_signals(human_pos, num_cows=2):
    """
    Convenience function for LoRa signal simulation
    
    Args:
        human_pos: Human position tuple
        num_cows: Number of cows to simulate
    
    Returns:
        List of cow data with RSSI and positions
    """
    return simulator.simulate_lora_signals(human_pos, num_cows)
