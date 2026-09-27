import bpy, bmesh, math, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index('--')+1:]
OUT, RX, RY, RZ, SAMPLES, RES = argv[0], float(argv[1]), float(argv[2]), float(argv[3]), int(argv[4]), int(argv[5])
GRID = 260 if RES < 700 else 520

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'Filmic'; sc.view_settings.look = 'Medium High Contrast'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.012, 0.018, 0.045, 1)

# ---- materiales ----
def gold_face():
    m = bpy.data.materials.new('face'); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Metallic'].default_value = 0.88; b.inputs['Roughness'].default_value = 0.33
    b.inputs['Coat Weight'].default_value = 0.2
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.5, 0.5, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load('/home/claude/seed/color.png')
    img.extension = 'EXTEND'
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], img.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0; mix.inputs[7].default_value = (0.95, 0.62, 0.28, 1)
    nt.links.new(img.outputs['Color'], mix.inputs[6]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    return m
def gold_plain():
    m = bpy.data.materials.new('edge'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.75, 0.42, 0.12, 1); b.inputs['Metallic'].default_value = 0.9; b.inputs['Roughness'].default_value = 0.34
    return m
mface, medge = gold_face(), gold_plain()

tex = bpy.data.textures.new('h', 'IMAGE'); tex.image = bpy.data.images.load('/home/claude/seed/height.png'); tex.extension = 'EXTEND'
AMP, HALF = 0.05, 0.07

def face(z, flip):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID, y_subdivisions=GRID, size=2)
    g = bpy.context.active_object
    bm = bmesh.new(); bm.from_mesh(g.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.xy.length > 1.0], context='VERTS')
    bm.to_mesh(g.data); bm.free()
    d = g.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.texture_coords = 'LOCAL'; d.mid_level = 0; d.strength = AMP
    bpy.ops.object.modifier_apply(modifier='d')
    for p in g.data.polygons: p.use_smooth = True
    g.data.materials.append(mface)
    g.location.z = z
    if flip: g.rotation_euler.x = math.pi
    return g
top = face(HALF, False); bot = face(-HALF, True)
edge_h = AMP * 0.55
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=1.0, depth=2*(HALF+edge_h), end_fill_type='NOTHING')
side = bpy.context.active_object
for p in side.data.polygons: p.use_smooth = True
side.data.materials.append(medge)

coin = bpy.data.objects.new('coin', None); sc.collection.objects.link(coin)
for o in (top, bot, side): o.parent = coin
coin.rotation_euler = (math.radians(RX), math.radians(RY), math.radians(RZ))

cd = bpy.data.cameras.new('c'); cd.lens = 85
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -9.5, 0); cam.rotation_euler = (math.radians(90), 0, 0)
cd.sensor_fit = 'VERTICAL'; cd.angle_y = 2*math.atan(1.18/9.5)

def light(loc, e, col, size):
    d = bpy.data.lights.new('l', 'AREA'); d.energy = e; d.color = col; d.size = size
    o = bpy.data.objects.new('l', d); o.location = loc; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0,0,0)) - Vector(loc)).to_track_quat('-Z','Y').to_euler()
light((-4, -5, 4.5), 260, (1, .9, .75), 4)     # principal cálida
light((4.5, 1.5, 2), 260, (.55, .68, 1), 2.5)  # contra fría (reflejo azul de la página)
light((1, 4, 4), 320, (1, .85, .6), 3)         # contorno
light((0, -6, -3), 25, (1, .95, .9), 5)        # relleno bajo
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
