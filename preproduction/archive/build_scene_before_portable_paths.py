"""Build the complete editable Valentine fan scene from local materials and Arthur.

Use a separate Blender process with --factory-startup and --disable-autoexec.
Original assets and the foreground Blender document are never overwritten.
"""
from pathlib import Path
import hashlib
import json
import math
import random
import sys
import time

import bpy
from mathutils import Matrix, Vector

SCRIPTS=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPTS))
from geometry import MeshBatch, collection, transform, text, instance, curve
from materials import palette
from architecture import storefront, keanes_construction, bank, chapel, roof
from props import make_library, dress_building, telegraph, fences
from landscape import road, terrain, vegetation, ground_height

ROOT=SCRIPTS.parent
SOURCE=ROOT.parent/"artur/source/ArthurMorgan.glb"
BLEND=ROOT/"Valentine_Fan_Recreation.blend"
START=time.monotonic()
random.seed(1899)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name="Valentine / after the rain"
scene.unit_settings.system="METRIC"
scene.unit_settings.scale_length=1
scene["project_type"]="Fan-made environment reconstruction"
scene["reference_scope"]="Smithfields, Worths, Keanes construction and Saints facade cues follow in-game captures. Measurements, rear geometry, peripheral lots and dressing are interpretations."
scene["asset_credit"]="Ground and timber scans: Poly Haven (CC0). Arthur: user-provided GLB; provenance unspecified. Building meshes and props created for this scene."


def phase(message):
    print(f"PHASE {time.monotonic()-START:.1f}s / {message}",flush=True)


phase("materials")
m=palette()
font_path=Path("/System/Library/Fonts/Supplemental/SuperClarendon.ttc")
font=bpy.data.fonts.load(str(font_path))
worldcol=collection("VALENTINE / town environment")
buildings=collection("04 / Main street architecture",worldcol)
dress=collection("05 / Street furniture and signs",worldcol)
lib=make_library(m,worldcol)

phase("reference-led north side")
entries=[]
entries.append(storefront("Smithfield's Saloon",0,0,12.0,11.2,6.25,m,buildings,font,"red",hero=True))
worth=storefront("Worth's General Store",-11.25,.05,9.2,12.0,6.65,m,buildings,font,"grey","WORTH'S","GENERAL STORE")
entries.append(worth)
text("Worths / sign band","GENERAL STORE",(0,-.13,5.77),8.7,.62,m["letter"],worth["collection"],worth["matrix"],font)
for px,word in [(-2.8,"PROVISIONS"),(2.7,"CLOTH\nLINEN")]:
    text("Worths / product lettering",word,(px,-.15,4.55),2.4,.32,m["letter"],worth["collection"],worth["matrix"],font)
entries.append(keanes_construction(12.0,.2,m,buildings,font))
entries.append(storefront("Valentine Doctor",23.0,.30,7.2,10.4,4.15,m,buildings,font,"grey","DOCTOR","TONICS  •  MEDICINES"))
entries.append(storefront("Sheriff's Office",32.4,.62,9.4,11.0,4.75,m,buildings,font,"darkwood","SHERIFF","VALENTINE  •  NEW HANOVER"))
entries.append(storefront("Farrier and smithy",-33.0,.80,12.0,12.4,4.1,m,buildings,font,"darkwood","FARRIER","HORSES SHOD  •  WAGON REPAIRS"))

phase("south side hotel, bank and shops")
hotel=storefront("Saints Hotel",-15.1,-27.5,13.8,15.5,6.55,m,buildings,font,"cream","SAINTS HOTEL","ROOMS  •  BATHS  •  LODGING",math.pi,"hotel")
entries.append(hotel)
entries.append(bank(.1,-27.3,m,buildings,font))
entries.append(storefront("Smith and Mackey",11.6,-27.0,8.5,10.3,4.8,m,buildings,font,"blue","SMITH & MACKEY","ATTORNEYS AT LAW",math.pi))
entries.append(storefront("Dalton Gunsmith",23.0,-26.6,9.0,11.2,5.25,m,buildings,font,"green","GUNSMITH","DALTON  •  ARMS & AMMUNITION",math.pi))
entries.append(storefront("Tailor and dry goods",34.3,-26.3,8.3,10,4.5,m,buildings,font,"grey","DRY GOODS","CLOTHING & BOOTS",math.pi))

# The hotel has a lower side annex and an exterior stair, unlike the saloon.
annex=MeshBatch("Saints Hotel / annex and exterior stair",hotel["collection"],hotel["matrix"])
annex.box((-8.8,5.4,1.8),(3.9,8.0,3.0),m["cream"])
annex.box((-8.8,5.4,3.36),(4.3,8.45,.14),m["roof"])
for i in range(15):
    annex.box((7.82,2+i*.24,.6+i*.18),(1.20,.28,.14),m["grey"])
for side in [-1,1]: annex.beam((7.82+side*.60,2,.98),(7.82+side*.60,5.5,3.60),.07,m["trim"])
annex.finish(.007)

# Unfinished lot to the west, visible framing and stacked planks.
lot=collection("Construction lot / inferred structural dressing",buildings)
b=MeshBatch("Construction / frame and timber pile",lot)
for x in [-24.5,-21,-17.5]:
    for y in [1,5,9]:
        b.box((x,y,2.2),(.16,.18,4.4),m["wood"])
        if y<9: b.beam((x,y,4.3),(x,y+4,4.3),.16,m["wood"])
for y in [1,5,9]: b.beam((-24.5,y,4.3),(-17.5,y,4.3),.16,m["wood"])
for i in range(24):
    b.box((-21.8+(i%5)*.15,-.45, .12+(i//5)*.105),(5.4,.14,.09),m["wood"])
b.beam((-24.5,1,.2),(-17.5,1,4.25),.12,m["grey"])
b.finish(.009)

phase("town periphery and railroad")
entries.append(storefront("Valentine railway depot",-42,-51.0,12,7.5,3.7,m,buildings,font,"cream","VALENTINE","PASSENGERS & FREIGHT",math.pi))
entries.append(storefront("Livestock office",57,20,11,13,4.4,m,buildings,font,"red","LIVESTOCK AUCTION","CATTLE  •  SHEEP  •  HORSES"))
entries.append(storefront("Livery stable",-53,22,13,16,5.2,m,buildings,font,"darkwood","LIVERY & FEED","STABLES",-.12))
entries.append(storefront("Keane's smaller saloon",54,-28,8.5,11,4.6,m,buildings,font,"green","KEANE'S SALOON","FINE LIQUOR",math.pi))
entries.append(storefront("House by the church",40,28,7,8.5,3.4,m,buildings,font,"cream","",angle=-.13))
entries.append(storefront("Town-edge lodging",-43,43,8,10,3.75,m,buildings,font,"grey","ROOMS",angle=.13))
church=chapel(59,41,m,buildings,font)
for obj in church.objects: obj.location.z+=.12

railcol=collection("Railroad / tracks and water tower",worldcol)
b=MeshBatch("Railway / sleepers and steel rails",railcol)
for x in range(-104,106):
    b.box((x*.82,-55,-.02),(.20,2.50,.15),m["darkwood"],tint=random.uniform(.6,1))
for y in [-54.27,-55.73]:
    b.box((0,y,.10),(178,.07,.13),m["iron"])
    b.box((0,y,.03),(178,.14,.045),m["iron"])
for x in [-60.8,-57.2]:
    for y in [-46.8,-43.2]: b.beam((x,y,0),(x*.98-1.2,y*.98-.9,6.4),.25,m["darkwood"])
for y in [-46.8,-43.2]:
    b.beam((-60.8,y,.3),(-57.2,y,5.8),.13,m["wood"])
    b.beam((-57.2,y,.3),(-60.8,y,5.8),.13,m["wood"])
b.cylinder((-59,-45,6.1),(-59,-45,9.5),2.35,m["wood"],36)
for z in [6.3,7.2,8.4,9.3]: b.ring((-59,-45,z),2.38,.08,.13,m["iron"],sides=40)
b.cylinder((-59,-45,9.6),(-59,-45,11.0),2.6,m["roof"],24,0)
b.finish(.006)

phase("landscape and foliage")
terrain(m,worldcol)
road(m,worldcol)
vegetation(m,worldcol)
fences(m,worldcol)

phase("street furniture")
for index,entry in enumerate(entries):
    if "House by" not in entry["name"]:
        dress_building(entry,lib,m,dress,font,index)
telegraph(m,worldcol)
for i,(x,y,a,s) in enumerate([(-29,-19.5,.02,1),(19,-19,.11,.94),(43,9,-.12,1.1),(-46,13,.15,.93)]):
    instance(lib["wagon"],f"Town / parked wagon {i+1}",(x,y,.03),dress,s,a)
    if i<2:
        for k in range(2): instance(lib["crate"],f"Wagon {i+1} / load {k+1}",(x+(k-.5)*.9,y,1.18),dress,.8,k*.1)

# Quiet human-scale details rather than oversized decorative props.
for i in range(15):
    x=random.uniform(-7,6)
    instance(lib["crate"],f"Freight and yard / crate {i+1}",(x+63,random.uniform(28,34),.1),dress,random.uniform(.7,1.3),random.uniform(-.2,.2))

phase("Arthur import and natural standing pose")
with SOURCE.open("rb") as stream: source_hash=hashlib.file_digest(stream,"sha256").hexdigest()
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
imported=set(bpy.data.objects)-before
charcol=collection("06 / Arthur Morgan",worldcol)
visible=[o for o in imported if any(not c.hide_render for c in o.users_collection)]
for obj in visible:
    for c in list(obj.users_collection): c.objects.unlink(obj)
    charcol.objects.link(obj)
arm=next(o for o in visible if o.type=="ARMATURE")
bpy.context.view_layer.update()
pose_log=[]
for side in ["L","R"]:
    upper=next(p for p in arm.pose.bones if p.name.endswith(f"SKEL_{side}_UpperArm"))
    fore=next(p for p in arm.pose.bones if p.name.endswith(f"SKEL_{side}_Forearm"))
    head=arm.matrix_world@upper.head
    tip=arm.matrix_world@fore.head
    sign=1 if head.x>0 else -1
    target=Vector((sign*.22,-.055,-1)).normalized()
    rotation=(tip-head).normalized().rotation_difference(target).to_matrix().to_4x4()
    change=arm.matrix_world.inverted()@Matrix.Translation(head)@rotation@Matrix.Translation(-head)@arm.matrix_world
    upper.matrix=change@upper.matrix
    bpy.context.view_layer.update()
    pose_log.append({"bone":upper.name,"intended_direction":list(target)})

root=bpy.data.objects.new("Arthur / placement",None)
charcol.objects.link(root)
for obj in visible:
    if obj.parent is None:
        world=obj.matrix_world.copy()
        obj.parent=root
        obj.matrix_world=world
root.location=(-4.9,-7.6,1.008+ground_height(-4.9,-7.6))
root.rotation_euler.z=-.20
# Different fabrics and metals should not all inherit the same flat gloss.
for mat in bpy.data.materials:
    if mat.node_tree and mat.name in ["Shirt","Pants","Boot","Hat","Satchel","Head","Hair"]:
        p=next((n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
        if p: p.inputs["Roughness"].default_value=.78 if mat.name in ["Shirt","Pants","Hat"] else .56

phase("cameras and natural light")
lightcol=collection("07 / Daylight and atmosphere")
world=bpy.data.worlds.new("High plains / clearing afternoon sky")
world.use_nodes=True
scene.world=world
nt=world.node_tree
sky=nt.nodes.new("ShaderNodeTexSky")
sky.sky_type="MULTIPLE_SCATTERING"
sky.sun_elevation=math.radians(27)
sky.sun_rotation=math.radians(212)
sky.altitude=.5
sky.air_density=1.2
sky.aerosol_density=2.2
sky.sun_disc=False
nt.links.new(sky.outputs["Color"],nt.nodes["Background"].inputs["Color"])
nt.nodes["Background"].inputs["Strength"].default_value=.17
sun_data=bpy.data.lights.new("Afternoon / soft sun","SUN")
sun_data.energy=3.0
sun_data.angle=math.radians(5)
sun_data.color=(1.0,.85,.68)
sun=bpy.data.objects.new(sun_data.name,sun_data)
lightcol.objects.link(sun)
sun.rotation_euler=Vector((50,80,-65)).to_track_quat("-Z","Y").to_euler()
fill_data=bpy.data.lights.new("Sky / broad street fill","AREA")
fill_data.energy=800
fill_data.shape="DISK"
fill_data.size=32
fill_data.color=(.88,.91,1)
fill=bpy.data.objects.new(fill_data.name,fill_data)
lightcol.objects.link(fill)
fill.location=(0,-10,19)

cameras=collection("08 / Composed cameras")
camera_specs=[
    ("01 / Smithfield hero",(-19.0,-22.5,2.85),(1.3,1.8,3.2),35),
    ("02 / Along the main street",(-43,-16.9,2.55),(12.5,-3.0,3.1),38),
    ("03 / Saints Hotel and bank",(9.0,-7.7,2.65),(-13.0,-28,3.3),35),
    ("04 / Town overview",(-39,-52,31),(4,-1,2.5),38),
    ("05 / Saloon entrance and Arthur",(-10.0,-15.8,2.1),(0,-.4,3.0),35),
]
for name,position,target,lens in camera_specs:
    data=bpy.data.cameras.new(name)
    data.lens=lens
    data.clip_start=.08
    data.clip_end=2000
    obj=bpy.data.objects.new(name,data)
    cameras.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    data.dof.use_dof=False
    marker=scene.timeline_markers.new(name,frame=int(name[:2]))
    marker.camera=obj
scene.frame_start=1
scene.frame_end=5
scene.frame_set(1)
scene.camera=bpy.data.objects["01 / Smithfield hero"]

scene.render.engine="CYCLES"
scene.cycles.samples=96
scene.cycles.use_denoising=True
scene.cycles.max_bounces=6
scene.cycles.diffuse_bounces=3
scene.cycles.glossy_bounces=3
scene.render.threads_mode="FIXED"
scene.render.threads=6
devices=[]
try:
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="METAL"
    prefs.get_devices()
    for device in prefs.devices:
        device.use=device.type=="METAL"
        devices.append({"name":device.name,"type":device.type,"enabled":device.use})
    scene.cycles.device="GPU" if any(d["type"]=="METAL" for d in devices) else "CPU"
except (TypeError,RuntimeError) as error:
    scene.cycles.device="CPU"
    devices=[{"fallback":str(error)}]
scene.render.resolution_x=2560
scene.render.resolution_y=1600
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.render.film_transparent=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=0
scene.render.filepath=str(ROOT/"renders/01_Smithfields_Main_Street.png")
scene.render.use_file_extension=True

# Set saved workspaces to a helpful camera view; originals stay organized in collections.
for obj in scene.objects: obj.select_set(False)
bpy.context.view_layer.objects.active=None
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_perspective="CAMERA"
            area.spaces.active.region_3d.view_camera_zoom=8
            area.spaces.active.shading.type="MATERIAL"
            area.spaces.active.shading.use_scene_world=True
            area.spaces.active.shading.use_scene_lights=True
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.show_region_ui=False
            area.spaces.active.clip_end=2000

phase("pack and save editable checkpoint")
bpy.context.view_layer.update()
# Font outlines become meshes to keep the deliverable independent of system fonts.
deps=bpy.context.evaluated_depsgraph_get()
for obj in list(bpy.data.objects):
    if obj.type=="FONT":
        old=obj.data
        mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
        replacement=bpy.data.objects.new(obj.name+" / outline",mesh)
        replacement.matrix_world=obj.matrix_world.copy()
        for coll in obj.users_collection: coll.objects.link(replacement)
        bpy.data.objects.remove(obj,do_unlink=True)
        if old.users==0:bpy.data.curves.remove(old)
bpy.ops.file.pack_all()
with SOURCE.open("rb") as stream: assert hashlib.file_digest(stream,"sha256").hexdigest()==source_hash
stats={
    "blender":bpy.app.version_string,"building_count":len(entries)+1,"objects":len(scene.objects),
    "mesh_objects":sum(o.type=="MESH" for o in scene.objects),"materials":len(bpy.data.materials),
    "mesh_triangles_before_modifiers":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=="MESH"),
    "packed_images":sum(bool(im.packed_file) for im in bpy.data.images),"render_device":scene.cycles.device,
    "devices":devices,"arthur_source_sha256":source_hash,"arthur_pose":pose_log,"build_seconds":round(time.monotonic()-START,1),
    "reference_fidelity":"Reference-led landmark facades; inferred dimensions, back walls, peripheral layout and prop placement.",
}
scene["building_count"]=len(entries)+1
scene["build_statistics"]=json.dumps(stats)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
(ROOT/"build_report.json").write_text(json.dumps(stats,indent=2)+"\n")
print("BUILD_COMPLETE",json.dumps(stats),flush=True)
