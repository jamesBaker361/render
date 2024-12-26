# given the scene, go through it and take a bunch of photos with the various projection matrix parameters
# save images and parameters to folder

import os
import random
import string

import bpy
import mathutils
from mathutils import Vector
from math import radians

base="C:\\Users\\jlbak\\render"

bpy.context.scene.render.resolution_x = 512  # Width
bpy.context.scene.render.resolution_y = 512  # Height
bpy.context.scene.render.resolution_percentage = 25  # Render at full resolution

def is_point_inside_bbox(point, obj):
    """
    Check if a given point is inside the bounding box of an object.
    
    :param point: The point to check (Vector or tuple).
    :param obj: The object whose bounding box is tested.
    :return: True if the point is inside the bounding box, False otherwise.
    """
    # Convert the point to a Vector if it's a tuple
    point = Vector(point) if not isinstance(point, Vector) else point

    # Get the world-space bounding box coordinates of the object
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Find the min and max points of the bounding box
    min_b = Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
    max_b = Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))

    # Check if the point is within the bounding box
    return (min_b.x <= point.x <= max_b.x and
            min_b.y <= point.y <= max_b.y and
            min_b.z <= point.z <= max_b.z)

def is_point_inside_object(point, objects=None):
    """
    Check if a point is inside any objects in the Blender scene.

    Args:
        point (tuple): A tuple (x, y, z) representing the point.
        objects (list): List of objects to check. Default is all mesh objects in the scene.

    Returns:
        bool: True if the point is inside any object, False otherwise.
    """
    if objects is None:
        objects = [obj for obj in bpy.context.scene.objects]

    point = mathutils.Vector(point)
    direction = mathutils.Vector((1, 0, 0))  # Arbitrary direction

    for obj in objects:
        if is_point_inside_bbox(point,obj):
            return True

    return False

class Cube:
    def __init__(self,x,y,z,h,w,l):
        self.x=x
        self.y=y
        self.z=z
        self.h=h
        self.w=w
        self.l=l

    def contains(self,x0,y0,z0):
        if self.z>z0 or self.z+self.l<z0:
            return False
        if self.x>x0 or self.x+self.h<x0:
            return False
        if self.y>y0 or self.y+self.w<y0:
            return False
        return True
    
cube_list=[
    Cube(0,0,0,5,5,5)
]

def get_valid_camera_coordinates():
    x_range=[0,10]
    y_range=[0,10]
    z_range=[0,10]
    x=random.uniform(*x_range)
    y=random.uniform(*y_range)
    z=random.uniform(*z_range)
    print(x,y,z)
    for cube in cube_list:
        if not cube.contains(x,y,z):
            return get_valid_camera_coordinates()
    return x,y,z

n_images=10
DIR=os.path.join(base,"image_dir")
os.makedirs(DIR,exist_ok=True)

CSV_DIR=os.path.join(base,"csv_dir")
os.makedirs(CSV_DIR,exist_ok=True)

camera = bpy.data.objects['Camera']  # Replace 'Camera' with your camera's name if different
camera.data.lens = 10

class LoopError(Exception):
    """A custom exception for specific errors."""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

random_id="room-"+''.join(random.choices(string.ascii_lowercase, k=5))
print(os.path.join(CSV_DIR, f"{random_id}.csv"))
with open(os.path.join(CSV_DIR, f"{random_id}.csv"),"w+") as csvfile:
    n=0
    while n<n_images:
        try:
            x,y,z=get_valid_camera_coordinates()
            camera.location=(x,y,z)
            for azimuthal in range(0,360,45):
                for polar in range(-90,91,45):
                    camera.rotation_euler=(radians(polar), 0, radians(azimuthal))
                    file_name=f"{random_id}_{n}.png"
                    bpy.context.scene.render.filepath = os.path.join(DIR, file_name)
                    
                    bpy.context.scene.render.image_settings.file_format = 'PNG'
                    

                    # Render and save the screenshot from the camera's perspective
                    bpy.ops.render.render(write_still=True)
                    csvfile.write(f"{file_name},{x},{y},{z},{polar},0,{azimuthal}")
                    print(f"{file_name},{x},{y},{z},{polar},0,{azimuthal}")
                    n+=1
                    if n>=n_images:
                        raise LoopError()
        except LoopError:
            print("all done")
