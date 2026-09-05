"""Hand-built period street furniture, wagons and dressings."""
import math
import random
import bpy
from mathutils import Matrix, Vector
from geometry import MeshBatch, collection, instance, text, curve, transform


def barrel(target,m):
    b=MeshBatch("Library / stave barrel",target)
    segments=22
    profile=[(.02,.31),(.12,.34),(.3,.38),(.52,.395),(.75,.365),(.94,.32)]
    for i in range(segments):
        a=i*math.tau/segments+.008
        aa=(i+1)*math.tau/segments-.008
        tint=random.uniform(.66,1.13)
        for (z,r),(zz,rr) in zip(profile,profile[1:]):
            b.polygon([(r*math.cos(a),r*math.sin(a),z),(r*math.cos(aa),r*math.sin(aa),z),
                       (rr*math.cos(aa),rr*math.sin(aa),zz),(rr*math.cos(a),rr*math.sin(a),zz)],m["wood"],
                      [(i/7,z),(i/7+.15,z),(i/7+.15,zz),(i/7,zz)],(tint,tint,tint,1))
    for z,r in [(.08,.33),(.25,.373),(.72,.38),(.9,.337)]: b.ring((0,0,z),r,.028,.058,m["iron"],sides=32)
    for z in [.025,.935]:
        for i in range(7):
            yy=(i-3)*.085
            length=2*math.sqrt(max(.31**2-yy**2,.001))
            b.box((0,yy,z),(length,.077,.025),m["grey"],tint=random.uniform(.7,1))
    b.cylinder((.1,.05,.952),(.1,.05,.969),.04,m["darkwood"],10)
    return b.finish(.003)


def crate(target,m):
    b=MeshBatch("Library / shipping crate",target)
    b.box((0,0,.30),(.75,.58,.58),m["interior"])
    for side in [-1,1]:
        for i in range(5):
            b.box((0,side*.306,.08+i*.115),(.8,.055,.108),m["wood"],tint=random.uniform(.65,1.05))
            b.box((side*.407,0,.08+i*.115),(.055,.64,.108),m["wood"],tint=random.uniform(.65,1.05))
        for x in [-.31,.31]: b.box((x,side*.342,.31),(.09,.035,.65),m["grey"])
        b.beam((-.35,side*.35,.03),(.35,side*.35,.6),.055,m["grey"],.065)
    for i in range(6): b.box((0,(i-2.5)*.109,.64),(.82,.103,.055),m["wood"])
    return b.finish(.004)


def lantern(target,m):
    b=MeshBatch("Library / iron oil lantern",target)
    b.box((0,0,.04),(.23,.23,.08),m["iron"])
    b.box((0,0,.15),(.16,.16,.13),m["flame"])
    for x in [-.104,.104]:
        for y in [-.104,.104]: b.beam((x,y,.055),(x*.83,y*.83,.40),.024,m["iron"])
    b.cylinder((0,0,.4),(0,0,.52),.19,m["iron"],4,.035)
    b.ring((0,0,.57),.066,.013,.015,m["iron"],Matrix.Rotation(math.pi/2,3,"X"),16)
    return b.finish(.003)


def bench(target,m):
    b=MeshBatch("Library / porch bench",target)
    for y in [-.15,0,.15]: b.box((0,y,.47),(1.7,.135,.07),m["grey"])
    for x in [-.66,.66]:
        for y in [-.16,.16]: b.box((x,y,.24),(.095,.095,.45),m["darkwood"])
        b.beam((x,.18,.2),(x,.28,1.06),.08,m["darkwood"])
    for z in [.79,.97]: b.box((0,.25,z),(1.73,.065,.15),m["wood"])
    return b.finish(.006)


def wagon(target,m):
    b=MeshBatch("Library / farm wagon with spoke wheels",target)
    for i in range(9): b.box((0,(i-4)*.17,1.10),(3.7,.16,.095),m["wood"],tint=random.uniform(.6,1))
    for y in [-.84,.84]:
        for z in [1.24,1.48,1.72]: b.box((0,y,z),(3.75,.08,.20),m["green"],tint=random.uniform(.7,1.12))
        for x in [-1.7,-.55,.65,1.7]: b.box((x,y*1.05,1.48),(.10,.075,.92),m["darkwood"])
    for x in [-1.85,1.85]:
        for z in [1.24,1.48,1.72]: b.box((x,0,z),(.08,1.7,.20),m["wood"])
    for x in [-1.27,1.25]:
        b.cylinder((x,-1.17,.65),(x,1.17,.65),.07,m["iron"],12)
        for y in [-1.02,1.02]:
            rot=Matrix.Rotation(math.pi/2,3,"X")
            b.ring((x,y,.65),.65,.11,.12,m["darkwood"],rot,40)
            b.ring((x,y,.65),.68,.035,.14,m["iron"],rot,40)
            b.cylinder((x,y-.13,.65),(x,y+.13,.65),.12,m["wood"],12)
            for i in range(12):
                a=i*math.tau/12
                b.beam((x+.11*math.cos(a),y,.65+.11*math.sin(a)),(x+.60*math.cos(a),y,.65+.60*math.sin(a)),.05,m["wood"])
    for y in [-.38,.38]: b.beam((1.55,y,.97),(4.2,y*.72,.46),.105,m["darkwood"])
    for y in [-.4,.4]: b.box((1.26,y,1.88),(.62,.09,.21),m["darkwood"])
    b.box((1.22,0,2.05),(.62,1.5,.11),m["grey"])
    return b.finish(.006)


def make_library(m,parent):
    lib=collection("00 / Reusable prop originals",parent)
    data={name:fn(lib,m) for name,fn in [("barrel",barrel),("crate",crate),("lantern",lantern),("bench",bench),("wagon",wagon)]}
    lib.hide_render=True
    lib.hide_viewport=True
    return data


def dress_building(building,lib,m,parent,font,index):
    col=collection(building["name"]+" / street furniture",parent)
    tr=building["matrix"]
    w=building["width"]
    for i,(x,y,z,s) in enumerate([(-w*.42,-1.6,.65,1),(w*.43,-1.8,.65,.9),(-w*.42-.65,-1.25,.65,.82)]):
        instance(lib["barrel"],building["name"]+f" / barrel {i+1}",tr@Vector((x,y,z)),col,s,index*.34)
    for i in range(3):
        local=Vector((w*.39-i*.59,-.56,.65+(i%2)*.05))
        instance(lib["crate"],building["name"]+f" / delivery crate {i+1}",tr@local,col,.85,.06*i)
    obj=instance(lib["bench"],building["name"]+" / bench",tr@Vector((-w*.23,-.63,.64)),col,1)
    obj.rotation_euler.z=tr.to_euler().z
    b=MeshBatch(building["name"]+" / hitching post and hardware",col,tr)
    for px in [-w*.34,w*.34]:
        b.box((px,-3.55,.60),(.18,.18,1.17),m["darkwood"])
        b.box((px,-3.55,1.20),(.21,.22,.09),m["wood"])
    b.beam((-w*.34,-3.55,.96),(w*.34,-3.55,.96),.115,m["wood"])
    for xx in [-w*.25,w*.25]:
        b.ring((xx,-3.64,.93),.064,.018,.02,m["iron"],Matrix.Rotation(math.pi/2,3,"X"),16)
    # Drainpipe from the awning to a rain barrel.
    b.cylinder((w*.45,-.12,3.25),(w*.45,-.12,.70),.04,m["iron"],10)
    b.finish(.006)
    for i,x in enumerate([-w*.135,w*.135]):
        loc=tr@Vector((x,-.46,2.06))
        instance(lib["lantern"],building["name"]+f" / entrance lantern {i+1}",loc,col,.80)
        if building["hero"] or index%3==0:
            d=bpy.data.lights.new(building["name"]+f" / lantern light {i+1}","POINT")
            d.energy=14 if building["hero"] else 8
            d.color=(1,.54,.23)
            d.shadow_soft_size=.12
            light=bpy.data.objects.new(d.name,d)
            col.objects.link(light)
            light.location=loc+Vector((0,0,.16))
    if building["hero"]:
        pole=MeshBatch("Smithfield / striped barber pole",col,tr)
        for j in range(36):
            z=1.6+j*.025
            for i in range(16):
                a=i*math.tau/16
                aa=(i+1)*math.tau/16
                color=[m["red"],m["letter"],m["blue"],m["letter"]][((i+j)//3)%4]
                pole.polygon([(5.2+.075*math.cos(a),-.40+.075*math.sin(a),z),(5.2+.075*math.cos(aa),-.40+.075*math.sin(aa),z),
                              (5.2+.075*math.cos(aa),-.40+.075*math.sin(aa),z+.026),(5.2+.075*math.cos(a),-.40+.075*math.sin(a),z+.026)],color)
        for zz in [1.55,2.53]: pole.cylinder((5.2,-.40,zz),(5.2,-.40,zz+.09),.105,m["iron"],16)
        pole.finish(.001)
        # A menu sign and a separate small wanted notice, typeset rather than fake noise.
        b=MeshBatch("Smithfield / sandwich board and notices",col,tr)
        for side in [-1,1]:
            for x in [-.31,.31]: b.beam((2.05+x,-2.2+side*.28,.64),(2.05+x,-2.2,1.95),.045,m["darkwood"])
        b.box((2.05,-2.39,1.4),(.74,.07,.93),m["darkwood"])
        b.box((4.40,-.088,1.7),(.43,.02,.60),m["paper"])
        b.finish(.004)
        text("Smithfield / menu","BEEF STEW\n\nFRESH MEALS\n\nWHISKEY",(2.05,-2.435,1.43),.62,.094,m["letter"],col,tr,font)
        text("Smithfield / help notice","HELP\nWANTED",(4.40,-.105,1.80),.36,.095,m["ink"],col,tr,font)
        text("Smithfield / notice detail","ENQUIRE\nWITHIN",(4.40,-.108,1.59),.33,.046,m["ink"],col,tr,font)


def telegraph(m,parent):
    col=collection("Street / telegraph poles and sagging wires",parent)
    locations=[(-41,-4.0),(-17,-3.8),(11,-4.3),(37,-3.9),(64,-4.4)]
    b=MeshBatch("Telegraph / poles, crossarms, glass insulators",col)
    for x,y in locations:
        b.cylinder((x,y,.05),(x,y,7.8),.16,m["darkwood"],12,.105)
        for z in [7.2,7.65]:
            b.box((x,y,z),(2.45,.13,.16),m["wood"])
            for dx in [-.95,-.40,.4,.95]:
                b.cylinder((x+dx,y,z+.05),(x+dx,y,z+.28),.048,m["glass"],10)
        b.beam((x,y,6.6),(x-.7,y,7.2),.06,m["iron"])
    b.finish(.008)
    for (x,y),(xx,yy) in zip(locations,locations[1:]):
        for dx in [-.95,.4,.95]:
            pts=[]
            for i in range(33):
                t=i/32
                pts.append((x+(xx-x)*t+dx,y+(yy-y)*t,7.88-1.0*4*t*(1-t)))
            curve("Telegraph / suspended copper",pts,.009,m["iron"],col)


def fences(m,parent):
    col=collection("Town edge / split rail fences",parent)
    b=MeshBatch("Paddock fences",col)
    segments=[((-65,18),(-31,18)),((-65,18),(-65,52)),((-65,52),(-32,52)),((42,19),(82,19)),((82,19),(82,52)),((40,52),(82,52))]
    for (x,y),(xx,yy) in segments:
        n=math.ceil(math.hypot(xx-x,yy-y)/2.6)
        for i in range(n+1):
            t=i/n
            px,py=x+(xx-x)*t,y+(yy-y)*t
            b.box((px,py,.72),(.16,.16,1.48),m["grey"],tint=random.uniform(.65,1))
            if i<n:
                nx,ny=x+(xx-x)*(i+1)/n,y+(yy-y)*(i+1)/n
                for z in [.51,1.04]: b.beam((px,py,z),(nx,ny,z+random.uniform(-.06,.06)),.105,m["wood"])
    b.finish(.009)
