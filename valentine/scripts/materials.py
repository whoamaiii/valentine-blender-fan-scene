"""Scene materials: scanned surfaces, weathered paint, glass, water and foliage."""
from pathlib import Path
import bpy

TEX=Path(__file__).resolve().parents[1]/"textures"


def node(tree, typ, name=None):
    n=tree.nodes.new(typ)
    if name: n.label=name
    return n


def base(name, color=(.2,.2,.2), rough=.65, metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m,p


def image_node(tree, asset, channel, coordinate=None):
    n=node(tree,"ShaderNodeTexImage",f"Poly Haven / {asset} / {channel}")
    n.image=bpy.data.images.load(str(TEX/f"{asset}_{channel}.jpg"),check_existing=True)
    if channel!="Diffuse": n.image.colorspace_settings.name="Non-Color"
    if coordinate: tree.links.new(coordinate,n.inputs["Vector"])
    return n


def wood(name, tint, paint=.0):
    m,p=base(name,tint,.79)
    t=m.node_tree
    scan=image_node(t,"rough_wood","Diffuse")
    nm=image_node(t,"rough_wood","nor_gl")
    rough=image_node(t,"rough_wood","Rough")
    normal=node(t,"ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value=.30
    t.links.new(nm.outputs["Color"],normal.inputs["Color"])
    t.links.new(normal.outputs["Normal"],p.inputs["Normal"])
    multiply=node(t,"ShaderNodeMixRGB")
    multiply.blend_type="MULTIPLY"
    multiply.inputs[0].default_value=1
    multiply.inputs[2].default_value=(*tint,1)
    t.links.new(scan.outputs["Color"],multiply.inputs[1])
    col=multiply.outputs["Color"]
    if paint:
        geom=node(t,"ShaderNodeTexCoord")
        noise=node(t,"ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=1.7
        noise.inputs["Detail"].default_value=4.2
        noise.inputs["Roughness"].default_value=.74
        t.links.new(geom.outputs["Object"],noise.inputs["Vector"])
        ramp=node(t,"ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.33
        ramp.color_ramp.elements[1].position=.7
        t.links.new(noise.outputs["Fac"],ramp.inputs[0])
        mix=node(t,"ShaderNodeMixRGB")
        t.links.new(ramp.outputs["Color"],mix.inputs[0])
        t.links.new(col,mix.inputs[1])
        mix.inputs[2].default_value=(*[v*paint for v in tint],1)
        col=mix.outputs["Color"]
    attr=node(t,"ShaderNodeVertexColor")
    attr.layer_name="BoardTone"
    variation=node(t,"ShaderNodeMixRGB")
    variation.blend_type="MULTIPLY"
    variation.inputs[0].default_value=.55
    t.links.new(col,variation.inputs[1])
    t.links.new(attr.outputs["Color"],variation.inputs[2])
    t.links.new(variation.outputs["Color"],p.inputs["Base Color"])
    adjust=node(t,"ShaderNodeMapRange")
    adjust.inputs["To Min"].default_value=.46
    adjust.inputs["To Max"].default_value=.91
    t.links.new(rough.outputs["Color"],adjust.inputs["Value"])
    t.links.new(adjust.outputs["Result"],p.inputs["Roughness"])
    return m


def aged_lettering(name, color):
    m,p=base(name,color,.91)
    t=m.node_tree
    tex=node(t,"ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=48
    tex.inputs["Detail"].default_value=3
    ramp=node(t,"ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.38
    ramp.color_ramp.elements[0].color=(*[c*.35 for c in color],1)
    ramp.color_ramp.elements[1].position=.7
    ramp.color_ramp.elements[1].color=(*color,1)
    t.links.new(tex.outputs["Fac"],ramp.inputs[0])
    t.links.new(ramp.outputs["Color"],p.inputs["Base Color"])
    bump=node(t,"ShaderNodeBump")
    bump.inputs["Distance"].default_value=.0015
    bump.inputs["Strength"].default_value=.28
    t.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    t.links.new(bump.outputs["Normal"],p.inputs["Normal"])
    return m


def ground(name, asset, scale, darken=1, wet=.0):
    m,p=base(name,(.1,.065,.036),.85)
    t=m.node_tree
    tc=node(t,"ShaderNodeTexCoord")
    mapping=node(t,"ShaderNodeVectorMath")
    mapping.operation="SCALE"
    mapping.inputs[3].default_value=scale
    t.links.new(tc.outputs["Object"],mapping.inputs[0])
    coord=mapping.outputs["Vector"]
    diffuse=image_node(t,asset,"Diffuse",coord)
    normal=image_node(t,asset,"nor_gl",coord)
    height=image_node(t,asset,"Displacement",coord)
    rough=image_node(t,asset,"Rough",coord)
    mix=node(t,"ShaderNodeMixRGB")
    mix.blend_type="MULTIPLY"
    mix.inputs[0].default_value=1
    mix.inputs[2].default_value=(darken,darken*.64,darken*.36,1)
    t.links.new(diffuse.outputs["Color"],mix.inputs[1])
    t.links.new(mix.outputs["Color"],p.inputs["Base Color"])
    nm=node(t,"ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value=.40
    t.links.new(normal.outputs["Color"],nm.inputs["Color"])
    bump=node(t,"ShaderNodeBump")
    bump.inputs["Distance"].default_value=.045
    bump.inputs["Strength"].default_value=.4
    t.links.new(height.outputs["Color"],bump.inputs["Height"])
    t.links.new(nm.outputs["Normal"],bump.inputs["Normal"])
    t.links.new(bump.outputs["Normal"],p.inputs["Normal"])
    mr=node(t,"ShaderNodeMapRange")
    mr.inputs["To Min"].default_value=.57 if wet else .69
    mr.inputs["To Max"].default_value=.83 if wet else .94
    t.links.new(rough.outputs["Color"],mr.inputs["Value"])
    t.links.new(mr.outputs["Result"],p.inputs["Roughness"])
    return m


def mottled(name, colors, scale=4, rough=.9):
    m,p=base(name,colors[0],rough)
    t=m.node_tree
    tex=node(t,"ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=4
    ramp=node(t,"ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(*colors[0],1)
    ramp.color_ramp.elements[1].color=(*colors[1],1)
    t.links.new(tex.outputs["Fac"],ramp.inputs[0])
    t.links.new(ramp.outputs["Color"],p.inputs["Base Color"])
    bump=node(t,"ShaderNodeBump")
    bump.inputs["Strength"].default_value=.3
    bump.inputs["Distance"].default_value=.035
    t.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    t.links.new(bump.outputs["Normal"],p.inputs["Normal"])
    return m


def verge():
    m=ground("Town / soil fading into pasture","mud_forest",.44,.63)
    t=m.node_tree
    p=t.nodes.get("Principled BSDF")
    soil=p.inputs["Base Color"].links[0].from_socket
    position=node(t,"ShaderNodeNewGeometry")
    xyz=node(t,"ShaderNodeSeparateXYZ")
    t.links.new(position.outputs["Position"],xyz.inputs[0])
    def operation(kind,a,b):
        op=node(t,"ShaderNodeMath")
        op.operation=kind
        if isinstance(a,(int,float)):op.inputs[0].default_value=a
        else:t.links.new(a,op.inputs[0])
        if isinstance(b,(int,float)):op.inputs[1].default_value=b
        else:t.links.new(b,op.inputs[1])
        return op.outputs[0]
    xx=operation("SUBTRACT",operation("ABSOLUTE",xyz.outputs["X"],0),77)
    yy=operation("SUBTRACT",operation("ABSOLUTE",operation("ADD",xyz.outputs["Y"],7),0),26)
    edge=operation("MAXIMUM",xx,yy)
    noise=node(t,"ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=.32
    noise.inputs["Detail"].default_value=4
    t.links.new(position.outputs["Position"],noise.inputs[0])
    border=operation("ADD",edge,operation("MULTIPLY",operation("SUBTRACT",noise.outputs["Fac"],.5),9))
    mask=node(t,"ShaderNodeMapRange")
    mask.inputs["From Min"].default_value=-2.5
    mask.inputs["From Max"].default_value=3.0
    t.links.new(border,mask.inputs["Value"])
    grass=node(t,"ShaderNodeValToRGB")
    grass.color_ramp.elements[0].color=(.040,.058,.016,1)
    grass.color_ramp.elements[1].color=(.18,.21,.075,1)
    t.links.new(noise.outputs["Fac"],grass.inputs[0])
    blend=node(t,"ShaderNodeMixRGB")
    t.links.new(mask.outputs["Result"],blend.inputs[0])
    t.links.new(soil,blend.inputs[1])
    t.links.new(grass.outputs["Color"],blend.inputs[2])
    t.links.new(blend.outputs[0],p.inputs["Base Color"])
    return m


def palette():
    m={}
    for key,tint,paint in [
        ("wood",(.52,.37,.23),0),("grey",(.53,.50,.43),0),("darkwood",(.22,.15,.095),0),
        ("red",(.38,.22,.16),.7),("cream",(.62,.59,.46),.77),("green",(.19,.29,.21),.7),
        ("blue",(.20,.28,.31),.65),("trim",(.58,.53,.39),.75),("roof",(.25,.23,.19),0)]:
        m[key]=wood("Timber / "+key,tint,paint)
    m["letter"]=aged_lettering("Weathered warm white sign paint",(.78,.73,.58))
    m["gold"]=aged_lettering("Faded ochre sign paint",(.7,.49,.22))
    m["ink"]=aged_lettering("Charcoal printed ink",(.033,.027,.021))
    m["iron"]=mottled("Oxidised forged iron",[(.025,.029,.027),(.095,.063,.035)],12,.6)
    m["iron"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=.72
    m["stone"]=mottled("Fieldstone foundation",[(.16,.15,.12),(.31,.28,.21)],5)
    m["brick"]=mottled("Soot and brick",[(.14,.063,.036),(.30,.14,.076)],9)
    m["grass"]=mottled("Pasture and town verges",[(.06,.09,.026),(.19,.24,.065)],3)
    m["leaf"]=mottled("Foliage / summer green",[(.048,.095,.019),(.16,.22,.047)],4,.8)
    m["pine"]=mottled("Foliage / distant pine",[(.026,.065,.030),(.09,.14,.048)],3)
    m["straw"]=mottled("Dry straw and seed heads",[(.20,.13,.045),(.40,.31,.12)],14)
    m["mud"]=ground("Road / compacted damp earth","brown_mud",.40,.72,True)
    m["soil"]=ground("Road / dry roadside debris","mud_forest",.44,.63,False)
    m["verge"]=verge()
    m["paper"]=mottled("Aged paper",[(.38,.30,.17),(.72,.65,.43)],6)
    m["canvas"]=mottled("Weathered wagon canvas",[(.29,.24,.15),(.62,.54,.34)],18)
    m["interior"],_=base("Unlit interior recess",(.014,.011,.008),.95)
    m["glass"],p=base("Old slightly green window glass",(.025,.039,.032),.22)
    p.inputs["Metallic"].default_value=.15
    p.inputs["Transmission Weight"].default_value=.3
    p.inputs["Coat Weight"].default_value=.28
    m["water"],p=base("Shallow muddy puddles",(.050,.032,.016),.25)
    p.inputs["IOR"].default_value=1.333
    p.inputs["Coat Weight"].default_value=.6
    p.inputs["Coat Roughness"].default_value=.21
    t=m["water"].node_tree
    tex=node(t,"ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=32
    bump=node(t,"ShaderNodeBump")
    bump.inputs["Distance"].default_value=.003
    bump.inputs["Strength"].default_value=.1
    t.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    t.links.new(bump.outputs["Normal"],p.inputs["Normal"])
    m["flame"],p=base("Lantern / warm flame",(1,.33,.045),.3)
    p.inputs["Emission Color"].default_value=(1,.36,.055,1)
    p.inputs["Emission Strength"].default_value=4
    return m
