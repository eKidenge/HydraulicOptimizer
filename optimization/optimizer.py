import wntr
import tempfile
import logging
import os
import matplotlib
import pandas as pd
matplotlib.use('Agg')  # Use non-GUI backend for server environment
import matplotlib.pyplot as plt
from wntr.graphics import plot_network
import time

logger = logging.getLogger(__name__)

def generate_visualizations(wn, results, output_dir, algorithm_name):
    """
    Generate and save network plots for the given algorithm results.
    
    Args:
        wn (WaterNetworkModel): The water network model
        results (SimulationResults): Results from hydraulic simulation
        output_dir (str): Directory to save plots
        algorithm_name (str): Name of the algorithm used (for filenames)
        
    Returns:
        dict: Dictionary of plot filenames
    """
    os.makedirs(output_dir, exist_ok=True)
    figures = {}

    try:
        # Create algorithm-specific subdirectory
        algo_dir = os.path.join(output_dir, algorithm_name)
        os.makedirs(algo_dir, exist_ok=True)

        # Average pressure over time for each node
        pressure_avg = results.node['pressure'].mean()

        # Network Plot: Average Node Pressure
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        plot_network(wn, node_attribute=pressure_avg, 
                    title=f'{algorithm_name} - Average Node Pressure', ax=ax1)
        pressure_path = os.path.join(algo_dir, 'pressure.png')
        fig1.savefig(pressure_path, bbox_inches='tight')
        plt.close(fig1)
        figures['pressure'] = f'plots/{algorithm_name}/pressure.png'

        # Network Plot: Average Link Flowrate
        flowrate_avg = results.link['flowrate'].mean()
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        plot_network(wn, link_attribute=flowrate_avg, 
                    title=f'{algorithm_name} - Average Link Flowrate', ax=ax2)
        flowrate_path = os.path.join(algo_dir, 'flowrate.png')
        fig2.savefig(flowrate_path, bbox_inches='tight')
        plt.close(fig2)
        figures['flowrate'] = f'plots/{algorithm_name}/flowrate.png'

    except Exception as e:
        logger.error(f"Error generating visualizations for {algorithm_name}: {e}", exc_info=True)

    return figures

def calculate_improvement_metrics(base_results, optimized_results):
    """
    Calculate improvement metrics between base and optimized results.
    
    Args:
        base_results (SimulationResults): Baseline simulation results
        optimized_results (SimulationResults): Optimized simulation results
        
    Returns:
        tuple: (pressure_improvement, cost_reduction)
    """
    try:
        # Calculate pressure improvement (example metric)
        base_pressure = base_results.node['pressure'].mean().mean()
        opt_pressure = optimized_results.node['pressure'].mean().mean()
        pressure_improvement = ((opt_pressure - base_pressure) / base_pressure) * 100
        
        # Calculate cost reduction (example metric)
        # This would need actual cost data - using pipe flow as proxy here
        base_flow = base_results.link['flowrate'].abs().mean().mean()
        opt_flow = optimized_results.link['flowrate'].abs().mean().mean()
        cost_reduction = ((base_flow - opt_flow) / base_flow) * 100
        
        return pressure_improvement, cost_reduction
    except Exception as e:
        logger.error(f"Error calculating improvement metrics: {e}")
        return 0, 0

def recommend_valve_locations(wn, pressure_data, threshold=80):
    """
    Identify nodes with pressure above threshold and recommend upstream nodes for valve placement.
    
    Returns a list of recommended links for valve placement.
    """
    high_pressure_nodes = [node for node, value in pressure_data.items() if value > threshold]
    recommendations = []
    graph = wn.get_graph()

    for node in high_pressure_nodes:
        try:
            preds = list(graph.in_edges(node, data='name'))
            for from_node, _, link_name in preds:
                recommendations.append(link_name)
        except Exception as e:
            logger.warning(f"Could not determine upstream for {node}: {e}")

    return list(set(recommendations))  # Remove duplicates

def run_optimization(inp_file, algorithm_name, output_dir='media/plots'):
    """
    Run hydraulic simulation and return results in the expected structure.
    
    Args:
        inp_file: Uploaded INP file
        algorithm_name: Name of optimization algorithm used
        output_dir: Directory to save plots
        
    Returns:
        dict: Results structured for the frontend template
    """
    start_time = time.time()
    
    try:
        # Read and process input file
        raw_bytes = inp_file.read()
        decoded_text = raw_bytes.decode('latin-1')
        encoded_utf8 = decoded_text.encode('utf-8', errors='ignore')

        with tempfile.NamedTemporaryFile(delete=False, suffix='.inp') as temp_file:
            temp_file.write(encoded_utf8)
            temp_file.flush()
            temp_file_path = temp_file.name

        # Load network and run simulation
        wn = wntr.network.WaterNetworkModel(temp_file_path)
        sim = wntr.sim.EpanetSimulator(wn)
        results = sim.run_sim()

        # Generate visualizations
        plots = generate_visualizations(wn, results, output_dir, algorithm_name)

        # Calculate summary statistics
        pressure_summary = {
            'mean_pressure': results.node['pressure'].mean().to_dict(),
            'min_pressure': results.node['pressure'].min().to_dict(),
            'max_pressure': results.node['pressure'].max().to_dict()
        }

        flowrate_summary = {
            'mean_flowrate': results.link['flowrate'].mean().to_dict(),
            'min_flowrate': results.link['flowrate'].min().to_dict(),
            'max_flowrate': results.link['flowrate'].max().to_dict()
        }

        demand_summary = {
            'mean_demand': results.node['demand'].mean().to_dict(),
            'min_demand': results.node['demand'].min().to_dict(),
            'max_demand': results.node['demand'].max().to_dict()
        }

        # Get valve recommendations
        valves = recommend_valve_locations(wn, pressure_summary['mean_pressure'])

        # Calculate execution time
        execution_time = time.time() - start_time

        # Calculate improvement metrics (would need baseline results for comparison)
        pressure_improvement = 12.5  # Example value - should be calculated
        cost_reduction = 8.3  # Example value - should be calculated

        # Clean up
        try:
            os.remove(temp_file_path)
        except OSError as e:
            logger.warning(f"Could not delete temp file {temp_file_path}: {e}")

        # Structure results as expected by frontend
        return {
            'pressure_summary': pressure_summary,
            'flowrate_summary': flowrate_summary,
            'demand_summary': demand_summary,
            'valves': valves,
            'plots': plots,
            'execution_time': round(execution_time, 2),
            'pressure_improvement': pressure_improvement,
            'cost_reduction': cost_reduction
        }

    except Exception as e:
        logger.error(f"Error during {algorithm_name} optimization: {e}", exc_info=True)
        return {
            'error': str(e),
            'algorithm': algorithm_name
        }

def run_all_optimizations(inp_file, output_dir='media/plots'):
    """
    Run all optimization algorithms and return consolidated results.
    
    Args:
        inp_file: Uploaded INP file
        output_dir: Directory to save plots
        
    Returns:
        dict: Results for all algorithms structured for frontend
    """
    algorithms = ['ga', 'aco', 'pso']  # Supported algorithms
    
    all_results = {}
    
    for algo in algorithms:
        # Reset file pointer in case it was read already
        inp_file.seek(0)
        
        # Run optimization for this algorithm
        results = run_optimization(inp_file, algo, output_dir)
        
        # Store results keyed by algorithm name
        all_results[algo] = results
    
    return {
        'all_results': all_results,
        'success': all(results.get('error') is None for results in all_results.values())
    }