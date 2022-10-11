from cobra.io import read_sbml_model
import cobra
import pandas as pd
import numpy as np
from cobra.flux_analysis import flux_variability_analysis
from scipy.optimize import curve_fit

class FSEOF():

    def __init__(self, path, biomassID, objectiveID):
        
        #Declare class variables that require user input
        self.model = read_sbml_model(path)
        self.objectiveID = objectiveID
        self.biomassID = biomassID
        
        #Declare other class variables
        self.initial_fluxes = None
        self.maxProductFlux = None
        self.initialProductFlux = None
        self.optimalGrowth = None
        self.solution = None
        self.targets = None
        self.sorted_targets = None

        #Calculate initial fluxes and maximal product flux
        self.calculate_intitial_fluxes()
        self.calculate_maxmimal_product_flux()

    def calculate_intitial_fluxes(self):
        
        """
        This function calculates the initial fluxes of the model. It stores the optimal growth rate of the organism
        and the flux through the reaction of interest.
        """
        
        self.initial_fluxes = self.model.optimize()
        self.initialProductFlux = self.initial_fluxes.get_primal_by_id(self.objectiveID)
        self.optimalGrowth = self.initial_fluxes.objective_value
    
    def calculate_maxmimal_product_flux(self):
        
        """
        Calculate & store the theoretical maximal flux through the reaction of interest
        """
       
        self.model.objective = self.model.reactions.get_by_id(self.objectiveID)
        self.solution = self.model.optimize() 
        self.model.objective = self.model.reactions.get_by_id(self.biomassID)
        self.maxProductFlux = self.solution.objective_value
    
    def find_targets(self, steps: int, maxFluxCutoff=0.95, useFVA=True, constrainBiomass=False):
        
        """
        DESCRIPTION:
        Find over-expression targets for the reaction of interest using the flux scanning based on enforced objective flux (FSEOF) algorithm. 
        
        Either FBA or FVA can be used. FVA will significantly increase the runtime.

        PARAMETERS:
        steps: int
            Number of steps used for the FSEOF algorithm
        
        constrainBiomass: bool, default: False
            Add a constrain for the biomass reaction during the FSEOF algorithm. The constrain can further be modified with the maxFluxCutoff parameter.

        maxFluxCutoff: float, default: 0.95
            Percentage of the theoretical maximal biomass flux that should be enfored during the FSEOF algorithm, if the constrainBiomass parameter is set to True.

        RETURNS:
        None
        """

        fluxes = pd.DataFrame()
        fluxCapacity = pd.DataFrame()
        enforcedFluxes = list()

        #define helper functions for linear regression
        def f(x, m, b):
            return m*x+b
            
        def getSlopes(y):
            popt, _ = curve_fit(f, enforcedFluxes, y)
            return popt[0]

        if constrainBiomass == True:
            #constrain growth rate to defined percentage of optimal growth rate
            growthConstraint = self.model.problem.Constraint(
                self.model.reactions.get_by_id(self.biomassID).flux_expression, lb = maxFluxCutoff * self.optimalGrowth
            )
            self.model.add_cons_vars(growthConstraint)
        
        if useFVA == True:

            for i in range(steps - 1):
                print("\nPERFORMING FVA No. {}\n".format(i+1))
                #calulate current enforced flux and add it as constraint to the model    
                lb = self.initialProductFlux + (i/steps) * (self.maxProductFlux - self.initialProductFlux)
                constraint = self.model.problem.Constraint(
                    self.model.reactions.get_by_id(self.objectiveID).flux_expression, lb=lb
                )
                self.model.add_cons_vars(constraint)

                #store enforced flux in enforcedFluxes list for x-values of linear regression
                enforcedFluxes.append(lb)

                #calculate FVA, Vavg, and flux capacity for all reaction with the current enforced flux
                FVA = flux_variability_analysis(self.model)
                fluxes["Average_{}".format(i)] = (FVA["maximum"] + FVA["minimum"]) / 2
                fluxCapacity["Flux_capacity_{}".format(i)] = FVA["maximum"] - FVA["minimum"]


            
            #calculate slopes of linear regressions for fluxes and flux capactiy
            fluxes["q_slope"] = fluxes.apply(lambda y: getSlopes(y), axis=1)
            fluxCapacity["l_sol"] = fluxCapacity.apply(lambda y: getSlopes(y), axis=1)
            
            #Store list of targets
            self.targets = pd.concat([fluxes["q_slope"], fluxCapacity["l_sol"]], axis=1)
        
        else:
            #perform FSEOF algorithm with FBA
            for i in range(steps - 1):
                
                lb = self.initialProductFlux + (i/steps) * (self.maxProductFlux - self.initialProductFlux)
                constraint = self.model.problem.Constraint(
                    self.model.reactions.get_by_id(self.objectiveID).flux_expression, lb=lb
                )
                self.model.add_cons_vars(constraint)

                enforcedFluxes.append(lb)

                solution = self.model.optimize()
                fluxes["Average_{}".format(i)] = solution.fluxes
            
            fluxes["q_slope"] = fluxes.apply(lambda y: getSlopes(y), axis=1)               
            self.targets = fluxes
 
    def sort_targets(self, useFVA=False):
        
        if useFVA == True:

            #The helper function classify() is used classify the type of the correlation of q_slope and l_sol
            #A value of 1 is assigend for a pos. correlation, -1 is assigend for neg. correlations and 0 if there is
            #no clear correlation between the tested reaction and reaction of interest
        
            def classify(x):
                if x > 1:
                    return 1
                elif x < 1:
                    return -1
                else:
                    return 0

            #Classify the calculated q_slopes and l_sol
            self.targets["q_slope_classifier"] = self.targets["q_slope"].apply(classify)
            self.targets["l_sol_classifier"] = self.targets["l_sol"].apply(classify)

            #Assign class of tested reaction
            def helper(q_slope_classifier, l_sol_classifier):
                if q_slope_classifier == 1:
                    if l_sol_classifier == 1:
                        return 1
                    elif l_sol_classifier == -1:
                        return 2
                    else:
                        return 3
                elif q_slope_classifier == -1:
                    if l_sol_classifier == 1:
                        return 4
                    elif l_sol_classifier == -1:
                        return 5
                    else:
                        return 6
                else:
                    if l_sol_classifier == 1:
                        return 7
                    elif l_sol_classifier == -1:
                        return 8
                    else:
                        return 9


            self.targets["reaction_class"] = self.targets[["q_slope_classifier", "l_sol_classifier"]].apply(
                lambda x: helper(*x), axis=1
            )

            #Sort list of reations by their reaction class
            self.targets.sort_values("reaction_class", inplace=True)

        else:
            self.targets.sort_values("q_slope", ascending=False, inplace=True)
    
    
    def addReactionData(self):
        metabolites = list()
        compartments = list()

        for reactionID in list(self.targets.index):
            metabolites.append(self.model.reactions.get_by_id(reactionID).build_reaction_string(use_metabolite_names=True))
            compartments.append(self.model.reactions.get_by_id(reactionID).get_compartments())
        
        self.targets["Reaction"] = metabolites
        self.targets["Compartments"] = compartments





        
        









