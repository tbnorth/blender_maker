import bpy
import bmesh
from mathutils import Matrix, Vector

"""
exec(open(r"u:\repo\drifter\cad\ref.py").read())
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

def what(obj, text):
    print("%s\n%s" % (text, '%'*20))
    get_data = lambda: [
        str(obj.location),
        str(obj.matrix_world),
        str(obj.dimensions),
        ' '.join([str(obj.bound_box[i][j]) for i in range(8) for j in range(3)]),
        str(obj.data.vertices[0].co),
    ]
    ans0 = get_data()
    bpyscene.update()
    ans1 = get_data()
    if ans0 != ans1:
        print("BEFORE")
        print('\n'.join(ans0))
        print("AFTER")
    print('\n'.join(ans1))
    print('\n')
    
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

