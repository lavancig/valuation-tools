from .DCF_FCFE import DCF_FCFE



class ValuationModel:
    def __init__(self):
        pass
    
    def registerController(self, controllerObj):
        self._controllerObj = controllerObj
        
    def requestFairValueCalculation(self, type, predictionWindow, ticker):
        self._type = type
        self._ticker = ticker
        self._predictionWindow = predictionWindow
        if type == "FCFE":
            self._valuationObj = DCF_FCFE(ticker)
        else:
            print("Valuation type " + type + " Unimplemented. Aborting")
        
        self._valuationObj.calculateFairValue(self._predictionWindow)
        
    def getValuationSummaryTable(self):
        return self._valuationObj.getValuationSummaryTable()

    def getFairValue(self):
        return self._valuationObj.getFairValue()

    def setDiscountTypeWACC(self):
        self._valuationObj.setDiscountWACC()
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setDiscountTypeConstant(self, value):
        self._valuationObj.setDiscountConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setProfitabilityTypeConstant(self, value):
        self._valuationObj.setProfitabilityConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setProfitabilityTypeLastYearsAverage(self):
        self._valuationObj.setProfitabilityLastYearsAverage()
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setSharesOutstanding(self, number):
        self._valuationObj.setSharesOutstanding(number)

    def getSharesOutstanding(self):
        return self._valuationObj.getSharesOutstanding()

    def setFCFConstant(self, value):
        self._valuationObj.setFCFConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setFCFLastYearsAverage(self):
        self._valuationObj.setFCFLastYearsAverage()
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setRevenueSpecialistEstimates(self):
        self._valuationObj.setRevenueSpecialistEstimates()
        self._valuationObj.calculateFairValue(self._predictionWindow)

    def setRevenueConstant(self, value):
        self._valuationObj.setRevenueConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow)
