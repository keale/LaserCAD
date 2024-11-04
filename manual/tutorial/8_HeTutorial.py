# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 18:06:09 2023

@author: mens
"""

# =============================================================================
# HEs Tutorial
# =============================================================================

# =============================================================================
# some usefull imports that should be copied to ANY project
# =============================================================================
import sys
pfad = __file__
pfad = pfad.replace("\\","/") #folder conventions windows linux stuff
pfad = pfad.lower()
ind = pfad.rfind("lasercad")
pfad = pfad[0:ind-1]
if not pfad in sys.path:
  sys.path.append(pfad)

from LaserCAD.basic_optics import Mirror, Curved_Mirror, Lens, Composition, Beam, Ray, Grating
from LaserCAD.freecad_models import freecad_da, clear_doc, setview

# =============================================================================
# about lenses, curved mirrors and spot diagrams
# =============================================================================

if freecad_da:
  clear_doc()

"""
LaserCAD User Guide

LaserCAD is a software for optical tracking and 3D modeling based on Python and FreeCAD. This article tries to give a brief introduction to how to use this software.

1 Introduction to basic objects
  In LaserCAD, all objects must contain one basic piece of information: geometric information. Geometric information has two components, the set position (pos) and the axes matrix (_axes), and for some simple objects, the direction of the object can represent the axes. Thus as for the most general case, we would recommend using normal direction (normal) to show the object's rotation. 
"""
A=Mirror() #Mirror is a basic optical element. In LaserCAD we define Mirror as a class to handle the function easily.
A.pos = (100,0,80) # This changes A's position to the (100,0,80). Units in mm.
A.normal = (1,1,0) # This changes A's normal vector to the (1,1,0). It can be normalized automatically.
A.draw() # This draws A by text or by 3D model.


#As an optical modeling software, light sources are essential, and LaserCAD defines a variety of light sources, of which there are two basic ones, Ray and Beam. Ray is a light with no width and forms the basis of the light source.

A = Ray()
A.length = 150 # define the propagation length
A.wavelenth = 500E-6 # The wavelength of the ray, unit in mm.
A.draw()

 
#Another light source is Beam. With a certain beam radius, the modeling of isotropic light can be replaced by a cone. The beam has two values: radius and angle. The angle is the dispersed angle of the beam.

A = Beam(radius=1.5,angle=0.01)
A.draw()

#  In some other cases, we might need some other distribution of the beam. So we built some default distribution of the beam.

A = Beam(distribution='square') # We can change the distribution to 'square', 'cone', 'Gaussian', and 'circular'
A.draw()
# B = Beam(distribution='circular')
# # B.make_circular_distribution() # We can also change the distribution by function "make_cone_distribution", "make_square_distribution", "make_circular_distribution", and "make_Gaussian_distribution"
# B.draw()

 # Next, we built some optical elements for construction, there is a short introduction of some: Mirror, Lens, and Grating.
 # The default mirror is the flat mirror.
  
A = Mirror(phi = 54, theta = 20) # phi is the rotation angle in the xy-plane and theta is the rotation angle out of the xy-plane.
A.aperture = 25.4*2 # Set the mirror's aperture, the default setting is 25.4(1 inch)
A.draw()

#  Besides, LaserCAD offers options for curved mirrors.

A = Curved_Mirror(radius = 200)
"""
Here we add a beam to test the focusing ability of the curved mirror.
"""
B = Beam()
A.pos = B.pos + (100,0,0)
A.normal = (1,1,0)
B_next = A.next_beam(B)
A.draw()
B.draw()
B_next.draw()
  
 # As for the lens and grating, they have some different values. But basically, they share the same program progress as a mirror.
  
A=Lens(f=100) # f: lens's focal length
B=Grating(grat_const=1/1000,order=1) # grating const in 1/mm and the diffraction order
A.draw()
B.draw()

#  From the Curved_Mirror example, we can find out that in order to get the result of the interaction between the beam and the optics, you have to define a new beam and get the next beam using the next_beam function. This creates a lot of inconvenience in complex optical modeling. Thus, we define a new class named Composition to classify all the beams, optical elements, and mounts.
  
A=Lens()
B=Mirror(phi=54)
C=Beam()
D=Composition()
D.set_light_source(C)
D.propagate(100)
D.add_on_axis(A)
D.propagate(200)
D.add_on_axis(B)
D.propagate(80)
D.draw()

#  In the code, the add_on_axis function is used to add the optics to the correct position on the axis. We can also add the optics to a certain position.
  
A=Lens()
A.pos += (100,0,0)
B=Mirror(phi=54)
B.pos += (200,0,0)
C=Beam()
D=Composition()
D.set_light_source(C)
D.add_fixed_elm(A)
D.add_fixed_elm(B)
D.propagate(50)
D.draw()

if freecad_da:
  setview()