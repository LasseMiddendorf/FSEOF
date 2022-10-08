#!/usr/bin/env python

from multiprocessing import freeze_support
from cobra.io import read_sbml_model
import cobra
import pandas as pd
import numpy as np
from cobra.flux_analysis import flux_variability_analysis
from scipy.optimize import curve_fit
import sys
import argparse
from FSEOF import FSEOF

#Parse arguments form the command line
parser = argparse.ArgumentParser(
    description="Identify gentetic targets for over-expression to increase the flux to a reaction of interest."
    )

parser.add_argument("sbmlFile", type=str, help="Path to the SBML model that should be scanned for over-expression targets. Needs to be a .xml file!")
parser.add_argument("biomassID", type=str, help="ID of the biomass reaction of the SBML file you provided")
parser.add_argument("reactionID", type=str, help="ID of the reaction that will be optimized by genetic engineering. Over-expression targets will be identified for this reaction of the SBML model")

parser.add_argument("--steps", type=int, action="store", default=30, help="Number of steps for the FSEOF algorithm. The default is 30. NOTE: This number should be decreased if flux variabillity is used.")
parser.add_argument("--useFVA", action="store_true", help="Changes the method for finding over-expression from flux balance analysis to flux variabillity analysis. This will significantly increase the runtime from a few minutes to several hours!")
parser.add_argument("--constrainBiomass", action="store_true", help="Constrains growth rate to 95%% of the theoretic maximum. This might improve the accuracy of the results, but can also lead to mathmatical infeasible solutions that will cause an error.")
parser.add_argument("--changeBiomassConstrain", type=float, action="store", default=0.95, help="If you would like to add an additional constrain to the growth rate, but not at 95%% of the theoretic maximum, use this option to specify at what percentage you want to set the constrain. NOTE: Percentages need to be passed as floats" )

args = parser.parse_args()


def main():
    
    f = FSEOF(args.sbmlFile, args.biomassID, args.reactionID)
    f.find_targets(args.steps, useFVA=args.useFVA, constrainBiomass=args.constrainBiomass, maxFluxCutoff=args.changeBiomassConstrain)
    f.sort_targets(useFVA=args.useFVA)

    #Save reuslts. Depending on which method was used for the FSEOF algorithm, different information are exported.  
    filename = args.reactionID
    
    if args.useFVA == True:
        f.targets.to_excel(
            "AmplificationTargets_{reaction}.xlsx".format(reaction=filename),
            columns=["q_slope", "l_sol", "q_slope_classifier", "l_sol_classifier", "reaction_class"]
        )
    
    else:
        f.targets.to_excel(
            "AmplificationTargets_{reaction}.xlsx".format(reaction=filename),
            columns=["q_slope"]
        )


if __name__ == "__main__":
    freeze_support() #can be neccessary for performing FVA to enable multiprocessing
    main()
