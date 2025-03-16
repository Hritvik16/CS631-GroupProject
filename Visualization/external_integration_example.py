import matplotlib.pyplot as plt
import json
from dynamic_visualization import SIRNVisualizer


def load_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

# Load all data
data = load_data('data.json')

# Get all cities and time steps
cities = sorted(data.keys(), key=int)
all_time_steps = set()
for city in cities:
    all_time_steps.update([int(t) for t in data[city].keys() if t.isdigit()])
time_steps = sorted(list(all_time_steps))

print(f"Found {len(cities)} cities and {len(time_steps)} time steps")

# Create visualizer
visualizer = SIRNVisualizer(auto_display=True)

# Initialize with all cities
visualizer.initialize(cities)

# Add data incrementally
try:
    for t_idx, time_step in enumerate(time_steps):
        time_str = str(time_step)
        print(f"Time step {time_step} ({t_idx+1}/{len(time_steps)})")
        
        for city in cities:
            if time_str in data[city]:
                print(f"  Adding data for city {city}")
                visualizer.add_data_point(city, time_step, data[city][time_str])
        
        plt.pause(0.5)  # Pause after each time step
        
except Exception as e:
    print(f"Error: {e}")

# Wait for window to be closed
visualizer.wait_for_close()