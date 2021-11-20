# Base class to return revenue streams

class IncomeBase:
    
    def __init__(self):
        pass

    def getIncomeStreams(self, timePeriod):
        raise NotImplementedError("Please implement getRevenueStreams method in concrete revenue class")