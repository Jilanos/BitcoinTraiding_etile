
import numpy as np
import matplotlib.pyplot as plt




def key_hyper_param_influents(hyper_params : dict):
    key="key_"
    for cle,value in hyper_params.items():
        key = key + cle + '_' + str(value) + '_'
    return key
        

def calculate_ema(newPrice : float, oldPrice : float, days : int = 10, smoothing : float = 2):
    return (newPrice * (smoothing / (1 + days))) + oldPrice * (1 - (smoothing / (1 + days)))

class indicator():
    
    def __init__(self):#,param : dict,tabKeys : list,tabValues : list):
        #parametres influant le calcul des indicateurs
        self.param_dict={}
        
# =============================================================================
#         key_param=key_hyper_param_influents(param)
#         self.param_dict[key_param]={}
#         for key,value in zip(tabKeys,tabValues):
#             self.param_dict[key_param][key]=value
# =============================================================================
        
    def addIndicator(self,param : dict, value ,key : str):
        key_param=key_hyper_param_influents(param)
        if (key_param not in self.param_dict):
            self.param_dict[key_param]={}
        self.param_dict[key_param][key]=value
        
    def get_Indicator(self,param : dict ,key : str):
        key_param=key_hyper_param_influents(param)
        return self.param_dict[key_param][key]
    
    def calculated(self, param : dict, key : str):
        key_param=key_hyper_param_influents(param)
        return key in self.param_dict[key_param]
    
    def getParamsKeys(self):
        keys=[]
        for key in self.param_dict:
            keys.append(key)
        return keys
    
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
    
def createIndicator(data,params):
    
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
        indicateurs.append(indicator(params,["closeV","highV","lowV","volume"],[closeV,highV,lowV,np.sqrt(np.sqrt(np.abs(volumeV))) * np.sign(volumeV)]))        
        indices=indicateurs[-1]
    indicateurs.append(indices)   
    return indicateurs,ratio  
   
def Init_indicator(indicateur,data,params):
    
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
    
    for i in range(len(closeData)) :
        volumeV=volumeData[i]
        indicateur[i].addIndicator(params,closeData[i] ,"closeV")
        indicateur[i].addIndicator(params,highData[i] ,"highV")
        indicateur[i].addIndicator(params,lowData[i] ,"lowV")
        indicateur[i].addIndicator(params,np.sqrt(np.sqrt(np.abs(volumeV))) * np.sign(volumeV) ,"volume")    
    return indicateur,ratio 

def createIndicator_bis(data):
    
    closeData = data.getValueStream('close')
    indices = {}
    indicateurs = []
    
    
    for closeV in closeData :
        indicateurs.append(indicator())        
        indices=indicateurs[-1]
    indicateurs.append(indices)   
    return indicateurs,np.max(closeData) 
  
def addIndicator(indicateurs,ratio ,hyperP : dict()):
    if not(indicateurs[-1].calculated(hyperP,'derivé')):
        for i in range(len(indicateurs)):
            #definition derivé 1
            if i<=1:
                indicateurs[i].addIndicator(hyperP,0,"derivé")
            else:
                value=indicateurs[i].get_Indicator(hyperP,"closeV")-indicateurs[i-1].get_Indicator(hyperP,"closeV")
                indicateurs[i].addIndicator(hyperP,value,"derivé")
    
    if not(indicateurs[-1].calculated(hyperP,'dérivé2')):
        for i in range(len(indicateurs)):
            #definition derivé 1
            if i<=1:
                indicateurs[i].addIndicator(hyperP,0,"dérivé2")
            else:
                value=indicateurs[i].get_Indicator(hyperP,"derivé")-indicateurs[i-1].get_Indicator(hyperP,"derivé")
                indicateurs[i].addIndicator(hyperP,value,"dérivé2")    
                
    if not(indicateurs[-1].calculated(hyperP,'close_moy_A')):
        for i in range(len(indicateurs)):
            #definition derivé 1
            if i<=1:
                value=indicateurs[i].get_Indicator(hyperP,"closeV")
                indicateurs[i].addIndicator(hyperP,value,"close_moy_A")
            else:
                value=calculate_ema(indicateurs[i].get_Indicator(hyperP,"closeV"), indicateurs[i-1].get_Indicator(hyperP,"close_moy_A"), hyperP["Theta"])
                indicateurs[i].addIndicator(hyperP,value,"close_moy_A")

    if not(indicateurs[-1].calculated(hyperP,'close_moy_B')):
        for i in range(len(indicateurs)):
            #definition derivé 1
            if i<=1:
                value=indicateurs[i].get_Indicator(hyperP,"closeV")
                indicateurs[i].addIndicator(hyperP,value,"close_moy_B")
            else:
                value=calculate_ema(indicateurs[i].get_Indicator(hyperP,"closeV"), indicateurs[i-1].get_Indicator(hyperP,"close_moy_B"), hyperP["Theta"]*hyperP["Theta_bis"])
                indicateurs[i].addIndicator(hyperP,value,"close_moy_B")

    if not(indicateurs[-1].calculated(hyperP,'sign_diff_moy')):
        for i in range(len(indicateurs)):
            value=(np.sign(indicateurs[i].get_Indicator(hyperP,"close_moy_B")-indicateurs[i].get_Indicator(hyperP,"close_moy_A")))
            indicateurs[i].addIndicator(hyperP,value,"sign_diff_moy")
            
    if not(indicateurs[-1].calculated(hyperP,'derive_diff_close')):
        for i in range(len(indicateurs)):
            if i<=0:
                value=0
            else:
                value=(indicateurs[i-1].get_Indicator(hyperP,"close_moy_B")+indicateurs[i].get_Indicator(hyperP,"close_moy_A")-indicateurs[i].get_Indicator(hyperP,"close_moy_B")-indicateurs[i-1].get_Indicator(hyperP,"close_moy_A"))
            indicateurs[i].addIndicator(hyperP,value,"derive_diff_close")  
            
    if not(indicateurs[-1].calculated(hyperP,'derive_moy_1')):
        for i in range(len(indicateurs)):
            if i<=0:
                value=indicateurs[i].get_Indicator(hyperP,"derivé")
            else:
                value=calculate_ema(indicateurs[i].get_Indicator(hyperP,"derivé"), indicateurs[i-1].get_Indicator(hyperP,"derive_moy_1"), hyperP["Theta_der"])
            indicateurs[i].addIndicator(hyperP,value,"derive_moy_1")
            
    if not(indicateurs[-1].calculated(hyperP,'derive_moy_2')):
        for i in range(len(indicateurs)):
            if i<=0:
                value=indicateurs[i].get_Indicator(hyperP,"derivé")
            else:
                value=calculate_ema(indicateurs[i].get_Indicator(hyperP,"derivé"), indicateurs[i-1].get_Indicator(hyperP,"derive_moy_2"), hyperP["Theta_der2"])
            indicateurs[i].addIndicator(hyperP,value,"derive_moy_2")

    if not(indicateurs[-1].calculated(hyperP,'RSI')):
        for i in range(len(indicateurs)):
            if i<=0:
                value=50
            else:
                value=(computeRSI([indicateurs[i-j].get_Indicator(hyperP,"closeV") for j in range(hyperP["Theta_RSI"])],d=hyperP["Theta_RSI"])- 50) / 6
            indicateurs[i].addIndicator(hyperP,value,"RSI")
            
    if not(indicateurs[-1].calculated(hyperP,'croisement_moyennes')):
        for i in range(len(indicateurs)):
            if i<=5:
                value=0
            else:
                dernier_croisement=[indicateurs[i-j].get_Indicator(hyperP,"croisement_moyennes") for j in range(1,5)]
                if (indicateurs[i].get_Indicator(hyperP,"sign_diff_moy")*indicateurs[i-2].get_Indicator(hyperP,"sign_diff_moy")==-1 and np.sum(np.abs(dernier_croisement))==0):
                    value=(10*indicateurs[i].get_Indicator(hyperP,"sign_diff_moy"))
                else:
                    value=(0)
            indicateurs[i].addIndicator(hyperP,value,"croisement_moyennes")
  
    return indicateurs



class indices():
    
    def __init__(self):
        #parametres influant le calcul des indicateurs
        
        self.list=[]
        
    def add_hyper_param(self,param : dict,data):
        idd,ratio=createIndicator(data)

        
params_1 = {
            "Theta" : 4,
            "Theta_bis" : 5,
            "Theta_der" : 3,
        }

params_2 = {
            "Theta" : 2,
            "Theta_bis" : 5,
            "Theta_der" : 3,
        }

params_3 = {
            "Theta" : 5,
            "Theta_bis" : 5,
            "Theta_der" : 6,
        }
params_4 = {
            "Theta" : 1,
            "Theta_bis" : 1,
            "Theta_der" : 3,
        }


# =============================================================================
# idd = ['RSI','moy1','moy2','derive']
# val = [1,2,3,4]
# indicateur=indicator(params_1,idd,val)
# for i in range(4):
#     indicateur.addIndicator(params_2, idd[i], val[i]+1)
#     indicateur.addIndicator(params_3, idd[i], val[i]/23)
#     indicateur.addIndicator(params_4, idd[i], val[i]*10)
# 
# keys=indicateur.getParamsKeys()
# print(len(keys))
# print(keys)
# 
# 
# =============================================================================
