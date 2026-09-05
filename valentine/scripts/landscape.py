"""Rutted street, shallow puddles, grazing ground and directional wooded hills."""
import math
import random
import bpy
from mathutils import Vector, noise
from geometry import MeshBatch, collection, instance

PUDDLES=[(-15,-12.4,3.0,.83),(-7,-8.7,2.2,.7),(3,-12.0,3.7,.9),(10,-7.7,1.65,.60),
         (17,-14.8,2.8,.77),(-23,-17.4,2.2,.85),(29,-9.3,3.0,.66),(-34,-8.3,2.4,.81),
         (3,-19.1,1.4,.65),(40,-13,3.4,.72),(1,-4.55,1.6,.38)]


def n(x,y,z=0):
    return noise.noise(Vector((x,y,z)))


def road_base(x,y):
    value=.028*math.sin(x*.23)+.020*math.cos(y*.7)
    value+=.065*n(x*2.1,y*2.1,.2)+.025*n(x*7,y*7,2.3)
    for lane in [-6.2,-8.0,-11.5,-13.25,-17.0,-18.8]:
        curve=lane+.28*math.sin(x*.057+lane)
        delta=y-curve
        value-=.115*math.exp(-(delta/.20)**2)
        value+=.035*math.exp(-((abs(delta)-.25)/.12)**2)
    return value


def ground_height(x,y):
    value=road_base(x,y)
    for idx,(cx,cy,rx,ry) in enumerate(PUDDLES):
        u,v=(x-cx)/rx,(y-cy)/ry
        angle=math.atan2(v,u)
        variation=.90+.06*math.sin(angle*7+idx)+.04*math.sin(angle*13+idx*2)
        radius=math.hypot(u,v)/variation
        if radius<1.4:
            water=road_base(cx,cy)-.017
            basin=water+.060*(radius*radius-1)
            blend=max(0,min(1,(radius-1.04)/.36))
            blend=blend*blend*(3-2*blend)
            value=basin*(1-blend)+value*blend
    return value


def road(m,parent):
    col=collection("01 / Sculpted mud street",parent)
    b=MeshBatch("Main road / ruts, churn and puddle basins",col)
    # Share vertices before material assignment to keep a continuous dense surface.
    xmin,xmax,ymin,ymax=-76,82,-24.5,-2.9
    nx,ny=940,160
    verts=[]
    for j in range(ny+1):
        y=ymin+(ymax-ymin)*j/ny
        for i in range(nx+1):
            x=xmin+(xmax-xmin)*i/nx
            verts.append((x,y,ground_height(x,y)))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i
            faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new(b.name)
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(m["mud"])
    obj=bpy.data.objects.new(b.name,mesh)
    col.objects.link(obj)
    uv=mesh.uv_layers.new(name="SurfaceUV")
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(v.x*.4,v.y*.4)
    water=MeshBatch("Street / shallow irregular rain puddles",col)
    for idx,(cx,cy,rx,ry) in enumerate(PUDDLES):
        # Keep the polygon perimeter below the bank; the ground itself clips the
        # visible waterline, including between samples of the road mesh.
        z=road_base(cx,cy)-.047
        points=[]
        for j in range(100):
            a=j*math.tau/100
            variation=.90+.06*math.sin(a*7+idx)+.04*math.sin(a*13+idx*2)
            points.append((cx+rx*variation*math.cos(a),cy+ry*variation*math.sin(a),z))
        water.polygon(points,m["water"])
    water.finish()
    # Raised ridges of compressed earth, hoof churn and grit catch low light.
    grit=MeshBatch("Street / granular mud and hoof churn",col)
    for i in range(4200):
        x=random.uniform(-55,65)
        y=random.uniform(-23,-3.1)
        if any(((x-cx)/rx)**2+((y-cy)/ry)**2<1.2 for cx,cy,rx,ry in PUDDLES):continue
        z=ground_height(x,y)
        r=random.uniform(.025,.085)
        height=random.uniform(.012,.045)
        pts=[(x+r*math.cos(j*math.tau/5),y+r*.7*math.sin(j*math.tau/5),z) for j in range(5)]
        for j in range(5): grit.polygon([pts[j],pts[(j+1)%5],(x,y,z+height)],m["soil"] if i%4 else m["stone"])
    grit.finish()
    return col


def heightfield(name,col,x0,y0,dx,dy,nx,ny,height,materials,choose_material):
    vertices=[(x0+i*dx,y0+j*dy,height(x0+i*dx,y0+j*dy)) for j in range(ny+1) for i in range(nx+1)]
    faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i
            faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    for mat in materials:mesh.materials.append(mat)
    for polygon in mesh.polygons:
        center=sum((mesh.vertices[k].co for k in polygon.vertices),Vector())/4
        polygon.material_index=choose_material(*center)
        polygon.use_smooth=True
    obj=bpy.data.objects.new(name,mesh)
    col.objects.link(obj)
    return obj


def terrain(m,parent):
    col=collection("02 / Ground, hills and horizon",parent)
    def town_height(x,y):
        z=-.18+.12*n(x*.16,y*.16)
        if y>31:z+=min(2.9,(y-31)/28)*(.8+.4*math.sin(x*.053))
        return z
    heightfield("Town / grassland and irregular verges",col,-190,-160,1.5,1.5,260,230,town_height,[m["verge"]],lambda x,y,z:0)
    base=MeshBatch("Horizon / continuous plains",col)
    base.polygon([(-2400,-2200,-1.0),(2400,-2200,-1.0),(2400,2100,-1.0),(-2400,2100,-1.0)],m["grass"])
    base.finish()

    # A continuous, eroded range: overlapping ridgelines rather than isolated cones.
    def mountain_height(x,y):
        envelope=math.exp(-((y-340)/135)**2)
        edge=max(0,1-(abs(x)/690)**6)
        ridge=39+21*math.sin(x*.013+.4)+13*math.sin(x*.035-1.1)
        ridge+=18*(1-abs(n(x*.021,y*.028,2.1)))
        detail=14*n(x*.047,y*.044,4.3)+6*n(x*.098,y*.083,1.1)+2*n(x*.23,y*.21)
        front=min(1,max(0,(y-170)/75))**2
        return -1+max(0,(ridge+detail)*envelope*edge*front)
    heightfield("North / eroded Cumberland foothills",col,-700,132,5,4,280,155,mountain_height,[m["grass"],m["stone"]],lambda x,y,z:1 if z>43+12*n(x*.07,y*.06) else 0)
    def plain_height(x,y):
        fade=max(0,1-((x-400)/270)**2)*max(0,1-((y+30)/530)**2)
        return -1+fade*(13+8*n(x*.012,y*.009)+4*n(x*.027,y*.031))
    heightfield("East / rolling open prairie",col,130,-560,5,5,108,212,plain_height,[m["grass"]],lambda x,y,z:0)
    def rock_height(x,y):
        shoulder=max(0,1-((x-58)/27)**4)
        front=67+1.4*n(x*.22,1)
        profile=max(0,min(1,(y-front)/1.9))*max(0,min(1,(84-y)/7))
        crest=5.8+2*n(x*.18,y*.14)+.6*n(x*.8,y*.5)
        return -.8+shoulder*profile*crest
    heightfield("Church rise / eroded rock outcrop",col,30,64,.65,.7,86,30,rock_height,[m["stone"]],lambda x,y,z:0)
    return col


def tree_template(name,m,lib,pine=False,seed=17):
    rng=random.Random(seed)
    b=MeshBatch(name,lib)
    h=9 if pine else 8.0
    b.cylinder((0,0,0),(.17,.06,h),.23,m["darkwood"],10,.05)
    for tier in range(8 if pine else 5):
        z=1.9+tier*(.78 if pine else 1.0)
        radius=(h-z)*.38+.12 if pine else 2.2
        for j in range(7 if pine else 5):
            a=j*math.tau/(7 if pine else 5)+tier*1.4
            tip=Vector((radius*math.cos(a),radius*math.sin(a),z+.55))
            b.cylinder((.07,.02,z),tip,.075 if pine else .095,m["darkwood"],6,.015)
            count=18 if pine else 90
            for k in range(count):
                f=rng.uniform(.25,1.15)
                pos=Vector((tip.x*f,tip.y*f,tip.z))+Vector((rng.uniform(-.55,.55),rng.uniform(-.55,.55),rng.uniform(-.38,.68)))
                if pine:
                    # Several angled needle sprays per bough, with a serrated perimeter.
                    span=rng.uniform(.26,.50)
                    ang=a+rng.uniform(-.7,.7)
                    p1=pos+Vector((-span*math.cos(ang),-span*math.sin(ang),-.10))
                    p2=pos+Vector((span*math.cos(ang),span*math.sin(ang),-.10))
                    p3=pos+Vector((0,0,.40))
                    b.polygon([p1,p2,p3],m["pine"])
                else:
                    for leaf in range(3):
                        ang=rng.uniform(0,math.tau)
                        size=rng.uniform(.10,.23)
                        p=pos+Vector((rng.uniform(-.22,.22),rng.uniform(-.22,.22),rng.uniform(-.18,.18)))
                        u=Vector((math.cos(ang),math.sin(ang),rng.uniform(-.3,.3)))*size
                        v=Vector((-math.sin(ang),math.cos(ang),rng.uniform(-.6,.6)))*size*.47
                        b.polygon([p-u,p+v,p+u,p-v],m["leaf"])
    return b.finish()


def vegetation(m,parent):
    col=collection("03 / Trees and roadside vegetation",parent)
    lib=collection("00 / Tree library",parent)
    broad=tree_template("Library / cottonwood",m,lib,False)
    pine=tree_template("Library / foothill pine",m,lib,True,27)
    lib.hide_render=True
    lib.hide_viewport=True
    for i in range(115):
        x=random.uniform(-120,130)
        y=random.uniform(35,94)
        z=-.12+max(0,(y-31)/28)*(.8+.4*math.sin(x*.053))
        instance(pine if i%3 else broad,f"Foothills / tree {i+1}",(x,y,z),col,random.uniform(.55,1.42),random.uniform(0,math.tau))
    for i,(x,y,s) in enumerate([(-34,12,1.3),(-23,21,.95),(36,24,1.05),(57,26,1.1),(-46,-31,1.0),(42,-37,1.1)]):
        instance(broad,f"Town / cottonwood {i+1}",(x,y,0),col,s,i)
    grass=MeshBatch("Verge / individual grass and dry seed blades",col)
    for i in range(11500):
        x=random.uniform(-83,90)
        y=random.uniform(-40,62)
        if -24<y<18 and abs(x)<66:continue
        z=-.12+max(0,(y-31)/28)*(.8+.4*math.sin(x*.053))
        for blade in range(3):
            a=random.uniform(0,math.tau)
            width=random.uniform(.014,.036)
            h=random.uniform(.12,.39)
            grass.polygon([(x-width,y,z),(x+width,y,z),(x+.1*math.cos(a),y+.1*math.sin(a),z+h)],m["grass"] if i%4 else m["straw"])
    grass.finish()
