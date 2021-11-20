# Base class to return revenue streams

class DiscountRateBase:
    
    def __init__(self):
        pass

    def getDiscountRates(self, dates):
        raise NotImplementedError("Please implement getRevenueStreams method in concrete revenue class")