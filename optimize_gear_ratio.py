import numpy as np
import argparse

def find_nearest_gear_ratio(target_ratio, max_teeth=500):
    """
    Find tooth counts for split ring compound planetary that produces 
    ratio closest to target while maintaining 120° carrier spacing (3 planets)
    
    Constraint: (r1_teeth + sun_teeth) must be divisible by 3 for even spacing
    """
    best_error = float('inf')
    best_config = None
    
    # Search through reasonable tooth count ranges
    for r1_teeth in range(20, max_teeth):
        for p1_teeth in range(8, min(r1_teeth//2, 30)):  # planet can't be too big
            
            sun_teeth = r1_teeth - 2*p1_teeth
            if(sun_teeth < 8):
                continue
            
            # Check constraint for 120° spacing: (r1_teeth + sun_teeth) divisible by 3
            if (r1_teeth + sun_teeth) % 3 != 0:
                continue
                
            if sun_teeth <= 0:  # sun must have positive teeth
                continue
                
            for r2_teeth in range(20, max_teeth):
                p2_teeth = r2_teeth - sun_teeth - p1_teeth
                
                if p2_teeth <= 0:  # p2 must have positive teeth
                    continue
                
                # Calculate gear ratio using your formulas
                I1 = r1_teeth / sun_teeth
                I2 = (r1_teeth * p2_teeth) / (r2_teeth * p1_teeth)
                G = (1 - I2) / (1 + I1)
                
                if abs(G) < 1e-10:  # avoid division by zero
                    continue
                    
                actual_ratio = 1 / G
                
                error = abs(actual_ratio - target_ratio)
                
                if error < best_error:
                    best_error = error
                    best_config = {
                        'sun_teeth': sun_teeth,
                        'p1_teeth': p1_teeth,
                        'r1_teeth': r1_teeth,
                        'p2_teeth': p2_teeth,
                        'r2_teeth': r2_teeth,
                        'actual_ratio': actual_ratio,
                        'error': error,
                        'error_percent': (error/target_ratio)*100
                    }
    
    return best_config

def find_minimum_ring1_gear_ratio(target_ratio, max_error_percent=5.0, max_teeth=500):
    """
    Find minimum ring1 tooth count that achieves target ratio within error tolerance
    while maintaining 120° carrier spacing (3 planets)
    
    Constraint: (r1_teeth + sun_teeth) must be divisible by 3 for even spacing
    """
    # Search from smallest ring1 to largest
    for r1_teeth in range(20, max_teeth):
        for p1_teeth in range(8, min(r1_teeth//2, 30)):
            
            sun_teeth = r1_teeth - 2*p1_teeth
            if(sun_teeth < 8):
                continue

            # Check constraint for 120° spacing: (r1_teeth + sun_teeth) divisible by 3
            if (r1_teeth + sun_teeth) % 3 != 0:
                continue
                
            if sun_teeth <= 0:  # sun must have positive teeth
                continue
                
            for r2_teeth in range(20, max_teeth):
                p2_teeth = r2_teeth - sun_teeth - p1_teeth
                
                if p2_teeth <= 0:  # p2 must have positive teeth
                    continue
                
                # Calculate gear ratio using your formulas
                I1 = r1_teeth / sun_teeth
                I2 = (r1_teeth * p2_teeth) / (r2_teeth * p1_teeth)
                G = (1 - I2) / (1 + I1)
                
                if abs(G) < 1e-10:  # avoid division by zero
                    continue
                    
                actual_ratio = 1 / G
                
                error_percent = abs(actual_ratio - target_ratio) / target_ratio * 100
                
                if error_percent <= max_error_percent:
                    return {
                        'sun_teeth': sun_teeth,
                        'p1_teeth': p1_teeth,
                        'r1_teeth': r1_teeth,
                        'p2_teeth': p2_teeth,
                        'r2_teeth': r2_teeth,
                        'actual_ratio': actual_ratio,
                        'error_percent': error_percent
                    }
    
    return None  # No solution found within tolerance

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optimize gear ratios for split ring compound planetary gearbox')
    parser.add_argument('target_ratio', type=float, help='Target gear ratio (required)')
    parser.add_argument('--min-error', action='store_true', 
                       help='Use minimum error algorithm instead of minimum tooth count (default: min-tooth)')
    parser.add_argument('--tolerance', type=float, default=5.0,
                       help='Error tolerance percentage for min-tooth algorithm (default: 5.0)')
    
    args = parser.parse_args()
    
    if args.min_error:
        # Use minimum error algorithm
        result = find_nearest_gear_ratio(args.target_ratio)
        print("=== MINIMUM ERROR ===")
        if result:
            print(f"Target ratio: {args.target_ratio}")
            print(f"Actual ratio: {result['actual_ratio']:.6f}")
            print(f"Error: {result['error_percent']:.4f}%")
            print(f"Sun teeth: {result['sun_teeth']}")
            print(f"Planet 1 teeth: {result['p1_teeth']}")
            print(f"Ring 1 teeth: {result['r1_teeth']}")
            print(f"Planet 2 teeth: {result['p2_teeth']}")
            print(f"Ring 2 teeth: {result['r2_teeth']}")
        else:
            print("No valid configuration found")
    else:
        # Use minimum tooth count algorithm (default)
        result = find_minimum_ring1_gear_ratio(args.target_ratio, max_error_percent=args.tolerance)
        print(f"=== MINIMUM TOOTH COUNT ({args.tolerance}% tolerance) ===")
        if result:
            print(f"Target ratio: {args.target_ratio}")
            print(f"Actual ratio: {result['actual_ratio']:.6f}")
            print(f"Error: {result['error_percent']:.4f}%")
            print(f"Sun teeth: {result['sun_teeth']}")
            print(f"Planet 1 teeth: {result['p1_teeth']}")
            print(f"Ring 1 teeth: {result['r1_teeth']}")
            print(f"Planet 2 teeth: {result['p2_teeth']}")
            print(f"Ring 2 teeth: {result['r2_teeth']}")
        else:
            print(f"No solution found within {args.tolerance}% tolerance")