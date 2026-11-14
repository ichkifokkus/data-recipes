"""Render a vertical (1080x1920) video frame sequence with Blender from plain Python.

No Blender install and no GPU needed: `pip install bpy` gives you Blender as a module
(Python version must match the wheel, e.g. bpy 5.3 needs Python 3.13).

    python blender_headless_render.py out/ 48    # 48 frames at 24 fps = 2 s
    ffmpeg -framerate 24 -i out/%04d.png -c:v libx264 -pix_fmt yuv420p clip.mp4
"""
import math
import sys

import bpy

out_dir, n_frames = sys.argv[1].rstrip("/"), int(sys.argv[2])

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# --- objects: a glossy ceramic sphere on a dark floor -------------------------
bpy.ops.mesh.primitive_plane_add(size=20)
floor = bpy.context.object
floor_mat = bpy.data.materials.new("floor")
floor_mat.use_nodes = True
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1)
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.25
floor.data.materials.append(floor_mat)

bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1), segments=96, ring_count=48)
bpy.ops.object.shade_smooth()
ball = bpy.context.object
mat = bpy.data.materials.new("ceramic")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.88, 1)
bsdf.inputs["Roughness"].default_value = 0.18
bsdf.inputs["Coat Weight"].default_value = 1.0
ball.data.materials.append(mat)

# --- light: one big soft key + a cyan rim --------------------------------------
for name, loc, energy, color, size in [("key", (-4, -4, 6), 1500, (1, 0.95, 0.9), 4),
                                       ("rim", (4, 3, 3), 800, (0.3, 0.9, 1), 1)]:
    light = bpy.data.lights.new(name, "AREA")
    light.energy, light.color, light.size = energy, color, size
    obj = bpy.data.objects.new(name, light)
    obj.location = loc
    obj.rotation_euler = (0, 0, 0)
    constraint = obj.constraints.new("TRACK_TO")
    constraint.target = ball
    scene.collection.objects.link(obj)

# --- camera: vertical 9:16, slow orbit keyed per frame -------------------------
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 50
cam.data.dof.use_dof = True
cam.data.dof.focus_object = ball
cam.data.dof.aperture_fstop = 2.8
track = cam.constraints.new("TRACK_TO")
track.target = ball
scene.collection.objects.link(cam)
scene.camera = cam
for f in range(n_frames):
    a = -math.pi / 2 + 0.6 * f / max(n_frames - 1, 1)
    cam.location = (7 * math.cos(a), 7 * math.sin(a), 2.2)
    cam.keyframe_insert("location", frame=f + 1)

# --- render settings: Cycles on CPU, few samples + denoiser ---------------------
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True            # OpenImageDenoise, runs on CPU
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = 1080, 1920
scene.render.resolution_percentage = 60      # 648x1152; upscale later if needed
scene.render.fps = 24
scene.render.use_motion_blur = True
scene.view_settings.view_transform = "AgX"
scene.render.image_settings.file_format = "PNG"
scene.frame_start, scene.frame_end = 1, n_frames
scene.render.filepath = f"{out_dir}/"

bpy.ops.render.render(animation=True)
