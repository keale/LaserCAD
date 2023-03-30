# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:06:17 2023

@author: 12816
"""

from .optical_element import Opt_Element
import numpy as np
from copy import deepcopy
from .ray import Ray
from .beam import Beam,RayGroup
import matplotlib.pyplot as plt
from .freecad_models import model_intersection_plane


class Intersection_plane(Opt_Element):
  """
  The class of the intersection plane.
  special functions: spot_diagram. Draw the Spot diagram at the intersection 
  plane
  """
  def __init__(self, dia=100, name="NewPlane", **kwargs):
    super().__init__(name=name, **kwargs)
    self.draw_dict["Radius"] = dia/2
    self.draw_dict["dia"]=dia
    self.aperture=dia
    
  def next_ray(self, ray):
    ray2=deepcopy(ray)
    ray2.pos = ray.intersect_with(self)
    return ray2
  
  def draw_fc(self):
    self.update_draw_dict()
    return model_intersection_plane(**self.draw_dict)
  
  
  def spot_diagram(self, beam):
    """
      Draw the Spot diagram at the intersection plane

      Parameters
      ----------
      beam : Beam
          Input beam.

      Returns
      -------
      None.

      """
    point_x = []
    point_y = []
    if isinstance(beam, RayGroup) or isinstance(beam, Beam):
      rays = beam.get_all_rays()
    else:
      rays = beam
    for point_i in rays:
      intersection_point = point_i.intersection(self)
      pos_diff = intersection_point - self.pos
      if self.draw_dict["dia"]**2<pos_diff[1]**2+pos_diff[2]**2:
        self.draw_dict["dia"] = pow(pos_diff[1]**2+pos_diff[2]**2,0.5)
        self.aperture=self.draw_dict["dia"]
      point_x.append(pos_diff[1])
      point_y.append(pos_diff[2])
    plt.figure()
    plt.scatter(point_x,point_y)
    plt.xlabel("x-axis, or y-axis if you follow the 3D coordinate (mm)")
    plt.ylabel("y-axis, or z-axis if you follow the 3D coordinate (mm)")
    plt.title("The spot diagram at " + self.name)
    plt.show()
  
  def __repr__(self):
    n = len(self.Klassenname())
    txt = 'Intersection_plane(dia=' + repr(self.aperture)
    txt += ', ' + super().__repr__()[n+1::]
    return txt