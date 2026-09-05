"""Render bounded stills from the saved scene. No animation is rendered."""
from pathlib import Path
import argparse
import json
import sys
import time
import bpy

parser=argparse.ArgumentParser()
parser.add_argument("--quality",choices=["preview","final"],default="preview")
parser.add_argument("--views",default="1")
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
root=Path(bpy.data.filepath).parent
scene=bpy.context.scene
scene.render.resolution_x=1120 if args.quality=="preview" else 2560
scene.render.resolution_y=700 if args.quality=="preview" else 1600
scene.render.resolution_percentage=100
scene.cycles.samples=20 if args.quality=="preview" else 112
scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="METAL"
    prefs.get_devices()
    available=False
    for d in prefs.devices:
        d.use=d.type=="METAL"
        available|=d.use
    scene.cycles.device="GPU" if available else "CPU"
except (TypeError,RuntimeError): scene.cycles.device="CPU"
names={1:"01 / Smithfield hero",2:"02 / Along the main street",3:"03 / Saints Hotel and bank",4:"04 / Town overview",5:"05 / Saloon entrance and Arthur"}
final_names={1:"01_Smithfields_Main_Street.png",2:"02_Along_Main_Street.png",3:"03_Saints_Hotel_and_Bank.png",4:"04_Town_Overview.png",5:"05_Arthur_at_Smithfields.png"}
outputs=[]
for number in [int(n) for n in args.views.split(",")]:
    scene.frame_set(number)
    scene.camera=bpy.data.objects[names[number]]
    filename=final_names[number] if args.quality=="final" else f"preview_{number:02d}.png"
    scene.render.filepath=str(root/"renders"/filename)
    start=time.monotonic()
    bpy.ops.render.render(write_still=True)
    result={"file":filename,"camera":names[number],"seconds":round(time.monotonic()-start,2),"samples":scene.cycles.samples,"size":[scene.render.resolution_x,scene.render.resolution_y],"device":scene.cycles.device}
    outputs.append(result)
    print("RENDER_COMPLETE",json.dumps(result),flush=True)
(root/f"render_{args.quality}_report.json").write_text(json.dumps(outputs,indent=2)+"\n")
