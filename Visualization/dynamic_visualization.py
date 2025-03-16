import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec
import time
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better interactivity

class SIRNVisualizer:
    """Simplified class for dynamic visualization of SIRN model data with scrolling support."""
    
    def __init__(self, auto_display=True):
        """
        Initialize the visualizer.
        
        Args:
            auto_display (bool): Whether to automatically show the visualization window
        """
        self.data = {}
        self.cities = []
        self.time_steps = []
        self.current_time_idx = 0
        self.auto_display = auto_display
        self.window_shown = False
        
        # Create figure
        plt.ion()  # Interactive mode
        self.fig = plt.figure(figsize=(14, 12))
        
        # Initially create a simple layout
        self.gs = gridspec.GridSpec(4, 1, figure=self.fig)
        
        # Placeholders
        self.pie_axes = []
        self.heatmap_s = None
        self.heatmap_i = None
        self.heatmap_r = None
        self.s_img = None
        self.i_img = None
        self.r_img = None
        self.slider = None
        self.slider_ax = None
        
        # For scrolling
        self.scroll_step = 0.1  # Fraction of figure height to scroll per wheel event
        self.scroll_pos = 0.0   # Current scroll position (0 = top, 1 = bottom)
    
    def _setup_layout(self):
        """Set up the layout based on number of cities."""
        # Clear existing figure
        self.fig.clear()
        self.pie_axes = []
        
        # Calculate dimensions based on number of cities
        num_cities = len(self.cities)
        pie_rows = (num_cities + 2) // 3  # 3 pie charts per row, rounded up
        
        # Set figure size for scrolling (larger than screen to allow scrolling)
        figure_width = 14
        figure_height = 8 + pie_rows * 4  # Base height + space for pie charts
        
        # Create a tall figure that can be scrolled
        self.fig.set_size_inches(figure_width, figure_height)
        
        # Create new GridSpec
        total_rows = pie_rows + 4  # Pie charts + 3 heatmaps + slider
        self.gs = gridspec.GridSpec(total_rows, 3, figure=self.fig, height_ratios=[4] * pie_rows + [3, 3, 3, 0.5])
        
        # Create pie chart subplots
        for i, city in enumerate(self.cities):
            row = i // 3
            col = i % 3
            ax = self.fig.add_subplot(self.gs[row, col])
            ax.set_title(f'City {city}')
            self.pie_axes.append(ax)
        
        # Create heatmap axes
        self.heatmap_s = self.fig.add_subplot(self.gs[pie_rows, :])
        self.heatmap_i = self.fig.add_subplot(self.gs[pie_rows+1, :])
        self.heatmap_r = self.fig.add_subplot(self.gs[pie_rows+2, :])
        
        self.heatmap_s.set_title('Susceptible Population (% of total)')
        self.heatmap_i.set_title('Infected Population (% of total)')
        self.heatmap_r.set_title('Recovered Population (% of total)')
        
        # Reset heatmap images
        self.s_img = None
        self.i_img = None
        self.r_img = None
        
        # Slider for time
        self.slider_ax = self.fig.add_subplot(self.gs[-1, :])
        self.slider = Slider(self.slider_ax, 'Time Step', 0, 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_time)
        
        # Set up scrolling
        self._setup_scrolling()
        
        # Reset scroll position
        self.scroll_pos = 0.0
        self._update_scroll()
        
        plt.tight_layout()
    
    def _setup_scrolling(self):
        """Set up event handlers for scrolling."""
        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)
    
    def _on_scroll(self, event):
        """Handle mouse wheel scroll events."""
        if event.button == 'up':
            # Scroll up (decrease position)
            self.scroll_pos = max(0, self.scroll_pos - self.scroll_step)
        elif event.button == 'down':
            # Scroll down (increase position)
            self.scroll_pos = min(1, self.scroll_pos + self.scroll_step)
        
        self._update_scroll()
    
    def _on_key(self, event):
        """Handle keyboard scroll events."""
        if event.key == 'up':
            # Scroll up
            self.scroll_pos = max(0, self.scroll_pos - self.scroll_step)
            self._update_scroll()
        elif event.key == 'down':
            # Scroll down
            self.scroll_pos = min(1, self.scroll_pos + self.scroll_step)
            self._update_scroll()
        elif event.key == 'home':
            # Scroll to top
            self.scroll_pos = 0
            self._update_scroll()
        elif event.key == 'end':
            # Scroll to bottom
            self.scroll_pos = 1
            self._update_scroll()
    
    def _update_scroll(self):
        """Update the figure's viewport based on current scroll position."""
        # Get figure manager
        manager = plt.get_current_fig_manager()
        
        # Calculate viewport (how much of the tall figure is visible)
        figure_height = self.fig.get_figheight()
        screen_height = figure_height * 0.7  # Approximate visible height
        
        # Calculate the top coordinate for the visible portion
        scroll_range = max(0, figure_height - screen_height)
        top = self.scroll_pos * scroll_range
        
        # Update the figure's viewport
        self.fig.subplots_adjust(top=1.0-top/figure_height, bottom=max(0, 1.0-(top+screen_height)/figure_height))
        
        # Redraw the figure
        self.fig.canvas.draw_idle()
    
    def update_time(self, val):
        """Handle slider value changes."""
        self.current_time_idx = int(val)
        self.update_plots()
    
    def update_data_arrays(self):
        """Update the data arrays based on current data."""
        if not self.cities or not self.time_steps:
            print("Cannot update arrays: no cities or time steps")
            return
        
        num_cities = len(self.cities)
        num_times = len(self.time_steps)
        
        # Create new arrays
        self.s_data = np.zeros((num_cities, num_times))
        self.i_data = np.zeros((num_cities, num_times))
        self.r_data = np.zeros((num_cities, num_times))
        
        # Fill with data
        for c_idx, city in enumerate(self.cities):
            for t_idx, time in enumerate(self.time_steps):
                t_str = str(time)
                if city in self.data and t_str in self.data[city]:
                    values = self.data[city][t_str]
                    s_val = float(values[0])
                    i_val = float(values[1])
                    r_val = float(values[2])
                    n_val = float(values[3]) if len(values) > 3 else (s_val + i_val + r_val)
                    
                    if n_val > 0:
                        self.s_data[c_idx, t_idx] = (s_val / n_val) * 100
                        self.i_data[c_idx, t_idx] = (i_val / n_val) * 100
                        self.r_data[c_idx, t_idx] = (r_val / n_val) * 100
    
    def update_slider_range(self):
        """Update the slider range based on current time steps."""
        if not self.time_steps:
            return
            
        max_val = len(self.time_steps) - 1
        if max_val < 0:
            return
            
        self.slider.valmax = max_val
        self.slider.ax.set_xlim(0, max_val)
        
        # Adjust current index if needed
        if self.current_time_idx > max_val:
            self.current_time_idx = max_val
            
        self.slider.set_val(self.current_time_idx)
    
    def update_plots(self):
        """Update all visualization elements."""
        if not self.time_steps or not self.cities:
            return
        
        # Get current time step
        if self.current_time_idx >= len(self.time_steps):
            self.current_time_idx = len(self.time_steps) - 1
            
        current_time = self.time_steps[self.current_time_idx]
        time_str = str(current_time)
        
        # Update pie charts
        for i, city in enumerate(self.cities):
            if i < len(self.pie_axes):
                self.pie_axes[i].clear()
                if city in self.data and time_str in self.data[city]:
                    # Get data
                    values = self.data[city][time_str]
                    s_val = float(values[0])
                    i_val = float(values[1])
                    r_val = float(values[2])
                    
                    # Create pie
                    wedges, texts, autotexts = self.pie_axes[i].pie(
                        [s_val, i_val, r_val],
                        labels=['S', 'I', 'R'],
                        colors=['blue', 'red', 'green'],
                        autopct='%1.1f%%'
                    )
                    # Make text white for visibility
                    for autotext in autotexts:
                        autotext.set_color('white')
                    self.pie_axes[i].set_title(f'City {city} at Time {time_str}')
                else:
                    self.pie_axes[i].text(0.5, 0.5, 'No data', ha='center', va='center', transform=self.pie_axes[i].transAxes)
                    self.pie_axes[i].set_title(f'City {i}')
        
        # Update heatmaps
        if self.s_data.size > 0:
            # Clear time markers
            for ax in [self.heatmap_s, self.heatmap_i, self.heatmap_r]:
                for line in ax.get_lines():
                    line.remove()
            
            # Update heatmap data
            if self.s_img is None:
                # Remove old colorbar if it exists
                if hasattr(self, 's_colorbar') and self.s_colorbar:
                    self.s_colorbar.remove()
                    
                self.heatmap_s.clear()
                self.s_img = self.heatmap_s.imshow(self.s_data, aspect='auto', cmap='Blues', vmin=0, vmax=100)
                # Store colorbar to prevent duplication
                self.s_colorbar = self.fig.colorbar(self.s_img, ax=self.heatmap_s)
                self.s_colorbar.set_label('% of population')
                self.heatmap_s.set_title('Susceptible Population (% of total)')
            else:
                self.s_img.set_data(self.s_data)
            
            if self.i_img is None:
                # Remove old colorbar if it exists
                if hasattr(self, 'i_colorbar') and self.i_colorbar:
                    self.i_colorbar.remove()
                    
                self.heatmap_i.clear()
                self.i_img = self.heatmap_i.imshow(self.i_data, aspect='auto', cmap='Reds', vmin=0, vmax=100)
                # Store colorbar to prevent duplication
                self.i_colorbar = self.fig.colorbar(self.i_img, ax=self.heatmap_i)
                self.i_colorbar.set_label('% of population')
                self.heatmap_i.set_title('Infected Population (% of total)')
            else:
                self.i_img.set_data(self.i_data)
            
            if self.r_img is None:
                # Remove old colorbar if it exists
                if hasattr(self, 'r_colorbar') and self.r_colorbar:
                    self.r_colorbar.remove()
                    
                self.heatmap_r.clear()
                self.r_img = self.heatmap_r.imshow(self.r_data, aspect='auto', cmap='Greens', vmin=0, vmax=100)
                # Store colorbar to prevent duplication
                self.r_colorbar = self.fig.colorbar(self.r_img, ax=self.heatmap_r)
                self.r_colorbar.set_label('% of population')
                self.heatmap_r.set_title('Recovered Population (% of total)')
            else:
                self.r_img.set_data(self.r_data)
            
            # Update labels and ticks for all heatmaps
            for ax in [self.heatmap_s, self.heatmap_i, self.heatmap_r]:
                ax.set_yticks(range(len(self.cities)))
                ax.set_yticklabels(self.cities)
                ax.set_xlabel('Time Step')
                
                # Time step labels
                step = max(1, len(self.time_steps) // 10)
                ticks = range(0, len(self.time_steps), step)
                ax.set_xticks(ticks)
                ax.set_xticklabels([str(self.time_steps[i]) for i in ticks])
                
                # Highlight current time
                ax.axvline(x=self.current_time_idx, color='black', linestyle='--')
        
        # Force redraw
        self.fig.canvas.draw_idle()
    
    def add_data_point(self, city, time_step, values):
        """
        Add a new data point and update the visualization.
        
        Args:
            city: City identifier (integer or string)
            time_step: Time step (integer or string)
            values: List of [S, I, R, N] values for the SIRN model
        """
        # Convert to strings for dictionary keys
        city_str = str(city)
        time_str = str(time_step)
        
        # Ensure window is shown if auto_display is enabled
        if self.auto_display and not self.window_shown:
            print("\nScrolling Instructions:")
            print("  - Use mouse wheel to scroll up/down")
            print("  - Use arrow keys (Up/Down) to scroll")
            print("  - Home key: Scroll to top")
            print("  - End key: Scroll to bottom")
            plt.show(block=False)
            plt.pause(0.5)
            self.window_shown = True
        
        # Add city if new
        if city_str not in self.data:
            self.data[city_str] = {}
            if city_str not in self.cities:
                self.cities.append(city_str)
                self.cities.sort(key=int)
                # Update the layout when cities change
                self._setup_layout()
        
        # Add data point
        self.data[city_str][time_str] = values
        
        # Add time step if new
        if time_step not in self.time_steps:
            self.time_steps.append(time_step)
            self.time_steps.sort()
            
            # Update arrays and slider
            self.update_data_arrays()
            self.update_slider_range()
        
        # Update the visualization
        self.current_time_idx = self.time_steps.index(time_step)
        self.slider.set_val(self.current_time_idx)
        self.update_plots()
    
    def initialize(self, cities_list=None):
        """
        Initialize the visualizer with a list of cities.
        This method should be called before adding data points if cities are known in advance.
        
        Args:
            cities_list (list): Optional list of city identifiers
        """
        if cities_list:
            for city in cities_list:
                if city not in self.cities:
                    self.cities.append(str(city))
            
            # Sort and setup layout
            self.cities.sort(key=int)
            self._setup_layout()
            
            # Show window if auto_display is enabled
            if self.auto_display and not self.window_shown:
                print("\nScrolling Instructions:")
                print("  - Use mouse wheel to scroll up/down")
                print("  - Use arrow keys (Up/Down) to scroll")
                print("  - Home key: Scroll to top")
                print("  - End key: Scroll to bottom")
                plt.show(block=False)
                plt.pause(0.5)
                self.window_shown = True
    
    def wait_for_close(self):
        """
        Switch to blocking mode and wait for the window to be closed.
        Call this at the end of your program to keep the visualization window open.
        """
        if not self.window_shown and self.auto_display:
            plt.show(block=False)
            self.window_shown = True
        
        plt.ioff()
        plt.show(block=True)

def load_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def run_static_visualization(data_file):
    """Run the visualization with all data loaded initially."""
    print("Running static visualization...")
    
    # Load all data
    data = load_data(data_file)
    
    # Get all cities and time steps
    cities = sorted(data.keys(), key=int)
    all_time_steps = set()
    for city in cities:
        all_time_steps.update([int(t) for t in data[city].keys() if t.isdigit()])
    time_steps = sorted(list(all_time_steps))
    
    print(f"Loading {len(cities)} cities and {len(time_steps)} time steps at once")
    
    # Create visualizer
    visualizer = SIRNVisualizer(auto_display=False)
    
    # Add all cities first
    visualizer.initialize(cities)
    
    # Process all data at once
    for city in cities:
        for time_step in time_steps:
            time_str = str(time_step)
            if time_str in data[city]:
                visualizer.data[city] = visualizer.data.get(city, {})
                visualizer.data[city][time_str] = data[city][time_str]
                
                # Add to time_steps list if not already present
                if time_step not in visualizer.time_steps:
                    visualizer.time_steps.append(time_step)
    
    # Sort time_steps
    visualizer.time_steps.sort()
    
    # Update arrays and slider
    visualizer.update_data_arrays()
    visualizer.update_slider_range()
    visualizer.update_plots()
    
    # Show instructions
    print("\nScrolling Instructions:")
    print("  - Use mouse wheel to scroll up/down")
    print("  - Use arrow keys (Up/Down) to scroll")
    print("  - Home key: Scroll to top")
    print("  - End key: Scroll to bottom")
    
    # Show window and wait for close
    plt.show(block=True)

def run_dynamic_visualization(data_file):
    """Run the visualization with data added incrementally."""
    print("Running dynamic visualization...")
    
    # Load all data for simulation
    data = load_data(data_file)
    
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

def run_demo():
    """Run a demo with synthetic data."""
    print("Running demo...")
    
    # Create visualizer
    visualizer = SIRNVisualizer(auto_display=True)
    
    # Parameters - generate more cities to demonstrate scrolling
    num_cities = 10
    
    # Initialize with cities
    cities = [str(i) for i in range(num_cities)]
    visualizer.initialize(cities)
    
    # More parameters
    max_time = 100
    time_step = 10
    
    # Initial conditions
    for city in range(num_cities):
        # Vary population based on city index
        if city < 3:
            N = 101  # Small
        elif city < 6: 
            N = 201  # Medium
        else:
            N = 501  # Large
        
        values = [N-1, 1, 0, N]  # [S, I, R, N]
        visualizer.add_data_point(city, 0, values)
    
    # Generate synthetic data
    try:
        for t in range(time_step, max_time+1, time_step):
            print(f"Generating data for time step {t}")
            
            for city in range(num_cities):
                # Get previous values
                prev_t = max([ts for ts in visualizer.time_steps if ts < t])
                prev_values = visualizer.data[str(city)][str(prev_t)]
                
                S, I, R, N = prev_values
                
                # Model parameters - vary by city
                beta = 0.2 + 0.03 * city  # Infection rate
                gamma = 0.1 + 0.01 * city  # Recovery rate
                
                # Update using simple model - smaller time steps for stability
                dt = t - prev_t
                num_substeps = 10
                sub_dt = dt / num_substeps
                
                for _ in range(num_substeps):
                    dS = -beta * S * I / N * sub_dt
                    dI = (beta * S * I / N - gamma * I) * sub_dt
                    dR = gamma * I * sub_dt
                    
                    S += dS
                    I += dI
                    R += dR
                    
                    # Ensure non-negative and sum to N
                    S = max(0, S)
                    I = max(0, I)
                    R = max(0, R)
                    
                    total = S + I + R
                    if abs(total - N) > 1e-9:
                        S = S * N / total
                        I = I * N / total
                        R = R * N / total
                
                # Add new data point
                visualizer.add_data_point(city, t, [S, I, R, N])
            
            plt.pause(0.5)
            
    except KeyboardInterrupt:
        print("Simulation stopped by user")
    
    # Wait for window to be closed
    visualizer.wait_for_close()


# Example of how to use the SIRNVisualizer as an imported module
def example_external_usage():
    """
    This shows how your partner might use the SIRNVisualizer class
    in their own script to visualize SIRN data dynamically.
    """
    # Create a visualizer - will automatically show a window when data is added
    visualizer = SIRNVisualizer(auto_display=True)
    
    # Initialize with known cities (optional but recommended)
    cities = ["0", "1", "2", "3"]
    visualizer.initialize(cities)
    
    # Your partner's simulation loop
    for time_step in range(0, 101, 10):
        print(f"Calculating data for time {time_step}")
        
        # For each city, calculate or generate data
        for city in cities:
            # This is where your partner would calculate their SIRN values
            # For this example, we'll just generate some dummy data
            city_idx = int(city)
            N = 100 + city_idx * 100
            
            # Simple dummy model
            t_normalized = time_step / 100.0
            S = N * (1 - t_normalized * (0.7 + 0.1 * city_idx))
            I = N * t_normalized * (0.4 - 0.05 * city_idx)
            R = N - S - I
            
            # Add the data point - this automatically updates the visualization
            visualizer.add_data_point(city, time_step, [S, I, R, N])
        
        # Optional: Add a small delay between time steps for visualization
        import time
        time.sleep(0.5)
    
    # Keep the window open until manually closed
    print("Simulation complete. Close the window to exit.")
    visualizer.wait_for_close()


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='SIRN Model Visualization')
    parser.add_argument('data_file', nargs='?', help='Path to JSON data file')
    parser.add_argument('--mode', '-m', choices=['static', 'dynamic', 'demo', 'example'], default='static',
                        help='Visualization mode: static, dynamic, demo, or example')
    parser.add_argument('--cities', type=int, default=None, 
                        help='In demo mode, specify the number of cities to generate')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'demo':
            run_demo()
        elif args.mode == 'example':
            example_external_usage()
        elif args.mode == 'static' or args.mode == 'dynamic':
            if not args.data_file:
                print(f"Error: data_file is required for {args.mode} mode")
                sys.exit(1)
            
            if args.mode == 'static':
                run_static_visualization(args.data_file)
            else:
                run_dynamic_visualization(args.data_file)
        else:
            print(f"Invalid mode: {args.mode}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)