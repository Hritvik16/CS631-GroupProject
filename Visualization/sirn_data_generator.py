import json
import numpy as np
import argparse
import os
import random

def generate_sirn_data(
    num_cities=3, 
    max_time=100, 
    time_step=10, 
    initial_infected=1,
    vary_params=True, 
    custom_populations=None,
    random_seed=None,
    stochastic=False,
    output_file=None
):
    """
    Generate synthetic SIRN model data for multiple cities.
    
    Args:
        num_cities (int): Number of cities to generate data for
        max_time (int): Maximum time step
        time_step (int): Interval between time steps
        initial_infected (int): Initial infected count
        vary_params (bool): Whether to vary parameters between cities
        custom_populations (list): List of populations for each city, or None to use defaults
        random_seed (int): Seed for random number generator (for reproducibility)
        stochastic (bool): Whether to add random variations to the model
        output_file (str): Path to output JSON file, or None to just return the data
        
    Returns:
        dict: SIRN data in the specified format
    """
    # Set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)
        np.random.seed(random_seed)
    
    # Create data structure
    data = {}
    
    # Generate default populations if not provided
    if custom_populations is None:
        custom_populations = []
        for i in range(num_cities):
            if i < num_cities // 3:
                custom_populations.append(100)  # Small city
            elif i < 2 * num_cities // 3:
                custom_populations.append(200)  # Medium city
            else:
                custom_populations.append(500)  # Large city
    
    # Ensure we have enough populations
    while len(custom_populations) < num_cities:
        custom_populations.append(100)  # Default
    
    # Generate data for each city
    for city in range(num_cities):
        city_str = str(city)
        data[city_str] = {}
        
        # Get city population
        N = custom_populations[city] + initial_infected
        
        # Set initial conditions
        S0 = N - initial_infected
        I0 = initial_infected
        R0 = 0
        
        # Initial data point at t=0
        data[city_str]["0"] = [float(S0), float(I0), float(R0), float(N)]
        
        # Set model parameters (can vary by city)
        if vary_params:
            # Infection rate increases with city index
            beta_base = 0.2 + 0.05 * city
            # Recovery rate slightly increases with city index
            gamma_base = 0.1 + 0.01 * city
        else:
            # Fixed parameters
            beta_base = 0.3
            gamma_base = 0.1
        
        # Current values
        S, I, R = S0, I0, R0
        
        # Generate time series data
        time_points = list(range(time_step, max_time + 1, time_step))
        if max_time not in time_points and max_time % time_step != 0:
            time_points.append(max_time)
            
        for t in time_points:
            # For numerical stability, use smaller steps for integration
            previous_t = time_points[time_points.index(t) - 1] if time_points.index(t) > 0 else 0
            dt = t - previous_t
            num_substeps = 10  # Number of sub-steps for numerical integration
            sub_dt = dt / num_substeps
            
            # Perform multiple small steps for better numerical stability
            for _ in range(num_substeps):
                # Add stochastic variations if enabled
                if stochastic:
                    beta = beta_base * (1 + np.random.normal(0, 0.05))  # 5% random variation
                    gamma = gamma_base * (1 + np.random.normal(0, 0.05))  # 5% random variation
                else:
                    beta = beta_base
                    gamma = gamma_base
                
                dS = -beta * S * I / N * sub_dt
                dI = (beta * S * I / N - gamma * I) * sub_dt
                dR = gamma * I * sub_dt
                
                S += dS
                I += dI
                R += dR
                
                # Ensure no negative values
                S = max(0, S)
                I = max(0, I)
                R = max(0, R)
                
                # Ensure values sum to N (fix numerical drift)
                total = S + I + R
                if abs(total - N) > 1e-9:  # Only correct if there's significant drift
                    S = S * N / total
                    I = I * N / total
                    R = R * N / total
            
            # Store data point
            data[city_str][str(t)] = [float(S), float(I), float(R), float(N)]
    
    # Write to JSON file if output_file is specified
    if output_file:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated SIRN data for {num_cities} cities saved to {output_file}")
    
    return data

def print_data_preview(data, num_cities=3, num_timesteps=3):
    """Print a preview of the generated data."""
    city_count = min(num_cities, len(data))
    
    for city in list(data.keys())[:city_count]:
        print(f"City {city}:")
        
        timesteps = sorted(data[city].keys(), key=lambda x: int(x))
        timestep_count = min(num_timesteps, len(timesteps))
        
        for timestep in timesteps[:timestep_count]:
            values = data[city][timestep]
            print(f"  Time {timestep}: S={values[0]:.2f}, I={values[1]:.2f}, R={values[2]:.2f}, N={values[3]:.2f}")
            
        if len(timesteps) > timestep_count:
            print(f"  ... and {len(timesteps) - timestep_count} more time steps")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic SIRN model data")
    parser.add_argument("--cities", type=int, default=3, help="Number of cities")
    parser.add_argument("--max-time", type=int, default=100, help="Maximum time step")
    parser.add_argument("--time-step", type=int, default=10, help="Time step interval")
    parser.add_argument("--initial-infected", type=int, default=1, help="Initial infected count")
    parser.add_argument("--output", default="sirn_data.json", help="Output JSON file")
    parser.add_argument("--fixed-params", action="store_true", help="Use fixed parameters for all cities")
    parser.add_argument("--populations", type=int, nargs="*", help="Population for each city")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--stochastic", action="store_true", help="Add random variations to the model")
    parser.add_argument("--preview", action="store_true", help="Print a preview of the generated data")
    
    args = parser.parse_args()
    
    data = generate_sirn_data(
        num_cities=args.cities,
        max_time=args.max_time,
        time_step=args.time_step,
        initial_infected=args.initial_infected,
        vary_params=not args.fixed_params,
        custom_populations=args.populations,
        random_seed=args.seed,
        stochastic=args.stochastic,
        output_file=args.output
    )
    
    if args.preview:
        print_data_preview(data)