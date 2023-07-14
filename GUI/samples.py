# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 13:15:19 2023

@author: He
"""

#!/usr/bin/python

import sys
import os
    
sys.path.append('C:\\ProgramData\\Anaconda3')

from LaserCAD import basic_optics

from LaserCAD.basic_optics import Mirror,Beam,Cylindrical_Mirror,Intersection_plane,Cylindrical_Mirror1,Curved_Mirror,Ray, Composition, Grating, Lam_Plane
from LaserCAD.basic_optics import Geom_Object,Lens
from LaserCAD.freecad_models import clear_doc, freecad_da

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
a0= Mirror(phi=180.0, theta=0.0, name="NewComposition_Mirror_01", pos=[100.,   0.,  80.], normal=[1., 0., 0.])
a0.normal=(1.0,0.0,0.0)
a1= Mirror(phi=180.0, theta=0.0, name="NewComposition_Mirror_02", pos=[ 0.,  0., 80.], normal=[-1.,  0.,  0.])
a1.normal=(-1.0,6.123233995736766e-17,0.0)
ls= Beam(radius=1.0, angle=0.0, distribution='square', name="NewComposition_Lightsource", pos=[ 0.,  0., 80.], normal=[1., 0., 0.])
comp= Composition(name="NewComposition", pos=[ 0.,  0., 80.], normal=[1., 0., 0.])
comp.set_light_source(ls)
comp.add_fixed_elm(a0)
comp.add_fixed_elm(a1)
comp.draw()