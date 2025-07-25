"""
Demonstration script for NavIC + LoRa monitoring system
Shows different scenarios and system capabilities
"""

import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation import simulator
from distance import get_distance_status_summary
import config

def demonstrate_system():
    """Demonstrate the monitoring system capabilities"""
    
    print("=" * 60)
    print("🛰️ NavIC + LoRa Real-Time Monitoring System Demo")
    print("=" * 60)
    print()
    
    print("📍 System Configuration:")
    print(f"   Base Location: {config.BASE_COORDS} (Bangalore, India)")
    print(f"   Update Interval: {config.UPDATE_INTERVAL} seconds (2 minutes)")
    print(f"   Distance Threshold: {config.DISTANCE_THRESHOLD} meters")
    print(f"   RSSI Range: {config.RSSI_MIN} to {config.RSSI_MAX} dBm")
    print()
    
    scenarios = [
        ('normal', '✅ Normal Operation - All cows within safe distance'),
        ('alert', '🚨 Alert Scenario - Cows beyond safe distance'),
        ('mixed', '⚠️ Mixed Scenario - Some cows safe, some alert')
    ]
    
    for scenario_type, description in scenarios:
        print(f"{description}")
        print("-" * 50)
        
        # Generate test scenario
        data = simulator.generate_test_scenario(scenario_type)
        
        # Get status summary
        human_pos = (data['human']['lat'], data['human']['lon'])
        status_summary = get_distance_status_summary(human_pos, data['cows'])
        
        # Display results
        print(f"🧑 Human Position (NavIC): {human_pos[0]:.6f}, {human_pos[1]:.6f}")
        print(f"📊 System Status:")
        print(f"   Total Cows: {status_summary['total_cows']}")
        print(f"   Cows Safe: {status_summary['cows_safe']}")
        print(f"   Active Alerts: {status_summary['alerts_active']}")
        print(f"   Distance Range: {status_summary['min_distance']}m - {status_summary['max_distance']}m")
        print()
        
        print("🐄 Individual Cow Status:")
        for cow_detail in status_summary['cow_details']:
            status_icon = "🟢" if cow_detail['status'] == 'safe' else "🔴"
            print(f"   {status_icon} Cow #{cow_detail['id']}: {cow_detail['distance']}m away, "
                  f"RSSI: {cow_detail['rssi']} dBm ({cow_detail['status'].upper()})")
        
        print()
        print("⏱️ Next scenario in 3 seconds...")
        time.sleep(3)
        print()
    
    print("🎯 Real-Time System Features:")
    print("   • Automatic updates every 2 minutes")
    print("   • Live web interface at http://localhost:5000")
    print("   • Interactive map with real-time markers")
    print("   • Distance-based color coding (Green=Safe, Red=Alert)")
    print("   • WebSocket communication for instant updates")
    print("   • Multi-client support for simultaneous viewing")
    print("   • Hardware-ready architecture for NavIC/LoRa integration")
    print()
    
    print("🌐 Web Interface Features:")
    print("   • Real-time position tracking")
    print("   • Visual distance alerts")
    print("   • Connection status monitoring")
    print("   • System statistics display")
    print("   • Interactive map markers with detailed popups")
    print("   • Countdown timer for next update")
    print("   • Export functionality (Ctrl+E)")
    print("   • Manual update requests (Ctrl+R)")
    print()
    
    print("✨ Demo completed! The system is now running with real 2-minute updates.")
    print("   Visit http://localhost:5000 to see the live monitoring interface.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        demonstrate_system()
    except KeyboardInterrupt:
        print("\n🔴 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
    finally:
        print("🔚 Demo session ended")
