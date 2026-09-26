import bpy, bmesh, math, os, json
from mathutils import Vector

OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob

def material(name,color,metal,rough):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m

gold=material('Oro satinado',(.83,.47,.115),.78,.29)

def interpolate(points,steps=7):
    out=[]
    for i in range(len(points)-1):
        p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
        for j in range(steps):
            t=j/steps
            out.append([.5*(2*b+(c-a)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t) for a,b,c,d in zip(p0,p1,p2,p3)])
    return out+[points[-1]]

# Continuous rotational silhouette, before removal of the five diagonal gaps.
profile=[(.001,0),(1.58,0),(1.73,.055),(1.81,.145),(1.83,.23),(1.78,.32),(1.64,.405),
         (1.39,.52),(1.31,.60),(1.35,.67),(1.46,.78),(1.46,.86),(1.36,.95),(1.21,1.08),
         (1.04,1.23),(.90,1.40),(.78,1.60),(.68,1.82),(.60,2.08),(.56,2.38),(.55,2.7),
         (.55,2.98),(.565,3.16),(.62,3.30),(.76,3.48),(.89,3.65),(.94,3.78),(.85,3.97),
         (.845,4.20),(.86,4.48),(.81,4.75),(.69,5.00),(.50,5.21),(.27,5.35),(.001,5.395)]
N=160;rings=interpolate(profile);vertices=[];faces=[]
for r,z in rings:
    for j in range(N):
        a=2*math.pi*j/N;vertices.append((max(.00001,r)*math.cos(a),max(.00001,r)*math.sin(a),z))
for i in range(len(rings)-1):
    for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
faces.extend([tuple(reversed(range(N))),tuple((len(rings)-1)*N+j for j in range(N))])
source=bpy.data.meshes.new('Perfil de revolución');source.from_pydata(vertices,[],faces);source.update()

def clip(bm,slope,height,keep_above):
    # z = slope*x + height. Every cut is real geometry with a closed planar face.
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,
        plane_co=(0,0,height),plane_no=(-slope,0,1),clear_inner=keep_above,clear_outer=not keep_above)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:
        result=bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
        for face in result['faces']:face.smooth=False

# Six independently editable sections. Slopes and heights trace the supplied graphic.
specs=[('01 · Base',None,(.35,.873)),
       ('02 · Fuste inferior',(.35,1.21),(.77,1.946)),
       ('03 · Fuste superior',(.78,2.46),(.30,3.01)),
       ('04 · Anillo fino',(.33,3.235),(.32,3.422)),
       ('05 · Cabeza inferior',(.40,3.762),(.50,4.22)),
       ('06 · Corona esférica',(.55,4.725),None)]
model=[];checks=[]
collection=bpy.data.collections.new('PEÓN · Seis secciones');bpy.context.scene.collection.children.link(collection)
for name,lower,upper in specs:
    bm=bmesh.new();bm.from_mesh(source)
    for f in bm.faces:f.smooth=True
    if lower:clip(bm,*lower,True)
    if upper:clip(bm,*upper,False)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    checks.append({'piece':name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=False)})
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);me.materials.append(gold);model.append(ob)
    active(ob)
    bevel=ob.modifiers.new('Microbisel de los cortes','BEVEL');bevel.width=.012;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.40
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    norm=ob.modifiers.new('Normales de superficie','WEIGHTED_NORMAL');norm.keep_sharp=True;norm.weight=40
    bpy.ops.object.modifier_apply(modifier=norm.name)

height=max(v.co.z for ob in model for v in ob.data.vertices);S=.100/height
for ob in model:
    for v in ob.data.vertices:v.co*=S
    # The pivot of each separate slice is its own centre for later animation.
    active(ob);bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
    ob['section']=ob.name;ob['reference']='Peón dorado con cinco cortes diagonales'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'

def look(ob,where):ob.rotation_euler=(Vector(where)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=Vector((0,-18,6.0))*S)
cam=bpy.context.object;cam.name='Vista principal';cam.data.type='ORTHO';cam.data.ortho_scale=6.3*S;cam.data.clip_start=.001
look(cam,(0,0,2.66*S));scene.camera=cam
def area(name,loc,power,size,color):
    bpy.ops.object.light_add(type='AREA',location=Vector(loc)*S);o=bpy.context.object;o.name=name;o.data.energy=power*S*S;o.data.size=size*S;o.data.color=color;look(o,(0,0,2.7*S))
area('Softbox izquierdo',(-4,-5,8),1000,5,(1,.90,.72))
area('Softbox derecho',(5,-2,5),800,4,(.82,.9,1))
area('Reflejo trasero',(2,4,7),1400,3,(1,.87,.60))
area('Relleno frontal',(-1,-6,2),170,4,(1,1,1))
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.55,.55,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.render.filepath=os.path.join(OUT,'peon-dorado-preview.png')
active(model[0])
for ob in model:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'peon-dorado.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.obj_export(filepath=os.path.join(OUT,'peon-dorado.obj'),export_selected_objects=True,export_materials=True)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        sp=a.spaces.active;sp.region_3d.view_distance=.17;sp.region_3d.view_location=(0,0,.05)
        sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO';sp.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'peon-dorado.blend'))
stats={'height_mm':100,'sections':len(model),'diagonal_gaps':5,'polygons':sum(len(o.data.polygons) for o in model),'pre_bevel_topology':checks}
with open(os.path.join(OUT,'model-info.json'),'w',encoding='utf-8') as f:json.dump(stats,f,ensure_ascii=False,indent=2)
assert all(c['boundary_edges']==0 and c['nonmanifold_edges']==0 and c['volume']>0 for c in checks),checks
print('MODEL_VALIDATED',stats,flush=True)
bpy.ops.render.render(write_still=True)
print('COMPLETE',flush=True)
