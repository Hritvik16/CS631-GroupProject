# SIRN Model Visualization

A dynamic visualization system for Susceptible-Infected-Recovered-N (SIRN) epidemiological models across multiple cities.

## Overview

This repository contains tools to visualize SIRN model data, showing how diseases spread through populations over time. The visualization displays:

- Pie charts for each city showing the proportion of Susceptible, Infected, and Recovered populations
- Heat maps tracking population percentages across all cities and time steps
- Interactive time slider for exploring the temporal evolution of the model
- Scrollable interface for handling many cities

## Files

- `dynamic_visualization.py`: The main visualization module with the `SIRNVisualizer` class
- `generate_sirn_data.py`: Script to generate synthetic SIRN model data
- `visualize_data.py`: Example script showing how to use the visualizer with your own data

## Requirements

- Python 3.6+
- matplotlib
- numpy
- json

Install dependencies:
```bash
pip install matplotlib numpy
```

## Usage

### Generating Test Data

Generate synthetic SIRN data:

```bash
python generate_sirn_data.py --cities 5 --max-time 100 --time-step 10 --output data.json --preview
```

Options:
- `--cities`: Number of cities to simulate
- `--max-time`: Maximum simulation time
- `--time-step`: Time interval between data points
- `--output`: Output JSON file
- `--preview`: Display a preview of the generated data
- `--stochastic`: Add random variations to the model
- `--populations`: Custom population sizes (e.g., `--populations 100 200 500 300`)

### Running the Visualization

#### 1. Command Line

The visualization can be run directly from the command line:

```bash
# Static visualization (load all data at once)
python dynamic_visualization.py data.json --mode static

# Dynamic visualization (simulate data appearing over time)
python dynamic_visualization.py data.json --mode dynamic

# Demo with synthetic data
python dynamic_visualization.py --mode demo

# Example of how external code might use the visualizer
python dynamic_visualization.py --mode example
```

#### 2. Integration with Your Code

Import the visualizer in your own Python scripts:

```python
from dynamic_visualization import SIRNVisualizer
import matplotlib.pyplot as plt

# Create visualizer
visualizer = SIRNVisualizer(auto_display=True)

# Optional: Initialize with known cities
cities = ["0", "1", "2"]  # Can be omitted if cities are unknown in advance
visualizer.initialize(cities)

# Add data points as they become available
for time_step in range(0, 101, 10):
    for city in cities:
        # Calculate or obtain your S, I, R, N values
        S, I, R, N = your_calculation_function(city, time_step)
        
        # Add to visualizer (automatically updates display)
        visualizer.add_data_point(city, time_step, [S, I, R, N])

# Keep window open until manually closed
visualizer.wait_for_close()
```

### Scrolling Controls

The visualization supports scrolling for many cities:
- Mouse wheel: Scroll up/down
- Arrow keys (Up/Down): Scroll up/down
- Home key: Scroll to top
- End key: Scroll to bottom

## How It Works

### Data Format

The SIRN data is stored in JSON format:
```json
{
  "0": {
    "0": [100, 1, 0, 101],
    "10": [90, 10, 1, 101],
    ...
  },
  "1": {
    "0": [200, 1, 0, 201],
    ...
  }
}
```

Where:
- The outer keys represent city identifiers
- The inner keys represent time steps
- The arrays contain [S, I, R, N] values:
  - S: Susceptible population
  - I: Infected population
  - R: Recovered population
  - N: Total population

### Visualization Components

The visualization includes:
1. Pie charts showing S, I, R proportions for each city
2. Heat maps showing population percentages over time for all cities
3. A time slider for navigating through the simulation
4. Scrollable interface to accommodate many cities

