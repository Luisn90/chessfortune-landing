import bpy, bmesh, math, os, json
from mathutils import Vector

OUT='/home/claude/peon/lite'
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
N=72;rings=interpolate(profile,4);vertices=[];faces=[]
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
    bevel=ob.modifiers.new('Microbisel de los cortes','BEVEL');bevel.width=.012;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=.40
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    norm=ob.modifiers.new('Normales de superficie','WEIGHTED_NORMAL');norm.keep_sharp=True;norm.weight=40
    bpy.ops.object.modifier_apply(modifier=norm.name)

height=max(v.co.z for ob in model for v in ob.data.vertices);S=.100/height
for ob in model:
    for v in ob.data.vertices:v.co*=S
    # The pivot of each separate slice is its own centre for later animation.
    active(ob);bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
    ob['section']=ob.name;ob['reference']='Peón dorado con cinco cortes diagonales'

import os
os.makedirs(OUT,exist_ok=True)
active(model[0])
for ob in model: ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'pawn.glb'),export_format='GLB',use_selection=True,export_apply=True,export_materials='NONE',export_texcoords=False,export_normals=True)
print('POLYS',sum(len(o.data.polygons) for o in model))
