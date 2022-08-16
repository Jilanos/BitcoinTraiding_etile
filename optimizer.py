

from wallet import Wallet
from policy import Policy, Policy_01, Policy_02, Policy_03
from agent import Agent
from data import Data, loadData#, calculate_ema, computeRSI, createIndicatorDICO,createIndicator, addIndicator
from indicator import calculate_ema, computeRSI,createIndicator_bis, addIndicator, Init_indicator
from Results import Results
import matplotlib.pyplot as plt
import optuna
from optuna import Trial
import pickle # Save and load data to and from storage
import random
import numpy as np 
from termcolor import colored
import datetime
import os
import time
import sys



class Optimizer() :

    """ Optimizes the input parameter space and output the best set found as well as intermediary visualization asset of the training """

    def __init__(self, data : Data, policy : type,ignoreTimer : int = 50,data_name : str="Results") :
        # Todo : Ensure variable types and values
        self._data = data # The data to be used
        self._policyClass = policy # The policy class to optimize
        self._results = Results()
        # optuna.logging.set_verbosity(optuna.logging.WARNING)
        self._study = optuna.create_study(direction="maximize") # The Optuna data structure to be used for the hyper-parameters tuning
        self.trainPerformances = [] # Save training performances over time. This is useful to know how much the model fits the training data.
        self.validPerformances = [] # Save validation performances over time. This is useful to know how much the model generalizes.
        self.testPerformances = [] # Save test performances over time. This is usefull to know how well the model would perform on new data.
        self.params = [] #Save params performances over time
        self.bestTrainedModel = -199999
        self.bestValidedModel = -199999
        self.bestTestedModel = -199999
        self.bestTrainParams= None
        self.bestValidParams= None
        self.bestTestParams= None
        self.ignoreTimer=ignoreTimer
        self.PRINTED = False
        self.countSincePrinted=0
        self.paramTemp=[[] for i in range(7)]
        self.paramImpact=[[] for i in range(7)]
        self.time=0
        path=os.getcwd()
        self.folder_name=path+"/Results/"+data_name+"/"
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
        
        
    def runExperiment(self, params : dict, dataset : str = "train", sequenceLength : int = 1000, sav : bool = False):
            # Get the proper data
        if (dataset == "train") : closeSequences, highSequences, lowSequences, volumeSequences, indics= self._data.trainSequences("close"), self._data.trainSequences("high"), self._data.trainSequences("low"),self._data.trainSequences("volume"),self._data.trainSequences("indic")
        if (dataset == "valid") : closeSequences, highSequences, lowSequences, volumeSequences, indics = self._data.validSequences("close"), self._data.validSequences("high"), self._data.validSequences("low"), self._data.validSequences("volume"),self._data.validSequences("indic")
        if (dataset == "test") : closeSequences, highSequences, lowSequences, volumeSequences, indics = self._data.testSequences("close"), self._data.testSequences("high"), self._data.testSequences("low"), self._data.testSequences("volume"),self._data.testSequences("indic")
            # Compute the performance of the policy on all the sequences
        totalPerformance = 0 # Sum of the performances over all the sequences
        UnitCount=0
        if sav:
            count,wins,loss=0,0,0
        for closeSequence, highSequence, lowSequence, volumeSequence, indic in zip(closeSequences, highSequences, lowSequences, volumeSequences,indics) :
               # Instanciate an agent to run the policy of our data
            wallet = Wallet(fees=0.0)
            policy = self._policyClass()
            policy.params = params # Always use the same params provided as arguments (instead of sampling again)
            agent = Agent(wallet, policy,ignoreTimer=self.ignoreTimer)
                # Run the agent on the data
            
            for closeValue, highValue, lowValue, volumValue, indicator in zip(closeSequence, highSequence, lowSequence, volumeSequence,indic) :
                UnitCount+=1
                agent.act(indicator, closeValue, highValue, lowValue, volumValue)
                # TODO : What is sequenceLength for ? Max length of a single sequence or all the sequences ?
            #datas=np.array(agent.policy.val)
            #print(agent.policy.val)
            #print([np.mean(datas),np.max(datas),np.min(datas)])
            for elt in policy.weight:
                for i in range(7):
                    self.paramTemp[i].append(elt[i])
            if sav:
                wins += len(policy.wins)
                loss += len(policy.loss)
                count+=1
                name = "best_test_"+str(count)+".png"
                closeSeq=[]
                
                
                
                        
                for elt in closeSequence:
                    closeSeq.append(elt)
                
                policy.plot(closeSeq,self.folder_name,self._data.ratio,name=name,ignoreTimer = 0)
                #print("plot  +  "+ name)
            totalPerformance += agent.wallet.profit(closeValue)
        if sav:
            #print(wins+loss)
            
            if wins+loss>0:
                wr=np.round(wins/(wins+loss)*100,decimals=1)
                
            else:
                wr=-1
            gain=np.round(totalPerformance/(UnitCount-self._data.numPartitions*self.ignoreTimer)*self._data.perday,decimals=3)
            tradeRate=np.round((wins+loss)/(UnitCount-self._data.numPartitions*self.ignoreTimer)*self._data.perday,decimals=2)
            print(colored("Résultat dans le test final : WR : {}%, gain quotidien {}%, nbr de trades quotidiens : {}".format(wr,gain, tradeRate),"green"))
        #print("totalunit : {}, total value : {}, resultat {}, perday {}".format(UnitCount,totalPerformance,totalPerformance/UnitCount*self._data.perday,self._data.perday))
        return totalPerformance/(UnitCount-self._data.numPartitions*self.ignoreTimer)*self._data.perday 

    def optiPrint(self,study, trial):
        global train_number
        train_number+=1
        
        if not(self._results.PRINTED) :
            self._results.PRINTED=True
            self._results.countSincePrinted=0
            print(colored("Trial: {} ==>  ".format(train_number),"cyan"),colored("Best Train: {}%".format(np.round(self._results.bestTrainedModel, decimals=3)),self._results.PRINTED_Train),colored(" ; Best Valid: {}%".format(np.round(self._results.bestValidedModel, decimals=4)),self._results.PRINTED_Valid),colored(" => Test: {}%".format(np.round(self._results.bestTestedModel, decimals=4)), 'cyan'))
        elif self._results.countSincePrinted>100:
            self._results.countSincePrinted=0
            dt=time.time()-self.time
            self.time=time.time()
            print("ecouled time : {}".format(dt))
            print(colored("Trial: {} ==>  Best Train: {}% ; Best Valid: {}% => Test: {}%".format(train_number,np.round(self._results.bestTrainedModel, decimals=3),np.round(self._results.bestValidedModel, decimals=4),np.round(self._results.bestTestedModel, decimals=4)), 'white'))
    
    def objective(self, trial : Trial) :
             # Sample a set of params to be tested
        policy = self._policyClass()
        policy.sampleFromTrial(trial) # TODO :: Make class method and remove policy instanciation
        params = policy.params
        self.params.append(params)
            # Compute performances
        self.paramTemp=[[] for i in range(7)] 
        
        trainPerformance = self.runExperiment(params, "train",False)
        validPerformance = self.runExperiment(params, "valid",False)
        testPerformance = self.runExperiment(params, "test",False)
        if(len(self.paramTemp[0])>0):
            for ind in range(7):
                self.paramImpact[ind].append(np.mean(self.paramTemp[ind]))
        
        self._results.saveExperiment(trainPerformance, validPerformance, testPerformance, params)

#             self.bestTestParams=params

            # Return training signal to Optuna
        return trainPerformance

    def fit(self, temps : float) :
        
        hyperP = {
            "Theta" : 5,
            "Theta_bis" : 3,
            "Theta_der" : 3,
            "Theta_der2" : 3,
            "Theta_RSI" : 14}
        
        #création des indicateurs pertinents pour la policy
        #indices,self._data.ratio=createIndicatorDICO(self._data, hyperP)
        
        
        indices,self._data.ratio=createIndicator_bis(self._data)#self._data
        
        for z in [5,7,9]:
            for e in [2,3,4,5,6]:
                hyperP = {
                    "Theta" : z,
                    "Theta_bis" : e,
                    "Theta_der" : 3,
                    "Theta_der2" : 3,
                    "Theta_RSI" : 14}
                indices,self._data.ratio = Init_indicator(indices, data, hyperP)
                indices=addIndicator(indices,self._data.ratio, hyperP)
        #suppression des self.ignoreTimer valeurs des data et de l'indicateur permettant d'avoir des moyennes stables
        indices=indices[self.ignoreTimer:]
        self._data.data=self._data.data[self.ignoreTimer:]
        
        
        
        #print(len(indices))
        #print(len(self._data.data))
        
        for j in range(len(self._data.data)):
            self._data.data[j].indic=indices[j]
        
        print(colored("Study launch for {} minutes, with {} partitions ".format(np.round(temps/60,decimals=2),self._data.numPartitions),"green"))
        
        debut=datetime.datetime.now()
        sf=int((debut.second+temps)%60)
        mf=(int((debut.second+temps)/60)+debut.minute)%60
        hf=int((int((debut.second+temps)/60)+debut.minute)/60+debut.hour)%24
        D=int(int((int((debut.second+temps)/60)+debut.minute)/60+debut.hour)/24)
        if D==0:
            print('Fin à {}h {}m {}s'.format(hf,mf,sf))
        elif D==1:
            print('Fin demain à {}h {}m {}s'.format(hf,mf,sf))
        # <budget> : Time allocated to the fit of the models in s # TODO : Handle budget
            # Optimize the objective
        optuna.logging.disable_default_handler()
        self._study.optimize(self.objective, timeout=temps,callbacks=[self.optiPrint])
            # After fitting, plot the data to visualize the training
        #self.plotPerformances()
        self._results.plotPerformances(self.folder_name)
        self._results.plotParams(self.folder_name)
        compt=0
        for tab in self.paramImpact:
            plt.figure()
            plt.title("indicateur nr° "+str(compt)+" moy="+str(np.mean(np.abs(tab))))
            plt.grid()
            plt.plot(tab)
            compt+=1
            
        self.runExperiment(self._results.bestValidParams,"test",sav=True)


    def getBestTrainModel(self) :
        return [self.bestTrainedModel,self.bestTrainParams] # TODO : Retrieve best model on train from study


    def getBestValidModel(self) :
        return [self.bestValidedModel,self.bestValidParams] # TODO : Retrieve best model on valid from study


    def saveState(self, folderPath : str = "./_data/optimizerStates/") :
        with open(f"{folderPath}opt_{random.random()}", "wb") as saveFile:
            pickle.dump(self, saveFile, protocol=pickle.HIGHEST_PROTOCOL)


    def loadState(self, savePath : str) :
        with open(savePath, "rb") as readFile:
            return pickle.load(readFile)


if __name__ == "__main__" :
        # Get data to feed to optimizer
    plt.close("all")
    ignoreTimer=50
    data_name="test_0fees_RR3"
    data = loadData(paire="BTCBUSD", sequenceLength=4*24*30*4, interval_str="3m", numPartitions=6, reload=True,ignoreTimer=ignoreTimer)
    data.plot() # and plot it
    train_number=0
    optimizer = Optimizer(data, Policy_03, ignoreTimer=ignoreTimer,data_name=data_name)
    optimizer.fit(60*5)
    #print("Fin algo")
    #optimizer.runExperiment(optimizer.bestTestParams,"test",sav=True)

