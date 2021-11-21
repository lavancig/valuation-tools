from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class ConstantGrowthRevenue(RevenueBase):
    
    def __init__(self, growthRate, perpetualGrowthRate, perpetualDiscount):
        self._growthRate = growthRate
        self._perpetualGrowthRate = perpetualGrowthRate
        self._perpetualDiscount = perpetualDiscount

    def getRevenueStreams(self, revenueStreams, untilTime):
        lastTime = revenueStreams.columns.values[-1]
        if untilTime <= lastTime:
            return revenueStreams

        revenueStreamPredictions = copy.deepcopy(revenueStreams)

        while True:
            lastTime = revenueStreamPredictions.columns.values[-1]
            nextTime = np.add(lastTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            lastRevenue = revenueStreamPredictions.loc['Total Revenue', lastTime]
            revenueStreamPredictions.loc['Total Revenue', nextTime] = lastRevenue * (1 + self._growthRate)
            
        lastTime = revenueStreamPredictions.columns.values[-1]
        lastRevenue = revenueStreamPredictions.loc['Total Revenue', lastTime]
        revenueStreamPredictions.loc['Total Revenue','perpetual'] = lastRevenue * (1 + self._perpetualGrowthRate) / ( self._perpetualDiscount - self._perpetualGrowthRate)
        return revenueStreamPredictions


