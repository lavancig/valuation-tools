#!/usr/bin/env python3
"""
Test script for the new parameter weights functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.DCF_FCFE import DCF_FCFE

def test_parameter_weights():
    """Test the new parameter weights functionality"""
    
    print("Testing Parameter Weights Functionality...")
    print("="*50)
    
    # Create DCF model for testing
    ticker = 'AAPL'
    try:
        dcf = DCF_FCFE(ticker)
        
        if not dcf._successful:
            print(f"Failed to download data for {ticker}")
            return
        
        print(f"Successfully loaded data for {ticker}")
        
        # Test 1: Baseline valuation (no parameter weights)
        print("\n1. Baseline Valuation (no parameter weights):")
        baseline_value, baseline_summary = dcf.calculateFairValue(5, storeResults=True)
        print(f"Baseline fair value: ${baseline_value:.2f}")
        
        # Test 2: Discount rate sensitivity
        print("\n2. Discount Rate Sensitivity:")
        discount_weights = [
            {'discount_rate': -0.1},  # 10% decrease
            {'discount_rate': 0.0},   # No change
            {'discount_rate': 0.1},   # 10% increase
            {'discount_rate': 0.2}    # 20% increase
        ]
        
        for weights in discount_weights:
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            change = weights['discount_rate'] * 100
            print(f"  Discount rate {change:+.0f}%: ${value:.2f}")
        
        # Test 3: Growth rate sensitivity
        print("\n3. Growth Rate Sensitivity:")
        growth_weights = [
            {'growth_rate': -0.2},  # 20% decrease
            {'growth_rate': 0.0},   # No change
            {'growth_rate': 0.2},   # 20% increase
            {'growth_rate': 0.4}    # 40% increase
        ]
        
        for weights in growth_weights:
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            change = weights['growth_rate'] * 100
            print(f"  Growth rate {change:+.0f}%: ${value:.2f}")
        
        # Test 4: Profitability sensitivity
        print("\n4. Profitability Sensitivity:")
        profit_weights = [
            {'profitability': -0.1},  # 10% decrease
            {'profitability': 0.0},   # No change
            {'profitability': 0.1},   # 10% increase
            {'profitability': 0.2}    # 20% increase
        ]
        
        for weights in profit_weights:
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            change = weights['profitability'] * 100
            print(f"  Profitability {change:+.0f}%: ${value:.2f}")
        
        # Test 5: Multiple parameter changes
        print("\n5. Multiple Parameter Changes:")
        multi_weights = [
            {
                'discount_rate': 0.1,    # 10% increase
                'growth_rate': -0.1,     # 10% decrease
                'profitability': 0.05,   # 5% increase
                'capex': 0.1,            # 10% increase
                'nwc': 0.05,             # 5% increase
                'net_borrowings': -0.05  # 5% decrease
            }
        ]
        
        for weights in multi_weights:
            value, _ = dcf.calculateFairValue(5, weights, storeResults=False)
            print(f"  Multiple changes: ${value:.2f}")
            print(f"    Changes: Discount +10%, Growth -10%, Profit +5%, CapEx +10%, NWC +5%, Borrowings -5%")
        
        # Test 6: Scenario-based weights (like the old scenarios)
        print("\n6. Scenario-based Parameter Weights:")
        
        pessimistic_weights = {
            'discount_rate': 0.15,      # 15% increase
            'growth_rate': -0.2,        # 20% decrease
            'profitability': -0.1,      # 10% decrease
            'capex': 0.1,               # 10% increase
            'nwc': 0.1,                 # 10% increase
            'net_borrowings': -0.1      # 10% decrease
        }
        
        optimistic_weights = {
            'discount_rate': -0.1,      # 10% decrease
            'growth_rate': 0.2,         # 20% increase
            'profitability': 0.1,       # 10% increase
            'capex': -0.1,              # 10% decrease
            'nwc': -0.1,                # 10% decrease
            'net_borrowings': 0.1       # 10% increase
        }
        
        pessimistic_value, _ = dcf.calculateFairValue(5, pessimistic_weights, storeResults=False)
        optimistic_value, _ = dcf.calculateFairValue(5, optimistic_weights, storeResults=False)
        
        print(f"  Pessimistic scenario: ${pessimistic_value:.2f}")
        print(f"  Optimistic scenario: ${optimistic_value:.2f}")
        print(f"  Range: ${pessimistic_value:.2f} - ${optimistic_value:.2f}")
        
        # Test 7: Verify parameter restoration
        print("\n7. Parameter Restoration Test:")
        print("  Testing that parameters are restored after calculation...")
        
        # Get original discount rate
        original_discount = dcf._discountObj._discountRate if hasattr(dcf._discountObj, '_discountRate') else 0.075
        print(f"  Original discount rate: {original_discount:.4f}")
        
        # Apply weights and calculate
        test_weights = {'discount_rate': 0.2}  # 20% increase
        dcf.calculateFairValue(5, test_weights, storeResults=False)
        
        # Check if restored
        restored_discount = dcf._discountObj._discountRate if hasattr(dcf._discountObj, '_discountRate') else 0.075
        print(f"  Restored discount rate: {restored_discount:.4f}")
        
        if abs(original_discount - restored_discount) < 0.0001:
            print("  ✓ Parameters successfully restored!")
        else:
            print("  ✗ Parameter restoration failed!")
        
        print("\n✓ Parameter weights functionality test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parameter_weights()
