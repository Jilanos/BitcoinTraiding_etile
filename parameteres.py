


class parameters():
    
    def __init__(self):
        
        self.parameters={}
        self.parametersInfluence={} #same key as self.parameters but the value 
                                    #is True if the param is influent
        
    def paramInfluents(self):
        paramInfluents = {}
        for key,value in self.parametersInfluence.items():
            if value:
                paramInfluents[key]=self.parameters[key]
        return paramInfluents
    
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
            "TP" : 1,#trial.suggest_float('TP',0.2,5),
            "SL" : 1,#trial.suggest_float('SL',1,8),
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