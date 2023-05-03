# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 16:28:07 2022

@author: mens
"""

# from basic_optics import Opt_Element, TOLERANCE, Ray
# from basic_optics.freecad_models import model_mirror, freecad_da
from .geom_object import TOLERANCE, NORM0
from .ray import Ray
from .freecad_models import model_mirror, mirror_mount, model_stripe_mirror
from .optical_element import Opt_Element
import numpy as np
from copy import deepcopy

try:
  import FreeCAD
  DOC = FreeCAD.activeDocument()
  print(DOC)
  from FreeCAD import Vector, Placement, Rotation
except:
  freecad_da = False
  DOC = None

from .freecad_models.utils import freecad_da, update_geom_info, get_DOC, rotate, thisfolder

class Mirror(Opt_Element):
  """
  Spiegelklasse, erbit von <Opt_Element>, nimmt einen ray und transformiert 
  ihn entsprechend des Reflexionsgesetzes
  Anwendung wie folgt:
    
  m = Mirror(phi=90)
  r = Ray()
  m.set_geom(r.get_geom())
  nr = m.next_ray(r)
  
  dreht <r> in der xy-Ebene um den Winkel <phi> €[-180,180] und dreht um 
  <theta> € [-90,90] aus der xy-Ebene heraus, wenn man die normale voher mit 
  set_geom() einstellt
  """
  def __init__(self, phi=180, theta=0, **kwargs):
    super().__init__(**kwargs)
    self.__incident_normal = np.array(NORM0) # default von Strahl von x
    self.__theta = theta
    self.__phi = phi
    self.update_normal()
    #Cosmetics
    self.draw_dict["Radius"] = 0
    

  def update_normal(self):
    """
    aktualisiert die Normale des Mirrors entsprechend der __incident_normal, 
    phi und theta
    """
    phi = self.__phi/180*np.pi
    theta = self.__theta/180*np.pi
    if phi == 0 and theta == 0:
      print("Warnung, Spiegel unbestimmt und sinnlos, beide Winkel 0")
      self.normal = (0,1,0)
      return -1

    rho = self.__incident_normal[0:2]
    rho_abs = np.linalg.norm(rho)
    z = self.__incident_normal[2]
    rho2_abs = rho_abs * np.cos(theta) - z * np.sin(theta)
    z2 = rho_abs * np.sin(theta) + z * np.cos(theta)
    if rho_abs == 0:
      x = rho2_abs
      y = 0
    else:
      x = rho[0] * rho2_abs/rho_abs
      y = rho[1] * rho2_abs/rho_abs
    x2 = x * np.cos(phi) - y * np.sin(phi)
    y2 = x * np.sin(phi) + y * np.cos(phi)
    self.normal = self.__incident_normal - (x2, y2, z2)

  def set_geom(self, geom):
    """
    setzt <pos> und __incident_normal auf <geom> und akturalisiert dann die 
    eigene <normal> entsprechend <phi> und <theta>

    Parameters
    ----------
    geom : 2-dim Tupel aus 3-D float arrays
      (pos, normal)
    """
    self.pos = geom[0]
    # self.__incident_normal = geom[1]
    axes = geom[1]
    self.__incident_normal = axes[:,0]
    self.update_normal()

  @property
  def phi(self):
    """
    beschreibt den Winkel <phi> um den der Mirror einen Strahl in 
    <__incident_normal> Richtung in der xy-Ebene durch Reflexion weiter dreht
    (mathematisch positive Drehrichtung)
    stellt über Setter sicher, dass die normale entsprechend aktualisiert wird
    """
    return self.__phi
  @phi.setter
  def phi(self, x):
    
    self.__phi = x
    self.update_normal()

  @property
  def theta(self):
    """
    beschreibt den Winkel <theta> um den der Mirror einen Strahl in 
    <__incident_normal> Richtung aus der xy-Ebene durch Reflexion weiter dreht
    (mathematisch positive Drehrichtung)
    stellt über Setter sicher, dass die normale entsprechend aktualisiert wird
    """
    return self.__theta
  @theta.setter
  def theta(self, x):
    self.__theta = x
    self.update_normal()

  def next_ray(self, ray):
    return self.reflection(ray)

  def set_incident_normal(self, vec):
    """
    setzt neue <__incident_normal> und berechnet daraus mit <phi> und <theta> 
    die neue <normal>
    """
    vec = vec / np.linalg.norm(vec)
    self.__incident_normal = np.array((1.0,1.0,1.0)) * vec
    self.update_normal()

  def recompute_angles(self):
    """
    berechnet die Winkel neu aus <__incident_normal> und <normal>
    """
    vec1 = self.__incident_normal
    dummy = Ray(normal=vec1)
    #nur um next_ray und reflectino zu nutzen
    reflected_dummy = self.next_ray(dummy)
    vec2 = reflected_dummy.normal
    xy1 = vec1[0:2]
    xy2 = vec2[0:2]
    teiler = np.linalg.norm(xy1) * np.linalg.norm(xy2)
    if teiler < TOLERANCE:
      #wenn die Komponenten verschwinden, kann kein Winkel bestimmt werden
      phi = 0
    else:
      phi0 = np.arcsin( (xy1[0]*xy2[1]-xy1[1]*xy2[0]) /teiler) * 180/np.pi
      scalar = np.sum(xy1*xy2)
      if scalar >= 0:
        phi = phi0
      else:
        phi = -180 - phi0 if (phi0 < 0) else 180 - phi0 
    v3 = np.array((np.linalg.norm(xy1), vec1[2]))
    v4 = np.array((np.linalg.norm(xy2), vec2[2]))
    teiler = np.linalg.norm(v3) * np.linalg.norm(v4)
    if teiler < TOLERANCE:
      #wenn die Komponenten verschwinden, kann kein Winkel bestimmt werden
      theta = 0
    else:
      theta = np.arcsin( (v3[0]*v4[1]-v3[1]*v4[0]) /teiler) * 180/np.pi
    return phi, theta

  def set_normal_with_2_points(self, p0, p1):
    """
    setzt die Normale neu, sodass der mirror einen Strahl reflektiert, der von
    p0 kommt, den Spiegel in self.pos trifft und dann zu p1 reflektiert wird
    berechnet anschließend die Winkel neu
    """
    inc = self.pos - p0
    refl = p1 - self.pos
    inc *= 1/np.linalg.norm(inc)
    refl *= 1/np.linalg.norm(refl)
    # print("nextnormal", (inc - refl)/np.linalg.norm(inc - refl))
    self.normal = inc - refl
    self.__phi, self.__theta =  self.recompute_angles()

  def __repr__(self):
    n = len(self.class_name())
    txt = 'Mirror(phi=' + repr(self.phi)
    txt += ", theta=" + repr(self.theta)
    txt += ', ' + super().__repr__()[n+1::]
    return txt

  def draw_fc(self):
    self.update_draw_dict()
    self.draw_dict["dia"]=self.aperture
    obj = model_mirror(**self.draw_dict)
    return obj

  def draw_mount_fc(self):
    self.update_draw_dict()
    self.draw_dict["dia"]=self.aperture
    # obj = mirror_mount(**self.draw_dict)
    # now we will use the old geom definition with (pos, norm) in a dirty, 
    # hacky way, because I don't want to fix the 10.000 usages of geom in
    # the mirror_mount function manually, no, I don't
    helper_dict = dict(self.draw_dict)
    # helper_dict["geom"] = (self.pos, self.normal)
    obj = mirror_mount(**helper_dict)
    return obj



class Curved_Mirror(Mirror):
  def __init__(self, radius=200, **kwargs):
    super().__init__(**kwargs)
    self.radius = radius
    self.draw_dict["Radius"] = self.radius

  @property
  def radius(self):
    return self.__radius
  @radius.setter
  def radius(self, x):
    self.__radius = x
    if x == 0:
      self._matrix[1,0] = 0
    else:
      self._matrix[1,0] = -2/x

  def focal_length(self):
    return self.radius/2

  def next_ray(self, ray):
    # r1 = self.refraction(ray)
    # r2 = self.reflection(r1)
    r2 = self.next_ray_trace(ray)
    return r2

  def __repr__(self):
    txt = 'Curved_Mirror(radius=' + repr(self.radius)
    txt += ', ' + super().__repr__()[7::]
    return txt

  # def next_geom(self, geom):
  #   r0 = Ray()
  #   r0.set_geom(geom)
  #   r1 = self.next_ray(r0)
  #   return r1.get_geom()

  def draw_fc(self):
    self.update_draw_dict()
    self.draw_dict["dia"]=self.aperture
    # self.draw_dict["mount_type"] = "POLARIS-K1-Step"
    self.draw_dict["Radius1"] = self.radius
    obj = model_mirror(**self.draw_dict)
    return obj
  
  
  
  def next_ray_trace(self, ray):
    """
    erzeugt den nächsten Ray auf Basis der analytischen Berechung von Schnitt-
    punkt von Sphere mit ray und dem vektoriellen Reflexionsgesetz
    siehe S Hb o LaO S 66 f

    Parameters
    ----------
    ray : TYPE Ray
      input ray

    Returns
    -------
    ray2 : TYPE Ray
      output ray

    """
    ray2 = deepcopy(ray)
    ray2.name = "next_" + ray.name
    
    center = self.pos - self.radius * self.normal
    p0 = ray.intersect_with_sphere(center, self.radius) #Auftreffpunkt p0
    surface_norm = p0 - center #Normale auf Spiegeloberfläche in p0 
    surface_norm *= 1/np.linalg.norm(surface_norm) #normieren
    #Reflektionsgesetz
    # if np.std(ray2.normal-self.normal)<TOLERANCE and np.std(p0-self.pos)<TOLERANCE:
    #   ray2.pos = p0
    #   a=ray2.normal
    #   a=a*-1
    #   ray3 = Ray(name = ray2.name)
    #   ray3.pos = p0
    #   ray3.normal = a
    #   return ray3
    ray2.normal = ray.normal - 2*np.sum(ray.normal*surface_norm)*surface_norm
    ray2.pos = p0
    return ray2

class Cylindrical_Mirror(Mirror):
  def __init__(self, radius=200,height=10, thickness=25, **kwargs):
    super().__init__(**kwargs)
    self.radius = radius
    self.draw_dict["Radius"] = radius
    self.draw_dict["height"]=height
    self.draw_dict["thickness"]=thickness
    self.draw_dict["model_type"]="Stripe"

  @property
  def radius(self):
    return self.__radius
  @radius.setter
  def radius(self, x):
    self.__radius = x
    if x == 0:
      self._matrix[1,0] = 0
    else:
      self._matrix[1,0] = -2/x

  def focal_length(self):
    return self.radius/2

  def next_ray(self, ray):
    # r1 = self.refraction(ray)
    # r2 = self.reflection(r1)
    r2 = self.next_ray_tracing(ray)
    return r2

  def __repr__(self):
    txt = 'Cylindrical_Mirror(radius=' + repr(self.radius)
    txt += ', ' + super().__repr__()[7::]
    return txt

  def next_geom(self, geom):
    r0 = Ray()
    r0.set_geom(geom)
    r1 = self.next_ray(r0)
    return r1.get_geom()

  def draw_fc(self):
    self.update_draw_dict()
    self.draw_dict["dia"]=self.aperture
    # self.draw_dict["mount_type"] = "POLARIS-K1-Step"
    self.draw_dict["Radius1"] = self.radius
    obj = model_mirror(**self.draw_dict)
    # default = Vector(0,0,1)
    # xx,yy,zz = self.get_coordinate_system()
    # zz = Vector(zz)
    # angle = default.getAngle(zz)*180/np.pi
    # vec = default.cross(zz)
    # rotate(obj, vec, angle, off0=0)
    return obj
  
  def next_ray_tracing(self, ray):
    """
    erzeugt den nächsten Ray auf Basis der analytischen Berechung von Schnitt-
    punkt von Sphere mit ray und dem vektoriellen Reflexionsgesetz
    siehe S Hb o LaO S 66 f

    Parameters
    ----------
    ray : TYPE Ray
      input ray

    Returns
    -------
    ray2 : TYPE Ray
      output ray

    """
    ray2 = deepcopy(ray)
    ray2.name = "next_" + ray.name
    self.normal *= 1/np.linalg.norm(self.normal)
    center = self.pos - self.radius * self.normal
    xx,yy,zz = self.get_coordinate_system()
    ray_origin = ray2.pos
    ray_direction = ray2.normal
    cylinder_center = center
    cylinder_axis = zz
    
    ray_origin = np.array(ray_origin)
    ray_direction = np.array(ray_direction)
    cylinder_center = np.array(cylinder_center)
    cylinder_axis = np.array(cylinder_axis)
    
    # oc = ray_origin - cylinder_center
    # a = np.dot(ray_direction, ray_direction) - np.dot(ray_direction, cylinder_axis)**2
    # b = 2 * (np.dot(ray_direction, oc) - np.dot(ray_direction, cylinder_axis) * np.dot(oc, cylinder_axis))
    # c = np.dot(oc, oc) - np.dot(oc, cylinder_axis)**2 - self.radius**2
    middle_vec = cylinder_center + cylinder_axis * (np.dot(ray_origin,cylinder_axis) - np.dot(cylinder_center,cylinder_axis))-ray_origin
    middle_vec2 = cylinder_axis*(np.dot(ray_direction,cylinder_axis))-ray_direction
    a = np.dot(middle_vec2 , middle_vec2)
    b = 2 * np.dot(middle_vec2 , middle_vec)
    c = np.dot(middle_vec , middle_vec) - self.radius **2
    
    
    # Compute discriminant
    discriminant = b**2 - 4 * a * c

    # If discriminant is negative, no intersection
    if discriminant < 0:
        print(ray2)
        ray2.draw()
        print("ray_origin=",ray_origin)
        print("ray_direction=",ray_direction)
        print("cylinder_center=",cylinder_center)
        print("cylinder_axis=",cylinder_axis)
        return None

    # Compute t parameter (parameter along the ray direction)
    t1 = (-b + np.sqrt(discriminant)) / (2 * a)
    t2 = (-b - np.sqrt(discriminant)) / (2 * a)

    # Check if intersection is within ray segment
    # if t1 < 0 and t2 < 0:
    #     return None

    # Select smallest positive t
    # t = min(t1, t2) if t1 >= 0 and t2 >= 0 else max(t1, t2)
    if self.radius>0:
      t = max(t1, t2)
    else:
      t = min(t1, t2)
    # Compute intersection point
    
    intersection_point = ray_origin + ray_direction * t
    p0 = intersection_point
    new_center = cylinder_center + cylinder_axis * (np.dot(p0,cylinder_axis)-np.dot(cylinder_center,cylinder_axis))
    surface_norm = p0 - new_center #Normale auf Spiegeloberfläche in p0 
    surface_norm *= 1/np.linalg.norm(surface_norm) #normieren
    #Reflektionsgesetz
    # print(cylinder_center,new_center)
    ray2.normal = ray.normal - 2*np.sum(ray.normal*surface_norm)*surface_norm
    ray2.pos = p0
    dist = p0-ray.pos
    ray.length=np.sqrt(dist[0]**2+dist[1]**2+dist[2]**2)
    return ray2
  
  
  
def intersect_ray_cylinder(ray_origin, ray_direction, cylinder_center, cylinder_axis, cylinder_radius):
    """
    Calculates the intersection point of a ray with a cylindrical surface.

    Args:
        ray_origin (numpy array): The origin of the ray, as a 3D vector.
        ray_direction (numpy array): The direction of the ray, as a 3D vector.
        cylinder_center (numpy array): The center of the cylinder, as a 3D vector.
        cylinder_axis (numpy array): The axis of the cylinder, as a 3D vector.
        cylinder_radius (float): The radius of the cylinder.

    Returns:
        numpy array or None: The intersection point, as a 3D vector, or None if no intersection.
    """

    # Convert inputs to numpy arrays for vector operations
    ray_origin = np.array(ray_origin)
    ray_direction = np.array(ray_direction)
    cylinder_center = np.array(cylinder_center)
    cylinder_axis = np.array(cylinder_axis)

    # Compute auxiliary vectors
    oc = ray_origin - cylinder_center
    a = np.dot(ray_direction, ray_direction) - np.dot(ray_direction, cylinder_axis)**2
    b = 2 * (np.dot(ray_direction, oc) - np.dot(ray_direction, cylinder_axis) * np.dot(oc, cylinder_axis))
    c = np.dot(oc, oc) - np.dot(oc, cylinder_axis)**2 - cylinder_radius**2
    
    
    # Compute discriminant
    discriminant = b**2 - 4 * a * c

    # If discriminant is negative, no intersection
    if discriminant < 0:
        return None

    # Compute t parameter (parameter along the ray direction)
    t1 = (-b + np.sqrt(discriminant)) / (2 * a)
    t2 = (-b - np.sqrt(discriminant)) / (2 * a)

    # Check if intersection is within ray segment
    if t1 < 0 and t2 < 0:
        return None

    # Select smallest positive t
    t = min(t1, t2) if t1 >= 0 and t2 >= 0 else max(t1, t2)

    # Compute intersection point
    intersection_point = ray_origin + t * ray_direction

    return intersection_point

def tests():
  m = Mirror(phi=90, theta=0) # einfacher Flip Mirror
  r0 = Ray()
  r1 = m.next_ray(r0)
  print(m)
  print(r0)
  print(r1)
  print()
  m.phi = 23
  m.theta = 34
  r2 = m.next_ray(r0)
  print(r2)
  m.draw()
  print(m.recompute_angles())
  return m, r0, r1, r2

def curved_mirror_test():
  cm = Curved_Mirror()
  r = Ray(pos = (-100, 0, 85))
  r2 = cm.next_ray(r)
  return cm, r,r2

if __name__ == "__main__":
  tests()