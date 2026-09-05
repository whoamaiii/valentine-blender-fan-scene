"""Reopen verification for the delivered scene, independent of the builder."""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(bpy.data.filepath).parent
scene=bpy.context.scene
errors=[]
required=["Smithfield's Saloon","Worth's General Store","Keane's / rooms and construction","Saints Hotel","Valentine Savings Bank","06 / Arthur Morgan"]
for name in required:
    if name not in bpy.data.collections:errors.append("Missing collection: "+name)
cameras=[obj for obj in scene.objects if obj.type=="CAMERA"]
if len(cameras)<5:errors.append("Missing review cameras")
images=[im for im in bpy.data.images if im.source=="FILE"]
for im in images:
    if not im.packed_file or min(im.size)<=0:errors.append("Texture unavailable: "+im.name)
meshes={obj.data for obj in scene.objects if obj.type=="MESH"}
nonfinite=[]
for mesh in meshes:
    if any(not math.isfinite(c) for v in mesh.vertices for c in v.co):nonfinite.append(mesh.name)
if nonfinite:errors.append("Non-finite geometry: "+str(nonfinite))
assert not errors,errors
source=root.parent/"artur/source/ArthurMorgan.glb"
with source.open("rb") as stream: source_hash=hashlib.file_digest(stream,"sha256").hexdigest()
build=json.loads((root/"build_report.json").read_text())
if source_hash!=build["arthur_source_sha256"]:errors.append("Arthur source changed")
deps=bpy.context.evaluated_depsgraph_get()
marker_checks=[]
for frame in range(1,6):
    scene.frame_set(frame)
    expected=next((c.name for c in cameras if c.name.startswith(f"{frame:02d} /")),None)
    actual=scene.camera.name
    marker_checks.append({"frame":frame,"camera":actual,"matches":actual==expected})
    if actual!=expected:errors.append(f"Camera selection failed at frame {frame}")
scene.frame_set(1)
road=bpy.data.objects["Main road / ruts, churn and puddle basins"]
water=bpy.data.objects["Street / shallow irregular rain puddles"]
surface=BVHTree.FromObject(road,deps)
edge_gaps=[]
for vertex in water.data.vertices:
    point=water.matrix_world@vertex.co
    hit,normal,index,distance=surface.ray_cast(point+Vector((0,0,1)),Vector((0,0,-1)),2)
    if hit is not None:edge_gaps.append(point.z-hit.z)
    else:errors.append("Puddle edge has no supporting road")
max_puddle_gap=max(edge_gaps,default=0)
if max_puddle_gap>.005:errors.append(f"Puddle edge floats above the road: {max_puddle_gap:.4f}m")
camera_rays=[]
for camera in cameras:
    direction=camera.matrix_world.to_quaternion()@Vector((0,0,-1))
    hit,loc,normal,index,obj,matrix=scene.ray_cast(deps,camera.location,direction,distance=1000)
    camera_rays.append({"camera":camera.name,"center_hit":obj.name if hit else "sky", "distance":round((loc-camera.location).length,3) if hit else None})
    if hit and (loc-camera.location).length<.35:errors.append("Camera occluded at near plane: "+camera.name)
arthur=[]
for obj in bpy.data.collections["06 / Arthur Morgan"].objects:
    if obj.type=="MESH":
        ev=obj.evaluated_get(deps)
        points=[ev.matrix_world@v.co for v in ev.data.vertices]
        arthur.extend(points)
character_bounds={"min":[min(v[a] for v in arthur) for a in range(3)],"max":[max(v[a] for v in arthur) for a in range(3)]}
if character_bounds["max"][2]-character_bounds["min"][2]>2.5:errors.append("Arthur pose bounding box has excessive height")
result={"status":"PASS" if not errors else "FAIL","blend":Path(bpy.data.filepath).name,"blender":bpy.app.version_string,
        "objects":len(scene.objects),"unique_meshes":len(meshes),"packed_image_count":len(images),"building_count":scene.get("building_count"),
        "camera_rays":camera_rays,"camera_markers":marker_checks,"max_puddle_edge_gap_m":max_puddle_gap,
        "arthur_bounds":character_bounds,"source_unchanged":source_hash==build["arthur_source_sha256"],"errors":errors}
(root/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
print("SCENE_VERIFICATION",json.dumps(result),flush=True)
assert not errors,errors
