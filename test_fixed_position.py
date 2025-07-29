"""
Test script to verify fixed position configuration
"""
import config
from simulation import PositionSimulator

print("Testing fixed position configuration...")
print(f"FIXED_POSITION_MODE: {config.FIXED_POSITION_MODE}")
print(f"FIXED_HUMAN_COORDS: {config.FIXED_HUMAN_COORDS}")

simulator = PositionSimulator()
position = simulator.simulate_navic_position()
print(f"Current simulated position: {position}")

if config.FIXED_POSITION_MODE:
    if position == config.FIXED_HUMAN_COORDS:
        print("✅ Fixed position is working correctly!")
    else:
        print("❌ Fixed position is not working - position differs from expected")
else:
    print("⚠️ Fixed position mode is disabled")
