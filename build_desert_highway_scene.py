import bpy, os, math, urllib.request

scene_path = r'C:\Users\nearf\OneDrive\Desktop\forest_scene.blend'
car_blend = r'C:\Users\nearf\Downloads\free-porsche-911-carrera-4s\source\9e528d02fb594880b6f241f668d63bc0.blend'
tex_dir = r'C:\Users\nearf\Downloads\highway_textures'
os.makedirs(tex_dir, exist_ok=True)

# --- Start from clean scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# --- Download online textures (Poly Haven CC0) ---
urls = {
    'road_diff.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/asphalt_02/asphalt_02_diff_1k.jpg',
    'road_rough.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/asphalt_02/asphalt_02_rough_1k.jpg',
    'road_nor.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/asphalt_02/asphalt_02_nor_gl_1k.jpg',
    'sand_diff.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/sand_01/sand_01_diff_1k.jpg',
    'sand_rough.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/sand_01/sand_01_rough_1k.jpg',
    'sand_nor.jpg': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/sand_01/sand_01_nor_gl_1k.jpg',
}

for fn, url in urls.items():
    out = os.path.join(tex_dir, fn)
    if not os.path.exists(out):
        urllib.request.urlretrieve(url, out)

# --- Materials helper ---
def make_pbr_mat(name, diff_path, rough_path, nor_path, tile=(1.0, 1.0, 1.0)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in list(nodes):
        nodes.remove(n)

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    texcoord = nodes.new('ShaderNodeTexCoord')
    mapn = nodes.new('ShaderNodeMapping')
    mapn.inputs['Scale'].default_value[0] = tile[0]
    mapn.inputs['Scale'].default_value[1] = tile[1]
    mapn.inputs['Scale'].default_value[2] = tile[2]

    tex_diff = nodes.new('ShaderNodeTexImage')
    tex_diff.image = bpy.data.images.load(diff_path)

    tex_rough = nodes.new('ShaderNodeTexImage')
    tex_rough.image = bpy.data.images.load(rough_path)
    tex_rough.image.colorspace_settings.name = 'Non-Color'

    tex_nor = nodes.new('ShaderNodeTexImage')
    tex_nor.image = bpy.data.images.load(nor_path)
    tex_nor.image.colorspace_settings.name = 'Non-Color'
    normal_map = nodes.new('ShaderNodeNormalMap')

    links.new(texcoord.outputs['UV'], mapn.inputs['Vector'])
    links.new(mapn.outputs['Vector'], tex_diff.inputs['Vector'])
    links.new(mapn.outputs['Vector'], tex_rough.inputs['Vector'])
    links.new(mapn.outputs['Vector'], tex_nor.inputs['Vector'])
    links.new(tex_diff.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(tex_nor.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    return mat

# --- Geometry: desert + highway ---
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, 0))
desert = bpy.context.active_object
desert.name = 'Desert'

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
road = bpy.context.active_object
road.name = 'Highway'
road.scale = (8, 900, 1)  # width ~16m, length ~1800m

# lane markings via emissive strips
for x in (-2.7, 2.7):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 0.015))
    line = bpy.context.active_object
    line.scale = (0.12, 900, 1)
    line.name = f'LaneLine_{x}'
    m = bpy.data.materials.new(f'LaneMat_{x}')
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.94, 0.82, 0.35, 1)
    bsdf.inputs['Emission Color'].default_value = (0.94, 0.82, 0.35, 1)
    bsdf.inputs['Emission Strength'].default_value = 0.35
    line.data.materials.append(m)

road_mat = make_pbr_mat(
    'RoadMat',
    os.path.join(tex_dir, 'road_diff.jpg'),
    os.path.join(tex_dir, 'road_rough.jpg'),
    os.path.join(tex_dir, 'road_nor.jpg'),
    tile=(3.5, 280, 1.0)
)
road.data.materials.append(road_mat)

sand_mat = make_pbr_mat(
    'SandMat',
    os.path.join(tex_dir, 'sand_diff.jpg'),
    os.path.join(tex_dir, 'sand_rough.jpg'),
    os.path.join(tex_dir, 'sand_nor.jpg'),
    tile=(140, 140, 1.0)
)
desert.data.materials.append(sand_mat)

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(150, -200, 300))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.rotation_euler = (math.radians(50), math.radians(0), math.radians(25))

world = scene.world
if world is None:
    world = bpy.data.worlds.new('World')
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.66, 0.77, 1.0, 1)
    bg.inputs['Strength'].default_value = 1.2

# --- Import Porsche car ---
with bpy.data.libraries.load(car_blend, link=False) as (data_from, data_to):
    data_to.objects = data_from.objects

imported = [o for o in data_to.objects if o is not None]
for obj in imported:
    bpy.context.collection.objects.link(obj)

car_meshes = [o for o in imported if o.type == 'MESH']
root = bpy.data.objects.new('CarRoot', None)
bpy.context.collection.objects.link(root)
for obj in imported:
    if obj.parent is None:
        obj.parent = root

# scale to reasonable size
root.scale = (2.2, 2.2, 2.2)
root.location = (0, -780, 0.05)
root.rotation_euler = (0, 0, math.radians(90))  # face +Y

# Animate driving down highway
scene.frame_start = 1
scene.frame_end = 900
scene.render.fps = 30
root.keyframe_insert(data_path='location', frame=1)
root.location = (0, 780, 0.05)
root.keyframe_insert(data_path='location', frame=900)

# linear interpolation for constant speed
if root.animation_data and root.animation_data.action and hasattr(root.animation_data.action, 'fcurves'):
    for fc in root.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

# Camera follow shot
bpy.ops.object.camera_add(location=(0, -800, 2.2), rotation=(math.radians(88), 0, math.radians(90)))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 30

# Track to car
trk = cam.constraints.new(type='TRACK_TO')
trk.target = root
trk.track_axis = 'TRACK_NEGATIVE_Z'
trk.up_axis = 'UP_Y'

# parent camera to offset empty that follows car
follow = bpy.data.objects.new('CamFollow', None)
bpy.context.collection.objects.link(follow)
follow.location = (0, -800, 2.2)
cam.parent = follow

follow.keyframe_insert(data_path='location', frame=1)
follow.location = (0, 760, 2.2)
follow.keyframe_insert(data_path='location', frame=900)
if follow.animation_data and follow.animation_data.action and hasattr(follow.animation_data.action, 'fcurves'):
    for fc in follow.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

bpy.ops.wm.save_as_mainfile(filepath=scene_path)
print('Built desert highway scene with driving car:', scene_path)
