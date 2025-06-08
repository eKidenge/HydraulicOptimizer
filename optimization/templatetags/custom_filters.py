# optimization/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def dict_get_best_algorithm(results_dict):
    """
    Determine the best algorithm based on weighted score of:
    - Pressure improvement (40% weight)
    - Cost reduction (40% weight)
    - Execution time (20% weight - lower is better)
    """
    if not results_dict:
        return None
    
    best_algo = None
    best_score = -float('inf')
    
    for algo, results in results_dict.items():
        if 'error' in results:
            continue
            
        try:
            # Normalize metrics (higher is better)
            pressure_imp = float(results.get('pressure_improvement', 0))
            cost_red = float(results.get('cost_reduction', 0))
            exec_time = float(results.get('execution_time', 0))
            
            # Invert execution time (since lower is better)
            exec_time_score = 1 / (exec_time + 0.0001)  # Avoid division by zero
            
            # Calculate weighted score
            score = (0.4 * pressure_imp) + (0.4 * cost_red) + (0.2 * exec_time_score * 100)  # Scale time factor
            
            if score > best_score:
                best_score = score
                best_algo = (algo, results)
        except (ValueError, TypeError):
            continue
    
    return best_algo