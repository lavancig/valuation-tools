#!/usr/bin/env python3
"""
Batch Valuation Tool

This script processes a CSV file containing ticker symbols and calculates
both FCFF and FCFE fair values for each ticker, outputting the results to a CSV file.

Usage:
    python -m src.batch_valuation input.csv output.csv
    python -m src.batch_valuation elevated_iv_tickers_nodriver.csv results.csv
"""

import sys
import os
import pandas as pd
import argparse
from datetime import datetime
import traceback
import importlib.util

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from DCF_FCFE import DCF_FCFE
from DCF_FCFF import DCF_FCFF


class BatchValuation:
    """Batch valuation processor for multiple tickers"""
    
    def __init__(self, prediction_window=5):
        """
        Initialize the batch valuation processor
        
        Args:
            prediction_window (int): Number of years to project (default: 5)
        """
        self.prediction_window = prediction_window
        self.results = []
        
    def process_ticker(self, ticker):
        """
        Process a single ticker and calculate both FCFF and FCFE valuations
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Results dictionary with ticker, FCFF value, FCFE value, and status
        """
        result = {
            'ticker': ticker,
            'fcff_fair_value': None,
            'fcfe_fair_value': None,
            'fcff_status': 'Failed',
            'fcfe_status': 'Failed',
            'fcff_error': None,
            'fcfe_error': None,
            'current_price': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Processing {ticker}...")
        
        # Try FCFF calculation
        try:
            fcff_model = DCF_FCFF(ticker)
            if fcff_model._successful:
                fcff_value, _ = fcff_model.calculateFairValue(self.prediction_window, storeResults=True)
                result['fcff_fair_value'] = round(fcff_value, 2)
                result['fcff_status'] = 'Success'
                result['current_price'] = fcff_model.getCurrentPrice()
                print(f"  FCFF: ${fcff_value:.2f}")
            else:
                result['fcff_error'] = "Failed to download company data"
                print(f"  FCFF: Failed - No data available")
        except Exception as e:
            result['fcff_error'] = str(e)
            print(f"  FCFF: Failed - {str(e)}")
        
        # Try FCFE calculation
        try:
            fcfe_model = DCF_FCFE(ticker)
            if fcfe_model._successful:
                fcfe_value, _ = fcfe_model.calculateFairValue(self.prediction_window, storeResults=True)
                result['fcfe_fair_value'] = round(fcfe_value, 2)
                result['fcfe_status'] = 'Success'
                if result['current_price'] is None:  # Use FCFE current price if FCFF failed
                    result['current_price'] = fcfe_model.getCurrentPrice()
                print(f"  FCFE: ${fcfe_value:.2f}")
            else:
                result['fcfe_error'] = "Failed to download company data"
                print(f"  FCFE: Failed - No data available")
        except Exception as e:
            result['fcfe_error'] = str(e)
            print(f"  FCFE: Failed - {str(e)}")
        
        return result
    
    def process_csv(self, input_file, output_file=None):
        """
        Process a CSV file containing ticker symbols
        
        Args:
            input_file (str): Path to input CSV file
            output_file (str): Path to output CSV file (optional)
            
        Returns:
            pd.DataFrame: Results DataFrame
        """
        print(f"Reading tickers from {input_file}...")
        
        # Read the CSV file
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
        
        # Get the ticker column (assume first column or column named 'Ticker')
        if 'Ticker' in df.columns:
            tickers = df['Ticker'].dropna().tolist()
        else:
            tickers = df.iloc[:, 0].dropna().tolist()
        
        print(f"Found {len(tickers)} tickers to process")
        
        # Process each ticker
        results = []
        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] Processing {ticker}")
            result = self.process_ticker(ticker)
            results.append(result)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save to output file if specified
        if output_file:
            print(f"\nSaving results to {output_file}...")
            results_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
        
        # Print summary
        self.print_summary(results_df)
        
        return results_df
    
    def print_summary(self, results_df):
        """Print a summary of the results"""
        total_tickers = len(results_df)
        fcff_success = len(results_df[results_df['fcff_status'] == 'Success'])
        fcfe_success = len(results_df[results_df['fcfe_status'] == 'Success'])
        
        print(f"\n{'='*50}")
        print(f"BATCH VALUATION SUMMARY")
        print(f"{'='*50}")
        print(f"Total tickers processed: {total_tickers}")
        print(f"FCFF successful: {fcff_success} ({fcff_success/total_tickers*100:.1f}%)")
        print(f"FCFE successful: {fcfe_success} ({fcfe_success/total_tickers*100:.1f}%)")
        print(f"Both successful: {len(results_df[(results_df['fcff_status'] == 'Success') & (results_df['fcfe_status'] == 'Success')])}")
        
        # Show some successful examples
        successful = results_df[(results_df['fcff_status'] == 'Success') | (results_df['fcfe_status'] == 'Success')]
        if len(successful) > 0:
            print(f"\nSample results:")
            print(successful[['ticker', 'fcff_fair_value', 'fcfe_fair_value', 'current_price']].head(10).to_string(index=False))


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Batch valuation tool for multiple tickers')
    parser.add_argument('input_file', help='Input CSV file containing ticker symbols')
    parser.add_argument('output_file', nargs='?', help='Output CSV file (optional)')
    parser.add_argument('--prediction-window', type=int, default=5, 
                       help='Prediction window in years (default: 5)')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output_file:
        base_name = os.path.splitext(args.input_file)[0]
        args.output_file = f"{base_name}_valuation_results.csv"
    
    # Create and run batch processor
    processor = BatchValuation(prediction_window=args.prediction_window)
    
    try:
        results_df = processor.process_csv(args.input_file, args.output_file)
        if results_df is not None:
            print(f"\nBatch valuation completed successfully!")
            print(f"Results saved to: {args.output_file}")
        else:
            print("Batch valuation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nBatch valuation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
