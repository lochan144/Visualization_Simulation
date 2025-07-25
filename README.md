# NavIC + LoRa Real-Time Distance Monitoring System

A comprehensive real-time livestock monitoring solution that simulates NavIC satellite positioning for humans and LoRa signal strength for livestock tracking. The system provides live visualization with automatic updates every 2 minutes and distance-based alerts.

## 🌟 Features

- **Real-time Monitoring**: Live updates every 2 minutes (120 seconds)
- **Human-centric Tracking**: NavIC satellite positioning simulation for human reference point
- **Livestock LoRa Tracking**: Two-cow monitoring with RSSI-based positioning
- **Distance Alerts**: Automatic alerts when livestock exceed 100m safe distance
- **Interactive Web Map**: Real-time browser-based visualization
- **Hardware-Ready**: Structured for easy integration with actual NavIC and LoRa hardware

## 📋 System Requirements

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Network connectivity for real-time updates
- Minimum 4GB RAM recommended

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd navic_lora_monitor

# Install required dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.py` to customize your setup:

```python
# Base coordinates (default: Bangalore, India)
BASE_COORDS = (12.9716, 77.5946)

# Update frequency (seconds)
UPDATE_INTERVAL = 120  # 2 minutes

# Distance threshold for alerts (meters)
DISTANCE_THRESHOLD = 100

# Web server settings
HOST = 'localhost'
PORT = 5000
```

### 3. Run the System

```bash
python app.py
```

### 4. Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## 🎯 How It Works

### Real-Time Operation
1. **Initialization**: System starts with base coordinates and begins monitoring loop
2. **Position Updates**: Every 2 minutes, the system:
   - Simulates human NavIC position with realistic movement
   - Generates cow LoRa RSSI signals and estimates positions
   - Calculates distances from human to each cow
   - Determines alert status based on distance threshold
3. **Live Broadcast**: Updates are automatically sent to all connected web clients
4. **Continuous Monitoring**: Process repeats indefinitely until manually stopped

### Distance Calculation
- **Reference Point**: Human position (NavIC simulation)
- **Target Entities**: Two cows with LoRa signal simulation
- **Calculation Method**: Geodesic distance using geopy library
- **Alert Threshold**: 100 meters (configurable)

### Data Flow
```
NavIC Simulation → Human Position
LoRa RSSI → Cow Positions → Distance Calculation → Alert Status → Map Update
```

## 🗂️ Project Structure

```
navic_lora_monitor/
├── app.py                 # Main Flask application & real-time server
├── simulation.py          # Position simulation for NavIC & LoRa
├── distance.py           # Distance calculations & alert logic
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── templates/
│   └── map.html         # Web interface template
├── static/
│   ├── css/
│   │   └── style.css    # Additional styling
│   └── js/
│       └── map.js       # Enhanced JavaScript functionality
└── README.md           # This file
```

## 🎮 Web Interface Features

### Main Dashboard
- **Live Map**: Interactive map with real-time position markers
- **Status Panel**: System information and connection status
- **Human Position**: Current NavIC coordinates and timestamp
- **Livestock Status**: Individual cow information with RSSI and distances
- **Alert Display**: Visual indicators for distance threshold breaches
- **Update Timer**: Countdown to next automatic update

### Map Elements
- **Human Marker**: Blue pin (👤) showing NavIC position
- **Cow Markers**: Colored circles indicating status
  - 🟢 Green: Safe (≤100m distance)
  - 🔴 Red: Alert (>100m distance)
- **Info Popups**: Click markers for detailed information
- **Auto-Refresh**: Map updates automatically without page reload

### Real-Time Features
- **Live Updates**: Automatic refresh every 2 minutes
- **Connection Status**: Visual indicator of server connectivity
- **Alert Notifications**: Immediate visual alerts for distance breaches
- **Multi-Client Support**: Multiple users can view simultaneously

## ⚙️ Configuration Options

### Timing Settings
```python
UPDATE_INTERVAL = 120        # Update frequency (seconds)
RECONNECT_TIMEOUT = 30       # Client reconnection timeout
MAX_RETRY_ATTEMPTS = 5       # Connection retry limit
```

### Distance Parameters
```python
DISTANCE_THRESHOLD = 100     # Alert distance (meters)
RSSI_REFERENCE = -40         # RSSI at 1 meter (dBm)
PATH_LOSS_EXPONENT = 2.7     # Signal propagation factor
```

### Movement Simulation
```python
HUMAN_MOVEMENT_RANGE = 0.001  # Human movement variation (degrees)
COW_MOVEMENT_RANGE = 0.002    # Cow movement variation (degrees)
RSSI_MIN = -120              # Minimum RSSI value (dBm)
RSSI_MAX = -30               # Maximum RSSI value (dBm)
```

## 🔧 Hardware Integration Ready

The system is designed for easy integration with real hardware:

### NavIC Integration
```python
# Replace simulation with actual NavIC receiver
def get_navic_position():
    # return serial_read_navic()  # Real hardware
    return simulate_navic_position()  # Current simulation
```

### LoRa Integration
```python
# Replace simulation with actual LoRa network
def get_lora_signals():
    # return lora_receiver.get_rssi_values()  # Real hardware
    return simulate_lora_signals()  # Current simulation
```

## 📊 Data Export & Analysis

### Export Features
- **Position History**: Track movement patterns over time
- **Alert History**: Log all distance threshold breaches
- **System Statistics**: Performance and connectivity metrics
- **JSON Format**: Standard format for data analysis

### Keyboard Shortcuts
- **Ctrl+E**: Export current data to JSON file
- **Ctrl+R**: Request immediate position update

## 🧪 Testing & Validation

### Simulation Testing
```python
# Test different scenarios
from simulation import simulator

# Normal operation
data = simulator.generate_test_scenario('normal')

# Force alert conditions
alert_data = simulator.generate_test_scenario('alert')

# Mixed conditions
mixed_data = simulator.generate_test_scenario('mixed')
```

### Performance Monitoring
- Monitor memory usage during extended operation
- Verify 2-minute update intervals with system logging
- Test real-time delivery across multiple browser sessions
- Validate distance calculations with known coordinates

## 🔍 Troubleshooting

### Common Issues

**Connection Problems**
- Check if port 5000 is available
- Verify firewall settings allow local connections
- Ensure all dependencies are installed correctly

**Map Not Loading**
- Check internet connection (required for map tiles)
- Verify JavaScript is enabled in browser
- Try refreshing the page or clearing browser cache

**Updates Not Appearing**
- Check browser console for error messages
- Verify WebSocket connection is established
- Restart the application if issues persist

### Debug Mode
Enable detailed logging by setting `DEBUG = True` in `config.py`

### Log Files
System logs appear in the console with timestamps and severity levels:
```
2024-07-25 10:30:15 - INFO - Update #5 completed
2024-07-25 10:30:15 - WARNING - ALERT: 1 cow(s) beyond safe distance!
```

## 🚀 Advanced Features

### Multi-Animal Support
Easily extend to monitor more livestock:
```python
# In simulation.py, modify num_cows parameter
cow_data = self.simulate_lora_signals(human_pos, num_cows=5)
```

### Custom Alert Zones
Add multiple distance thresholds:
```python
# In distance.py
def determine_multiple_alert_levels(distance):
    if distance <= 50:
        return 'safe'
    elif distance <= 100:
        return 'caution'
    else:
        return 'alert'
```

### Historical Tracking
Store data for pattern analysis:
```python
# Add database integration
import sqlite3

def store_position_data(timestamp, human_pos, cow_data):
    # Store in database for historical analysis
    pass
```

## 🌐 Deployment Options

### Local Network Access
Change `HOST = '0.0.0.0'` in `config.py` to allow network access

### Cloud Deployment
- **Heroku**: Use `Procfile` with `web: python app.py`
- **AWS**: Deploy using Elastic Beanstalk or EC2
- **Docker**: Containerize with provided Dockerfile template

### Mobile Access
The web interface is responsive and works on smartphones and tablets

## 📈 Future Enhancements

### Planned Features
- **Mobile App**: Native smartphone application
- **SMS Alerts**: Text message notifications for critical distances
- **Machine Learning**: Predictive analysis for animal behavior
- **Cloud Database**: Historical data storage and analytics
- **Multi-Farm Support**: Monitor multiple locations simultaneously

### Hardware Roadmap
- **NavIC Receiver Integration**: Real satellite positioning
- **LoRa Network Setup**: Actual livestock transmitters
- **Sensor Expansion**: Temperature, heart rate, activity monitoring
- **Power Management**: Solar-powered field deployment

## 📞 Support & Contributing

### Getting Help
- Check the troubleshooting section above
- Review system logs for error messages
- Ensure all dependencies are correctly installed

### Contributing
Contributions are welcome! Areas for improvement:
- Additional visualization features
- Enhanced alert mechanisms
- Hardware integration modules
- Performance optimizations
- Documentation improvements

## 📄 License

This project is designed for educational and development purposes. Ensure compliance with local regulations for livestock monitoring and satellite positioning systems.

## 🙏 Acknowledgments

- **NavIC**: Indian Regional Navigation Satellite System
- **LoRa**: Long Range wireless communication protocol
- **Flask-SocketIO**: Real-time web communication
- **Leaflet.js**: Interactive mapping library
- **OpenStreetMap**: Map tile provider

---

*NavIC + LoRa Real-Time Distance Monitoring System - Bringing precision livestock tracking to modern agriculture* 🛰️🐄📍
