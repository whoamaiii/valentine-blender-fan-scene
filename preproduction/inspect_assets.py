"""Rebuild the isolated asset review; source GLBs are never modified.

Run with Blender --background --factory-startup --disable-autoexec --python.
This is an inspection scene, not a recreation of Valentine.
"""
from pathlib import Path
import collections
import hashlib
import json
import struct

import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SOURCES = [
    ("Saloon asset review", ROOT / "saloon_with_textures.glb", "saloon"),
    ("Arthur asset review", ROOT / "artur/source/ArthurMorgan.glb", "arthur"),
]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def metadata(path):
    with path.open("rb") as f:
        magic, version, length = struct.unpack("<4sII", f.read(12))
        assert magic == b"glTF" and version == 2 and length == path.stat().st_size
        n, kind = struct.unpack("<II", f.read(8))
        assert kind == 0x4E4F534A
        return json.loads(f.read(n))


def aim(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def prepare_studio(scene, lo, hi):
    center = (lo + hi) / 2
    span = max(hi - lo)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 6
    scene.render.resolution_x = 900
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new(scene.name + " world")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.18, 0.20, 0.24, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scene.view_settings.view_transform = "AgX"
    studio = bpy.data.collections.new(scene.name + " lighting")
    scene.collection.children.link(studio)
    for name, offset, power, color in [
        ("Key", (0.2, -0.8, 1.4), 160, (1.0, 0.9, 0.8)),
        ("Fill", (-1.0, 0.2, 0.8), 100, (0.8, 0.88, 1.0)),
        ("Rim", (0.7, 1.0, 1.0), 130, (1.0, 1.0, 1.0)),
    ]:
        data = bpy.data.lights.new(scene.name + " " + name, "AREA")
        data.energy = power * span * span
        data.shape = "DISK"
        data.size = span
        data.color = color
        obj = bpy.data.objects.new(data.name, data)
        studio.objects.link(obj)
        obj.location = center + Vector(offset) * span
        aim(obj, center)
    camera = bpy.data.objects.new(scene.name + " camera", bpy.data.cameras.new(scene.name + " camera"))
    studio.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = span * 1.95
    camera.data.clip_start = span / 1000
    camera.data.clip_end = span * 100
    scene.camera = camera
    return camera, center, span


bpy.ops.wm.read_factory_settings(use_empty=True)
report = {"blender_version": bpy.app.version_string, "purpose": "Asset inspection only; not Valentine reconstruction", "assets": []}
for index, (scene_name, path, stem) in enumerate(SOURCES):
    before = digest(path)
    gltf = metadata(path)
    scene = bpy.context.scene if index == 0 else bpy.data.scenes.new(scene_name)
    scene.name = scene_name
    bpy.context.window.scene = scene
    previous = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = set(bpy.data.objects) - previous
    # The importer adds an Icosphere in a hidden collection for bone shapes.
    # It is a rig display helper, not character geometry or a size reference.
    meshes = [obj for obj in imported if obj.type == "MESH"
              and not obj.hide_render and any(not c.hide_render for c in obj.users_collection)]
    armatures = [obj for obj in imported if obj.type == "ARMATURE"]
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(v) for obj in meshes for v in obj.bound_box]
    lo = Vector([min(v[a] for v in corners) for a in range(3)])
    hi = Vector([max(v[a] for v in corners) for a in range(3)])
    images = {node.image for obj in meshes for mat in obj.data.materials if mat and mat.node_tree
              for node in mat.node_tree.nodes if node.type == "TEX_IMAGE" and node.image}
    tris = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        tris += len(obj.data.loop_triangles)
    item = {
        "source": str(path.relative_to(ROOT)), "sha256_before": before,
        "bytes": path.stat().st_size, "source_metadata": gltf.get("asset"),
        "objects": len(imported), "meshes": len(meshes), "triangles": tris,
        "importer_helper_meshes": [obj.name for obj in imported if obj.type == "MESH" and obj not in meshes],
        "materials": len(gltf.get("materials", [])), "images": len(gltf.get("images", [])),
        "normal_mapped_materials": sum("normalTexture" in m for m in gltf.get("materials", [])),
        "roughness_metallic_mapped_materials": sum("metallicRoughnessTexture" in m.get("pbrMetallicRoughness", {}) for m in gltf.get("materials", [])),
        "armatures": len(armatures), "bones": sum(len(obj.data.bones) for obj in armatures),
        "animations_in_source": len(gltf.get("animations", [])),
        "original_import_bounds": {"min": list(lo), "max": list(hi), "size": list(hi-lo)},
        "meshes_without_uvs": [obj.name for obj in meshes if not obj.data.uv_layers],
        "images_without_pixels": [im.name for im in images if min(im.size) == 0],
        "texture_sizes": dict(collections.Counter(f"{im.size[0]}x{im.size[1]}" for im in images)),
        "renders": [],
    }
    camera, center, span = prepare_studio(scene, lo, hi)
    directions = [("a", (0.8, -1.0, 0.60)), ("b", (-0.8, 1.0, 0.48))] if stem == "saloon" else [("a", (0.4, -1.0, 0.2))]
    for suffix, direction in directions:
        camera.location = center + Vector(direction).normalized() * span * 3
        aim(camera, center)
        scene.render.filepath = str(OUT / f"{stem}_{suffix}.png")
        bpy.ops.render.render(write_still=True)
        item["renders"].append(Path(scene.render.filepath).name)
    item["sha256_after"] = digest(path)
    item["source_unchanged"] = item["sha256_after"] == before
    item["images_without_pixels"] = [im.name for im in images if min(im.size) == 0 or len(im.pixels) == 0]
    print("ASSET_CHECK", json.dumps(item), flush=True)
    assert item["source_unchanged"], "Source hash changed"
    assert not item["images_without_pixels"], item["images_without_pixels"]
    report["assets"].append(item)

bpy.context.window.scene = bpy.data.scenes["Saloon asset review"]
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "Asset_Review.blend"))
(OUT / "asset_audit.json").write_text(json.dumps(report, indent=2) + "\n")
print("ASSET_REVIEW_COMPLETE", flush=True)
