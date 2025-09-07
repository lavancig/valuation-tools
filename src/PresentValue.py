import pandas as pd
import numpy as np


# Calculates fair value based on free cash flow to equity
class PresentValue:
    def __init__(self, timeNow):
        self._timeNow = timeNow

    def getPresentValues(self, fcfValues, discountRates, type="FCFE"):
        presentValues = pd.DataFrame()
        discountRate = 1
        for date in fcfValues.columns[:-1]:
            timeDistance = np.datetime64(date, 'Y') - np.datetime64(self._timeNow, 'Y')
            if(timeDistance.astype(int) < 1):
                presentValues.loc['Present Value', date] = 0
            else:
                # Discount rate may be variable, so we have to go year by year
                presentValues.loc['Present Value', date] = 0
                discountRate = 1
                datevec = [np.datetime64(value, 'ns') for value in fcfValues.columns.values[:-1]]
                laterThanNow = np.array(datevec > np.datetime64(self._timeNow, 'ns'))
                beforeDate = np.array(datevec <= np.datetime64(date, 'ns'))
                indexes = np.where(np.logical_and(laterThanNow, beforeDate))
                for idx in indexes[0]:
                    # Check if the index is within bounds of the discount rates table
                    if idx < len(discountRates.columns) - 1:  # -1 to exclude 'perpetual' column
                        discountRate = discountRate * (1 + discountRates.loc['Discount Rate'].iloc[idx])
                    else:
                        # If we're beyond the available discount rates, use the last available rate
                        last_available_idx = len(discountRates.columns) - 2  # Last year (excluding 'perpetual')
                        discountRate = discountRate * (1 + discountRates.loc['Discount Rate'].iloc[last_available_idx])
                # Handle both FCFE and FCFF
                presentValues.loc['Present Value', date] = fcfValues.loc[type, date] / discountRate

        # Present value of perpetual growth part. Keeps the last discount rate and multiplies by the perpetual growth
            presentValues.loc['Present Value', 'perpetual'] = fcfValues.loc[type, 'perpetual'] / (discountRate * (1 + discountRates.loc['Discount Rate', 'perpetual']))  
        return presentValues

    def getPresentValue(self, fcfValues, discountRates, type="FCFE"):
        return sum(np.squeeze(self.getPresentValues(fcfValues, discountRates, type).values))