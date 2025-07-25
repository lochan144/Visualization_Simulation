"""
System status checker for NavIC + LoRa monitoring system
"""

import requests
import json
import sys
import os

def check_system_status():
    """Check if the monitoring system is running and display status"""
    
    print("🔍 NavIC + LoRa System Status Check")
    print("=" * 40)
    
    try:
        # Check if web server is responding
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        
        if response.status_code == 200:
            status_data = response.json()
            
            print("✅ System Status: RUNNING")
            print(f"📊 Updates Completed: {status_data.get('update_count', 'N/A')}")
            print(f"🔗 Connected Clients: {status_data.get('connected_clients', 'N/A')}")
            print(f"⏱️ System Uptime: {status_data.get('uptime_seconds', 0):.1f} seconds")
            print(f"📅 Last Update: {status_data.get('last_update', 'N/A')}")
            print(f"🚨 Recent Alerts: {status_data.get('recent_alerts', 'N/A')}")
            
            # Check current data
            try:
                data_response = requests.get('http://localhost:5000/api/current_data', timeout=5)
                if data_response.status_code == 200:
                    current_data = data_response.json()
                    
                    print("\n📍 Current Position Data:")
                    if 'human' in current_data:
                        human = current_data['human']
                        print(f"   👤 Human (NavIC): {human['lat']:.6f}, {human['lon']:.6f}")
                    
                    if 'cows' in current_data:
                        print(f"   🐄 Tracking {len(current_data['cows'])} cows:")
                        for cow in current_data['cows']:
                            status_icon = "🟢" if cow.get('status') == 'safe' else "🔴"
                            distance = cow.get('distance', 0)
                            rssi = cow.get('rssi', 'N/A')
                            status = cow.get('status', 'unknown').upper()
                            print(f"      {status_icon} Cow #{cow['id']}: {distance:.1f}m, {rssi} dBm ({status})")
                    
                    alert_count = current_data.get('alerts_active', 0)
                    safe_count = current_data.get('cows_safe', 0)
                    print(f"\n📈 Summary: {safe_count} safe, {alert_count} alerts")
                    
            except Exception as e:
                print(f"\n⚠️ Could not fetch current data: {e}")
        
        else:
            print(f"❌ System Status: ERROR (HTTP {response.status_code})")
    
    except requests.exceptions.ConnectionError:
        print("❌ System Status: NOT RUNNING")
        print("💡 To start the system, run: python app.py")
    
    except requests.exceptions.Timeout:
        print("⏳ System Status: TIMEOUT")
        print("💡 System may be starting up or overloaded")
    
    except Exception as e:
        print(f"❌ System Status: ERROR - {e}")
    
    print("\n🌐 Web Interface: http://localhost:5000")
    print("🔧 To start system: python app.py")
    print("📊 To run demo: python demo.py")
    print("=" * 40)

if __name__ == "__main__":
    check_system_status()
