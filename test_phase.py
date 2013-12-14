#!/usr/bin/python

from numpy import *
from collections import defaultdict

from Phase import Phase
from IdealGas import IdealGas
from UNIFAC import UNIFAC
from Solid import *

from UNIFACGroup import UNIFACGroup
from Molecule import Molecule

from StreamLL import *

################################################################################
################################################################################
################################################################################
f = open('antoine.dat')
lines = f.readlines()
f.close()

antoineCoeff = {}
for line in lines:
    data = line.split()
    name = data[0]
    antoineCoeff[name] = [float(data[1]), float(data[2]), float(data[3])]


################################################################################
################################################################################
f = open('param_example.dat')
lines = f.readlines()
f.close()

group_dict = {}
for line in lines:
    data = line.split()
    name = data[0]
    id   = int( data[1] )
    R = float( data[2] )
    Q = float( data[3] )
    group = UNIFACGroup(name, id)
    group.set_R(R)
    group.set_Q(Q)
    group_dict[name] = group
#    print group.get_name(), group.get_id()


################################################################################
################################################################################
f = open('param2_example.dat')
lines = f.readlines()
f.close()

A_mat = defaultdict(dict)
B_mat = defaultdict(dict)
for line in lines:
    data = line.split()
    if (len(data)==4):
        print data
        i = data[0]
        j = data[1]
        A = float( data[2] )
        B = float( data[3] )
        A_mat[i][j] = A
        B_mat[i][j] = B


################################################################################
################################################################################
#liquid = FreeEnergy('liquid', 'test 2')
liquid = UNIFAC('liquid', group_dict, A_mat, B_mat)
liquid.setTemperature(308.15)
print liquid.get_tau('CH3', 'CH3')


################################################################################
################################################################################
# create molecules

moleculeDict = {}

print '---'
name = 'diethylamine'
mol = Molecule(name, 1)
mol.setAntoineCoefficients(antoineCoeff[name])
mol.add_group( group_dict['CH3'], 2 )
mol.add_group( group_dict['CH2'], 1 )
mol.add_group( group_dict['CH2NH'], 1 )
mol.set_parameters()
mol.print_group_list()
moleculeDict[name] = mol
liquid.add_molecule(mol)


print '---'
name = 'n-heptane'
mol = Molecule(name, 2)
mol.setAntoineCoefficients(antoineCoeff[name])
mol.add_group( group_dict['CH3'], 2 )
mol.add_group( group_dict['CH2'], 5 )
mol.set_parameters()
mol.print_group_list()
moleculeDict[name] = mol
liquid.add_molecule(mol)

liquid.print_molecule_list()
liquid.print_group_list()


from pylab import *
T_data = arange(200.0, 400.0, 10.0)

for name in moleculeDict:
    p_data = []
    for T in T_data:
        p_data.append( moleculeDict[name].vaporPressure(T)*1.0e-5 )
    plot(T_data, p_data)

ylabel(r'pressure / bar')
show()


################################################################################
################################################################################
liquid.set_conc('diethylamine', 0.4)
liquid.set_conc('n-heptane', 0.6)
liquid.print_conc()


liquid.methodName()
ln_gamma = liquid.get_lngamma()
print ln_gamma


################################################################################
################################################################################
vapor = IdealGas('vapor')
vapor.set_conc('diethylamine', 0.6)
vapor.set_conc('n-heptane', 0.4)


################################################################################
################################################################################
solid = Solid('solid')
solid.set_conc('diethylamine', 1.0)


phase_dict = {}
phase_dict['liquid'] = liquid
phase_dict['vapor'] = vapor
phase_dict['solid'] = solid


T = 350.0
p = 1.0e5
stream = StreamLL()
stream.setTemperature(T)
stream.setPressure(p)

stream.addPhase(liquid)
stream.addPhase(vapor)
#stream.addPhase(solid)

stream.setMoleNumber('diethylamine', 1.0)
stream.setMoleNumber('n-heptane', 1.0)
print 'stream mole numbers = ', stream.getMoleNumbers()

#x = 0.0
#stream.gibbsFreeEnergy(x)
stream.equilibrate(2)
