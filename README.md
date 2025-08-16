# Valuation Tools

A comprehensive Python application for evaluating the fair value of publicly traded companies using Discounted Cash Flow (DCF) analysis with Free Cash Flow to Equity (FCFE) methodology.

## Features

- **DCF Valuation**: Calculate company fair value using FCFE methodology
- **Interactive GUI**: User-friendly interface with multiple tabs for different parameters
- **Real-time Data**: Fetches financial data from Yahoo Finance
- **Flexible Parameters**: Adjustable discount rates, growth assumptions, and profitability margins
- **Multiple Valuation Models**: Support for different revenue growth and profitability scenarios

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
1. Clone this repository:
```bash
git clone <repository-url>
cd valuation-tools
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python valuation.py
```

This will launch the GUI application with the following tabs:

- **Suitability**: Under development
- **Valuation**: Main valuation results and controls
- **Discount**: Configure discount rate parameters
- **Profitability**: Set profitability margin assumptions
- **FCF**: Configure free cash flow parameters
- **Revenue**: Set revenue growth assumptions
- **Parameters**: Global economic parameters

### Basic Workflow
1. Enter a company ticker symbol (e.g., AAPL, MSFT, GOOGL)
2. Set your prediction window (years into the future)
3. Choose valuation type (currently supports FCFE)
4. Adjust parameters as needed:
   - Risk-free interest rate
   - Market return expectations
   - Economy growth rate
   - Profitability margins
   - Revenue growth rates
5. View the calculated fair value per share

## Architecture

The application follows a Model-View-Controller (MVC) pattern:

- **Model**: `ValuationModel` and related classes handle business logic
- **View**: `GuiMain` and tab classes provide the user interface
- **Controller**: `Controller` coordinates between model and view

### Key Components

- **DCF_FCFE**: Core valuation engine using Free Cash Flow to Equity
- **Revenue Models**: Support for constant growth and analyst estimates
- **Income Models**: Constant margin profitability assumptions
- **Discount Rate Models**: WACC and constant rate options
- **Present Value**: Time value of money calculations

## Dependencies

- `yfinance`: Yahoo Finance data fetching
- `pandas`: Data manipulation and analysis
- `pandastable`: Enhanced table display in GUI
- `numpy`: Numerical computations
- `tkinter`: GUI framework (built-in with Python)

## Data Sources

The application fetches real-time financial data from Yahoo Finance, including:
- Income statements
- Balance sheets
- Cash flow statements
- Analyst estimates
- Company information (beta, shares outstanding, etc.)

## Limitations

- Requires internet connection for data fetching
- Depends on Yahoo Finance data availability
- Assumes constant margins and growth rates (configurable)
- Limited to publicly traded companies with available financial data

## Contributing

This is an open-source project. Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the terms specified in the LICENSE file.

## Disclaimer

This tool is for educational and research purposes only. The valuations provided are estimates based on the assumptions and data available. Always conduct thorough research and consider consulting with financial professionals before making investment decisions.
