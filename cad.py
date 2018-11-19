import bpy
import bmesh
from mathutils import Matrix

"""
exec(open(r"u:\repo\drifter\cad\cad.py").read())
"""

bpyscene = bpy.context.scene

OREL = {
    'bottom_corners': [
        (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0),
    ],
}   

def rel_coords(obj, orel):
    return [
        (obj.location.x + i[0]*obj.dimensions.x,     
         obj.location.y + i[1]*obj.dimensions.y,     
         obj.location.z + i[2]*obj.dimensions.z)
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

def clip_with(obj, clip):
    # see also https://stackoverflow.com/a/14483593
    bool_one = obj.modifiers.new(type="BOOLEAN", name="snippy")
    bool_one.operation = "DIFFERENCE"
    bool_one.object = clip
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bool_one.name)    

def translate(obj, vect):
    obj.matrix_world *= Matrix.Translation(vect)

reset_blend()
basic_cube = new_obj()
obj_add(basic_cube)

basic_cube2 = new_obj()
obj_add(basic_cube2)

translate(basic_cube2, (-0.5, -0.5, -0.5))

clip_with(basic_cube, basic_cube2)

print(rel_coords(basic_cube, 'bottom_corners'))

