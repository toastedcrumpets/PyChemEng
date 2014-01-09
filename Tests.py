#!/usr/bin/env python

##################################################################
# WARNING! DO NOT EDIT THIS FILE!  THIS FILE CONTAINS TEST CASES
# WORKED OUT USING OTHER SOFTWARE AND IS A STRONG TEST OF THE
# PyChemEng FRAMEWORK. THIS DATA TOOK A LOT OF TIME TO GENERATE! ONLY
# EDIT IF YOU KNOW WHAT YOU ARE DOING!
##################################################################

def relativeError(val, ref):
    import math
    return math.fabs((val - ref) / (ref + (ref==0)))

def validate(output, expected, error=0.025):
    if relativeError(output, expected) > error:
        raise Exception("Failed test with error of "+str(relativeError(output, expected)))

##################################################################
# Elements
##################################################################
#Test that elemental data can be accessed
from Elements import elements
elements[2]
elements[(1,2)]
elements["C"]
elements["e-"]
elements["n"]

##################################################################
# Antione coefficients
##################################################################
import AntoineData
from Data import speciesData
validate(speciesData['CO2'].Psat(400), 4.89027e5)

##################################################################
# Stream
##################################################################
#Test streams
from Stream import IdealGasStream

Input=IdealGasStream(300, {"C2H5OH":1}, P=1e5)
validate(len(Input.components.elementalComposition()), 3)
validate(Input.components.elementalComposition()["C"], 2)
validate(Input.components.elementalComposition()["H"], 6)
validate(Input.components.elementalComposition()["O"], 1)

#Reference test from GasEq program
#print "N2 test"
Input=IdealGasStream(300, {"N2":0.79}, P=1e5)
validate(Input.Cp() / Input.components.total(), 29.075)
validate(Input.enthalpy() / Input.components.total() / Input.components.avgMolarMass(), 1.97)
validate(Input.entropy() * 1000.0 / Input.components.total() / Input.components.avgMolarMass(), 6842.1)
validate(Input.gibbsFreeEnergy() / Input.components.total() / Input.components.avgMolarMass(), -2050.66)
#print "N2 O2 test"
Input=IdealGasStream(300, {"N2":0.79, "O2":0.21}, P=1e5)
validate(Input.Cp() / Input.components.total(), 29.129)
validate(Input.enthalpy() / Input.components.total() / Input.components.avgMolarMass(), 1.90)
validate(Input.entropy() * 1000.0 / Input.components.total() / Input.components.avgMolarMass(), 6890.37)
validate(Input.gibbsFreeEnergy() / Input.components.total() / Input.components.avgMolarMass(), -2065.21)
#print "Pre-Burn test 1: low temp"
Input=IdealGasStream(300, {"CH4":0.105, "N2":0.79, "O2":0.21}, P=1e5)
validate(Input.Cp() / Input.components.total(), 29.711)
validate(Input.enthalpy() / Input.components.total() / Input.components.avgMolarMass(), -255.50)
validate(Input.entropy() * 1000.0 / Input.components.total() / Input.components.avgMolarMass(), 7245.25)
validate(Input.gibbsFreeEnergy() / Input.components.total() / Input.components.avgMolarMass(), -2429.07)
#print "Pre-Burn test 1: high temp"
Input=IdealGasStream(1000, {"CH4":0.105, "N2":0.79, "O2":0.21}, P=1e5)
validate(Input.Cp() / Input.components.total(), 36.918)
validate(Input.enthalpy() / Input.components.total() / Input.components.avgMolarMass(), 585.60)
validate(Input.entropy() * 1000.0 / Input.components.total() / Input.components.avgMolarMass(), 8660.58)
validate(Input.gibbsFreeEnergy() / Input.components.total() / Input.components.avgMolarMass(), -8074.98)
#print "Post-Burn test:"
Input=IdealGasStream(2665.8, {"N2":0.79, "H2O":0.21, "CO2":0.0824, "O2":0.0113, "CH4":7.675e-15, "CO":0.0226}, P=8.977 * 1.01325e5)
validate(Input.Cp() / Input.components.total(), 42.018)
validate(Input.enthalpy() / Input.components.total() / Input.components.avgMolarMass(), 464.47)
validate(Input.entropy() * 1000.0 / Input.components.total() / Input.components.avgMolarMass(), 9498.39)
validate(Input.gibbsFreeEnergy() / Input.components.total() / Input.components.avgMolarMass(), -24856.19)

#Test mixing of streams
Input1 = IdealGasStream(300, {"N2":1, "O2":1}, P=1e5)
Input2 = IdealGasStream(600, {"N2":0.5, "O2":2}, P=1e5)
Output = Input1 + Input2
validate(Output.components["N2"], 1.5)
validate(Output.components["O2"], 3)
validate(Output.enthalpy(), Input1.enthalpy() + Input2.enthalpy())

##################################################################
# Reaction
##################################################################
#When checking the calculations below in GasEq, ensure that the
#reactants are present in the products, otherwise GasEq does not
#converge!
import Reaction

#Equilibrium at defined T and P
InGas = IdealGasStream(2600, {"N2":0.79, "O2":0.21, "CH4":0.105}, P=1.01325e5)
OutGas = Reaction.react(InGas, {"N2", "H2O", "CO2", "CO", "O2"}, constP=True, constT=True)
validate(OutGas.T, 2600)
validate(OutGas.P, 1.01325e5)
validate(InGas.components.totalMass(), OutGas.components.totalMass())
validate(OutGas.components["N2"], 0.79)
validate(OutGas.components["H2O"], 0.21)
validate(OutGas.components["CO2"], 0.07057)
validate(OutGas.components["O2"], 0.01722)
validate(OutGas.components["CH4"], 0.0)
validate(OutGas.components["CO"], 0.03443)

#Adiabatic T at constant P
InGas = IdealGasStream(300, {"N2":0.79, "O2":0.21, "CH4":0.105}, P=1.01325e5)
OutGas = Reaction.react(InGas, {"N2", "H2O", "CO2", "CO", "O2"}, constP=True, constT=False)
validate(InGas.enthalpy(), OutGas.enthalpy())
validate(InGas.components.totalMass(), OutGas.components.totalMass())
validate(OutGas.P, 1.01325e5)
validate(OutGas.T, 2259.3)
validate(OutGas.components["N2"], 0.79)
validate(OutGas.components["H2O"], 0.21)
validate(OutGas.components["CO2"], 0.09351)
validate(OutGas.components["O2"], 0.00574)
validate(OutGas.components["CH4"], 0)
validate(OutGas.components["CO"], 0.01149)

#Adiabatic T at constant V
InGas = IdealGasStream(300, {"N2":0.79, "O2":0.21, "CH4":0.105}, P=1.01325e5)
OutGas = Reaction.react(InGas, {"N2", "H2O", "CO2", "CO", "O2"}, constP=False, constT=False)
validate(InGas.internalEnergy(), OutGas.internalEnergy())
validate(InGas.components.totalMass(), OutGas.components.totalMass())
validate(OutGas.T, 2665.8)
validate(OutGas.components["N2"], 0.79)
validate(OutGas.components["H2O"], 0.21)
validate(OutGas.components["CO2"], 0.08240)
validate(OutGas.components["O2"], 0.01130)
validate(OutGas.components["CH4"], 0)
validate(OutGas.components["CO"], 0.02260)

#Harder test
InputS = IdealGasStream(700, {"CH4":0.105, "O2":0.21, "N2":0.79}, P = 8 * 1.01325e5)
OutGas = Reaction.react(InputS, {"H2O", "CO2", "CO", "OH", "H", "O", "H2", "NO"}, outputlevel=0, constP=True, constT=False)
validate(InGas.components.totalMass(), OutGas.components.totalMass())
validate(OutGas.T, 2483.4)
validate(OutGas.components["N2"], 0.78796)
validate(OutGas.components["H2O"], 0.20197)
validate(OutGas.components["CO2"], 0.09083)
validate(OutGas.components["CO"], 0.01417)
validate(OutGas.components["O2"], 0.00634)
#validate(OutGas.components["OH"], 0.00505)
#validate(OutGas.components["H2"], 0.00519)
#validate(OutGas.components["NO"], 0.00407)
#validate(OutGas.components["H"], 6.254e-4)
#validate(OutGas.components["O"], 3.934e-4)

#Adiabatic flame test, calculated values from http://direns.mines-paristech.fr/Sites/Thopt/en/co/applet-calc-comb.html
InputS = IdealGasStream(300, {"CH4":1, "H2O":0, "O2":2.0, "N2":2.0 / 0.21 * 0.781, "Ar":2.0 / 0.21 * 0.009, "CO2":0}, P=1e5)
OutGas = Reaction.react(InputS, {}, outputlevel=0, constP=True, constT=False)
validate(OutGas.T, 2332.8)
normComp = OutGas.components.normalised()
validate(normComp["CO2"], 0.0950226)
validate(normComp["H2O"], 0.190045)
validate(normComp["N2"], 0.706787)
validate(normComp["Ar"], 0.0081448)
