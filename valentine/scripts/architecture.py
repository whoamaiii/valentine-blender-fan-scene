"""Reference-led main street architecture and reusable weathered timber details."""
import math
import random
import bpy
from mathutils import Matrix, Vector
from geometry import MeshBatch, collection, transform, text, curve


def wall(batch, width, low, high, material, y=0, holes=(), step=.185):
    row=0
    z=low+step/2
    while z<high:
        segments=[(-width/2,width/2)]
        for left,right,bottom,top in holes:
            if z+step/2>bottom and z-step/2<top:
                next_segments=[]
                for a,b in segments:
                    if a<left: next_segments.append((a,min(b,left)))
                    if b>right: next_segments.append((max(a,right),b))
                segments=next_segments
        for a,b in segments:
            # Stagger the joints of long siding; no identical wall-sized strips.
            start=a
            while start<b-.03:
                length=min(b-start,random.uniform(2.4,4.8))
                batch.box((start+length/2,y+random.uniform(-.006,.006),z),
                          (length-.008,.070,min(step-.012,high-z+step/2)),material,tint=random.uniform(.65,1.12))
                start+=length
        row+=1
        z+=step


def window(batch,x,z,w,h,m,y=-.10,rows=3,shutters=False):
    batch.box((x,y+.04,z),(w,.07,h),m["interior"])
    batch.box((x,y-.013,z),(w-.13,.023,h-.13),m["glass"])
    for dx in [-w/2,w/2]: batch.box((x+dx,y-.07,z),(.11,.16,h+.20),m["trim"])
    for dz in [-h/2,h/2]: batch.box((x,y-.07,z+dz),(w+.20,.16,.13),m["trim"])
    batch.box((x,y-.10,z),(.06,.055,h-.1),m["darkwood"])
    for i in range(1,rows):
        batch.box((x,y-.105,z-h/2+h*i/rows),(w-.1,.057,.055),m["darkwood"])
    batch.box((x,y-.17,z-h/2-.10),(w+.33,.36,.12),m["wood"])
    batch.box((x,y-.10,z+h/2+.15),(w+.30,.20,.09),m["trim"])
    if shutters:
        for side in [-1,1]:
            sx=x+side*(w*.5+.29)
            batch.box((sx,y+.03,z),(.43,.06,h+.08),m["green"])
            for j in range(10): batch.box((sx,y-.035,z-h/2+.1+j*(h-.16)/9),(.40,.045,.075),m["green"])


def door(batch,x,bottom,m,width=1.1,height=2.3,y=-.11,saloon=False):
    batch.box((x,y+.16,bottom+height/2),(width,.075,height),m["interior"])
    for dx in [-width/2,width/2]: batch.box((x+dx,y-.02,bottom+height/2),(.13,.2,height+.16),m["trim"])
    batch.box((x,y-.03,bottom+height+.04),(width+.23,.2,.14),m["trim"])
    if saloon:
        for side in [-1,1]:
            cx=x+side*(width/4+.055)
            angle=side*.13
            for j in range(6):
                px=cx+(j-2.5)*width/12
                top=bottom+1.42+.10*math.cos((j-2.5)*.8)
                batch.box((px,y-.055,bottom+.72+(top-bottom-.72)/2),
                          (width/12-.014,.085,top-bottom-.72),m["darkwood"],Matrix.Rotation(angle,3,"Z"))
            for zz in [bottom+.81,bottom+1.30]:
                batch.box((cx,y-.13,zz),(width/2-.045,.06,.1),m["wood"])
    else:
        batch.box((x,y,bottom+height/2),(width-.13,.09,height-.1),m["darkwood"])
        for xx in [-.24,.24]:
            for zz in [.5,1.3,1.88]:
                batch.box((x+xx,y-.065,bottom+zz),(width*.30,.027,.40),m["wood"])
        batch.cylinder((x+width*.30,y-.13,bottom+1.04),(x+width*.30,y-.21,bottom+1.04),.038,m["iron"],10)


def porch(batch,w,depth,floor,m,posts=True,cover=True,balcony=False):
    front=-depth
    for xx in [-w/2+.14,0,w/2-.14]:
        batch.box((xx,-depth/2,floor-.2),(.18,depth,.30),m["darkwood"])
    n=math.ceil(w/.23)
    for i in range(n):
        x=-w/2+(i+.5)*w/n
        batch.box((x,-depth/2,floor+random.uniform(-.008,.008)),(w/n-.015,depth,.13),m["grey"],tint=random.uniform(.58,1.12))
    for zz in [.17,.38]:
        batch.box((0,front-.3-.36*(.38-zz)/.21,zz),(2.25,.8,.19),m["grey"])
    if posts:
        count=round(w/2.5)
        for i in range(count+1):
            x=-w/2+.12+(w-.24)*i/count
            batch.box((x,front+.14,1.80),(.14,.14,2.7),m["grey"],tint=random.uniform(.66,1))
            for side in [-1,1]:
                batch.beam((x,front+.13,2.64),(x+side*.42,front+.13,3.10),.085,m["grey"])
    if cover:
        slope=Matrix.Rotation(-.075,3,"X")
        batch.box((0,-depth/2,3.18),(w+.3,depth+.4,.12),m["roof"],slope)
        for i in range(math.ceil(w/.28)):
            x=-w/2+i*.28
            batch.box((x,-depth/2,3.26),(.27,depth+.4,.045),m["roof"],slope,tint=random.uniform(.55,1.0))
        batch.box((0,front-.16,3.04),(w+.35,.14,.21),m["trim"])
        for x in [-w/2,w/2]: batch.beam((x,-.1,3.31),(x,front-.18,3.02),.12,m["trim"])
    if balcony:
        for i in range(math.ceil(w/.22)):
            batch.box((-w/2+i*.22,front+.05,3.70),(.045,.055,.8),m["trim"])
        for z in [3.34,4.12]: batch.box((0,front+.05,z),(w,.10,.10),m["trim"])


def roof(batch,w,d,eaves,m,rise=1.5,shingles=True):
    for side in [-1,1]:
        pitch=math.atan2(rise,w/2)
        slant=math.hypot(w/2,rise)
        rot=Matrix.Rotation(side*pitch,3,"Y")
        # Each roof plane slopes from the centre ridge down towards its side.
        batch.box((side*w/4,d/2+.35,eaves+rise/2),(slant+.35,d-.30,.12),m["roof"],rot)
        if shingles:
            rows=math.ceil(slant/.30)
            cols=math.ceil(d/.45)
            for r in range(rows):
                f=(r+.5)/rows
                xx=side*(w/2*f)
                zz=eaves+rise*(1-f)+.08
                for c in range(cols):
                    yy=.48+(c+.5)*(d-.55)/cols+(.07 if r%2 else 0)
                    batch.box((xx,yy,zz),(slant/rows+.045,d/cols-.008,.035),m["roof"],rot,tint=random.uniform(.57,1.13))
    batch.box((0,d/2+.35,eaves+rise+.13),(.18,d-.25,.16),m["darkwood"])
    for y in [.45,d]:
        batch.polygon([(-w/2,y,eaves),(w/2,y,eaves),(0,y,eaves+rise)],m["grey"],[(0,0),(w/2,0),(w/4,rise)])


def shell(batch,w,d,height,m,body,holes):
    # A continuous dark substrate stops sky light leaking through siding joints.
    levels=sorted(set([.5,height]+[max(.5,min(height,z)) for a,b,lo,hi in holes for z in [lo,hi]]))
    for bottom,top in zip(levels,levels[1:]):
        spans=[(-w/2,w/2)]
        for left,right,lo,hi in holes:
            if lo<(bottom+top)/2<hi:
                result=[]
                for a,b in spans:
                    if a<left:result.append((a,min(b,left)))
                    if b>right:result.append((max(a,right),b))
                spans=result
        for a,b in spans:
            if b>a:batch.box(((a+b)/2,.08,(bottom+top)/2),(b-a,.055,top-bottom),m["interior"])
    batch.box((0,d-.08,(height+.5)/2),(w,.055,height-.5),m["interior"])
    for side in [-1,1]:batch.box((side*(w/2-.08),d/2,(height+.5)/2),(.055,d,height-.5),m["interior"])
    wall(batch,w,.57,height,m[body],holes=holes)
    wall(batch,w,.57,height,m[body],y=d)
    for side in [-1,1]:
        for i in range(math.ceil((height-.5)/.19)):
            z=.6+i*.19
            batch.box((side*w/2,d/2,z),(.065,d,.178),m[body],tint=random.uniform(.68,1.1))
    for x in [-w/2,w/2]:
        for y in [0,d]: batch.box((x,y,height/2),(.16,.18,height),m["trim"])
    for x in range(math.ceil(w/.65)):
        for y in [0,d]: batch.box((-w/2+(x+.5)*w/math.ceil(w/.65),y,.28),(.60,.4,.48),m["stone"],tint=random.uniform(.7,1.0))
    batch.box((0,d/2,.49),(w,d,.1),m["darkwood"])


def storefront(name,x,y,w,d,h,m,parent,font,body="grey",label="",sub="",angle=0,kind="store",hero=False):
    col=collection(name,parent)
    mat=transform(x,y,0,angle)
    b=MeshBatch(name+" / siding and joinery",col,mat)
    openings=[(-.7,.7,.58,2.9)]
    wx=w*.29
    ww=min(2.25,w*.23)
    for sx in [-wx,wx]: openings.append((sx-ww/2,sx+ww/2,1.03,2.8))
    shell(b,w,d,h,m,body,openings)
    window(b,-wx,1.92,ww,1.68,m,rows=3)
    window(b,wx,1.92,ww,1.68,m,rows=3)
    door(b,0,.57,m,width=1.4,height=2.3,saloon=hero)
    floor=.57
    porch(b,w+.35,2.65 if hero else 2.35,floor,m,posts=True,cover=True,balcony=(kind=="hotel"))
    if kind=="hotel":
        for px in [-w*.34,0,w*.34]: window(b,px,4.95,1.35,1.72,m,shutters=px!=0)
    # Main false front is deliberately distinct from the roof behind it.
    top=h+(.9 if hero else .55)
    b.box((0,.06,(h+top)/2),(w,.055,top-h),m["darkwood"])
    wall(b,w,h,top,m[body],y=-.02)
    for z in [top,top-.16]: b.box((0,-.11,z),(w+.4,.24,.13),m["trim"])
    if hero:
        gw=4.35
        peak=top+.90
        b.polygon([(-gw/2,-.045,top),(gw/2,-.045,top),(0,-.045,peak)],m[body],[(0,0),(4,0),(2,1)])
        for side in [-1,1]:
            b.beam((side*(gw/2+.18),-.14,top-.02),(0,-.14,peak+.09),.14,m["trim"],width=.18)
        b.box((0,-.15,4.00),(5.5,.12,.7),m["darkwood"])
        text(name+" / saloon sign","SALOON",(0,-.225,4.0),5.0,.72,m["letter"],col,mat,font)
        text(name+" / painted name","SMITHFIELDS",(0,-.10,5.45),w-.62,1.35,m["letter"],col,mat,font)
        for sx,word in [(-w*.33,"ROOMS"),(0,"MEALS"),(w*.33,"BARBERS")]:
            b.box((sx,-2.87,2.86),(3.35,.07,.41),m["darkwood"])
            text(name+" / services / "+word,word,(sx,-2.915,2.86),3.0,.44,m["letter"],col,mat,font)
        # A shallow visible interior behind the swinging doors.
        b.box((0,4.7,1.12),(7.8,.75,1.1),m["darkwood"])
        b.box((0,4.7,1.73),(8.0,.95,.13),m["wood"])
        for zz in [1.5,2.15,2.8]: b.box((0,6.0,zz),(7.5,.40,.10),m["wood"])
        b.box((0,6.25,2.1),(7.7,.10,2.8),m["darkwood"])
    else:
        size=1.05 if name=="Worth's General Store" else min(.72,w/11)
        text(name+" / main sign",label or name,(0,-.14,top-.52),w-.48,size,m["letter"],col,mat,font)
        if sub: text(name+" / trade sign",sub,(0,-2.64,3.01),w-.5,.24,m["gold"],col,mat,font)
    # Secondary side windows have real frames; an otherwise unseen side is inferred.
    sb=MeshBatch(name+" / side window details",col,mat@transform(w/2+.05,0,0,math.pi/2))
    for sy in [d*.28,d*.73]: window(sb,sy,2.0,1.2,1.5,m,rows=3)
    sb.finish(.007)
    r=MeshBatch(name+" / individual roof shingles",col,mat)
    roof(r,w,d,h-.15,m,1.25 if hero else 1.4,shingles=True)
    r.finish(.004)
    b.finish(.008)
    # Masonry chimney with staggered brick courses.
    cb=MeshBatch(name+" / brick chimney",col,mat)
    for row in range(12):
        for side in [-1,1]:
            for j in range(3):
                cb.box((w*.28+(j-1)*.20, d*.67+side*.22,h+.30+row*.10),(.19,.14,.085),m["brick"],tint=random.uniform(.65,1.05))
    cb.box((w*.28,d*.67,h+1.52),(.77,.70,.14),m["stone"])
    cb.finish(.005)
    return {"name":name,"collection":col,"matrix":mat,"width":w,"depth":d,"height":h,"hero":hero}


def keanes_construction(x,y,m,parent,font):
    name="Keane's / rooms and construction"
    col=collection(name,parent)
    tr=transform(x,y)
    b=MeshBatch(name+" / old timber and exposed new framing",col,tr)
    w,d=9.6,11.5
    shell(b,w,d,5.8,m,"darkwood",[(-.7,.7,.6,2.7)])
    door(b,0,.58,m,1.3,2.2)
    for xx in [-2.95,2.9]: window(b,xx,1.95,1.55,1.7,m)
    for xx in [-3.2,0,3.2]: window(b,xx,4.68,1.35,1.65,m)
    porch(b,w,2.7,.58,m,True,True,True)
    for x0 in [-w/2,w/2]:
        for y0 in [-2.48,2,6,10.8]: b.box((x0,y0,4.9),(.17,.18,4.0),m["wood"])
    for yy in [-2.5,0,2.5,5.0,7.5,10.8]:
        for side in [-1,1]: b.beam((side*(w/2+.15),yy,6.40),(0,yy,8.0),.14,m["wood"],.18)
        b.beam((-w/2,yy,6.4),(w/2,yy,6.4),.14,m["wood"])
    for side in [-1,1]: b.beam((side*w/2,-2.5,6.4),(side*w/2,11,6.4),.17,m["darkwood"])
    b.beam((0,-2.6,8),(0,11.2,8),.18,m["wood"])
    # Partial tarpaulin over the construction, with a visibly sagging edge.
    verts=[]
    for xx,yy,zz in [(-4.9,1,6.46),(-.2,1,7.82),(-.2,7.2,7.81),(-4.9,7.2,6.46)]: verts.append((xx,yy,zz))
    b.polygon(verts,m["canvas"],[(0,0),(1,0),(1,2),(0,2)])
    for i in range(10): b.box((-3.4+i*.13,-3.6,.16+i*.018),(3.8,.12,.09),m["wood"],Matrix.Rotation(.07,3,"Z"))
    for dx in [-.30,.30]: b.beam((4.0+dx,-3.2,.03),(4.0+dx,-.60,5.2),.075,m["grey"])
    for i in range(15):
        t=(i+.5)/15
        b.beam((3.7,-3.2+2.6*t,5.2*t),(4.3,-3.2+2.6*t,5.2*t),.055,m["grey"])
    b.box((0,-2.77,5.32),(8.2,.12,.72),m["green"])
    b.finish(.008)
    text(name+" / sign","KEANE'S ROOMS FOR RENT",(0,-2.855,5.33),7.7,.41,m["letter"],col,tr,font)
    text(name+" / restaurant sign","HOTEL  &  RESTAURANT",(0,-2.86,3.07),8.3,.27,m["gold"],col,tr,font)
    return {"name":name,"collection":col,"matrix":tr,"width":w,"depth":d,"height":8,"hero":False}


def bank(x,y,m,parent,font,angle=math.pi):
    name="Valentine Savings Bank"
    col=collection(name,parent)
    tr=transform(x,y,0,angle)
    b=MeshBatch(name+" / masonry and storefront",col,tr)
    w,d,h=10.5,10,4.4
    openings=[(-.78,.78,.45,3.1),(-4.5,-2.5,1.1,3.1),(2.5,4.5,1.1,3.1)]
    b.box((0,d/2,h/2),(w,d,h),m["brick"])
    for row in range(36):
        z=.1+row*.12
        for col_idx in range(36):
            px=-w/2+(col_idx+.5+(row%2)*.5)*.30
            if px>w/2: continue
            if any(a<px<b_ and lo<z<hi for a,b_,lo,hi in openings):continue
            b.box((px,-.05,z),(.286,.085,.104),m["brick"],tint=random.uniform(.6,1.13))
    for z in [.32,3.45,3.65,4.25,4.48]: b.box((0,-.15,z),(w+.35,.25,.13 if z!=3.65 else .3),m["stone"])
    for xx in [-4.9,-1.10,1.10,4.9]: b.box((xx,-.22,1.92),(.30,.36,3.55),m["stone"])
    door(b,0,.32,m,1.52,2.75)
    for xx in [-3.48,3.48]:
        window(b,xx,2.02,1.92,1.98,m,y=-.15,rows=3)
        for dx in [-.66,-.33,0,.33,.66]: b.box((xx+dx,-.40,2.02),(.025,.03,1.85),m["iron"])
    for i in range(3): b.box((0,-.50-i*.33,.27-i*.08),(2.65,.6,.14),m["stone"])
    b.box((0,d/2,4.4),(w+.3,d+.3,.16),m["roof"])
    b.finish(.005)
    text(name+" / stone frieze","VALENTINE SAVINGS BANK",(0,-.32,3.90),w-.70,.38,m["ink"],col,tr,font)
    return {"name":name,"collection":col,"matrix":tr,"width":w,"depth":d,"height":h,"hero":False}


def chapel(x,y,m,parent,font):
    col=collection("Hill / timber church",parent)
    tr=transform(x,y,0,-.08)
    b=MeshBatch("Church / clapboard and bell tower",col,tr)
    shell(b,7.2,12,5.1,m,"cream",[(-.9,.9,.5,3.1)])
    door(b,0,.5,m,1.8,2.8)
    for side in [-1,1]: window(b,side*2.4,2.3,1,2,m)
    roof(b,7.2,12,5.1,m,2.2,False)
    b.box((0,1.6,7.3),(2.3,2.3,3.5),m["cream"])
    b.box((0,1.6,8.2),(1.3,2.38,1.8),m["interior"])
    for xx in [-1.05,1.05]:
        for yy in [.55,2.65]: b.box((xx,yy,8.7),(.19,.19,2.2),m["trim"])
    b.cylinder((0,1.6,9.7),(0,1.6,12.0),1.65,m["roof"],4,0)
    b.box((0,1.6,12.15),(.10,.10,.8),m["darkwood"])
    b.box((0,1.6,12.25),(.5,.10,.10),m["darkwood"])
    porch(b,7.1,1.5,.53,m,False,False)
    b.finish(.01)
    return col
