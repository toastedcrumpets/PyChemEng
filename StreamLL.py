#!/usr/bin/python


from numpy import *
from collections import defaultdict
from scipy.optimize import fmin_slsqp

from Phase import Phase
from Molecule import Molecule


################################################################################
################################################################################
################################################################################
class StreamLL:

    def __init__(self):
        self.moleNumbers = {}
        self.phase_dict = {}
        self.molecule_dict = {}

    def addPhase(self, phase):
        name = phase.get_name()
        self.phase_dict[name] = phase
        molecule_dict = phase.molecules()
        self.molecule_dict.update(molecule_dict)

    def setMoleNumber(self, name, Ninput):
        self.moleNumbers[name] = Ninput
        
    def getMoleNumbers(self):
        return self.moleNumbers

    def setTemperature(self, Tinput):
        self.T = Tinput

    def setPressure(self, pinput):
        self.p = pinput
#    def addMolecule(self, mol, Ninput=0.0):
#        name = mol.get_name()
#        self.molecule_dict[name] = mol
#        self.moleNumbers[name] = Ninput


################################################################################
################################################################################
    def gibbsFreeEnergy(self, x):

#        print '=== in gibbsFreeEnergy ==='
#        print 'x =', x
#   translate x to component mole numbers
        index = 0
        phaseList = self.phase_dict.keys()
        phaseList.sort()
        for A in phaseList:
            moleculeList = self.phase_dict[A].moleNumbers().keys()
            moleculeList.sort()
#            print '--- ', A, ' ---'
            N = self.phase_dict[A].moleNumbers()
            for a in moleculeList:
                self.phase_dict[A].set_conc(a, x[index])
#                print a, index, N[a], x[index]
                index += 1

        G = 0.0
        for A in self.phase_dict:
            G += self.phase_dict[A].gibbsFreeEnergy()
#        print 'G =', G
            
        return G


    def moleBalance(self, x):
#   translate x to component mole numbers
        index = 0
        phaseList = self.phase_dict.keys()
        phaseList.sort()
        for A in phaseList:
            moleculeList = self.phase_dict[A].moleNumbers().keys()
            moleculeList.sort()
#            print '--- ', A, ' ---'
            N = self.phase_dict[A].moleNumbers()
            for a in moleculeList:
                self.phase_dict[A].set_conc(a, x[index])
#                print a, index, N[a], x[index]
                index += 1

        res = []
        moleculeList = self.molecule_dict.keys()
        moleculeList.sort()
        for a in moleculeList:
            f = - self.moleNumbers[a]
            for A in self.phase_dict:
                f += self.phase_dict[A].getMoleNumber(a)
            res.append( f )
        return res
                

    def equilibrate(self, outputlevel=0):
        phaseList = self.phase_dict.keys()
        phaseList.sort()
        for A in phaseList:
            self.phase_dict[A].setTemperature(self.T)
            self.phase_dict[A].setPressure(self.p)
        
        x_init = []
        variableBounds = []
        index = 0
        for A in phaseList:
            moleculeList = self.phase_dict[A].moleNumbers().keys()
            moleculeList.sort()
            print '--- ', A, ' ---'
            N = self.phase_dict[A].moleNumbers()
            for a in moleculeList:
                print a, index, N[a]
                x_init.append( N[a] )
                variableBounds.append( [0.0, self.moleNumbers[a]] )
                index += 1
        print x_init
        print variableBounds
        
        res = self.moleBalance(x_init)
        print 'res=', res

        print 'G=', self.gibbsFreeEnergy(x_init)

        x_equil = fmin_slsqp(self.gibbsFreeEnergy,
                             x_init,
                             f_eqcons=self.moleBalance,
                             bounds=variableBounds,
                             iprint=outputlevel,
                             )
        print x_equil

#       translate x to component mole numbers
        index = 0
        phaseList = self.phase_dict.keys()
        phaseList.sort()
        for A in phaseList:
            moleculeList = self.phase_dict[A].moleNumbers().keys()
            moleculeList.sort()
            print '--- ', A, ' ---'
            N = self.phase_dict[A].moleNumbers()
            for a in moleculeList:
                self.phase_dict[A].set_conc(a, x_equil[index])
                print a, index, N[a], x_equil[index]
                index += 1


################################################################################
################################################################################
################################################################################