#!/usr/bin/env python3
"""
Test script for Monte Carlo simulation with explicit weight application
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from src.DCF_FCFE import DCF_FCFE

def test_monte_carlo_weights():
    """Test Monte Carlo simulation with explicit weight application"""
    
    print("Testing Monte Carlo Simulation with Explicit Weight Application...")
    print("="*60)
    
    # Create DCF model for testing
    ticker = 'AAPL'
    try:
        dcf = DCF_FCFE(ticker)
        
        if not dcf._successful:
            print(f"Failed to download data for {ticker}")
            return
        
        print(f"Successfully loaded data for {ticker}")
        
        # Test 1: Baseline valuation
        print("\n1. Baseline Valuation:")
        baseline_value, _ = dcf.calculateFairValue(5, storeResults=True)
        print(f"Baseline fair value: ${baseline_value:.2f}")
        
        # Test 2: Single parameter variation
        print("\n2. Single Parameter Variations:")
        
        # Test discount rate variation
        discount_weights = [
            {'discount_rate': -0.1},  # 10% decrease
            {'discount_rate': 0.0},   # No change
            {'discount_rate': 0.1},   # 10% increase
        ]
        
        for weights in discount_weights:
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            change = weights['discount_rate'] * 100
            print(f"  Discount rate {change:+.0f}%: ${value:.2f}")
        
        # Test 3: Multiple parameter variations (simulating Monte Carlo samples)
        print("\n3. Multiple Parameter Variations (Monte Carlo Style):")
        
        # Generate some random parameter weights
        np.random.seed(42)  # For reproducible results
        
        for i in range(5):
            # Generate random parameter weights
            weights = {
                'discount_rate': np.random.normal(0, 0.05),              # ±5% variation
                'perpetual_growth': np.random.normal(0, 0.03),           # ±3% variation
                'prediction_window_growth': np.random.normal(0, 0.03),   # ±3% variation
                'profitability': np.random.normal(0, 0.05),              # ±5% variation
                'capex': np.random.normal(0, 0.1),                       # ±10% variation
                'nwc': np.random.normal(0, 0.1),                         # ±10% variation
                'net_borrowings': np.random.normal(0, 0.1)               # ±10% variation
            }
            
            # Clamp weights to reasonable ranges
            weights['discount_rate'] = max(-0.2, min(0.2, weights['discount_rate']))
            weights['perpetual_growth'] = max(-0.1, min(0.1, weights['perpetual_growth']))  # ±10% max for perpetual growth
            weights['prediction_window_growth'] = max(-0.1, min(0.1, weights['prediction_window_growth']))  # ±10% max for prediction window growth
            weights['profitability'] = max(-0.2, min(0.2, weights['profitability']))
            weights['capex'] = max(-0.3, min(0.3, weights['capex']))
            weights['nwc'] = max(-0.3, min(0.3, weights['nwc']))
            weights['net_borrowings'] = max(-0.3, min(0.3, weights['net_borrowings']))
            
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            
            print(f"  Sample {i+1}: ${value:.2f}")
            print(f"    Weights: Discount {weights['discount_rate']*100:+.1f}%, "
                  f"Perpetual Growth {weights['perpetual_growth']*100:+.1f}%, "
                  f"Prediction Growth {weights['prediction_window_growth']*100:+.1f}%, "
                  f"Profit {weights['profitability']*100:+.1f}%")
        
        # Test 4: Simulate a small Monte Carlo run
        print("\n4. Small Monte Carlo Simulation (10 scenarios):")
        
        monte_carlo_results = []
        np.random.seed(123)  # For reproducible results
        
        for i in range(10):
            # Generate random parameter weights
            weights = {
                'discount_rate': np.random.normal(0, 0.05),
                'perpetual_growth': np.random.normal(0, 0.03),
                'prediction_window_growth': np.random.normal(0, 0.03),
                'profitability': np.random.normal(0, 0.05),
                'capex': np.random.normal(0, 0.1),
                'nwc': np.random.normal(0, 0.1),
                'net_borrowings': np.random.normal(0, 0.1)
            }
            
            # Clamp weights
            for key in weights:
                weights[key] = max(-0.2, min(0.2, weights[key]))
            
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            monte_carlo_results.append(value)
        
        # Calculate statistics
        mean_value = np.mean(monte_carlo_results)
        std_value = np.std(monte_carlo_results)
        min_value = np.min(monte_carlo_results)
        max_value = np.max(monte_carlo_results)
        
        print(f"  Results: Mean=${mean_value:.2f}, Std=${std_value:.2f}")
        print(f"  Range: ${min_value:.2f} - ${max_value:.2f}")
        print(f"  Baseline: ${baseline_value:.2f}")
        
        # Test 5: Verify explicit weight application
        print("\n5. Verifying Explicit Weight Application:")
        
        # Test with known weights
        test_weights = {
            'discount_rate': 0.1,                    # 10% increase
            'perpetual_growth': -0.1,               # 10% decrease in perpetual growth
            'prediction_window_growth': 0.03,       # 3% increase in prediction window growth
            'profitability': 0.05,                   # 5% increase
        }
        
        value_with_weights, _ = dcf.calculateFairValue(5, test_weights, storeResults=False)
        print(f"  With weights: ${value_with_weights:.2f}")
        print(f"  Without weights: ${baseline_value:.2f}")
        print(f"  Difference: ${value_with_weights - baseline_value:.2f}")
        
        print("\n✓ Monte Carlo simulation with explicit weight application test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_monte_carlo_weights()
