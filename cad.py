from math import pi, radians

import bpy
import bmesh
from mathutils import Vector, Euler

"""
exec(open(r"u:\repo\drifter\cad\cad.py").read())
exec(open(r"/home/tbrown/t/Proj/blender_maker/cad.py").read())
"""

bpyscene = bpy.context.scene

FINAL = False  # use slower code to get details right
OFFSET = 0.00001  # offset of Freestyle off setting
DR = 7  # rotate drill bit by DR between holes to stop Freestyle drawing tangents
PARENTS = {}

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


def vmult(a, b):
    # https://blender.stackexchange.com/a/27759/13707
    return Vector(x * y for x, y in zip(a, b))


def ll_ur(obj):
    bpyscene.update()
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
        * _v(
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
        bpy.data.lamps,
        # bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)


def new_obj(name=None, parent=None):
    # Create an empty mesh and the object.
    if name is None:
        name = "Obj"
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpyscene.objects.link(obj)
    bpyscene.objects.active = obj
    if parent:
        PARENTS[obj.name] = parent.name
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
    bool_one.solver = 'CARVE'
    bpy.context.scene.objects.active = obj
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




def crange(obj, start, end, steps):
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
    return ans


def bind_parents():
    bpyscene.update()
    for k, v in PARENTS.items():
        if k in bpy.data.objects and v in bpy.data.objects:
            state = bpy.data.objects[k].matrix_world
            bpy.data.objects[k].parent = bpy.data.objects[v]
            bpy.data.objects[k].matrix_world = state

reset_blend()

pyb = new_obj("PyBoard")
obj_add(pyb)
size(pyb, (32, 41, 1))
translate(pyb, (-120, 0, 0))
# make ~toroid mount points, but don't attach yet, that would change bounds
cyl = new_obj()
obj_add(cyl, what='unit_cyl')
size(cyl, (3, 3, 1))
drill = replicate(cyl)
size(drill, (2, 2, 2))
do_bool(cyl, drill, 'DIFFERENCE')

size(drill, (0.75, 0.75, 2))  # to drill holes around the edge
# rather than diffing out each hole one at a time, merge all holes
# into `alt` and diff all at once, much cleaner mesh
alt = new_obj()
for coord in crange(pyb, (0.03, 0.03, 0.5), (0.97, 0.97, 0.5), (2, 16, 1)):
    move_to(drill, coord)
    if FINAL:  # slow
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    else:
        replicate(drill, "tmp_hole")
for n, coord in enumerate(
    crange(pyb, (0.03, 0.97, 0.5), (0.97, 0.97, 0.5), (12, 1, 1))
):
    if n in (0, 11):
        continue
    move_to(drill, coord)
    if FINAL:  # slow
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    else:
        replicate(drill, "tmp_hole")
do_bool(pyb, alt, "DIFFERENCE")
delete(alt)


# "chip" objects with ccb origin
chip = new_obj("CPU", parent=pyb)
obj_add(chip)
size(chip, (11, 11, 1))
origin(chip, 'ccb', offset=OFFSET)
move_to(chip, rel_coords(pyb, 'cct'))
base = replicate(chip, "reset")
move_to(base, rel_coords(pyb, (0.25, 0.25, 1)))
size(base, (3, 2, 1))
knob = replicate(base)
size(knob, (1.2, 1, 1))
move_to(knob, rel_coords(base, 'cct'))
do_bool(base, knob, "UNION")
delete(knob)
base = replicate(base, "user")
move_to(base, rel_coords(pyb, (0.45, 0.25, 1)))
for n, coord in enumerate(crange(pyb, (0.375, 0.02, 1), (0.375, 0.2, 1), (1, 4, 1))):
    led = replicate(chip, "LED")
    if n >= 2:
        rotate(led, (0, 0, 90))
    size(led, (0.5, 0.7, 0.5))
    move_to(led, coord)

# with cfb origin
chip = replicate(chip, "USB")
origin(chip, 'cfb', offset=OFFSET)
move_to(chip, rel_coords(pyb, (0.2, 0, 1)))
size(chip, (6, 4, 2))
chip = replicate(chip, "uSD")
move_to(chip, rel_coords(pyb, (0.6, 0, 1)))
size(chip, (11, 5, 2))

# now add the ~toroid mount points
origin(cyl, 'lcc', offset=-0.1)
move_to(cyl, rel_coords(pyb, (1, 0.05, 0.5)))
do_bool(pyb, cyl, 'UNION')
rotate(cyl, (0, 0, 180))
move_to(cyl, rel_coords(pyb, (0, 0.95, 0.5)))
do_bool(pyb, cyl, 'UNION')
delete(cyl)

cond = new_obj("Cond_controller")
obj_add(cond)
size(cond, (38, 65, 1))
translate(cond, (-60, 0, 0))
cap = new_obj("Cap.", parent=cond)
obj_add(cap, what='unit_cyl')
size(cap, (7, 7, 10))
origin(cap, 'ccb', offset=0.01)
move_to(cap, rel_coords(cond, (0.35, 0.225, 1)))
cap = replicate(cap)
scale(cap, (0.65, 0.65, 0.5))
move_to(cap, rel_coords(cond, (0.3, 0.12, 1)))

alt = new_obj()
size(drill, (3, 3, 3))
for coord in crange(cond, (0.075, 0.05, 0.5), (0.925, 0.95, 0.5), (2, 2, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
size(drill, (0.75, 0.75, 3))
for coord in crange(cond, (0.925, 0.35, 0.5), (0.925, 0.45, 0.5), (1, 3, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
    rotate(drill, (0, 0, DR))
for coord in crange(cond, (0.1, 0.9, 0.5), (0.45, 0.9, 0.5), (6, 1, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
    rotate(drill, (0, 0, DR))
do_bool(cond, alt, "DIFFERENCE")
delete(alt)

switch = new_obj("switch", parent=cond)
obj_add(switch)
size(switch, (5, 4, 2))
origin(switch, 'ccb', offset=0.01)
move_to(switch, rel_coords(cond, (0.15, 0.825, 1)))
knob = replicate(switch)
size(knob, (1, 0.5, 0.7))
for coord in crange(switch, (0.3, 0.3, 1), (0.3, 0.7, 1), (1, 2, 1)):
    move_to(knob, coord)
    do_bool(switch, knob, "UNION")
delete(knob)


gps = new_obj("GPS")
obj_add(gps)
size(gps, (34, 22, 1))
translate(gps, (-20, 0, 0))
ant = replicate(gps, "Ant", parent=gps)
size(ant, (16, 16, 5))
origin(ant, 'ccb', offset=0.01)
move_to(ant, rel_coords(gps, 'cct'))

alt = new_obj()
size(drill, (3, 3, 3))
for coord in crange(gps, (0.07, 0.1, 0.5), (0.07, 0.9, 0.5), (1, 2, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
size(drill, (0.75, 0.75, 3))
for coord in crange(gps, (0.95, 0.05, 0.5), (0.95, 0.95, 0.5), (1, 9, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
    rotate(drill, (0, 0, DR))
do_bool(gps, alt, "DIFFERENCE")
delete(alt)


adpt = new_obj("rad.adapt")
obj_add(adpt)
size(adpt, (26, 40, 1))
translate(adpt, (20, 0, 0))


size(drill, (0.75, 0.75, 3))
alt = new_obj()
for coord in crange(adpt, (0.07, 0.065, 0.5), (1-0.07, 0.065, 0.5), (10, 1, 1)):
    move_to(drill, coord)
    do_bool(alt, drill, "UNION")
    rotate(drill, (0, 0, DR))
do_bool(adpt, alt, "DIFFERENCE")
delete(alt)

blk = new_obj(name='socket', parent=adpt)
obj_add(blk)
size(blk, (2.5, 21, 7))
origin(blk, 'lfb', offset=OFFSET)
move_to(blk, rel_coords(adpt, (0, 0.35, 1)))
replicate(blk)
origin(blk, 'rfb', offset=OFFSET)
move_to(blk, rel_coords(adpt, (1, 0.35, 1)))

rad = new_obj('rad', parent=adpt)
obj_add(rad)
size(rad, (26, 35, 1))

origin(rad, 'cbb', offset=OFFSET)
move_to(rad, rel_coords(adpt, 'cbt')+_v(0, 0, blk.dimensions.z))
bvl = new_obj()
obj_add(bvl)
size(bvl, 40)
rotate(bvl, (0, 0, 45))
move_to(bvl, rel_coords(rad, 'ccc')+_v(0, -2.8, 0))
do_bool(rad, bvl, "INTERSECT")
delete(bvl)

# doesn't work to do this at end, rel_coords wrong then?
cap = new_obj("Cap.", parent=adpt)
obj_add(cap, what='unit_cyl')
size(cap, (3, 3, 6.7))
origin(cap, 'ccb', offset=0.01)
move_to(cap, rel_coords(adpt, (0.9, 1, 1)) - _v(0, 35, 0))

d = 2.5
led = new_obj(name='red', parent=adpt)
obj_add(led, what='unit_cyl')
size(led, (d, d, 4))
top = new_obj()
obj_add(top, what='uvsphere', u_segments=40, v_segments=40, diameter=1)
size(top, d-OFFSET)
move_to(top, rel_coords(led, 'cct'))
do_bool(led, top, "UNION")
delete(top)
origin(led, 'ccb', offset=OFFSET)
move_to(led, rel_coords(adpt, (0.075, 0.95, 1)))
grn = replicate(led, name='grn')
move_to(grn, rel_coords(adpt, (1-0.075, 0.95, 1)))



delete(drill)
bind_parents()
