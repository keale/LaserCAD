# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:57:20 2023
hi
i@author: mens
"""


import numpy as np
import sys
import os
import matplotlib.pyplot as plt

pfad = __file__
pfad = pfad[0:-7] #nur wenn das Skript auch wirklich main.py heißt
sys.path.append(pfad)
inch = 25.4


from basic_optics.freecad_models import clear_doc, setview, freecad_da, freecad_model_lens
from basic_optics import Beam, Mirror, Opt_Element, Geom_Object, Curved_Mirror, Intersection_plane
from basic_optics import Lens, Ray, Composition, Grating, Propagation
from basic_optics.freecad_models import input_output_test
# from basic_optics.tests import all_moduls_test
from basic_optics.moduls import Make_Stretcher, Make_Telescope
from basic_optics.resonator import Resonator



if freecad_da:
  clear_doc()

inch = 25.4

# from basic_optics.tests import three_resonators_test
# res1,res2,res3 = three_resonators_test()
# teles = Make_Telescope()
# teles.draw()

# if freecad_da:
#   input_output_test()
# stretcher = Make_Stretcher()
# stretcher.pos=(0,0,100)
# stretcher.draw_elements()
# stretcher.draw_rays()
# stretcher.draw()

d1 = 317
d2 = 126
d3 = 285
d4 = 384
angle1 = (np.pi-(np.arctan(7/8)+np.arctan(3/5)))*180/np.pi
angle_TFP = 56 * 2
angle2 = 5
End_Mirror1 = Mirror(phi=180)
M1 = Mirror(phi = -(180-angle1))
M_TFP = Mirror(phi = -(180-angle_TFP))
M_TFP.aperture = inch*2
M_TFP.draw_dict["model_type"] = "polarizer"
Curved_Mirror = Curved_Mirror(phi=-(180-angle2),radius=750)
Curved_Mirror.aperture = 2 * inch
End_Mirror2 = Mirror()
lightsourse=Beam(distribution="cone")
lightsourse.normal = (-1,0,0)
ip = Intersection_plane()
ip.pos = (317.,  -0., 100.)+(0.30653, -0.95186,  0.)*500

ip.normal
# Comp = Composition(pos=(10,0,100),normal=(-1,0,0))
Comp = Resonator(pos= (0,0,100),normal=(-1,0,0))
# Comp.set_light_source(lightsourse)
# Comp.propagate(10)
Comp.add_on_axis(End_Mirror1)
Comp.propagate(d1)
Comp.add_on_axis(M1)
Comp.propagate(d2)
Comp.add_on_axis(M_TFP)
Comp.propagate(d3)
Comp.add_on_axis(Curved_Mirror)
Comp.propagate(d4)
Comp.add_on_axis(End_Mirror2)


seq = np.array([0,1,2,3,4,3,2,1])
roundtrip_sequence = list(seq)

roundtrip=1
for n in range(roundtrip-1):
  seq = np.append(seq,roundtrip_sequence)
seq=np.append(seq, [0,1])
Comp.set_sequence(seq)
Comp.propagate(500)

q = Comp.compute_eigenmode()

Comp.draw()
from basic_optics.tests import three_resonators_test
# a=three_resonators_test()


# alpha = -8
# beta = -0.1
# print("g1*g2 = ", alpha*beta)
# focal = 250
# dist1 = (1-alpha)*focal
# dist2 = (1-beta)*focal
# wavelength = 0.1
# res2 = Resonator()
# res2.pos += (0,100, 0)
# mir1 = Mirror()
# mir2 = Mirror()
# le1 = Lens(f=focal)

# res2.add_on_axis(mir1)
# res2.propagate(dist1)
# res2.add_on_axis(le1)
# res2.propagate(dist2)
# res2.add_on_axis(mir2)

# q = res2.compute_eigenmode()

# print()
# print(res2.matrix())
# print()

# redu = (1-alpha*beta)*focal
# mat2 = np.array([[beta*alpha - redu/focal, 2*alpha*redu], [-2*beta/focal, beta*alpha - redu/focal]])
# print()
# print()
# print(mat2)
# print()

# res2.draw()

# x0=0
# prop_x = []
# prop_w = []
# for ii in res2._beams:
#   q_para = ii.q_para
#   z0 = np.imag(q_para)
#   z_start=np.real(q_para)
#   w0 = pow(wavelength*z0/np.pi,0.5)
#   prop0 = np.linspace(x0, x0+ii.length,int((ii.length)/5))
#   width0 = w0*np.sqrt(((prop0-x0+z_start)/z0)**2+1)
#   prop_x=np.append(prop_x,prop0)
#   prop_w=np.append(prop_w,width0)
#   x0 += ii.length
# plt.figure()
# plt.plot(prop_x, prop_w)
# plt.xlabel("propagation length (mm)")
# plt.ylabel("beam width (mm)")
# plt.show()
if freecad_da:
  setview()