import bpy, bmesh, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--')+1:]
PIECE, OUT, YAW = argv[0], argv[1], float(argv[2])
SAMPLES = int(argv[3]) if len(argv) > 3 else 160

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False
sc.render.film_transparent = True
sc.render.resolution_x = 900
sc.render.resolution_y = 1200
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [x.identifier for x in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'

world = bpy.data.worlds.new('w'); sc.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.006, 0.012, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0

mat = bpy.data.materials.new('navy'); mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.028, 0.055, 0.14, 1)
bsdf.inputs['Roughness'].default_value = 0.32
bsdf.inputs['Coat Weight'].default_value = 0.35
bsdf.inputs['Coat Roughness'].default_value = 0.15

def lathe(name, prof, steps=64):
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i+1])) for i in range(len(vs)-1)]
    bmesh.ops.spin(bm, geom=vs+es, cent=(0,0,0), axis=(0,0,1), angle=2*math.pi, steps=steps)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(40)
    return ob

def box(loc, size, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    b = bpy.context.active_object; b.scale = size; return b

def cut(target, cutter):
    m = target.modifiers.new('b', 'BOOLEAN'); m.object = cutter; m.operation = 'DIFFERENCE'; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier='b')
    bpy.data.objects.remove(cutter)

def base_profile(top):
    return [(0,0),(0.70,0),(0.72,0.03),(0.72,0.13),(0.67,0.17),(0.59,0.20),(0.59,0.26),(0.54,0.29)] + top

objs = []
if PIECE == 'pawn':
    prof = base_profile([(0.52,0.36),(0.40,0.46),(0.30,0.70),(0.26,0.98),(0.46,1.04),(0.47,1.10),(0.30,1.14),(0.26,1.18)])
    body = lathe('pawn', prof)
    head = lathe('head', [(0, 1.14)] + [(0.40*math.sin(a/20*math.pi), 1.52-0.40*math.cos(a/20*math.pi)) for a in range(1, 21)], 64)
    objs = [body, head]; H = 1.95
elif PIECE == 'rook':
    prof = base_profile([(0.56,0.36),(0.48,0.48),(0.44,1.20),(0.56,1.30),(0.62,1.36),(0.62,1.76),(0.46,1.76),(0.46,1.62),(0,1.62)])
    body = lathe('rook', prof)
    for i in range(4):
        a = i*math.pi/4
        cut(body, box((0,0,1.74), (0.9, 0.09, 0.14), (0,0,a)))
    objs = [body]; H = 2.15
elif PIECE == 'bishop':
    prof = base_profile([(0.50,0.36),(0.38,0.50),(0.26,0.98),(0.44,1.04),(0.44,1.10),(0.28,1.14)])
    mit = [(0.28,1.14)] + [(0.36*math.sin(t)+0.0*t, 1.44-0.32*math.cos(t)*1.0 if t<math.pi/2 else 1.44+0.62*(t-math.pi/2)/(math.pi/2)) for t in [x/12*math.pi for x in range(1,13)]]
    mit = [(0.28,1.14),(0.34,1.22),(0.38,1.36),(0.36,1.52),(0.28,1.68),(0.16,1.82),(0.06,1.88),(0.10,1.92),(0.12,1.97),(0.08,2.02),(0,2.04)]
    body = lathe('bishop', prof + mit[1:])
    cut(body, box((0.18,0,1.62), (0.5, 0.6, 0.035), (0, math.radians(-38), 0)))
    objs = [body]; H = 2.1
elif PIECE == 'knight':
    prof = [(0,0),(0.70,0),(0.72,0.03),(0.72,0.13),(0.67,0.17),(0.57,0.21),(0.46,0.30),(0.40,0.46),(0.45,0.52),(0.47,0.59),(0.41,0.65),(0.36,0.71),(0,0.71)]
    body = lathe('kbase', prof)
    pts = [(-0.38,0.68),(0.30,0.68),(0.28,0.86),(0.14,1.04),(0.58,1.14),(0.70,1.30),(0.62,1.42),(0.34,1.58),(0.32,1.84),(0.16,1.74),(0.02,1.90),(-0.14,1.82),(-0.36,1.62),(-0.47,1.28),(-0.45,0.96)]
    me = bpy.data.meshes.new('head'); head = bpy.data.objects.new('head', me); sc.collection.objects.link(head)
    bm = bmesh.new()
    t = 0.21
    f1 = [bm.verts.new((x, -t, z)) for x, z in pts]
    f2 = [bm.verts.new((x, t, z)) for x, z in pts]
    bm.faces.new(f1[::-1]); bm.faces.new(f2)
    n = len(pts)
    for i in range(n):
        j = (i+1) % n
        bm.faces.new((f1[i], f1[j], f2[j], f2[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    bv = head.modifiers.new('bv', 'BEVEL'); bv.width = 0.09; bv.segments = 1; bv.limit_method = 'NONE'
    # narrower muzzle: taper toward front
    for v in me.vertices:
        f = max(0.0, (v.co.x - 0.1)) * 0.55
        v.co.y *= (1 - f)
    for p_ in me.polygons: p_.use_smooth = False
    objs = [body, head]; H = 2.0
elif PIECE == 'queen':
    prof = base_profile([(0.52,0.36),(0.40,0.48),(0.28,1.10),(0.46,1.16),(0.46,1.22),(0.30,1.26),(0.34,1.40),(0.46,1.62),(0.52,1.72),(0.40,1.75),(0.22,1.80),(0.10,1.86),(0,1.87)])
    body = lathe('queen', prof)
    for i in range(9):
        a = i*2*math.pi/9
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, location=(0.53*math.cos(a), 0.53*math.sin(a), 1.76))
        cut(body, bpy.context.active_object)
    ball = lathe('ball', [(0,1.84)] + [(0.11*math.sin(k/16*math.pi), 1.95-0.11*math.cos(k/16*math.pi)) for k in range(1,17)])
    objs = [body, ball]; H = 2.15
elif PIECE == 'king':
    prof = base_profile([(0.52,0.36),(0.40,0.48),(0.30,1.12),(0.48,1.18),(0.48,1.24),(0.32,1.28),(0.36,1.44),(0.45,1.64),(0.43,1.72),(0.24,1.76),(0.12,1.80),(0,1.81)])
    body = lathe('king', prof)
    v = box((0,0,2.00),(0.055,0.055,0.20)); h = box((0,0,2.04),(0.15,0.055,0.05))
    objs = [body, v, h]; H = 2.3
elif PIECE == 'knight2':
    import numpy as np
    prof = [(0,0),(0.72,0),(0.74,0.03),(0.74,0.12),(0.70,0.16),(0.62,0.19),(0.60,0.24),(0.54,0.27),(0.50,0.34),(0.47,0.40),(0.52,0.45),(0.54,0.51),(0.50,0.56),(0.44,0.60),(0.44,0.66),(0.40,0.70),(0,0.70)]
    body = lathe('kbase', prof)
    pts = [(-0.40,0.62),(0.34,0.62),(0.42,0.78),(0.44,0.95),(0.37,1.08),(0.31,1.14),(0.36,1.22),(0.50,1.25),(0.66,1.24),(0.79,1.21),(0.88,1.25),(0.91,1.33),(0.87,1.42),(0.73,1.52),(0.57,1.64),(0.45,1.76),(0.40,1.87),(0.36,1.99),(0.30,2.13),(0.22,2.01),(0.14,1.98),(-0.02,1.94),(-0.22,1.84),(-0.38,1.66),(-0.48,1.44),(-0.53,1.18),(-0.50,0.90)]
    me = bpy.data.meshes.new('head'); head = bpy.data.objects.new('head', me); sc.collection.objects.link(head)
    bm = bmesh.new()
    f1 = [bm.verts.new((x, -0.3, z)) for x, z in pts]
    f2 = [bm.verts.new((x, 0.3, z)) for x, z in pts]
    bm.faces.new(f1[::-1]); bm.faces.new(f2)
    n = len(pts)
    for i in range(n):
        j = (i+1) % n
        bm.faces.new((f1[i], f1[j], f2[j], f2[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    bpy.context.view_layer.objects.active = head
    rm = head.modifiers.new('rm', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.014
    bpy.ops.object.modifier_apply(modifier='rm')
    P = np.array(pts); A = P; B = np.roll(P, -1, axis=0)
    co = np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co', co); co = co.reshape(-1,3)
    Q = co[:, [0,2]]
    AB = B - A
    tt = np.clip(((Q[:,None,:]-A[None])*AB[None]).sum(-1) / (AB**2).sum(-1)[None], 0, 1)
    proj = A[None] + tt[...,None]*AB[None]
    d = np.sqrt(((Q[:,None,:]-proj)**2).sum(-1)).min(1)
    x, z = Q[:,0], Q[:,1]
    cl = lambda v: np.clip(v, 0, 1)
    T = 0.28 - 0.11*cl((x-0.30)/0.55) - 0.12*cl((z-1.88)/0.22) - 0.05*cl((0.9-z)/0.3)
    prof_f = 0.30 + 0.70*np.sqrt(cl(d/0.16))
    co[:,1] = np.sign(co[:,1]) * np.abs(co[:,1])/0.3 * T * prof_f
    me.vertices.foreach_set('co', co.ravel()); me.update()
    sm = head.modifiers.new('sm', 'SMOOTH'); sm.factor = 0.8; sm.iterations = 10
    bpy.ops.object.modifier_apply(modifier='sm')
    def surf_y(px, pz):
        q = np.array([px, pz]); tt_ = np.clip(((q-A)*AB).sum(-1)/(AB**2).sum(-1), 0, 1)
        dd = np.sqrt(((q-(A+tt_[:,None]*AB))**2).sum(-1)).min()
        T_ = 0.28 - 0.11*min(max((px-0.30)/0.55,0),1) - 0.12*min(max((pz-1.88)/0.22,0),1)
        return T_*(0.30+0.70*math.sqrt(min(dd/0.16,1)))
    def sphere(loc, r, sy=1.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
        o = bpy.context.active_object; o.scale = (1.25, sy, 1.0); return o
    for sgn in (-1, 1):
        cut(head, sphere((0.47, sgn*(surf_y(0.47,1.67)+0.022), 1.67), 0.052, 0.8))   # ojo hundido
        cut(head, sphere((0.83, sgn*(surf_y(0.83,1.37)+0.018), 1.37), 0.036, 0.8))   # ollar
    cut(head, box((0.30, 0, 2.10), (0.10, 0.028, 0.10)))                              # separa las dos orejas
    cut(head, box((0.80, 0, 1.285), (0.11, 0.4, 0.011), (0, math.radians(8), 0)))    # boca
    mane = [(-0.04,1.92,-12),(-0.17,1.86,-25),(-0.29,1.76,-38),(-0.38,1.64,-50),(-0.45,1.50,-62),(-0.50,1.35,-72),(-0.52,1.20,-82),(-0.52,1.05,-90)]
    for mx, mz, ang in mane:
        a_ = math.radians(ang)
        c = box((mx, 0, mz), (0.13, 0.4, 0.016), (0, a_+math.pi/2, 0))
        cut(head, c)
    for p_ in me.polygons: p_.use_smooth = True
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(60)
    objs = [body, head]; H = 2.2

for o in objs:
    o.data.materials.append(mat)
    o.rotation_euler[2] = math.radians(YAW)

# camera
cam_d = bpy.data.cameras.new('c'); cam_d.lens = 70
cam = bpy.data.objects.new('c', cam_d); sc.collection.objects.link(cam); sc.camera = cam
target = Vector((0, 0, H*0.5))
cam.location = Vector((0, -7.2, H*0.5 + 0.9))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_d.sensor_fit = 'VERTICAL'
cam_d.angle_y = 2*math.atan((H*0.62)/ (target - cam.location).length)

def light(name, kind, loc, energy, color, size=1.0):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.size = size
    o = bpy.data.objects.new(name, d); o.location = loc
    o.rotation_euler = (target - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(o)

light('key', 'AREA', (-3.5, -3.0, 4.0), 130, (0.55, 0.68, 1.0), 2.5)   # frío, arriba-izq
light('rim', 'AREA', (3.2, 2.8, 2.6), 650, (0.40, 0.55, 1.0), 1.2)     # contorno azul
light('warm', 'AREA', (-3.0, 2.6, 1.6), 380, (1.0, 0.66, 0.34), 1.0)   # filo dorado de marca
light('fill', 'AREA', (0, -4, -0.5), 18, (0.4, 0.5, 0.9), 4)

sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
