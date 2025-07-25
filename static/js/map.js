// Additional JavaScript functionality for map interactions
// Enhanced real-time features and UI improvements

class MonitoringDashboard {
    constructor() {
        this.alertHistory = [];
        this.positionHistory = [];
        this.maxHistoryLength = 100;
        this.isMapInitialized = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    // Track alert history for analytics
    trackAlert(cowId, distance, timestamp) {
        const alert = {
            cowId: cowId,
            distance: distance,
            timestamp: timestamp,
            type: 'distance_alert'
        };
        
        this.alertHistory.push(alert);
        
        // Keep only recent alerts
        if (this.alertHistory.length > this.maxHistoryLength) {
            this.alertHistory.shift();
        }
        
        this.updateAlertStatistics();
    }
    
    // Track position history for movement analysis
    trackPosition(human, cows, timestamp) {
        const positionRecord = {
            timestamp: timestamp,
            human: human,
            cows: cows
        };
        
        this.positionHistory.push(positionRecord);
        
        // Keep only recent positions
        if (this.positionHistory.length > this.maxHistoryLength) {
            this.positionHistory.shift();
        }
    }
    
    // Update alert statistics display
    updateAlertStatistics() {
        const recentAlerts = this.alertHistory.filter(alert => {
            const alertTime = new Date(alert.timestamp);
            const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
            return alertTime > hourAgo;
        });
        
        // Could add a statistics panel to the UI
        console.log(`Recent alerts (last hour): ${recentAlerts.length}`);
    }
    
    // Enhanced marker creation with custom icons
    createCustomMarker(position, type, data) {
        let icon, popupContent;
        
        switch (type) {
            case 'human':
                icon = L.divIcon({
                    html: '<div class="human-icon">👤</div>',
                    className: 'custom-div-icon',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                });
                
                popupContent = `
                    <div class="popup-content">
                        <h4>👤 Human Position</h4>
                        <p><strong>NavIC Coordinates:</strong><br>
                        ${position[0].toFixed(6)}, ${position[1].toFixed(6)}</p>
                        <p><strong>Timestamp:</strong><br>
                        ${new Date(data.timestamp).toLocaleString()}</p>
                        <p><strong>Positioning System:</strong> ${data.positioning_system}</p>
                    </div>
                `;
                break;
                
            case 'cow':
                const isAlert = data.status === 'alert';
                const iconColor = isAlert ? '#dc3545' : '#28a745';
                const iconSymbol = isAlert ? '⚠️' : '🐄';
                
                icon = L.divIcon({
                    html: `<div class="cow-icon" style="background-color: ${iconColor};">${iconSymbol}</div>`,
                    className: 'custom-div-icon',
                    iconSize: [25, 25],
                    iconAnchor: [12, 12]
                });
                
                popupContent = `
                    <div class="popup-content">
                        <h4>🐄 Cow #${data.id}</h4>
                        <p><strong>LoRa Coordinates:</strong><br>
                        ${position[0].toFixed(6)}, ${position[1].toFixed(6)}</p>
                        <p><strong>Distance from Human:</strong> 
                        <span style="color: ${iconColor}; font-weight: bold;">
                        ${(data.distance || 0).toFixed(1)}m</span></p>
                        <p><strong>Status:</strong> 
                        <span style="color: ${iconColor}; font-weight: bold;">
                        ${(data.status || 'unknown').toUpperCase()}</span></p>
                        <p><strong>RSSI:</strong> ${data.rssi} dBm</p>
                        <p><strong>Signal Quality:</strong> ${data.signal_quality}</p>
                        <p><strong>Timestamp:</strong><br>
                        ${new Date(data.timestamp).toLocaleString()}</p>
                    </div>
                `;
                break;
        }
        
        const marker = L.marker(position, { icon: icon });
        marker.bindPopup(popupContent);
        
        return marker;
    }
    
    // Handle connection errors with retry logic
    handleConnectionError() {
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts <= this.maxReconnectAttempts) {
            console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                if (socket && !socket.connected) {
                    socket.connect();
                }
            }, 2000 * this.reconnectAttempts); // Exponential backoff
        } else {
            console.log('Max reconnection attempts reached');
            this.showConnectionError();
        }
    }
    
    // Show connection error message
    showConnectionError() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'connection-error';
        errorDiv.innerHTML = `
            <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <strong>Connection Lost</strong><br>
                Unable to reconnect to the monitoring server. 
                <button onclick="location.reload()" style="margin-left: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Reload Page
                </button>
            </div>
        `;
        
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.insertBefore(errorDiv, sidebar.firstChild);
        }
    }
    
    // Add distance circles around human position
    addDistanceCircles(humanPos, map) {
        // Remove existing circles
        if (this.distanceCircles) {
            this.distanceCircles.forEach(circle => map.removeLayer(circle));
        }
        
        this.distanceCircles = [];
        
        // Add 100m alert threshold circle
        const alertCircle = L.circle(humanPos, {
            radius: 100,
            color: '#dc3545',
            fillColor: '#dc3545',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(map);
        
        alertCircle.bindPopup('100m Alert Threshold');
        this.distanceCircles.push(alertCircle);
        
        // Add 50m safe zone circle
        const safeCircle = L.circle(humanPos, {
            radius: 50,
            color: '#28a745',
            fillColor: '#28a745',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '3, 3'
        }).addTo(map);
        
        safeCircle.bindPopup('50m Safe Zone');
        this.distanceCircles.push(safeCircle);
    }
    
    // Export data for analysis
    exportData() {
        const exportData = {
            alertHistory: this.alertHistory,
            positionHistory: this.positionHistory,
            exportTime: new Date().toISOString(),
            systemInfo: {
                updateInterval: 120,
                distanceThreshold: 100,
                version: '1.0.0'
            }
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `navic_lora_data_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }
    
    // Calculate movement statistics
    getMovementStatistics() {
        if (this.positionHistory.length < 2) {
            return null;
        }
        
        const recent = this.positionHistory.slice(-10); // Last 10 positions
        let totalDistance = 0;
        
        for (let i = 1; i < recent.length; i++) {
            const prev = recent[i - 1];
            const curr = recent[i];
            
            // Calculate distance moved
            const humanDist = this.calculateDistance(
                [prev.human.lat, prev.human.lon],
                [curr.human.lat, curr.human.lon]
            );
            
            totalDistance += humanDist;
        }
        
        return {
            totalDistance: totalDistance,
            averageSpeed: totalDistance / (recent.length - 1), // meters per update
            updateCount: recent.length
        };
    }
    
    // Helper function to calculate distance between two points
    calculateDistance(pos1, pos2) {
        const R = 6371000; // Earth's radius in meters
        const lat1 = pos1[0] * Math.PI / 180;
        const lat2 = pos2[0] * Math.PI / 180;
        const deltaLat = (pos2[0] - pos1[0]) * Math.PI / 180;
        const deltaLon = (pos2[1] - pos1[1]) * Math.PI / 180;
        
        const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                Math.cos(lat1) * Math.cos(lat2) *
                Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return R * c;
    }
}

// Initialize dashboard
const dashboard = new MonitoringDashboard();

// Enhanced update function with dashboard integration
function enhancedUpdateMapMarkers(data) {
    // Track position history
    dashboard.trackPosition(data.human, data.cows, data.system_time);
    
    // Check for alerts and track them
    if (data.cows) {
        data.cows.forEach(cow => {
            if (cow.status === 'alert') {
                dashboard.trackAlert(cow.id, cow.distance, data.system_time);
            }
        });
    }
    
    // Add distance circles if enabled
    if (data.human && typeof addDistanceCircles !== 'undefined') {
        dashboard.addDistanceCircles([data.human.lat, data.human.lon], map);
    }
    
    // Update movement statistics
    const stats = dashboard.getMovementStatistics();
    if (stats) {
        console.log('Movement stats:', stats);
    }
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+E to export data
    if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        dashboard.exportData();
    }
    
    // Ctrl+R to request immediate update
    if (event.ctrlKey && event.key === 'r') {
        event.preventDefault();
        if (socket && socket.connected) {
            socket.emit('request_update');
        }
    }
});

// Add export button to UI
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            const exportButton = document.createElement('button');
            exportButton.innerHTML = '📊 Export Data';
            exportButton.style.cssText = `
                width: 100%;
                padding: 10px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                margin-top: 15px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s ease;
            `;
            
            exportButton.onmouseover = () => {
                exportButton.style.background = '#5a6fd8';
            };
            
            exportButton.onmouseout = () => {
                exportButton.style.background = '#667eea';
            };
            
            exportButton.onclick = () => {
                dashboard.exportData();
            };
            
            sidebar.appendChild(exportButton);
        }
    }, 1000);
});
