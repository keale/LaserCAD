# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 14:40:56 2023

@author: mens
"""

# from ..basic_optics import Component
# from ..freecad_models.utils import thisfolder, load_STL,freecad_da
# from ..freecad_models.freecad_model_mounts import load_mount_from_csv,lens_mount,mirror_mount

import sys
sys.path.append('C:\\ProgramData\\Anaconda3')
# from LaserCAD.basic_optics import Component
# from .component import Component
from LaserCAD.freecad_models.utils import thisfolder,load_STL,freecad_da,clear_doc,rotate
from LaserCAD.freecad_models.freecad_model_composition import initialize_composition_old,add_to_composition
from LaserCAD.freecad_models.freecad_model_mounts import lens_mount,mirror_mount,DEFAULT_MOUNT_COLOR,DEFAULT_MAX_ANGULAR_OFFSET,draw_rooftop_mount
from LaserCAD.freecad_models.freecad_model_grating import grating_mount
from LaserCAD.basic_optics.geom_object import Geom_Object
from copy import deepcopy
import csv
import os
import numpy as np

DEFALUT_CAV_PATH = thisfolder
DEFALUT_MIRROR_PATH = thisfolder + "mount_meshes\\mirror"
DEFALUT_LENS_PATH = thisfolder + "mount_meshes\\lens"
DEFALUT_SPEIAL_MOUNT_PATH = thisfolder + "mount_meshes\\special mount"
MIRROR_LIST1 = os.listdir(DEFALUT_MIRROR_PATH)
MIRROR_LIST = []
for i in MIRROR_LIST1:
  a,b,c = str.partition(i, ".")
  MIRROR_LIST.append(a)

LENS_LIST1 = os.listdir(DEFALUT_LENS_PATH)
LENS_LIST = []
for i in LENS_LIST1:
  a,b,c = str.partition(i, ".")
  LENS_LIST.append(a)
  
SPECIAL_LIST1 = os.listdir(DEFALUT_SPEIAL_MOUNT_PATH)
SPECIAL_LIST = []
for i in SPECIAL_LIST1:
  a,b,c = str.partition(i, ".")
  SPECIAL_LIST.append(a)
del a,b,c,i,SPECIAL_LIST1,LENS_LIST1,MIRROR_LIST1


def rotate_vector(shiftvec=np.array((1.0,0,0)),vec=np.array((1.0,0,0)),angle=0):
  """
  rotates the shiftvec around vec with angle 
  Parameters
  ----------
  shiftvec : np.array(), optional
    The vector needs to be rotated. The default is np.array((1,0,0)).
  vec : np.array(), optional
    The rotating axis. The default is np.array((1,0,0)).
  angle : float/int, optional
    The angle. The default is 0.

  Returns
  -------
  vector:
    retated vector
  """
  k=np.dot(shiftvec,np.cos(angle))+np.cross(vec,shiftvec)*np.sin(angle)+np.dot(vec,(np.sum(vec*shiftvec))*(1-np.cos(angle)))
  return k

class Mount(Geom_Object):
  def __init__(self, name="mount",model="default",aperture=25.4,elm_type="mirror", **kwargs):
    super().__init__(name, **kwargs)


    
    self.draw_dict["color"]=DEFAULT_MOUNT_COLOR
    self.draw_dict["geom"]=self.get_geom()
    self.elm_type = elm_type
    self.draw_dict["drawing_post"] = False
    self.draw_dict["Filp90"] = False
    self.docking_obj = Geom_Object(pos = self.pos+(1,0,3),normal=(0,0,1))
    if elm_type == "lens":
      if model == "default":
        if aperture<= 25.4/2:
          model = "MLH05_M"
        elif aperture <= 25.4:
          model = "LMR1_M"
        elif aperture <= 25.4*1.5:
          model = "LMR1.5_M"
        elif aperture <=25.4*2:
          model = "LMR2_M"
    elif elm_type == "mirror":
      if model == "default":
        if aperture<= 25.4/2:
          model = "POLARIS-K05"
        elif aperture <= 25.4:
          model = "POLARIS-K1"
        elif aperture <= 25.4*1.5:
          model = "POLARIS-K15S4"
        elif aperture <=25.4*2:
          model = "POLARIS-K2"
        elif aperture <=25.4*3:
          model = "POLARIS-K3S5"
        elif aperture <=25.4*4:
          model = "KS4"
    self.model = model
    if model in MIRROR_LIST:
      stl_file=thisfolder+"\\mount_meshes\\adjusted mirror mount\\" + model + ".stl"
    elif model in LENS_LIST:
      stl_file=thisfolder+"\\mount_meshes\\adjusted lens mount\\" + model + ".stl"
    else:
      stl_file=thisfolder+"\\mount_meshes\\special mount\\" + model + ".stl"
    self.draw_dict["stl_file"]=stl_file
    self.mount_in_database = self.set_by_table()
    
  def set_by_table(self):
    """
    sets the docking object and the model by reading the "the file.csv"

    Returns
    -------
    bool
      DESCRIPTION.

    """
    buf = []
    mount_in_database = False
    aperture =height = price = xshift = offset=0
    if self.model in MIRROR_LIST:model_type ="mirror" 
    else:model_type="lens"
    with open(thisfolder+model_type+"mounts.csv") as csvfile: 
      reader = csv.DictReader(csvfile)
      for row in reader:
        buf.append(row)
    for mount_loop in buf:
      if mount_loop["name"] == self.model:
        mount_in_database = True
        aperture = float(mount_loop["aperture"])
        height = float(mount_loop["height"])
        price = float(mount_loop["price"])
        xshift = float(mount_loop["xshift"])
        offset = (float(mount_loop["offsetX"]),
                        float(mount_loop["offsetY"]),
                        float(mount_loop["offsetZ"]))
        rotation = (float(mount_loop["rot_angleZ"]),
                            float(mount_loop["rot_angleY"]),
                            float(mount_loop["rot_angleX"]))
    if not mount_in_database:
      return False
    self.aperture = aperture
    self.zshift = -height
    self.price = price
    self.xshift = xshift
    self.draw_dict["xshift"]=xshift
    self.draw_dict["height"]=height
    self.yshift = 0
    self.offset_vector = offset
    # self.post_docking_pos = self.pos+np.array([xshift,0,height])
    docking_pos = np.array([xshift,0,-height])
    docking_normal = (0,0,1)
    a=(1,0,0)
    # updates the docking geom for the first time
    if np.sum(np.cross(a,self.normal))!=0:
      rot_axis = np.cross(a,self.normal)/np.linalg.norm(np.cross(a,self.normal))
      rot_angle = np.arccos(np.sum(a*self.normal)/(np.linalg.norm(a)*np.linalg.norm(self.normal)))
      docking_pos = rotate_vector(docking_pos,rot_axis,rot_angle)
      docking_normal = rotate_vector(docking_normal,rot_axis,rot_angle)
    self.docking_obj = Geom_Object(pos = self.pos+docking_pos,normal=docking_normal)
    if self.normal[2]<DEFAULT_MAX_ANGULAR_OFFSET/180*np.pi:
      tempnormal = self.normal
      tempnormal[2]=0
      self.normal=tempnormal
      self.normal = self.normal/np.linalg.norm(self.normal)
      self.post_docking_direction = (0,0,1)
    else:
      print("this post should not be placed in the ground plate")
    self.rotation = rotation
    return True
  
  def _pos_changed(self, old_pos, new_pos):
    self._rearange_subobjects_pos( old_pos, new_pos, [self.docking_obj])
  
  def _axes_changed(self, old_axes, new_axes):
    self._rearange_subobjects_axes( old_axes, new_axes, [self.docking_obj])
  
  def draw_fc(self):
    self.update_draw_dict()
    if self.mount_in_database:
      self.draw_dict["mount_type"] = self.model
      if self.model in MIRROR_LIST:
        # return mirror_mount(**self.draw_dict)
        if self.draw_dict["Filp90"]:
          a=load_STL(**self.draw_dict)
          rotate(a,self.normal,90)
          return a
        return load_STL(**self.draw_dict)
      else:
        return load_STL(**self.draw_dict)
    elif self.model in SPECIAL_LIST or self.model in MIRROR_LIST or self.model in LENS_LIST:
      return load_STL(**self.draw_dict)
    else:
      self.draw_dict["stl_file"]=self.model
      print("This mount is not in the correct folder")
      return load_STL(**self.draw_dict)

class Grating_mount(Mount):
  def __init__(self, name="grating_mounmt",model="grating_mount",height=50,thickness=8, **kwargs):
    super().__init__(name, **kwargs)
    self.draw_dict["height"]=height
    self.draw_dict["thickness"]= thickness
    self.draw_dict["drawing_post"] = False
    self.draw_dict["geom"]=self.get_geom()
    self.xshift = 17
  def draw_fc(self):
    return grating_mount(**self.draw_dict)

class Special_mount(Mount):
  def __init__(self, name="special_mounmt",model="special_mount",aperture=25.4,thickness=10,
               docking_pos = (1,2,3),docking_normal=(0,0,1), **kwargs):
    super().__init__(name, **kwargs)
    self.draw_dict["aperture"] = aperture
    self.draw_dict["thickness"] = thickness
    self.draw_dict["geom"]=self.get_geom()
    self.model = model
    if model=="rooftop mirror mount":
      self.list_rooptop_mirror_mount(aperture)
      docking_pos = (38,0,-5)
      docking_normal = (1,0,0)
    if model == "Stripe mirror mount":
      self.list_rooptop_mirror_mount(aperture)
    a=(1,0,0)
    if np.sum(np.cross(a,self.normal))!=0:
      rot_axis = np.cross(a,self.normal)/np.linalg.norm(np.cross(a,self.normal))
      rot_angle = np.arccos(np.sum(a*self.normal)/(np.linalg.norm(a)*np.linalg.norm(self.normal)))
      docking_pos = rotate_vector(docking_pos,rot_axis,rot_angle)
      docking_normal = rotate_vector(docking_normal,rot_axis,rot_angle)
    self.docking_obj = Geom_Object(pos = self.pos+docking_pos,normal=docking_normal)
    
  def list_rooptop_mirror_mount(self,aperture=25.4, **keywords):
    self.xshift=38#+aperture/2
    self.zshift=-5
    self.draw_dict["stl_file"]=thisfolder+"\\mount_meshes\\special mount\\rooftop mirror mount.stl"
    self.draw_dict["mount_type"] = "rooftop_mirror_mount"
    
  def list_stripe_mirror_mount(self,thickness=25.4, **keywords):
    self.draw_dict["model_type"] = "Stripe"
    self.xshift = thickness-7
    self.yshift = 104.3
  
  @property
  def docking_pos(self):
    return np.array(self.docking_obj.pos) * 1.0
  @docking_pos.setter
  def docking_pos(self, x):
    self.docking_pos = np.array(x) * 1.0
    self.docking_obj.pos = self.docking_pos
  
  @property
  def docking_normal(self):
    return np.array(self.docking_obj.normal) * 1.0
  @docking_normal.setter
  def docking_normal(self, x):
    self.docking_normal = np.array(x) * 1.0
    self.docking_obj.normal = self.docking_normal
    
  def draw_fc(self):
    if self.model=="rooftop mirror mount" or self.model=="Stripe mirror mount":
      self.draw_dict["geom"]=self.get_geom()
      self.draw_dict["stl_file"]=thisfolder+"\\mount_meshes\\special mount\\" + self.model + ".stl"
      return load_STL(**self.draw_dict)
      # return mirror_mount(**self.draw_dict)
    else:
      self.draw_dict["geom"]=self.get_geom()
      self.draw_dict["stl_file"]=thisfolder+"\\mount_meshes\\special mount\\" + self.model + ".stl"
      return load_STL(**self.draw_dict)
    
class Composed_Mount(Mount):
  def __init__(self, **kwargs):
    self.mount_list = []
    super().__init__(**kwargs)
    self.docking_obj = Geom_Object()
    self.docking_obj.set_geom(self.get_geom())
    
  def add(self, mount):
    mount.set_geom(self.docking_obj.get_geom())
    self.mount_list.append(mount)
    self.docking_obj.set_geom(mount.docking_obj.get_geom())
    
  def draw_fc(self):
    for mount in self.mount_list:
      mount.draw_fc()
    
  def _pos_changed(self, old_pos, new_pos):
    self._rearange_subobjects_pos( old_pos, new_pos, [self.docking_obj])
    self._rearange_subobjects_pos( old_pos, new_pos, self.mount_list)
  
  def _axes_changed(self, old_axes, new_axes):
    self._rearange_subobjects_axes( old_axes, new_axes, [self.docking_obj])
    self._rearange_subobjects_axes( old_axes, new_axes, self.mount_list)

# if freecad_da:
#   clear_doc()

# M1 = Special_mount(name = "aaa",model= "H45CN",docking_pos=(22,22,0),docking_normal=(1,1,0),normal=(1,1,0))
# M1.normal=(1,0,0)
# M1.draw()
# # M2= Mount(name="bbb",model= "KM200CP_M",pos=M1.docking_pos,normal=M1.docking_normal)
# M2= Mount(name="bbb",model= "KM200CP_M")
# M2.draw()

# Comp = Composed_Mount()
# Comp.add(M1)
# Comp.add(M2)
# Comp.draw()