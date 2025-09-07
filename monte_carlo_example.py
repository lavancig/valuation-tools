#!/usr/bin/env python3
"""
Example of Monte Carlo simulation with explicit weight application
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from src.DCF_FCFE import DCF_FCFE

def monte_carlo_example():
    """Example of how Monte Carlo simulation works with explicit weights"""
    
    print("Monte Carlo Simulation Example with Explicit Weight Application")
    print("="*60)
    
    # Create DCF model
    ticker = 'AAPL'
    dcf = DCF_FCFE(ticker)
    
    if not dcf._successful:
        print(f"Failed to load data for {ticker}")
        return
    
    print(f"Loaded data for {ticker}")
    
    # Get baseline valuation
    baseline_value, _ = dcf.calculateFairValue(5, storeResults=True)
    print(f"Baseline fair value: ${baseline_value:.2f}")
    
    # Simulate Monte Carlo with 100 scenarios
    print(f"\nRunning Monte Carlo simulation with 100 scenarios...")
    
    results = []
    np.random.seed(42)  # For reproducible results
    
    for i in range(100):
        # Generate random parameter weights
        # These represent percentage changes from baseline values
        weights = {
            'discount_rate': np.random.normal(0, 0.05),              # ±5% variation in discount rate
            'perpetual_growth': np.random.normal(0, 0.03),           # ±3% variation in perpetual growth
            'prediction_window_growth': np.random.normal(0, 0.03),   # ±3% variation in prediction window growth
            'profitability': np.random.normal(0, 0.05),              # ±5% variation in profitability
            'capex': np.random.normal(0, 0.1),                       # ±10% variation in CapEx
            'nwc': np.random.normal(0, 0.1),                         # ±10% variation in NWC
            'net_borrowings': np.random.normal(0, 0.1)               # ±10% variation in net borrowings
        }
        
        # Clamp weights to reasonable ranges
        for key in weights:
            weights[key] = max(-0.2, min(0.2, weights[key]))
        
        # Calculate fair value with these parameter weights
        # The calculateFairValue method will apply these weights explicitly to each calculated table
        fair_value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
        
        if fair_value is not None and not np.isnan(fair_value):
            results.append(fair_value)
        
        # Progress indicator
        if (i + 1) % 20 == 0:
            print(f"  Completed {i + 1}/100 scenarios...")
    
    # Calculate statistics
    results = np.array(results)
    mean_value = np.mean(results)
    median_value = np.median(results)
    std_value = np.std(results)
    min_value = np.min(results)
    max_value = np.max(results)
    p5_value = np.percentile(results, 5)
    p95_value = np.percentile(results, 95)
    
    print(f"\nMonte Carlo Results ({len(results)} successful scenarios):")
    print("="*50)
    print(f"Mean:        ${mean_value:.2f}")
    print(f"Median:      ${median_value:.2f}")
    print(f"Std Dev:     ${std_value:.2f}")
    print(f"Min:         ${min_value:.2f}")
    print(f"Max:         ${max_value:.2f}")
    print(f"5th %ile:    ${p5_value:.2f}")
    print(f"95th %ile:   ${p95_value:.2f}")
    print(f"Baseline:    ${baseline_value:.2f}")
    
    # Calculate range and confidence interval
    range_value = max_value - min_value
    confidence_interval = p95_value - p5_value
    
    print(f"\nRange:       ${range_value:.2f}")
    print(f"90% CI:      ${p5_value:.2f} - ${p95_value:.2f}")
    
    # Show how the explicit weight application works
    print(f"\nHow Explicit Weight Application Works:")
    print("="*50)
    print("1. Generate parameter weights (percentage changes)")
    print("2. Call calculateFairValue(5, weights)")
    print("3. Inside calculateFairValue:")
    print("   - Calculate growthTable, then apply perpetual_growth weights to perpetual column")
    print("   - Apply prediction_window_growth weights to non-perpetual columns")
    print("   - Calculate discountTable, then apply discount_rate weights")
    print("   - Calculate profitabilityTable, then apply profitability weights")
    print("   - Calculate capExTable, then apply capex weights")
    print("   - Calculate deltaNWCTable, then apply nwc weights")
    print("   - Calculate netBorrowingsTable, then apply net_borrowings weights")
    print("   - Continue with remaining calculations using adjusted tables")
    print("4. Return fair value based on adjusted parameters")
    
    print(f"\n✓ Monte Carlo simulation example completed!")

if __name__ == "__main__":
    monte_carlo_example()
