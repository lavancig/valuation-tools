from .DiscountRateBase import DiscountRateBase
import pandas as pd
import numpy as np 
import copy

class ConstantDiscountRate(DiscountRateBase):
    
    def __init__(self, discountRate):
        self._discountRate = discountRate

    def getDiscountRates(self, dates):
        discountRates = pd.DataFrame(np.asarray(np.ones([1, len(dates)]) * self._discountRate))
        discountRates.columns = dates.values
        discountRates.index = ['Discount Rate']
        return discountRates


