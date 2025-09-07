# Sensitivity Analysis - Monte Carlo Simulation

## Overview

The Sensitivity Analysis tab provides comprehensive Monte Carlo simulation capabilities to analyze the impact of parameter uncertainty on fair value estimates. This feature allows you to run thousands of scenarios with varying input parameters to understand the distribution of possible fair values.

## Features

### 1. Monte Carlo Simulation
- **Configurable scenarios**: Run 100-10,000 scenarios
- **Real-time progress tracking**: Visual progress bar and status updates
- **Background processing**: Non-blocking simulation execution
- **Robust error handling**: Graceful handling of failed scenarios

### 2. Parameter Sensitivity Analysis

#### Discount Rate (Cost of Equity)
- **Base**: 7.5% (configurable)
- **Range**: ±1.0-1.5% around base
- **Typical range**: 6.5% → 9.0%
- **Impact**: High sensitivity - directly affects present value calculations

#### Perpetual Growth Rate
- **Base**: 2.9% (configurable)
- **Range**: ±0.5-1.0%
- **Typical range**: 2.0% → 3.5%
- **Impact**: High sensitivity - affects terminal value significantly

#### Profitability (Net Income Margin)
- **Base**: ~25% (configurable)
- **Range**: ±2-3 percentage points
- **Typical range**: 22% → 28%
- **Impact**: Medium sensitivity - affects cash flow generation

#### Reinvestment Needs
- **CapEx Variation**: ±10-20% around base
- **Working Capital Variation**: ±10-15% around base
- **Impact**: Lower sensitivity for mature companies like Apple

#### Leverage Policy (Net Borrowings)
- **Base**: Small debt repayment
- **Range**: ±20-30% around base
- **Impact**: Lower sensitivity for equity-focused valuations

### 3. Statistical Analysis
- **Mean**: Average fair value across all scenarios
- **Median**: Middle value (50th percentile)
- **Standard Deviation**: Measure of uncertainty
- **Min/Max**: Range of possible values
- **5th/95th Percentiles**: Confidence intervals

### 4. Visualization
- **Histogram**: Distribution of fair values
- **Statistical markers**: Mean, median, and percentile lines
- **Interactive plots**: Zoom and pan capabilities
- **Export functionality**: Save plots as high-resolution images

## Usage Instructions

### 1. Prerequisites
- Run a baseline valuation first (use the Valuation tab)
- Ensure all required data is loaded and parameters are set

### 2. Running the Simulation
1. Navigate to the "Sensitivity Analysis" tab
2. Set the number of scenarios (default: 1000)
3. Adjust parameter ranges if needed
4. Click "Run Monte Carlo Simulation"
5. Monitor progress in the progress bar
6. View results when simulation completes

### 3. Interpreting Results

#### Histogram Analysis
- **Peak location**: Most likely fair value
- **Distribution width**: Uncertainty level
- **Skewness**: Asymmetric risk (upside vs. downside)

#### Statistical Metrics
- **Mean vs. Median**: Indicates distribution skewness
- **Standard Deviation**: Higher values indicate more uncertainty
- **Percentiles**: 5th and 95th percentiles show 90% confidence interval

#### Parameter Impact
- **High sensitivity parameters**: Focus risk management efforts
- **Low sensitivity parameters**: Less critical for accuracy

## Technical Implementation

### Architecture
- **Threading**: Non-blocking simulation execution
- **Parameter sampling**: Normal distribution with configurable ranges
- **Batch processing**: Efficient handling of large scenario counts
- **Error recovery**: Graceful handling of failed scenarios

### Parameter Modification
The simulation temporarily modifies model parameters:
1. **Backup**: Store original parameter values
2. **Modify**: Apply sampled parameter values
3. **Calculate**: Run valuation with new parameters
4. **Restore**: Return to original parameter values

### Performance Optimization
- **Batch processing**: Process scenarios in batches
- **Progress updates**: Real-time feedback to user
- **Memory management**: Efficient handling of large result sets
- **Error isolation**: Failed scenarios don't affect others

## Example Results

### Typical Output for Apple (AAPL)
```
SENSITIVITY ANALYSIS SUMMARY
============================
Baseline Fair Value: $150.25
Discount Rate Range: $120.50 - $185.75
Growth Rate Range: $135.20 - $170.80
Profitability Range: $140.15 - $165.30

Sensitivity Coefficients:
Discount Rate: $4,350 per 1% change
Growth Rate: $1,780 per 1% change
Profitability: $1,250 per 1% change
```

### Interpretation
- **Discount rate** has the highest sensitivity
- **Growth rate** has moderate sensitivity
- **Profitability** has lower sensitivity
- **Total range**: $120.50 - $185.75 (54% spread)

## Best Practices

### 1. Parameter Range Selection
- **Conservative ranges**: Start with ±1-2% for key parameters
- **Realistic bounds**: Don't exceed economically reasonable limits
- **Historical analysis**: Use past volatility as a guide

### 2. Scenario Count
- **Minimum**: 100 scenarios for basic analysis
- **Recommended**: 1,000 scenarios for reliable statistics
- **Maximum**: 10,000 scenarios for high precision

### 3. Risk Management
- **Focus on high-sensitivity parameters**: Prioritize accuracy
- **Monitor confidence intervals**: Use 5th-95th percentiles
- **Regular updates**: Re-run analysis when market conditions change

### 4. Interpretation Guidelines
- **Mean vs. baseline**: Compare to single-point estimate
- **Distribution shape**: Normal vs. skewed distributions
- **Outlier analysis**: Investigate extreme scenarios

## Troubleshooting

### Common Issues
1. **Simulation fails**: Check if baseline valuation works
2. **No results**: Ensure sufficient scenarios complete successfully
3. **Extreme values**: Verify parameter ranges are reasonable
4. **Slow performance**: Reduce scenario count or parameter complexity

### Error Messages
- **"No valuation model available"**: Run baseline valuation first
- **"Simulation failed"**: Check parameter ranges and data quality
- **"Insufficient results"**: Increase scenario count or adjust ranges

## Future Enhancements

### Planned Features
- **Correlation analysis**: Parameter interdependencies
- **Scenario filtering**: Focus on specific outcome ranges
- **Export functionality**: Save results to Excel/CSV
- **Advanced visualizations**: 3D plots, correlation matrices
- **Custom distributions**: Non-normal parameter sampling
- **Risk metrics**: VaR, CVaR, and other risk measures

### Integration Opportunities
- **Portfolio analysis**: Multi-stock sensitivity analysis
- **Risk budgeting**: Allocate risk across parameters
- **Stress testing**: Extreme scenario analysis
- **Real-time updates**: Live parameter monitoring

## Conclusion

The Sensitivity Analysis feature provides powerful tools for understanding valuation uncertainty and parameter sensitivity. By running thousands of scenarios with varying inputs, you can:

- **Quantify uncertainty**: Understand the range of possible outcomes
- **Identify key risks**: Focus on high-sensitivity parameters
- **Improve decision-making**: Make informed choices with confidence intervals
- **Communicate results**: Present findings with statistical rigor

This comprehensive analysis helps bridge the gap between single-point estimates and the reality of parameter uncertainty in financial modeling.
