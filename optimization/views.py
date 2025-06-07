import os
import json
import logging
from django.shortcuts import render
from django.conf import settings
from .forms import OptimizationForm
from .optimizer import run_all_optimizations  # Updated import
import plotly.graph_objs as go
import plotly.utils as putils

logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        form = OptimizationForm(request.POST, request.FILES)
        if form.is_valid():
            inp_file = request.FILES['inp_file']
            optimization_method = form.cleaned_data.get('optimization_method', 'ga')
            
            # Run all optimizations and get results for all algorithms
            result = run_all_optimizations(inp_file)
            
            if not result.get('success', False):
                return render(request, 'optimization/index.html', {
                    'form': form,
                    'error': "Error running one or more optimizations"
                })

            all_results = result.get('all_results', {})
            
            # Prepare context with all algorithm results
            context = {
                'form': form,
                'all_results': all_results,
            }
            
            # Add comparison data if multiple algorithms were run
            if len(all_results) > 1:
                context['comparison_data'] = prepare_comparison_data(all_results)
            
            return render(request, 'optimization/results.html', context)
    else:
        form = OptimizationForm()

    return render(request, 'optimization/index.html', {'form': form})

def prepare_comparison_data(all_results):
    """
    Prepare data for algorithm comparison charts and tables.
    
    Args:
        all_results (dict): Results from all optimization algorithms
        
    Returns:
        dict: Processed comparison data
    """
    comparison = {
        'algorithms': [],
        'execution_times': [],
        'pressure_improvements': [],
        'cost_reductions': []
    }
    
    for algo, results in all_results.items():
        comparison['algorithms'].append(algo.upper())
        comparison['execution_times'].append(results.get('execution_time', 0))
        comparison['pressure_improvements'].append(results.get('pressure_improvement', 0))
        comparison['cost_reductions'].append(results.get('cost_reduction', 0))
    
    # Create Plotly comparison chart
    comparison['chart_json'] = create_comparison_chart(comparison)
    
    return comparison

def create_comparison_chart(comparison_data):
    """
    Create a Plotly bar chart comparing algorithm performance.
    
    Args:
        comparison_data (dict): Prepared comparison data
        
    Returns:
        str: JSON representation of the Plotly figure
    """
    try:
        fig = go.Figure()
        
        # Add execution time trace
        fig.add_trace(go.Bar(
            x=comparison_data['algorithms'],
            y=comparison_data['execution_times'],
            name='Execution Time (s)',
            marker_color='rgb(55, 83, 109)'
        ))
        
        # Add pressure improvement trace
        fig.add_trace(go.Bar(
            x=comparison_data['algorithms'],
            y=comparison_data['pressure_improvements'],
            name='Pressure Improvement (%)',
            marker_color='rgb(26, 118, 255)'
        ))
        
        # Add cost reduction trace
        fig.add_trace(go.Bar(
            x=comparison_data['algorithms'],
            y=comparison_data['cost_reductions'],
            name='Cost Reduction (%)',
            marker_color='rgb(255, 65, 54)'
        ))
        
        # Update layout
        fig.update_layout(
            title='Algorithm Performance Comparison',
            xaxis_title='Algorithm',
            yaxis_title='Value',
            barmode='group',
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=putils.PlotlyJSONEncoder)
    except Exception as e:
        logger.error(f"Error creating comparison chart: {e}")
        return None

def results(request):
    """Fallback results view if accessed directly"""
    return render(request, 'optimization/results.html')