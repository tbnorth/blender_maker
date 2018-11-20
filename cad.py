from math import pi, radians

import bpy
import bmesh
from mathutils import Matrix, Euler

"""
exec(open(r"u:\repo\drifter\cad\cad.py").read())
"""

bpyscene = bpy.context.scene

OREL = {
    # order these "clockwise from above" (or front, or right) for convenient
    # placement of parts at an angle, which will be rotated 90 degrees between
    # placements
    'bottom_corners': [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
    'top_corners': [(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)],
    'xy_faces': [(0, 0.5, 0.5), (0.5, 1, 0.5), (1, 0.5, 0.5), (0.5, 0, 0.5)],
}


def vmult(a, b):
    # https://blender.stackexchange.com/a/27759/13707
    return Vector(x * y for x, y in zip(a, b))


def ll_ur(obj):
    bbox = obj.bound_box
    return bbox[0][0], bbox[0][1], bbox[0][2], bbox[6][0], bbox[6][1], bbox[6][2]


def rel_coords(obj, orel):
    bpyscene.update()
    bbox = ll_ur(obj)
    return [
        (
            bbox[0] + (bbox[3] - bbox[0]) * i[0],
            bbox[1] + (bbox[4] - bbox[1]) * i[1],
            bbox[2] + (bbox[5] - bbox[2]) * i[2],
        )
        for i in OREL[orel]
    ]


def reset_blend():

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.lamps,
        bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)


def new_obj():
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('Basic_Cube')
    basic_cube = bpy.data.objects.new("Basic_Cube", mesh)
    bpyscene.objects.link(basic_cube)
    bpyscene.objects.active = basic_cube
    return basic_cube


def obj_add(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(obj.data)
    bm.free()


def do_bool(obj, other, op):
    # see also https://stackoverflow.com/a/14483593
    bool_one = obj.modifiers.new(type="BOOLEAN", name="snippy")
    bool_one.operation = op
    bool_one.object = other
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bool_one.name)
    bpyscene.update()


def translate(obj, vect):
    obj.location += Vector(vect)


def move_to(obj, vect):
    obj.location = Vector(vect)


def scale(obj, vect):
    if isinstance(vect, (int, float)):
        vect = Vector((vect, vect, vect))
    obj.scale = vmult(obj.scale, vect)
    bpyscene.update()

def rotate(obj, vect):
    # obj.matrix_world *= Euler(map(radians, vect), 'XYZ').to_matrix().to_4x4()
    eul = Euler(map(radians, vect), 'XYZ')
    old = obj.rotation_euler
    obj.rotation_euler = Euler((old[0]+eul[0], old[1]+eul[1], old[2]+eul[2]))



def replicate(obj):
    """Drop a copy of the object"""
    rep = new_obj()
    rep.location = obj.location
    rep.rotation_euler = obj.rotation_euler
    rep.scale = obj.scale
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.to_mesh(rep.data)
    bm.free()


def delete(obj):
    bpy.data.objects.remove(obj)


reset_blend()
basic_cube = new_obj()
obj_add(basic_cube)

basic_cube2 = new_obj()
obj_add(basic_cube2)

scale(basic_cube2, (0.2, 0.2, 0.5))

for corner in rel_coords(basic_cube, 'bottom_corners'):
    move_to(basic_cube2, corner)
    do_bool(basic_cube, basic_cube2, 'DIFFERENCE')

for corner in rel_coords(basic_cube, 'top_corners'):
    move_to(basic_cube2, corner)
    replicate(basic_cube2)

rotate(basic_cube2, (0, 90, 0))
for corner in rel_coords(basic_cube, 'xy_faces'):
    move_to(basic_cube2, corner)
    do_bool(basic_cube, basic_cube2, 'UNION')
    rotate(basic_cube2, (90, 0, 0))

rotate(basic_cube2, (-45, 0, 0))
for corner in rel_coords(basic_cube, 'top_corners'):
    move_to(basic_cube2, corner)
    replicate(basic_cube2)
    rotate(basic_cube2, (90, 0, 0))

delete(basic_cube2)

print(rel_coords(basic_cube, 'top_corners'))
