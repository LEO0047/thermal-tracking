# Builds models/starship.glb: the full Starship stack (Super Heavy booster + ship) from the
# procedural geometry in LEO0047/Starship-Mars-Simulator (src/components/three/starship.tsx).
# The exhaust plume is not in the file; the page draws it live so it can flicker.
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/build_starship.py -- starship.glb
#   base64 -i starship.glb -o models/starship.glb.txt      # 頁面讀的是 base64 文字版
#
# Blender is Z-up; the glTF exporter turns it into Y-up. 1 unit = 1 unit of the original scene
# (the ship is 0.9 wide), so the page frames it by its bounding box, not by real-world metres.
import bpy, bmesh, math, sys

out = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'starship.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, metal=.8, rough=.3, emit=None, strength=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m

def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)

M = {
    'steel':  mat('Steel | stainless', srgb('#c9d0d3'), .8, .3),
    'tiles':  mat('Heat shield | black tiles', srgb('#2a3236'), .2, .7),
    'nose':   mat('Steel | nose', srgb('#9ca4a6'), .9, .28),
    'weld':   mat('Steel | weld rings', srgb('#545b5b'), .8, .4),
    'flap':   mat('Metal | flaps', srgb('#464d50'), .82, .32),
    'dark':   mat('Metal | engine bay', srgb('#111719'), .5, .6),
    'bell':   mat('Metal | engine bells', srgb('#343c3e'), .9, .25),
    'fin':    mat('Metal | grid fins', srgb('#383c3e'), .8, .4),
    'chine':  mat('Metal | chines', srgb('#777f81'), .8, .3),
    'vent':   mat('Metal | hot-stage vents', srgb('#33383b'), .6, .5),
    # 引擎噴口內側：熱感裡最燙的一圈
    'throat': mat('Signal | engine throat', srgb('#ffb36b'), 0, .5, emit=srgb('#ffcf8a'), strength=9),
}

parts = []
def add(obj, m):
    obj.data.materials.clear(); obj.data.materials.append(M[m]); parts.append(obj); return obj

def cyl(r1, r2, h, z, x=0., y=0., seg=48, m='steel', caps=True):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r1, radius2=r2, depth=h, location=(x, y, z),
                                    end_fill_type='NGON' if caps else 'NOTHING')
    return add(bpy.context.object, m)

def box(sx, sy, sz, loc, rot_y=0., rot_z=0., m='flap'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, rot_y, rot_z))
    o = bpy.context.object; o.scale = (sx, sy, sz); return add(o, m)

def ring(r, z, minor, m='weld'):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=minor, major_segments=48, minor_segments=4, location=(0, 0, z))
    return add(bpy.context.object, m)

def lathe(profile, z0, seg=48, m='nose'):
    me = bpy.data.meshes.new('nose'); bm = bmesh.new(); rows = []
    for r, y in profile:
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), y + z0)) for k in range(seg)])
    for a, b in zip(rows, rows[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('nose', me); bpy.context.collection.objects.link(o)
    return add(o, m)

# ---------- Super Heavy booster ----------
cyl(.45, .45, 7.2, 3.6, m='steel')
cyl(.452, .452, .12, 7.26, m='vent', caps=False)                       # 熱分離環
for i in range(22): ring(.453, .2 + i * .31, .008)
for i in range(4):
    a = i * math.pi / 2
    box(.55, .5, .1, (math.cos(a) * .63, math.sin(a) * .63, 6.85), rot_z=a, m='fin')   # 柵格翼
    box(.07, .13, 1.8, (math.cos(a) * .47, math.sin(a) * .47, 1.2), rot_z=a, m='chine')
cyl(.44, .44, .06, -.01, m='dark')
for i in range(13):
    x, y = math.cos(i * 2.4) * .3, math.sin(i * 2.4) * .3
    cyl(.075, .055, .18, -.1, x, y, seg=16, m='bell')
    cyl(.06, .06, .012, -.195, x, y, seg=16, m='throat')

# ---------- Ship（疊在推進器上方 7.4） ----------
S = 7.4
# 機身一半不鏽鋼、一半黑色隔熱瓦：同一個圓柱，按面朝向分兩種材質
body = cyl(.45, .45, 3.6, S + 1.8, seg=64, m='steel')
body.data.materials.append(M['tiles'])
for p in body.data.polygons:
    if p.center.x < -1e-4: p.material_index = 1
lathe([(.45, 3.6), (.44, 3.95), (.37, 4.35), (.24, 4.72), (.1, 5.02), (0, 5.16)], S)
for i in range(13): ring(.451, S + .2 + i * .27, .006)
for side in (-1, 1):
    box(.48, .065, 1.3, (side * .57, 0, S + .74), rot_y=side * .16)    # 後襟翼
    box(.27, .055, .63, (side * .43, 0, S + 3.9), rot_y=-side * .22)  # 前襟翼
cyl(.44, .44, .09, S, m='dark')
for i in range(6):
    x, y = math.cos(i * math.pi / 3) * .27, math.sin(i * math.pi / 3) * .27
    cyl(.12, .07, .24, S - .14, x, y, seg=16, m='bell')

# 合併成一個物件，原點放在推進器底部中心
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.join()
ship = bpy.context.object; ship.name = 'Starship_Stack'
bpy.ops.object.shade_auto_smooth(angle=math.radians(35)) if hasattr(bpy.ops.object, 'shade_auto_smooth') else None

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True,
                          export_yup=True, export_materials='EXPORT')
print('wrote', out, 'tris', sum(len(p.vertices) - 2 for p in ship.data.polygons))
