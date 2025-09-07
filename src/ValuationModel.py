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
        
        # Calculate all three scenarios (this includes the realistic scenario)
        self._scenarioValues = self._valuationObj.calculateAllScenarios(self._predictionWindow)
        # Note: calculateAllScenarios already calls calculateFairValue internally for the realistic scenario
        
    def getValuationSummaryTable(self):
        return self._valuationObj.getValuationSummaryTable()

    def getFairValue(self):
        return self._valuationObj.getFairValue()
    
    def getAllScenarioValues(self):
        """Get fair values for all three scenarios"""
        return self._scenarioValues

    def setDiscountTypeWACC(self):
        self._valuationObj.setDiscountWACC()
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setDiscountCostOfEquity(self):
        self._valuationObj.setDiscountCostOfEquity()
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setDiscountTypeConstant(self, value):
        self._valuationObj.setDiscountConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setProfitabilityTypeConstant(self, value):
        self._valuationObj.setProfitabilityConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setProfitabilityTypeLastYearsAverage(self):
        self._valuationObj.setProfitabilityLastYearsAverage()
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setSharesOutstanding(self, number):
        self._valuationObj.setSharesOutstanding(number)

    def getSharesOutstanding(self):
        return self._valuationObj.getSharesOutstanding()

    def setFCFConstant(self, value):
        self._valuationObj.setFCFConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setFCFLastYearsAverage(self):
        self._valuationObj.setFCFLastYearsAverage()
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setRevenueSpecialistEstimates(self):
        self._valuationObj.setRevenueSpecialistEstimates()
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)

    def setRevenueConstant(self, value):
        self._valuationObj.setRevenueConstant(value)
        self._valuationObj.calculateFairValue(self._predictionWindow, storeResults=True)
