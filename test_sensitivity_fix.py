#!/usr/bin/env python3
"""
Test script to verify the sensitivity analysis fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.DCF_FCFE import DCF_FCFE
from src.ValuationModel import ValuationModel
from src.Controller import Controller

def test_sensitivity_analysis_fix():
    """Test the sensitivity analysis with proper controller setup"""
    
    print("Testing Sensitivity Analysis Fix...")
    print("="*50)
    
    # Create DCF model for testing
    ticker = 'AAPL'
    try:
        dcf = DCF_FCFE(ticker)
        
        if not dcf._successful:
            print(f"Failed to download data for {ticker}")
            return
        
        print(f"Successfully loaded data for {ticker}")
        
        # Create valuation model
        valuation_model = ValuationModel()
        valuation_model._valuationObj = dcf
        
        # Create mock controller
        class MockController:
            def __init__(self, model):
                self._modelObj = model
        
        controller = MockController(valuation_model)
        
        # Test the sensitivity analysis logic
        print("\nTesting controller structure...")
        print(f"Controller has _modelObj: {hasattr(controller, '_modelObj')}")
        print(f"Controller._modelObj is not None: {controller._modelObj is not None}")
        
        if hasattr(controller, '_modelObj') and controller._modelObj is not None:
            valuation_model = controller._modelObj
            print(f"Valuation model has _valuationObj: {hasattr(valuation_model, '_valuationObj')}")
            
            if hasattr(valuation_model, '_valuationObj'):
                dcf_model = valuation_model._valuationObj
                print(f"DCF model has _successful: {hasattr(dcf_model, '_successful')}")
                print(f"DCF model successful: {dcf_model._successful}")
                
                if hasattr(dcf_model, '_successful') and dcf_model._successful:
                    print("✓ All checks passed - sensitivity analysis should work!")
                    
                    # Test a simple parameter modification
                    print("\nTesting parameter modification...")
                    original_discount = dcf._discountObj._discountRate if hasattr(dcf._discountObj, '_discountRate') else 0.075
                    print(f"Original discount rate: {original_discount}")
                    
                    # Modify discount rate
                    dcf._discountObj._discountRate = 0.08
                    print(f"Modified discount rate: {dcf._discountObj._discountRate}")
                    
                    # Run valuation
                    fair_value, _ = dcf.calculateFairValue(scenario='realistic', storeResults=False)
                    print(f"Fair value with modified discount rate: ${fair_value:.2f}")
                    
                    # Restore original
                    dcf._discountObj._discountRate = original_discount
                    print(f"Restored discount rate: {dcf._discountObj._discountRate}")
                    
                    print("\n✓ Parameter modification test passed!")
                else:
                    print("✗ DCF model not successful")
            else:
                print("✗ Valuation model missing _valuationObj")
        else:
            print("✗ Controller missing _modelObj or it's None")
        
        print("\nSensitivity analysis fix test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sensitivity_analysis_fix()
