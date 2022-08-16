
import matplotlib.pyplot as plt
from binance.client import Client
import numpy as np
import random
import optuna
import math
import pprint
import sys
import pickle # Save and load data to and from storage
from os.path import exists
from termcolor import colored

from apiKeys import apiSecretKey
from apiKeys import apiKey



class Datum() :
    def __init__(self, openTime : float, openi : float, high : float, low : float, close : float, volume : float, closeTime : float, qav : float, numTrades : float, tbbavn : float, tbqav : float, indicators : list) :
        self.openTime = float(openTime)
        self.open = float(openi)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = float(volume)
        self.closeTime = float(closeTime)
        self.qav = float(qav)
        self.numTrades = float(numTrades)
        self.tbbavn = float(tbbavn)
        self.tbqav = float(tbqav)
        self.indic = indicators
        self.ratio=float()



class Data() :

    """ Contains the full sequence of values and provides train, validation and test sequences """

    def __init__(self, numPartitions : int = 5, trainProp : float = 0.7, validProp : float = 0.2, testProp : float = 0.1, ignoreTimer : int = 50, perday : float =96, sequenceLength : int = 10000) :
        # In order to shuffle train, valid and test data, the original sequence is partitionned into <numPartitions> equal partitions
        # Each partition contains a test, valid and test sequence.
        # Example with 2 partitions :
        # Full data sequence : [==============================================data==============================================]
        # Two partitions :     [===================Partition1==================][===================Partition2==================]
        # Train valid test :   [===========train1===========][==valid1==][test1][===========train2===========][==valid2==][test2]

            # Check type and value
        assert isinstance(numPartitions, int), f"[Type Error] :: <numPartitions> should be an integer (got '{type(numPartitions)}' instead)."
        assert numPartitions > 0, f"[Value Error] :: <numPartitions> should be > 0 (got '{numPartitions}' instead)."
        assert isinstance(trainProp, (float, int)), f"[Type Error] :: <trainProp> should be a float or an integer (got '{type(trainProp)}' instead)."
        assert trainProp >= 0, f"[Value Error] :: <trainProp> should be >= 0 (got '{trainProp}' instead)."
        assert trainProp <= 1, f"[Value Error] :: <trainProp> should be <= 1 (got '{trainProp}' instead)."
        assert isinstance(validProp, (float, int)), f"[Type Error] :: <validProp> should be a float or an integer (got '{type(validProp)}' instead)."
        assert validProp >= 0, f"[Value Error] :: <validProp> should be >= 0 (got '{validProp}' instead)."
        assert validProp <= 1, f"[Value Error] :: <validProp> should be <= 1 (got '{validProp}' instead)."
        assert isinstance(testProp, (float, int)), f"[Type Error] :: <testProp> should be a float or an integer (got '{type(testProp)}' instead)."
        assert testProp >= 0, f"[Value Error] :: <testProp> should be >= 0 (got '{testProp}' instead)."
        assert testProp <= 1, f"[Value Error] :: <testProp> should be <= 1 (got '{testProp}' instead)."
        totalProportions = trainProp + validProp + testProp
        assert abs(1 - totalProportions) < math.sqrt(sys.float_info.epsilon) , f"[Value Error] :: <totalProportions> should be == 1 (got '{totalProportions}' instead)."

            # Store values in object
        self.numPartitions = numPartitions
        self.trainprop = trainProp
        self.validProp = validProp
        self.testProp = testProp
        self.data = []
        self.ignoreTimer = ignoreTimer
        self.perday = perday
        self.length=sequenceLength #longueure de sequence active : celle sur la quelle est effectivement faite les trades

    def addDatum(self, datum : Datum) :
        self.data.append(datum)
        #print( self.data)


    def getValueStream(self, keyword : str = "close", minIndex : int = 0, maxIndex : int = -1) :
        return [_datum.__dict__[keyword] for _datum in self.data[minIndex:maxIndex]]


    def getTrainIndices(self, partitionIndex : int = None) :
            # Retun the train indices of a partition
        if partitionIndex is None :
            partitionIndex = random.randint(0, self.numPartitions-1)
        partitionLength = (len(self.data)) / self.numPartitions
        minIndex = math.ceil(partitionIndex * partitionLength)
        maxIndex = math.ceil(minIndex + self.trainprop * partitionLength)
        return minIndex, maxIndex


    def trainSequence(self, keyword : str = "close", partitionIndex : int = None) :
            # Retun the train sequence of a partition
        minIndex, maxIndex = self.getTrainIndices(partitionIndex=partitionIndex)
        return self.getValueStream(keyword=keyword, minIndex=minIndex, maxIndex=maxIndex)


    def trainSequences(self, keyword : str = "close") :
        # Retun the train sequences of all partitions
        for partitionIndex in range(self.numPartitions) :
            yield self.trainSequence(keyword=keyword, partitionIndex=partitionIndex)


    def getValidIndices(self, partitionIndex : int = None) :
            # Retun the valid indices of a partition
        if partitionIndex is None :
            partitionIndex = random.randint(0, self.numPartitions-1)
        partitionLength = (len(self.data)) / self.numPartitions
        minIndex = math.ceil(partitionIndex * partitionLength + self.trainprop * partitionLength)
        maxIndex = math.ceil(minIndex + self.validProp * partitionLength)
        return minIndex, maxIndex


    def validSequence(self, keyword : str = "close", partitionIndex : int = None) :
            # Retun the valid sequence of a partition
        minIndex, maxIndex = self.getValidIndices(partitionIndex=partitionIndex)
        return self.getValueStream(keyword=keyword, minIndex=minIndex, maxIndex=maxIndex)


    def validSequences(self, keyword : str = "close") :
        # Retun the valid sequences of all partitions
        for partitionIndex in range(self.numPartitions) :
            yield self.validSequence(keyword=keyword, partitionIndex=partitionIndex)


    def getTestIndices(self, partitionIndex : int = None) :
            # Return the test indices of a partition
        if partitionIndex is None :
            partitionIndex = random.randint(0, self.numPartitions-1)
        partitionLength = len(self.data) / self.numPartitions
        minIndex = math.ceil(partitionIndex * partitionLength + (self.trainprop + self.validProp) * partitionLength)
        maxIndex = math.ceil(minIndex + self.testProp * partitionLength)
        return minIndex, maxIndex


    def testSequence(self, keyword : str = "close", partitionIndex : int = None) :
            # Retun the test sequence of a partition
        minIndex, maxIndex = self.getTestIndices(partitionIndex=partitionIndex)
        return self.getValueStream(keyword=keyword, minIndex=minIndex, maxIndex=maxIndex)


    def testSequences(self, keyword : str = "close") :
        # Retun the test sequences of all partitions
        for partitionIndex in range(self.numPartitions) :
            yield self.testSequence(keyword=keyword, partitionIndex=partitionIndex)


    def plot(self, savePath : str = "_temp/data.png", keyword : str = "close", title : str = "", xlabel : str = "", ylabel : str = "") :
        plt.figure(figsize=(17,10))
        plt.plot(self.getValueStream(keyword))
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

            # Highlight partitions
        i=0
        for partitionIndex in range(self.numPartitions) :
            i+=1
            partitionColor = [0.6 + 0.4 * random.random() for _ in range(3)]
                # Highlight train sequence
            minIndex, maxIndex = self.getTrainIndices(partitionIndex=partitionIndex)
            #print("min index : {}, max index : {} for partition {} train".format(minIndex,maxIndex,i))
            color = [value - 0.2 for value in partitionColor]
            plt.axvspan(minIndex, maxIndex, color=color, alpha=0.5)
                # Highlight valid sequence
            minIndex, maxIndex = self.getValidIndices(partitionIndex=partitionIndex)
            #print("min index : {}, max index : {} for partition {} valid".format(minIndex,maxIndex,i))
            color = [value - 0.1 for value in partitionColor]
            plt.axvspan(minIndex, maxIndex, color=color, alpha=0.5)
                # Highlight train sequence
            minIndex, maxIndex = self.getTestIndices(partitionIndex=partitionIndex)
            #print("min index : {}, max index : {} for partition {} test".format(minIndex,maxIndex,i))
            color = partitionColor
            plt.axvspan(minIndex, maxIndex, color=color, alpha=0.5)
        plt.savefig(savePath)
        plt.close()


def loadData(paire : str = "BTCUSDT", sequenceLength : int = 100, interval_str : str = "15m", trainProp : float = 0.7, validProp : float = 0.2, testProp : float = 0.1, numPartitions : int = 5, reload : bool = True, ignoreTimer : int = 50) :
        # Check variable types and values
    assert isinstance(paire, str), f"[Type Error] :: <paire> should be a str (got '{type(paire)}' instead)."
    validPaires = ["BTCUSDT", "ETHUSDT", "DOGEUSDT","BTCBUSD"]
    assert paire in validPaires, f"[Value Error] :: <paire> should be one of {validPaires} (got '{paire}' instead)."
    assert isinstance(sequenceLength, int), f"[Type Error] :: <sequenceLength> should be an integer  (got '{type(sequenceLength)}' instead)."
    assert sequenceLength > 0, f"[Value Error] :: <sequenceLength> should be > 0 (got '{sequenceLength}' instead)."
    assert isinstance(interval_str, str), f"[Type Error] :: <interval_str> should be a str  (got '{type(interval_str)}' instead)."
    validIntervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
    assert interval_str in validIntervals, f"[Value Error] :: <interval_str> should be one of {validIntervals} (got '{interval_str}' instead)."
        # Format request
    intervalValue, intervalUnit = (int(interval_str[:-1]), interval_str[-1])
    duration = (sequenceLength+ignoreTimer) * intervalValue
    perday=24*60/intervalValue
    if intervalUnit == "h" :
        duration *= 60
    elif intervalUnit == "d" :
        duration *= 60 * 24
    elif intervalUnit == "w" :
        duration *= 60 * 24 * 7
    elif intervalUnit == "M" :
        duration *= 60 * 24 * 7 * 4
    duration = f"{duration} minutes˓→ago UTC"

        # Check if required data already exists in _temp/
    savePath = f"_temp/data_{paire}_{interval_str}_{sequenceLength}_{numPartitions}.pkl"
    if reload:
        if exists(savePath) :
            with open(savePath, "rb") as readFile:
                print(colored("Data opened","green"))   
                return pickle.load(readFile)
    #connect to Binance if no relaod of previous stored data
    binanceClient = Client(apiKey, apiSecretKey)
        # Request data
    klines = binanceClient.get_historical_klines(paire, interval_str, duration)

    data = Data(trainProp=trainProp, validProp=validProp, testProp=testProp, numPartitions=numPartitions,ignoreTimer=ignoreTimer,perday=perday,sequenceLength=sequenceLength)

    print("nombre de datua : {}".format(len(klines)))
    for line in klines : # klines format : https://python-binance.readthedocs.io/en/latest/binance.html
        data.addDatum(Datum(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10],[0]))
    print("nombre de data.data : {}".format(len(data.data)))
        # Save data locally for future usage
    with open(savePath, "wb") as saveFile:
        pickle.dump(data, saveFile, protocol=pickle.HIGHEST_PROTOCOL)

        # Return data to user
    print(colored("Data downloaded","green"))
    return data



def calculate_ema(newPrice : float, oldPrice : float, days : int = 10, smoothing : float = 2):
    return (newPrice * (smoothing / (1 + days))) + oldPrice * (1 - (smoothing / (1 + days)))


def computeRSI(der, d : int = 14) :
    if len(der) < d :
        return 50
    gp = 0
    lp = 0
    for k in range(d):
        if der[-(1 + k)] > 0 :
            gp += der[-(1 + k)]
        elif der[-(1 + k)] < 0 :
            lp -= der[-(1 + k)]
    if lp <= 0 :
        return 100
    else :
        RS = gp / lp
        return 100 - 100 / (1 + RS)

    
def createIndicatorDICO(data,hyperP : dict()):
    
    closeData = data.getValueStream('close')
    volumeData = data.getValueStream('volume')
    openData = data.getValueStream('open')
    highData = data.getValueStream('high')
    lowData = data.getValueStream('low')
    ratio =np.max(closeData)
    closeData /= ratio
    highData /= ratio
    openData /= ratio
    lowData /= ratio
    indices = {}
    indicateurs = []#0price regularized, 1volume, 
    #2derivé 1, 3dérivé 2, 4prix moyenné 1, 5prix moyenné 2, 6RSI, 7signe diff moy, 8dérivé diff moy
    #9dérivé 1 moy, 10dérivé 2 moy,11 signe écart
    
    
    for closeV, highV, lowV, volumeV in zip(closeData, highData, lowData, volumeData) :
        indicateurs.append({"closeV" : closeV})#0price regularized, 1volume, 
        #2derivé 1, 3dérivé 2, 4prix moyenné 1, 5prix moyenné 2, 6RSI, 7signe diff moy, 8dérivé diff moy
        #9dérivé 1 moy, 10dérivé 2 moy
        #definition du prix
        indicateurs[-1]={"closeV" : closeV}
     
        #definition du volume
        indicateurs[-1]["volume"]=np.sqrt(np.sqrt(np.abs(volumeV))) * np.sign(volumeV)
        
        #definition derivé 1
        if len(indicateurs)<=1:
            indicateurs[-1]["derivé"]=0
        else:
            indicateurs[-1]["derivé"]=indicateurs[-1]["closeV"]-indicateurs[i-1]["closeV"]
            
        #definition de derive 2
        if len(indicateurs)<2:
            indicateurs[-1]["dérivé2"]=0
        else:
            indicateurs[-1]["dérivé2"]=(indicateurs[-1]["derivé"]-indicateurs[-2]["derivé"])
            
        #definition prix moyenné 1
        if len(indicateurs)<=1:
            indicateurs[-1]["close_moy_1"]=indicateurs[-1]["closeV"]
        else:
            indicateurs[-1]["close_moy_1"]=calculate_ema(indicateurs[-1]["closeV"], indicateurs[-2]["close_moy_1"], hyperP["Theta"])
        
        #definition prix moyenné 2        
        if len(indicateurs)<=1:
            indicateurs[-1]["close_moy_2"]=indicateurs[-1]["closeV"]
        else:
            indicateurs[-1]["close_moy_2"]=calculate_ema(indicateurs[-1]["closeV"], indicateurs[-2]["close_moy_2"], hyperP["Theta_bis"]*hyperP["Theta"])
        
        #ajout de la différence de signe des moyennes
        indicateurs[-1]["sign_diff_moy"]=(np.sign(indicateurs[-1]["close_moy_2"]-indicateurs[-1]["close_moy_1"]))
        
        #ajout de la dérivée de diff de signe
        if len(indicateurs)<=1:
            indicateurs[-1]["derive_diff_close"]=(0)
        else:
            indicateurs[-1]["derive_diff_close"]=(indicateurs[-1]["close_moy_1"]-indicateurs[-1]["close_moy_2"]-indicateurs[-2]["close_moy_1"]+indicateurs[-2]["close_moy_2"])
        
        #definition dérivé moyennée 1
        if len(indicateurs)<=1:
            indicateurs[-1]["derive_moy_1"]=(indicateurs[-1]["derivé"])
        else:
            indicateurs[-1]["derive_moy_1"]=(calculate_ema(indicateurs[-1]["derivé"], indicateurs[-2]["derive_moy_1"], hyperP["Theta_der"]))        
            
        #definition dérivé moyennée 2
        if len(indicateurs)<=1:
            indicateurs[-1]["derive_moy_2"]=(indicateurs[-1]["derivé"])
        else:
            indicateurs[-1]["derive_moy_2"]=(calculate_ema(indicateurs[-1]["derivé"], indicateurs[-2]["derive_moy_2"], hyperP["Theta_der2"]))        
        
        #definition RSI
        if len(indicateurs)<=hyperP["Theta_RSI"]:
            indicateurs[-1]["RSI"]=50
        else:
            indicateurs[-1]["RSI"]=(computeRSI([indicateurs[-1-i]["closeV"] for i in range(hyperP["Theta_RSI"])],d=hyperP["Theta_RSI"])- 50) / 6
        
        #definition du croisement des courbes
        if len(indicateurs)<=5:
            indicateurs[-1]["croisement_moyennes"]=(0)
        else:
            dernier_croisement=[indicateurs[-i]["croisement_moyennes"] for i in range(2,6)]
            if (indicateurs[-1]["sign_diff_moy"]*indicateurs[-2]["sign_diff_moy"]==-1 and np.sum(np.abs(dernier_croisement))==0):
                indicateurs[-1]["croisement_moyennes"]=(10*indicateurs[-1]["sign_diff_moy"])
            else:
                indicateurs[-1]["croisement_moyennes"]=(0)
            
        
        indices=indicateurs[-1]
    indicateurs.append(indices)   
    return indicateurs,ratio  
  
    
def createIndicator(data):
    
    closeData = data.getValueStream('close')
    volumeData = data.getValueStream('volume')
    openData = data.getValueStream('open')
    highData = data.getValueStream('high')
    lowData = data.getValueStream('low')
    ratio =np.max(closeData)
    closeData /= ratio
    highData /= ratio
    openData /= ratio
    lowData /= ratio
    indices = {}
    indicateurs = []#0price regularized, 1volume, 
    #2derivé 1, 3dérivé 2, 4prix moyenné 1, 5prix moyenné 2, 6RSI, 7signe diff moy, 8dérivé diff moy
    #9dérivé 1 moy, 10dérivé 2 moy,11 signe écart
    
    
    for closeV, highV, lowV, volumeV in zip(closeData, highData, lowData, volumeData) :
        indicateurs.append({"closeV" : closeV})#0price regularized, 1volume, 
        #2derivé 1, 3dérivé 2, 4prix moyenné 1, 5prix moyenné 2, 6RSI, 7signe diff moy, 8dérivé diff moy
        #9dérivé 1 moy, 10dérivé 2 moy
        #definition du prix
        indicateurs[-1]={"closeV" : closeV}
        
        #definition du prix high
        indicateurs[-1]["highV"] = highV
        
        #definition du prix low
        indicateurs[-1]["lowV"]= lowV
     
        #definition du volume
        indicateurs[-1]["volume"]=np.sqrt(np.sqrt(np.abs(volumeV))) * np.sign(volumeV)
        

        
        indices=indicateurs[-1]
    indicateurs.append(indices)   
    return indicateurs,ratio  
  
def addIndicator(indicateurs,ratio ,hyperP : dict()):
    if 'deriv2' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):
            #definition derivé 1
            if i<=1:
                indicateurs[i]["derivé"]=0
            else:
                indicateurs[i]["derivé"]=indicateurs[i]["closeV"]-indicateurs[i-1]["closeV"]
                
    if 'dérivé2' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):            
            #definition de derive 2
            if i<2:
                indicateurs[i]["dérivé2"]=0
            else:
                indicateurs[i]["dérivé2"]=(indicateurs[i]["derivé"]-indicateurs[i-1]["derivé"])
                
    key_close_moy_A='close_moy_A_'+str(hyperP["Theta"])
    if 'close_moy_1' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):            
            #definition prix moyenné 1
            if i<=1:
                indicateurs[i][key_close_moy_A]=indicateurs[i]["closeV"]
            else:
                indicateurs[i][key_close_moy_A]=calculate_ema(indicateurs[i]["closeV"], indicateurs[i-1][key_close_moy_A], hyperP["Theta"])
    
    key_close_moy_B='close_moy_B_'+str(hyperP["Theta"])+'_'+str(hyperP["Theta_bis"])
    if key_close_moy_B not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):        
            #definition prix moyenné 2        
            if i<=1:
                indicateurs[i][key_close_moy_B]=indicateurs[i]["closeV"]
            else:
                indicateurs[i][key_close_moy_B]=calculate_ema(indicateurs[i]["closeV"], indicateurs[i-1][key_close_moy_B], hyperP["Theta_bis"]*hyperP["Theta"])
    
    key_signe_diff_moy='sign_diff_moy'+str(hyperP["Theta"])+'_'+str(hyperP["Theta_bis"])
    if key_signe_diff_moy not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):        
            #ajout de la différence de signe des moyennes
            indicateurs[i][key_signe_diff_moy]=(np.sign(indicateurs[i][key_close_moy_B]-indicateurs[i][key_close_moy_A]))

    key_derive_diff_moy='derive_diff_close'+str(hyperP["Theta"])+'_'+str(hyperP["Theta_bis"])
    if key_derive_diff_moy not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):            
            #ajout de la dérivée de diff de signe
            if i<=1:
                indicateurs[i][key_derive_diff_moy]=(0)
            else:
                indicateurs[i][key_derive_diff_moy]=(indicateurs[i][key_close_moy_A]-indicateurs[i][key_close_moy_B]-indicateurs[i-1][key_close_moy_A]+indicateurs[i-1][key_close_moy_B])

    if 'derive_moy_1' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):        
            #definition dérivé moyennée 1
            if i<=1:
                indicateurs[i]["derive_moy_1"]=(indicateurs[i]["derivé"])
            else:
                indicateurs[i]["derive_moy_1"]=(calculate_ema(indicateurs[i]["derivé"], indicateurs[i-1]["derive_moy_1"], hyperP["Theta_der"]))        

    if 'derive_moy_2' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):            
            #definition dérivé moyennée 2
            if i<=1:
                indicateurs[i]["derive_moy_2"]=(indicateurs[i]["derivé"])
            else:
                indicateurs[i]["derive_moy_2"]=(calculate_ema(indicateurs[i]["derivé"], indicateurs[i-1]["derive_moy_2"], hyperP["Theta_der2"]))        

    if 'RSI' not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):        
            #definition RSI
            if i<=hyperP["Theta_RSI"]:
                indicateurs[i]["RSI"]=50
            else:
                indicateurs[i]["RSI"]=(computeRSI([indicateurs[i-j]["closeV"] for j in range(hyperP["Theta_RSI"])],d=hyperP["Theta_RSI"])- 50) / 6
    
    key_croisement_moyennes='croisement_moyennes'+str(hyperP["Theta"])+'_'+str(hyperP["Theta_bis"])
    if key_croisement_moyennes not in indicateurs[-1].keys():
        for i in range(len(indicateurs)):
            #definition du croisement des courbes
            if i<=5:
                indicateurs[i][key_croisement_moyennes]=(0)
            else:
                dernier_croisement=[indicateurs[i-j][key_croisement_moyennes] for j in range(1,5)]
                if (indicateurs[i][key_signe_diff_moy]*indicateurs[-2][key_signe_diff_moy]==-1 and np.sum(np.abs(dernier_croisement))==0):
                    indicateurs[i][key_croisement_moyennes]=(10*indicateurs[i][key_signe_diff_moy])
                else:
                    indicateurs[i][key_croisement_moyennes]=(0)
    return indicateurs
            
if __name__ == "__main__" :
    plt.close("all")
        # Run few tests
    paire = "BTCUSDT"
    sequenceLength = 1005
    interval_value = 15
    interval_unit = "m"
    interval_str = f"{interval_value}{interval_unit}"
    data = loadData(paire=paire, sequenceLength=sequenceLength, interval_str=interval_str, numPartitions=3)
    data.plot()

    print("Train")
    for trainSequence in data.trainSequences() :
        print(len(trainSequence))

    print("\nValid")
    for validSequence in data.validSequences() :
        print(len(validSequence))

    print("\nTest")
    for testSequence in data.testSequences() :
        print(len(testSequence))
        
        
    hyperP = {
            "Theta" : 5,
            "Theta_bis" : 4,
            "Theta_der" : 3,
            "Theta_der2" : 3,
            "Theta_RSI" : 14}
    indices,ratio=createIndicatorDICO(data, hyperP)
    moy1=[]
    for i in indices:
        moy1.append(i["close_moy_1"]*ratio)
    moy2=[]
    for i in indices:
        moy2.append(i["close_moy_2"]*ratio)
# =============================================================================
#     plt.title("version entière")
#     plt.plot(moy1,c='red',label="moy1")
#     plt.plot(moy2,c='orange',label="moy2")
#     plt.plot(data.getValueStream(),c='black',label="TRUE")
#     plt.legend()
#     plt.grid()
# =============================================================================
    
    indices=indices[50:]
    data.data=data.data[50:]
    moy1=[]
    for i in indices:
        moy1.append(i["close_moy_1"]*ratio)
    moy2=[]
    for i in indices:
        moy2.append(i["close_moy_B"]*ratio)
    croisement=[]
    for i in indices:
        croisement.append(i["croisement_moyennes"]*100+47500)
    
    plt.figure()
    plt.title("version tronquée")
    plt.plot(moy1,c='red',label="moy1")
    plt.plot(moy2,c='orange',label="moy2")
    #plt.plot(data.getValueStream(),c='black',label="TRUE")
    
    plt.plot(croisement,c='black',label="croisement")
    plt.legend()
    plt.grid()
    plt.show()
    