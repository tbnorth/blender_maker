"""just some probes for information"""

import bpy
import bmesh
from mathutils import Matrix, Vector

"""
exec(open(r"u:\repo\drifter\cad\ref.py").read())
"""

bpyscene = bpy.context.scene

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

def what(obj, text):
    print("## %s\n\n```" % text)
    get_data = lambda: '\n'.join([
        'LOC:'+str(obj.location),
        'WLD:'+str(obj.matrix_world),
        'DIM:'+str(obj.dimensions),
        'BBX:'+' '.join([str(obj.bound_box[i][j]) for i in range(4) for j in range(3)]),
        '    '+' '.join([str(obj.bound_box[i][j]) for i in range(4,8) for j in range(3)]),
        'CO0:'+str(obj.data.vertices[0].co),
    ]).split('\n')
    ans0 = get_data()
    bpyscene.update()
    ans1 = get_data()
    for t0, t1 in zip(ans0, ans1):
        if t0.split() == t1.split():  # ignore whitespace differences
            print('  '+t0)
        else:
            print('- '+t0)
            print('+ '+t1)
    print("```\n")

reset_blend()
basic_cube = new_obj()
obj_add(basic_cube)

what(basic_cube, 'Intial')
basic_cube.location -= Vector((0.25, 0, 0))
what(basic_cube, 'Location - 0.25')
basic_cube.matrix_world *= Matrix.Translation(Vector((-0.25, 0, 0)))
what(basic_cube, 'matrix_world - 0.25')
basic_cube.data.vertices[0].co -= Vector((0.25, 0, 0))
what(basic_cube, 'vert 0 - 0.25')

