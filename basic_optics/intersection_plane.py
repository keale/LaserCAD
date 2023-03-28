# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:06:17 2023

@author: 12816
"""

from .optical_element import Opt_Element
import numpy as np
from copy import deepcopy
from .ray import Ray
from .beam import Beam
import matplotlib.pyplot as plt
from .freecad_models import model_diaphragms,iris_post


class Intersection_plane(Opt_Element):
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
    return model_diaphragms(**self.draw_dict)
  
  
  def spot_diagram(self, beam):
    point_x = []
    point_y = []
    rays = beam.get_all_rays()

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
    plt.show()
  
  def __repr__(self):
    n = len(self.Klassenname())
    txt = 'Intersection_plane(dia=' + repr(self.aperture)
    txt += ', ' + super().__repr__()[n+1::]
    return txt