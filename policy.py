
import numpy as np
import abc # Abstract Basic Class
import random
from bet import Bet # For type checking
from optuna import Trial # for type checking
from regularizer import Regularizer_EMA, Regularizer_AvgStd, Derivator
import matplotlib.pyplot as plt

class Policy() :

    """ Parametrized policies define what action should be taken """

    params = None # All parametrized policies must have parameters

    @abc.abstractmethod
    def sample(self) : # All parametrized policies must be sampleable uniformely ...
        pass


    @abc.abstractmethod
    def sample(self, trial : Trial) : # ... and by an Optuna trial
        pass


    @abc.abstractmethod
    def betToMake(self) : # All policies must predict what bet to make
        pass



class Policy_01(Policy) :

    """ First serious policy implemented """

    def __init__(self) :
        self.ratio=None
        self.val = []
        self.past = []
        self.RSI = []
        self.pastVolume = []
        self.derive1 = []
        self.derive2 = []
        self.pastMOY = []
        self.pastMOYbis = []
        self.pastMOYgap = []
        self.pastMOYgapder = []
        self.derive1MOY = []
        self.derive2MOY = []
        self.entryPrice=[]
        self.wins=[]
        self.loss=[]
        self.moneyToBet = 100
        self.params= {}
        


    def sampleFromTrial(self, trial : Trial) :
            # Sample the policy space and return the associated params
# =============================================================================
#         self.params = {
#             "Theta" : trial.suggest_float('Theta', 4, 13),
#             "TP" : 1,#trial.suggest_float('TP',0.2,5),
#             "SL" : 1,#trial.suggest_float('SL',1,8),
#             "Theta_bis" : trial.suggest_float('Theta_bis',1.5,4),
#             "Theta_der" : trial.suggest_float('Theta_der',2,10),
#             "Theta_der2" : trial.suggest_float('Theta_der2',2,10),
#             "Theta_RSI" : 14,
#             "weight_0" : trial.suggest_float('weight_0', -1, 1),
#             "weight_1" : trial.suggest_float('weight_1', -1, 1),
#             "weight_2" : trial.suggest_float('weight_2', -1, 1),
#             "weight_3" : trial.suggest_float('weight_3', -1, 1),
#             "weight_4" : trial.suggest_float('weight_4', -1, 1),
#             "weight_5" : 0,
#             "normFactor" : trial.suggest_float('normFactor', 0.001, 100),
#         }
# =============================================================================
       self.params = {
            "Theta" : trial.suggest_float('Theta', 4, 13),
            "TP" : trial.suggest_float('TP', 0.2, 5),
            "SL" : trial.suggest_float('SL', 1, 8),
            "Theta_bis" : 3,
            "Theta_der" : 5,
            "Theta_der2" : 5,
            "Theta_RSI" : 14,
            "weight_0" : trial.suggest_float('weight_0', -1, 1),
            "weight_1" : trial.suggest_float('weight_1', -1, 1),
            "weight_2" : trial.suggest_float('weight_2', -1, 1),
            "weight_3" : trial.suggest_float('weight_3', -1, 1),
            "weight_4" : trial.suggest_float('weight_4', -1, 1),
            "normFactor" : trial.suggest_float('normFactor', 0.01, 1000),
        }


    def calculate_ema(self, newPrice : float, oldPrice : float, days : int = 10, smoothing : float = 2):
        return (newPrice * (smoothing / (1 + days))) + oldPrice * (1 - (smoothing / (1 + days)))


    def computeDerivative(self, values : list) :
        return [values[valueIndex] - values[valueIndex-1] for valueIndex in range(len(values)) if valueIndex >= 1]


    def computeRSI(self, d : int = 14) :
        if len(self.derive1) < d :
            return 50
        gp = 0
        lp = 0
        for k in range(d):
            if self.derive1[-(1 + k)] > 0 :
                gp += self.derive1[-(1 + k)]
            elif self.derive1[-(1 + k)] < 0 :
                lp -= self.derive1[-(1 + k)]
        if lp <= 0 :
            return 100
        else :
            RS = gp / lp
            return 100 - 100 / (1 + RS)


    def betToMake(self, priceRegularized : float, highestRegularized : float, lowestRegularized : float, volume : float, timer : int, bet : Bet) :
        if self.ratio == None :
            self.past.append(1)
            self.ratio = priceRegularized
        else:
            self.past.append(priceRegularized / self.ratio)
        self.pastVolume.append(volume)
        if len(self.past) >= 2 :
            self.derive1.append(self.past[-1] - self.past[-2])
        if len(self.derive1) >= 2 :
            self.derive2.append(self.derive1[-1] - self.derive1[-2])

        if len(self.past) == 1 :
            self.pastMOY.append(self.past[-1])
        else:
            self.pastMOY.append(self.calculate_ema(self.past[-1], self.pastMOY[-1], days=self.params["Theta"]))
        if len(self.past) == 1 :
            self.pastMOYbis.append(self.past[-1])
        else:
            self.pastMOYbis.append(self.calculate_ema(self.past[-1], self.pastMOYbis[-1], days=self.params["Theta"] * self.params["Theta_bis"]))

        self.pastMOYgap.append(self.pastMOY[-1] - self.pastMOYbis[-1])
        if len(self.pastMOYgap) >= 2 :
            self.pastMOYgapder.append(self.pastMOYgap[-1] - self.pastMOYgap[-2])
            

        if len(self.derive1) == 1 :
            self.derive1MOY.append(self.derive1[-1])
        elif len(self.derive1) > 1 :
            self.derive1MOY.append(self.calculate_ema(self.derive1[-1], self.derive1MOY[-1], days=self.params["Theta_der"]))
        if len(self.derive2) == 1 :
            self.derive2MOY.append(self.derive2[-1])
        elif len(self.derive2) > 1 :
            self.derive2MOY.append(self.calculate_ema(self.derive2[-1], self.derive2MOY[-1], days=self.params["Theta_der2"]))
        self.RSI.append(self.computeRSI(d=self.params["Theta_RSI"]))

        if (timer != 0 or bet != None) :
            return "", None, None, None

        val = self.params["weight_0"] *  np.sqrt(np.sqrt(np.abs(self.derive1MOY[-1]))) * np.sign(self.derive1MOY[-1])
        val += self.params["weight_1"] *  np.sqrt(np.sqrt(np.abs(self.derive2MOY[-1]))) * np.sign(self.derive2MOY[-1])
        val += self.params["weight_2"] *  (self.RSI[-1] - 50) / 6
        val += self.params["weight_3"] *  np.sqrt(np.sqrt(np.abs(self.pastMOYgapder[-1]))) * np.sign(self.pastMOYgapder[-1])
        val += self.params["weight_4"] *  np.sign(self.pastMOYgap[-1])
        val += self.params["weight_5"] *  np.sqrt(np.sqrt(np.abs(volume))) * np.sign(volume)
        val /= self.params["normFactor"]
        self.val.append(val)
        if val > 1 :
            self.entryPrice = [len(self.past) - 1, priceRegularized]
            return "Long", self.moneyToBet, self.params["TP"], self.params["SL"]
        elif val < -1:
            self.entryPrice = [len(self.past) - 1, priceRegularized]
            return "Short", self.moneyToBet, self.params["TP"], self.params["SL"]
        else :
            return "", None, None, None
        print("priceRegularized, highestRegularized, lowestRegularized : ", priceRegularized, highestRegularized, lowestRegularized)


    def addTrade(self, win : bool, val : float) :
        if win == True :
            self.wins.append([self.entryPrice[0], self.entryPrice[1], len(self.past), val])
        else :
            self.loss.append([self.entryPrice[0], self.entryPrice[1], len(self.past), val])
            
    def plot(self,name:str, ignoreTimer : int = 50):
        plt.figure(figsize=(16,9))
        plt.xlabel('Minutes')
        plt.ylabel('Price')
        plt.plot(np.array(self.past[ignoreTimer:])*self.ratio, label='Closing Prices')
# =============================================================================
#         print("WINS")
#         print(self.wins)
#         print("LOSS")
#         print(self.loss)
# =============================================================================
        for a in self.wins:
            plt.scatter(a[0]-ignoreTimer,a[1],s=60,marker='x',c='g')#length_includes_head=True,head_width=5,head_length=30
            plt.arrow(a[0]-ignoreTimer,a[1],a[2]-a[0],a[3]-a[1],color='g')
        for a in self.loss:
            plt.scatter(a[0]-ignoreTimer,a[1],s=60,marker='x',c='r')
            plt.arrow(a[0]-ignoreTimer,a[1],a[2]-a[0],a[3]-a[1],color='r')
        plt.savefig("_temp/Results/"+name)
        #plt.close()



class Policy_02(Policy) :

    """ Another policy based on the tools used for Policy_01 """

    def __init__(self, derivativeNumber : int = 3, moneyToBet : float = 10) :
        # TODO : Check type and value

        # Base signal : [Price]
        # Apply regularization : [Price_reg]
        # Apply n derivations : [Price_reg, Price_reg', Price_reg'', ...]
        # Apply low-pass filters ("EMA"). "P" is price : [P_reg_lp, P_reg_lp', P_reg_lp'', ...]
        # Regularizing the n+1 values provides the full signal that is weighted summed to determine the next action

        self.derivativeNumber = derivativeNumber
        self.moneyToBet = moneyToBet

        self.price_regularizer = Regularizer_AvgStd()
        self.price_derivators = []
        for n in range(self.derivativeNumber - 1) : # Order zero mean no derivation so we only need n-1 derivators
            self.price_derivators.append(Derivator())
        self.price_lp = []
        for n in range(self.derivativeNumber) :
            self.price_lp.append(Regularizer_EMA())


    def sample(self) :
        self.params = {}
        for column in ["'" * n for n in range(self.derivativeNumber)] :
            paramName = f"P{column}"
            self.params[paramName] = -1 + 2 * random.random()
        self.params["TP"] = 0.2 + 4.8 * random.random()
        self.params["SL"] = 1 + 7 * random.random()

    def sampleFromTrial(self, trial : Trial) :
        self.params = {}
        for column in ["'" * n for n in range(self.derivativeNumber)] :
            paramName = f"P{column}"
            self.params[paramName] = trial.suggest_float(paramName, -1, 1)
        self.params["TP"] = trial.suggest_float('TP', 0.2, 5)
        self.params["SL"] = trial.suggest_float('SL', 1, 8)


    def betToMake(self, price : float, highest : float, lowest : float, timer : int, bet : Bet) :
            # Compute the signal
        price_reg = self.price_regularizer(price)
        price_derivatives = []
        for n in range(self.derivativeNumber) :
            if (n == 0) :
                price_derivatives.append(price_reg)
            else :
                price_derivatives.append(self.price_derivators[n-1](price_derivatives[n-1]))
        price_derivatives_lp = []
        for n in range(self.derivativeNumber) :
            price_derivatives_lp.append(self.price_lp[n](price_derivatives[n]))

            # No need to predict anything if we already have a bet
        if (timer != 0 or bet != None) :
            return "", None, None, None

            # Compute weighted sum
        val = 0
        for columnNumber, column in enumerate(["'" * n for n in range(self.derivativeNumber)]) :
            val += self.params[f"P{column}"] * price_derivatives_lp[columnNumber]

            # Determine next action based on weighted sum
        if val > 1 :
            return "Long", self.moneyToBet, self.params["TP"], self.params["SL"]
        elif val < -1:
            return "Short", self.moneyToBet, self.params["TP"], self.params["SL"]
        else :
            return "", None, None, None


class Policy_03(Policy) :

    """ First serious policy implemented """

    def __init__(self) :
        self.ratio=None
        self.val = []
        self.count=0
        self.entryPrice=[]
        self.wins=[]
        self.loss=[]
        self.moneyToBet = 100
        self.params= {}
        
        self.weight=[]
        


    def sampleFromTrial(self, trial : Trial) :
            # Sample the policy space and return the associated params
# =============================================================================
#         self.params = {
#             "TP" : 1,#trial.suggest_float('TP',0.2,5),
#             "SL" : 1,#trial.suggest_float('SL',1,8),
#             "weight_0" : 1,
#             "weight_1" : 1,
#             "weight_2" : 1,
#             "weight_3" : 1,
#             "weight_4" : 1,
#             "weight_5" : 1,
#             "weight_6" : 1,
#             "Theta":    7,
#             "Theta_bis":    3,
#             "normFactor" : 15,
#         }
# =============================================================================
        self.params = {
            "TP" : 0.5,#trial.suggest_float('TP',0.2,5),
            "SL" : 1.5,#trial.suggest_float('SL',1,8),
            "weight_0" : trial.suggest_float('weight_0', -1, 1),
            "weight_1" : trial.suggest_float('weight_1', -1, 1),
            "weight_2" : trial.suggest_float('weight_2', -1, 1),
            "weight_3" : trial.suggest_float('weight_3', -1, 1),
            "weight_4" : trial.suggest_float('weight_4', -1, 1),
            "weight_5" : trial.suggest_float('weight_5', -1, 1),
            "weight_6" : trial.suggest_float('weight_6', -1, 1),
            "Theta":    trial.suggest_int("Theta", 5, 9,2),
            "Theta_bis":    trial.suggest_int("Theta_bis", 2,6),
            "normFactor" : trial.suggest_float('normFactor', 0.001, 100),
        }


    def betToMake(self, priceRegularized : float,indic, highestRegularized : float, lowestRegularized : float, volume : float, bet : Bet) :
        self.count+=1
        if (bet != None) :
            return "", None, None, None
        #print(indic)
# =============================================================================
#         key_derive_diff_moy='derive_diff_close'+str(self.params["Theta"])+'_'+str(self.params["Theta_bis"])
#         key_signe_diff_moy='sign_diff_moy'+str(self.params["Theta"])+'_'+str(self.params["Theta_bis"])
#         key_croisement_moyennes='croisement_moyennes'+str(self.params["Theta"])+'_'+str(self.params["Theta_bis"])
# =============================================================================
        param = {
            "Theta" : self.params["Theta"],
            "Theta_bis" : self.params["Theta_bis"],
            "Theta_der" : 3,
            "Theta_der2" : 3,
            "Theta_RSI" : 14}
        val = self.params["weight_0"] *   indic.get_Indicator(param, "derivé")
        val += self.params["weight_1"] *  indic.get_Indicator(param, "dérivé2")
        val += self.params["weight_2"] * indic.get_Indicator(param, "RSI")
        val += self.params["weight_3"] * indic.get_Indicator(param, "derive_diff_close")
        val += self.params["weight_4"] *  indic.get_Indicator(param, "sign_diff_moy")
        val += self.params["weight_5"] *  indic.get_Indicator(param, "volume")
        val += self.params["weight_6"] *  indic.get_Indicator(param, "croisement_moyennes")
        param_pese=["derivé","dérivé2","RSI","derive_diff_close","sign_diff_moy","volume","croisement_moyennes"]
        
        poids=[100*(self.params["weight_"+str(i)] *  indic.get_Indicator(param,param_pese[i]))/val for i in range(7)]
        
        val /= self.params["normFactor"]
        self.val.append(val)
        if val > 1 :
            self.entryPrice = [self.count-1, priceRegularized]
            self.weight.append(poids)
            return "Long", self.moneyToBet, self.params["TP"], self.params["SL"]
        elif val < -1:
            self.entryPrice = [self.count-1, priceRegularized]
            self.weight.append(poids)
            return "Short", self.moneyToBet, self.params["TP"], self.params["SL"]
        else :
            return "", None, None, None
        print("priceRegularized, highestRegularized, lowestRegularized : ", priceRegularized, highestRegularized, lowestRegularized)


    def addTrade(self, win : bool, val : float) :
        if win == True :
            self.wins.append([self.entryPrice[0], self.entryPrice[1], self.count-1, val])
        else :
            self.loss.append([self.entryPrice[0], self.entryPrice[1], self.count-1, val])
            
    def plot(self, closeSequence,folder_name,ratio,name:str, ignoreTimer : int = 0):
        plt.figure(figsize=(16,9))
        plt.xlabel('Minutes')
        plt.ylabel('Price')
        plt.plot(np.array(closeSequence[ignoreTimer:]), label='Closing Prices')
# =============================================================================
#         print("WINS")
#         print(self.wins)
#         print("LOSS")
#         print(self.loss)
# =============================================================================
        for a in self.wins:
            plt.scatter(a[0]-ignoreTimer,a[1],s=60,marker='x',c='g')#length_includes_head=True,head_width=5,head_length=30
            plt.arrow(a[0]-ignoreTimer,a[1],a[2]-a[0],a[3]-a[1],color='g')
        for a in self.loss:
            plt.scatter(a[0]-ignoreTimer,a[1],s=60,marker='x',c='r')
            plt.arrow(a[0]-ignoreTimer,a[1],a[2]-a[0],a[3]-a[1],color='r')
        plt.savefig(folder_name+name)
        #plt.close()



if __name__ == "__main__" :
    policy = Policy_01()
    policy.sample()

    policy = Policy_02()
    policy.sample()
