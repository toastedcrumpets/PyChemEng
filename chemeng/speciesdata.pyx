#!/usr/bin/env python
#distutils: language = c++

####################################################################
# Physical constants
####################################################################
#Constant used in the NASA data set! (If changed, will need to rescale the data)
R = 8.31451 

#STP is 25 celcius at 1 bar
T0 = 273.15 + 25
P0 = 1.0e5

from chemeng.elementdata import elements
from chemeng.components cimport Components

####################################################################
# Fit functions
####################################################################
#fitFunctions is a dictionary of functions used for data fitting. Each
#function must take two arguments, T and Coeffs.
fitFunctions={}

def registerFitFunction(name, function):
    if name in fitFunctions:
        raise Exception("This function name is already in use!")
    fitFunctions[name] = function

def registerCpFitFunction(name, function, integratedfunction, integratedfunctionOverT):
    if name in fitFunctions:
        raise Exception("This function name is already in use!")
    fitFunctions[name] = function
    fitFunctions[name+"Integrated"] = integratedfunction
    fitFunctions[name+"IntegratedOverT"] = integratedfunctionOverT

####################################################################
# Helper functions
####################################################################
#Functions used throughout the code
def relativeError(val, ref):
    import math
    return math.fabs((val - ref) / (ref + (ref==0)))

####################################################################
# Species data
####################################################################
#Species data is a dictionary of thermodynamic data on different
#species/components and their phases. This is addressed using the
#chemical formula of the species to be studied.  
speciesData={}

from collections import namedtuple
ThermoConstantsType = namedtuple('ThermoConstantsType', ['Tmin', 'Tmax', 'fitFunction', 'constants', 'HConst', 'SConst'])
AntoineConstantsType = namedtuple('AntoineConstantsType', ['Tmin', 'Tmax', 'fitFunction', 'constants'])

cdef class PhaseData:
    cdef public str name
    cdef public str comments
    cdef public list constants
    def __init__(self, name, comments):
        self.name = name
        self.comments = comments
        self.constants = []
        
    def __str__(self):
        output = "Phase{"+self.name+", \""+str(self.comments)+"\", "+str(len(self.constants))+" constants, "
        for data in self.constants:
            output += "["+str(data.Tmin)+", "+str(data.Tmax)+"] "
        return output + "}"
    
    def __repr__(self):
        return self.__str__()

cdef class SpeciesDataType:
    """
    This class represents the isobaric (P=P0) data for a species, and may include multiple phases
    """

    cdef public str name
    cdef public double mass
    cdef public Components elementalComposition
    cdef public dict phases
    cdef public list antoineData

    def __init__(self, name, mass, elementalComposition):
        self.name = name
        self.mass = mass
        self.elementalComposition = Components(elementalComposition)
        self.phases = {}
        self.antoineData = []

    def __str__(self):
        output = "Species{"+self.name+", ["
        for num, phase in self.phases.iteritems():
            output += str(num)+":"+phase.name+", "
        return output[:-2] +"]}"

    def __repr__(self):
        return self.__str__()

    def inDataRange(self, T, phase):
        for Tmin, Tmax, func, C, Hconst, Sconst in self.phases[phase].constants:
            if T >= Tmin and T <= Tmax:
                return True
        return False
        
    def registerPhase(self, phasenumber, phasename, comments):
        #Check if this phase has been registered before, if not,
        #create it
        if phasenumber not in self.phases:
            self.phases[phasenumber] = PhaseData(phasename, comments)

        #Check that the data is consistent (tests for consistency if
        #the phase existed before)
        if phasename != self.phases[phasenumber].name:
            raise Exception("Trying to register phase "+phasename+":"+str(phasenumber)+" but we have "+str(self.phaseNames))

    def registerAntoineData(self, Tmin, Tmax, fitFunction, constants):
        self.antoineData.append(AntoineConstantsType(Tmin, Tmax, fitFunction, constants))
        
    def registerPhaseCoeffs(self, Coeffs, phase):
        self.phases[phase].constants.append(ThermoConstantsType(*Coeffs))
        #Ensure that the data is sorted from lowest to highest temperature range
        self.phases[phase].constants.sort(key = lambda x : (x.Tmin, x.Tmax))
        
    def Cp0(self, T, phase):
        for Tmin, Tmax, func, C, Hconst, Sconst in self.phases[phase].constants:
            if T >= Tmin and T <= Tmax:
                return R * fitFunctions[func](T, C)
        raise Exception("Cannot find valid Cp0 expression for "+self.name+" at "+str(T)+"K")

    def Hf0(self, T, phase):
        for Tmin, Tmax, func, C, Hconst, Sconst in self.phases[phase].constants:
            if T >= Tmin and T <= Tmax:
                return R * (fitFunctions[func+"Integrated"](T, C) + Hconst)
        raise Exception("Cannot find valid Hf0 expression for "+self.name+" at "+str(T)+"K")

    def S0(self, T, phase):
        for Tmin, Tmax, func, C, Hconst, Sconst in self.phases[phase].constants:
            if T >= Tmin and T <= Tmax:
                return R * (fitFunctions[func+"IntegratedOverT"](T, C) + Sconst)
        raise Exception("Cannot find valid S0 expression for "+self.name+" at "+str(T)+"K")

    def Psat(self, T):
        for Tmin, Tmax, func, C in self.antoineData:
            if T >= Tmin and T <= Tmax:
                return fitFunctions[func](T, C)
        raise Exception("Cannot find valid Psat expression for "+self.name+" at "+str(T)+"K")

    def PsatTRange(self):
        minval = 1e300
        maxval = -1e300
        for Tmin, Tmax, func, C in self.antoineData:
            minval = min(Tmin, minval)
            maxval = max(Tmax, maxval)
        return [minval, maxval]

    def Gibbs0(self, T, phase):
        return self.Hf0(T, phase) - T * self.S0(T, phase)

def registerSpecies(name, elementalComposition, mass=None):
    calcMass = 0
    for element, amount in elementalComposition.iteritems():
        if element not in elements:
            raise Exception("Species "+name+" with elemental composition "+str(elementalComposition)+" has an unknown element, "+element)
        else:
            calcMass += elements[element].mass * amount
    if mass is None:
        mass = calcMass
    else:
        if relativeError(calcMass, mass) > 0.01:
            raise Exception("Calculated species mass is significantly different when compared to passed value. Is the elemental composition or molMass correct?\n" + name + ", " + str(elementalComposition) + ", " + str(mass) + ", " + str(calcMass))
    if name not in speciesData:
        speciesData[name] = SpeciesDataType(name, mass, elementalComposition)
