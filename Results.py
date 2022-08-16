

from wallet import Wallet
from policy import Policy, Policy_01, Policy_02
from agent import Agent
from data import loadData, Data
import matplotlib.pyplot as plt
import optuna
from optuna import Trial
import pickle # Save and load data to and from storage
import random
import numpy as np 
from termcolor import colored


class Results():
    
    def __init__(self) :
        # Todo : Ensure variable types and values
        
        #sauvegardes de l'ensembles des jeux de paramètres des meilleurs réusltats et les performances associées
        self.trainPerformances = [] # Save training performances over time. This is useful to know how much the model fits the training data.
        self.trainParams = []
        self.validPerformances = [] # Save validation performances over time. This is useful to know how much the model generalizes.
        self.validParams = []
        self.testPerformances = [] # Save test performances over time. This is usefull to know how well the model would perform on new data.
        self.params = [] #Save params performances over time
        
        #Sauvegarde des meilleurs perfs (%de gain quotidien) aisin que les paramètres associés
        self.bestTrainedModel = -199999
        self.bestValidedModel = -199999
        self.bestTestedModel = -199999
        self.bestTrainParams= None
        self.bestValidParams= None
    
        #liste des key des params
        self.keyParams= []
        self.trainBestParams =[]#création des liste contenant les liste de param au cours des trials
        self.validBestParams =[]
        
        #Paramètres divers
        self.PRINTED = False
        self.PRINTED_Valid = "cyan"
        self.PRINTED_Train = "cyan"
        self.countSincePrinted=0
    
    def  saveExperiment(self, trainPerformance : float,validPerformance : float,testPerformance : float, params) :
        self.params.append(params)
        if trainPerformance==0:
            trainPerformance=-99999
        if validPerformance==0:
            validPerformance=-99999
        if testPerformance==0:
            testPerformance=-99999
            # Save the results for later access
            
        self.PRINTED_Train = "cyan"
        self.PRINTED_Valid = "cyan"
        if trainPerformance>self.bestTrainedModel:
            self.PRINTED=False
            self.PRINTED_Train = "green"
            self.bestTrainedModel=trainPerformance
            self.bestTrainParams=params
        
        if validPerformance>self.bestValidedModel:
            self.PRINTED=False
            self.PRINTED_Valid = "green"
            self.bestValidedModel=validPerformance
            self.bestValidParams=params
            self.bestTestedModel=testPerformance
            self.bestTestParams=params
        self.countSincePrinted +=1
            # Save the results for later access
        self.trainPerformances.append(self.bestTrainedModel)
        self.trainParams.append(self.bestTrainParams)        
        self.validPerformances.append(self.bestValidedModel)
        self.validParams.append(self.bestValidParams)   
        self.testPerformances.append(self.bestTestedModel)
        
    def plotParams(self,savePath : str = "_temp/Results/"):
        for key in self.params[0]:
            self.keyParams.append(key)
            self.trainBestParams.append([])#complétion d'autant de liste de param qu'il y a de params
            self.validBestParams.append([])
            
        for i in range(len(self.trainParams)):#remplissages des listes
            for j,key in enumerate(self.trainParams[i]):
                self.trainBestParams[j].append(self.trainParams[i][key])
                self.validBestParams[j].append(self.validParams[i][key])
        
        plt.figure(figsize=(17,10))
        for i,key in enumerate(self.keyParams):
            plt.title("Evolution de "+key+" au cours des trials")
            plt.ylabel("Valeurs du paramètres")
            plt.xlabel("steps d'optimisation")
            plt.plot(self.trainBestParams[i],label="Train param")
            plt.plot(self.validBestParams[i],label="Valid param")
            plt.legend()
            plt.grid()
            plt.savefig(savePath+key+"_evolution.png")
            plt.clf()
        plt.close()
    
    def plotPerformances(self, savePath : str = "_temp/Results/") :
        plt.figure(figsize=(16,9))
        plt.plot(self.trainPerformances,label='Train')
        plt.title("Performance en Train, valid et test")
        plt.xlabel("Step")
        plt.ylabel("Score")
        plt.plot(self.validPerformances,label='Valid')
        #plt.title("Validation")
        plt.plot(self.testPerformances,label='Test')
        plt.legend()
        #plt.title("Test")
        debut=round(len(self.trainPerformances)/10)
        plt.ylim(-0.1+np.min([np.min(self.trainPerformances[debut:]),np.min(self.validPerformances[debut:])]),0.2+np.max([np.max(self.trainPerformances),np.max(self.validPerformances),np.max(self.testPerformances)]))
        plt.grid()
        plt.savefig(savePath+"Performances.png")
        plt.close()
                
                
                    
        
        
        