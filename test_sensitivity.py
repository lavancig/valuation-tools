#!/usr/bin/env python3
"""
Test script for Sensitivity Analysis functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt
from src.DCF_FCFE import DCF_FCFE

def test_sensitivity_analysis():
    """Test the sensitivity analysis with a simple example"""
    
    print("Testing Sensitivity Analysis...")
    print("="*50)
    
    # Create DCF model for testing
    ticker = 'AAPL'
    try:
        dcf = DCF_FCFE(ticker)
        
        if not dcf._successful:
            print(f"Failed to download data for {ticker}")
            return
        
        print(f"Successfully loaded data for {ticker}")
        
        # Run a baseline valuation
        print("\nRunning baseline valuation...")
        baseline_value, baseline_summary = dcf.calculateFairValue(scenario='realistic', storeResults=True)
        print(f"Baseline fair value: ${baseline_value:.2f}")
        
        # Test parameter sensitivity manually
        print("\nTesting parameter sensitivity...")
        
        # Test discount rate sensitivity
        print("\n1. Discount Rate Sensitivity:")
        original_discount = dcf._discountObj._discountRate if hasattr(dcf._discountObj, '_discountRate') else 0.075
        
        discount_rates = [0.065, 0.075, 0.085, 0.095]
        discount_results = []
        
        for rate in discount_rates:
            dcf._discountObj._discountRate = rate
            value, _ = dcf.calculateFairValue(scenario='realistic', storeResults=False)
            discount_results.append(value)
            print(f"  Discount Rate {rate*100:.1f}%: ${value:.2f}")
        
        # Restore original discount rate
        dcf._discountObj._discountRate = original_discount
        
        # Test growth rate sensitivity
        print("\n2. Perpetual Growth Rate Sensitivity:")
        original_growth = dcf._revenueObj._perpetualGrowthRate if hasattr(dcf._revenueObj, '_perpetualGrowthRate') else 0.029
        
        growth_rates = [0.02, 0.025, 0.029, 0.035]
        growth_results = []
        
        for rate in growth_rates:
            dcf._revenueObj._perpetualGrowthRate = rate
            value, _ = dcf.calculateFairValue(scenario='realistic', storeResults=False)
            growth_results.append(value)
            print(f"  Growth Rate {rate*100:.1f}%: ${value:.2f}")
        
        # Restore original growth rate
        dcf._revenueObj._perpetualGrowthRate = original_growth
        
        # Test profitability sensitivity
        print("\n3. Profitability Sensitivity:")
        original_profitability = dcf._incomeObj._incomeMargin if hasattr(dcf._incomeObj, '_incomeMargin') else 0.25
        
        profitability_rates = [0.22, 0.24, 0.25, 0.27, 0.28]
        profitability_results = []
        
        for rate in profitability_rates:
            dcf._incomeObj._incomeMargin = rate
            value, _ = dcf.calculateFairValue(scenario='realistic', storeResults=False)
            profitability_results.append(value)
            print(f"  Profitability {rate*100:.1f}%: ${value:.2f}")
        
        # Restore original profitability
        dcf._incomeObj._incomeMargin = original_profitability
        
        # Create simple sensitivity plots
        print("\nCreating sensitivity plots...")
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Discount rate sensitivity
        axes[0].plot([r*100 for r in discount_rates], discount_results, 'bo-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Discount Rate (%)')
        axes[0].set_ylabel('Fair Value ($)')
        axes[0].set_title('Discount Rate Sensitivity')
        axes[0].grid(True, alpha=0.3)
        
        # Growth rate sensitivity
        axes[1].plot([r*100 for r in growth_rates], growth_results, 'go-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Perpetual Growth Rate (%)')
        axes[1].set_ylabel('Fair Value ($)')
        axes[1].set_title('Growth Rate Sensitivity')
        axes[1].grid(True, alpha=0.3)
        
        # Profitability sensitivity
        axes[2].plot([r*100 for r in profitability_rates], profitability_results, 'ro-', linewidth=2, markersize=8)
        axes[2].set_xlabel('Profitability (%)')
        axes[2].set_ylabel('Fair Value ($)')
        axes[2].set_title('Profitability Sensitivity')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sensitivity_analysis.png', dpi=300, bbox_inches='tight')
        print("Sensitivity plots saved as 'sensitivity_analysis.png'")
        
        # Summary statistics
        print("\n" + "="*50)
        print("SENSITIVITY ANALYSIS SUMMARY")
        print("="*50)
        
        print(f"Baseline Fair Value: ${baseline_value:.2f}")
        print(f"Discount Rate Range: ${min(discount_results):.2f} - ${max(discount_results):.2f}")
        print(f"Growth Rate Range: ${min(growth_results):.2f} - ${max(growth_results):.2f}")
        print(f"Profitability Range: ${min(profitability_results):.2f} - ${max(profitability_results):.2f}")
        
        # Calculate sensitivity coefficients
        discount_sensitivity = (max(discount_results) - min(discount_results)) / (max(discount_rates) - min(discount_rates))
        growth_sensitivity = (max(growth_results) - min(growth_results)) / (max(growth_rates) - min(growth_rates))
        profitability_sensitivity = (max(profitability_results) - min(profitability_results)) / (max(profitability_rates) - min(profitability_rates))
        
        print(f"\nSensitivity Coefficients:")
        print(f"Discount Rate: ${discount_sensitivity:.2f} per 1% change")
        print(f"Growth Rate: ${growth_sensitivity:.2f} per 1% change")
        print(f"Profitability: ${profitability_sensitivity:.2f} per 1% change")
        
        print("\nSensitivity analysis completed successfully!")
        
    except Exception as e:
        print(f"Error during sensitivity analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sensitivity_analysis()
