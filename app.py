"""
Main Flask application for NavIC + LoRa Real-Time Distance Monitoring
Provides web interface with real-time updates every 2 minutes
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
import logging

# Import our modules
import config
from simulation import get_current_positions
from distance import (
    calculate_cow_distances, 
    determine_alert_status,
    get_distance_status_summary
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'navic_lora_monitoring_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for monitoring
monitoring_active = False
current_data = None
connected_clients = 0
update_thread = None


class MonitoringSystem:
    """Handles the real-time monitoring operations"""
    
    def __init__(self):
        self.is_running = False
        self.update_count = 0
        self.start_time = datetime.now()
        self.last_update = None
        self.alert_history = []
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        self.is_running = True
        self.start_time = datetime.now()
        logger.info("🛰️ NavIC + LoRa monitoring system started")
        logger.info(f"📍 Base coordinates: {config.BASE_COORDS}")
        logger.info(f"⏱️ Update interval: {config.UPDATE_INTERVAL} seconds")
        logger.info(f"📏 Distance threshold: {config.DISTANCE_THRESHOLD} meters")
        
        while self.is_running:
            try:
                self.perform_update_cycle()
                time.sleep(config.UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(5)  # Brief pause before retry
    
    def perform_update_cycle(self):
        """Perform a single update cycle"""
        global current_data
        
        try:
            # Get current positions from simulation
            position_data = get_current_positions()
            
            # Calculate distances and status
            human_pos = (position_data['human']['lat'], position_data['human']['lon'])
            cow_data = position_data['cows']
            
            # Calculate distances from human to each cow
            distances = calculate_cow_distances(human_pos, cow_data)
            
            # Update cow data with distance and status information
            for i, (cow, distance) in enumerate(zip(cow_data, distances)):
                cow['distance'] = distance
                cow['status'] = determine_alert_status(distance)
            
            # Get comprehensive status summary
            status_summary = get_distance_status_summary(human_pos, cow_data)
            
            # Prepare data for transmission
            current_data = {
                'human': position_data['human'],
                'cows': cow_data,
                'system_time': position_data['system_time'],
                'update_count': self.update_count,
                'alerts_active': status_summary['alerts_active'],
                'cows_safe': status_summary['cows_safe'],
                'distance_summary': {
                    'min_distance': status_summary['min_distance'],
                    'max_distance': status_summary['max_distance']
                }
            }
            
            # Log update information
            self.update_count += 1
            self.last_update = datetime.now()
            
            logger.info(f"📊 Update #{self.update_count} completed")
            logger.info(f"👤 Human: {human_pos[0]:.6f}, {human_pos[1]:.6f}")
            
            alert_cows = [cow for cow in cow_data if cow['status'] == 'alert']
            if alert_cows:
                logger.warning(f"🚨 ALERT: {len(alert_cows)} cow(s) beyond safe distance!")
                for cow in alert_cows:
                    logger.warning(f"   Cow #{cow['id']}: {cow['distance']:.1f}m away")
                    self.alert_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'cow_id': cow['id'],
                        'distance': cow['distance'],
                        'rssi': cow['rssi']
                    })
            else:
                logger.info(f"✅ All {len(cow_data)} cows within safe distance")
            
            # Broadcast to all connected clients
            socketio.emit('position_update', current_data, namespace='/')
            
            # Send system status
            socketio.emit('system_status', {
                'message': f'Update #{self.update_count} completed',
                'timestamp': self.last_update.isoformat(),
                'connected_clients': connected_clients,
                'alerts_active': status_summary['alerts_active']
            }, namespace='/')
            
        except Exception as e:
            logger.error(f"Error in update cycle: {e}")
            socketio.emit('system_status', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("🔴 Monitoring system stopped")
    
    def get_status(self):
        """Get current system status"""
        uptime = datetime.now() - self.start_time if self.start_time else None
        return {
            'is_running': self.is_running,
            'update_count': self.update_count,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'uptime_seconds': uptime.total_seconds() if uptime else 0,
            'connected_clients': connected_clients,
            'recent_alerts': len([a for a in self.alert_history if 
                                (datetime.now() - datetime.fromisoformat(a['timestamp'])).total_seconds() < 3600])
        }


# Initialize monitoring system
monitoring_system = MonitoringSystem()


@app.route('/')
def index():
    """Serve the main monitoring interface"""
    return render_template('map.html')


@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return json.dumps(monitoring_system.get_status())


@app.route('/api/current_data')
def api_current_data():
    """API endpoint for current position data"""
    global current_data
    if current_data:
        return json.dumps(current_data)
    else:
        return json.dumps({'error': 'No data available yet'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global connected_clients
    connected_clients += 1
    logger.info(f"🔗 Client connected. Total clients: {connected_clients}")
    
    # Send current data to newly connected client
    if current_data:
        emit('position_update', current_data)
    
    # Send welcome message
    emit('system_status', {
        'message': 'Connected to NavIC + LoRa monitoring system',
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'update_interval': config.UPDATE_INTERVAL,
            'distance_threshold': config.DISTANCE_THRESHOLD,
            'base_coordinates': config.BASE_COORDS
        }
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    logger.info(f"🔌 Client disconnected. Total clients: {connected_clients}")


@socketio.on('request_update')
def handle_request_update():
    """Handle manual update requests from clients"""
    logger.info("📱 Manual update requested by client")
    if current_data:
        emit('position_update', current_data)
    else:
        emit('system_status', {
            'message': 'No data available yet, please wait for next update cycle',
            'timestamp': datetime.now().isoformat()
        })


@socketio.on('request_status')
def handle_request_status():
    """Handle status requests from clients"""
    status = monitoring_system.get_status()
    emit('system_status', status)


def start_monitoring_thread():
    """Start the monitoring system in a separate thread"""
    global update_thread
    if update_thread is None or not update_thread.is_alive():
        update_thread = threading.Thread(
            target=monitoring_system.start_monitoring,
            daemon=True
        )
        update_thread.start()
        logger.info("🚀 Monitoring thread started")


def create_live_map(human_pos, cow_data):
    """
    Create a live map with current positions (legacy function for compatibility)
    Note: Map generation is now handled by the frontend JavaScript
    """
    # This function is kept for potential server-side map generation
    # Currently, all map rendering is done client-side for better performance
    pass


def broadcast_updates():
    """
    Broadcast updates to connected clients (legacy function)
    Note: Broadcasting is now handled directly in the monitoring cycle
    """
    # This function is kept for compatibility
    # Actual broadcasting happens in perform_update_cycle()
    pass


if __name__ == '__main__':
    try:
        logger.info("🌟 Starting NavIC + LoRa Real-Time Monitoring System")
        logger.info("=" * 60)
        logger.info(f"🖥️ Web interface: http://{config.HOST}:{config.PORT}")
        logger.info(f"📊 Monitoring dashboard: Real-time updates every {config.UPDATE_INTERVAL}s")
        logger.info(f"🎯 Distance threshold: {config.DISTANCE_THRESHOLD}m")
        logger.info("=" * 60)
        
        # Start monitoring in background thread
        start_monitoring_thread()
        
        # Start Flask-SocketIO server
        socketio.run(
            app,
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False  # Disable reloader to prevent thread issues
        )
        
    except KeyboardInterrupt:
        logger.info("\n🔴 Shutting down monitoring system...")
        monitoring_system.stop_monitoring()
        logger.info("✅ System shutdown complete")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        monitoring_system.stop_monitoring()
    finally:
        logger.info("👋 NavIC + LoRa monitoring system terminated")
