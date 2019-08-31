from pprint import pprint
from math import pi, radians

import bpy
import bmesh
from mathutils import Vector, Euler

"""
exec(open(r"u:\repo\drifter\cad\cad.py").read())
exec(open(r"/home/tbrown/t/Proj/misc_py/blender_maker/cad.py").read())

import sys
sys.path.insert(0, "/home/tbrown/t/Proj/misc_py/blender_maker")
"""

bpyscene = bpy.context.collection

OFFSET = 0.00001  # offset of Freestyle off setting
DR = 7  # rotate drill bit by DR between holes to stop Freestyle drawing tangents
PARENTS = {}
MATERIALS = ['White']

def _v(*args):
    if len(args) == 1:
        return Vector(*args)
    return Vector(args)


OREL = {
    # order these "clockwise from above" (or front, or right) for convenient
    # placement of parts at an angle, which will be rotated 90 degrees between
    # placements
    'bottom_corners': [_v(0, 0, 0), _v(0, 1, 0), _v(1, 1, 0), _v(1, 0, 0)],
    'top_corners': [_v(0, 0, 1), _v(0, 1, 1), _v(1, 1, 1), _v(1, 0, 1)],
    'xy_faces': [_v(0, 0.5, 0.5), _v(0.5, 1, 0.5), _v(1, 0.5, 0.5), _v(0.5, 0, 0.5)],
}
# create all combinations of left/center/right, front/center/back, and
# bottom/center/top, as 'lfb' (left, front, bottom), 'ccc', etc.
for x, rx in (('l', 0), ('c', 0.5), ('r', 1)):
    for y, ry in (('f', 0), ('c', 0.5), ('b', 1)):
        for z, rz in (('b', 0), ('c', 0.5), ('t', 1)):
            OREL[x + y + z] = _v(rx, ry, rz)

TEXT_ALIGN = {i[0]: i for i in
    ('LEFT', 'RIGHT', 'CENTER', 'TOP', 'BOTTOM')}

def vmult(a, b):
    # https://blender.stackexchange.com/a/27759/13707
    return Vector(x * y for x, y in zip(a, b))


def ll_ur(obj):
    bpy.context.view_layer.update()
    bbox = obj.bound_box
    return bbox[0][0], bbox[0][1], bbox[0][2], bbox[6][0], bbox[6][1], bbox[6][2]


def rel_coords(obj, orel):
    bbox = ll_ur(obj)
    if isinstance(orel, str):
        orel = OREL[orel]
    one = isinstance(orel[0], (int, float)) and len(orel) == 3
    if one:
        orel = [orel]

    ans = [
        obj.matrix_world
        @ _v(
            bbox[0] + (bbox[3] - bbox[0]) * i[0],
            bbox[1] + (bbox[4] - bbox[1]) * i[1],
            bbox[2] + (bbox[5] - bbox[2]) * i[2],
        )
        for i in orel
    ]
    return ans[0] if one else ans


def reset_blend():

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            pass
            # scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
        # bpy.data.objects,
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.lights,
        bpy.data.collections,
        # bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)


def new_obj(name=None, parent=None, what='mesh'):
    # Create an empty mesh and the object.
    if name is None:
        name = "Obj"
    if what == 'mesh':
        data = bpy.data.meshes.new(name)
    else:
        data = bpy.data.curves.new(name, type='FONT')
    obj = bpy.data.objects.new(name, data)
    bpyscene.objects.link(obj)
    # bpyscene.objects.active = obj
    bpy.context.view_layer.objects.active = obj
    if not isinstance(parent, (str, None.__class__)):
        parent = parent.name
    if parent:
        PARENTS[obj.name] = parent
    for material in MATERIALS:
        obj.data.materials.append(bpy.data.materials[material])
    return obj


def obj_add(obj, what='cube', **kwargs):
    if what == 'unit_cyl':
        return obj_add(
            obj,
            what='cone',
            diameter1=0.5,
            diameter2=0.5,
            depth=1,
            segments=40,
            cap_ends=True,
        )
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    getattr(bmesh.ops, 'create_' + what)(bm, **kwargs)
    # bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(obj.data)
    bm.free()


def do_bool(obj, other, op):
    # see also https://stackoverflow.com/a/14483593
    bool_one = obj.modifiers.new(type="BOOLEAN", name="snippy")
    bool_one.operation = op
    bool_one.object = other
    # bool_one.solver = 'CARVE'
    bpy.context.view_layer.objects.active = obj
    # bpy.context.render_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bool_one.name)


def translate(obj, vect):
    obj.location += Vector(vect)


def move_to(obj, vect):
    obj.location = Vector(vect)


def scale(obj, vect):
    if isinstance(vect, (int, float)):
        vect = Vector((vect, vect, vect))
    obj.scale = vmult(obj.scale, vect)


def rotate(obj, vect):
    # obj.matrix_world *= Euler(map(radians, vect), 'XYZ').to_matrix().to_4x4()
    eul = Euler(map(radians, vect), 'XYZ')
    old = obj.rotation_euler
    obj.rotation_euler = Euler((old[0] + eul[0], old[1] + eul[1], old[2] + eul[2]))


def replicate(obj, name=None, parent=None):
    """Drop a copy of the object"""
    rep = new_obj(name=(name or obj.name))
    rep.location = obj.location
    rep.rotation_euler = obj.rotation_euler
    rep.scale = obj.scale
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.to_mesh(rep.data)
    bm.free()
    if parent:
        PARENTS[rep.name] = parent.name
    elif obj.name in PARENTS:
        PARENTS[rep.name] = PARENTS[obj.name]
    return rep


def delete(obj):
    bpy.data.objects.remove(obj)


def test():
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


def size(obj, vect):
    if isinstance(vect, (int, float)):
        vect = _v(vect, vect, vect)
    obj.dimensions = vect


def origin(obj, pos=None, offset=None):
    if pos is None:
        pos = _v(0.5, 0.5, 0.5)
    if isinstance(pos, str):
        pos = OREL[pos]
        assert isinstance(pos[0], (int, float)) and len(pos) == 3
    if offset:
        if isinstance(offset, (int, float)):
            offset = [-offset if i == 0 else offset if i == 1 else 0 for i in pos]
        pos = pos + _v(offset)  # don't use +=, alters OREL
    minmax = []
    for dim in range(3):
        x = [i.co[dim] for i in obj.data.vertices]
        minmax.append((min(x), max(x)))
    delta = Vector(
        -(minmax[dim][0] + (minmax[dim][1] - minmax[dim][0]) * pos[dim])
        for dim in range(3)
    )
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    for vert in bm.verts:
        vert.co += delta
    bm.to_mesh(obj.data)
    bm.free()


def crange(obj, start, end, steps, enum=False):
    ans = []
    start = rel_coords(obj, start)
    end = rel_coords(obj, end)
    for i in range(steps[0]):
        for j in range(steps[1]):
            for k in range(steps[2]):
                ans.append(
                    _v(
                        start[0] + (end[0] - start[0]) * (i / max(1, steps[0] - 1)),
                        start[1] + (end[1] - start[1]) * (j / max(1, steps[1] - 1)),
                        start[2] + (end[2] - start[2]) * (k / max(1, steps[2] - 1)),
                    )
                )
                if enum:
                    ans[-1] = ((i, j, k), ans[-1])
    return ans


def bind_parents():
    bpy.context.view_layer.update()
    group = {}
    for v in set(PARENTS.values()):
        g = bpy.data.collections.new(v)
        group[v] = g.name  # catch .001 appended if there's a clash
        # add root (parent) object to group
        g.objects.link(bpy.data.objects[v])
    for k, v in PARENTS.items():
        if k in bpy.data.objects and v in bpy.data.objects:
            child = bpy.data.objects[k]
            parent = bpy.data.objects[v]
            state = child.matrix_world
            child.parent = parent
            child.matrix_world = state
            if child.type != 'FONT':
                bpy.data.collections[group[v]].objects.link(child)


