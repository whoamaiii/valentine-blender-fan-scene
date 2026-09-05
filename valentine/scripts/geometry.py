"""Small explicit mesh builders. Coordinates use metres; fronts face local -Y."""
import math
import random
import bpy
from mathutils import Matrix, Vector


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def transform(x=0, y=0, z=0, rotation=0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(rotation, 4, "Z")


class MeshBatch:
    def __init__(self, name, target, matrix=None):
        self.name, self.target = name, target
        self.matrix = matrix if matrix is not None else Matrix.Identity(4)
        self.vertices, self.faces, self.indices, self.uvs, self.colors = [], [], [], [], []
        self.materials = []
        self.vertex_groups=[]
        self._group=0
        self._active_group=None

    def begin_solid(self):
        previous=self._active_group
        self._group+=1
        self._active_group=self._group
        return previous

    def polygon(self, vertices, mat, uv=None, color=(1, 1, 1, 1)):
        offset = len(self.vertices)
        self.vertices.extend([tuple(self.matrix @ Vector(v)) for v in vertices])
        if self._active_group is None:
            self._group+=1
        self.vertex_groups.extend([self._active_group if self._active_group is not None else self._group]*len(vertices))
        self.faces.append(tuple(range(offset, offset + len(vertices))))
        if mat not in self.materials:
            self.materials.append(mat)
        self.indices.append(self.materials.index(mat))
        self.uvs.append(uv or [(v[0], v[1]) for v in vertices])
        self.colors.append(color)

    def box(self, center, size, mat, rotation=None, tint=1.0):
        previous=self.begin_solid()
        center, half = Vector(center), Vector(size) * .5
        points = [Vector((x * half.x, y * half.y, z * half.z)) for x,y,z in
                  [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        points = [center + (rotation @ p if rotation is not None else p) for p in points]
        faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        lengths = [(size[0],size[1]),(size[0],size[1]),(size[0],size[2]),(size[1],size[2]),(size[0],size[2]),(size[1],size[2])]
        for face,(a,b) in zip(faces,lengths):
            u,v = random.uniform(0,8),random.uniform(0,8)
            # Scan grain follows V. Align its long direction to each plank face.
            if a >= b:
                uv=[(u,v),(u,v+a/2.0),(u+b/1.2,v+a/2.0),(u+b/1.2,v)]
            else:
                uv=[(u,v),(u+a/1.2,v),(u+a/1.2,v+b/2.0),(u,v+b/2.0)]
            self.polygon([points[i] for i in face], mat, uv, (tint,tint,tint,1))
        self._active_group=previous

    def beam(self, start, end, thickness, mat, width=None, tint=1):
        start,end = Vector(start),Vector(end)
        direction=end-start
        rotation=direction.to_track_quat("Z","Y").to_matrix()
        self.box((start+end)*.5,(width or thickness,thickness,direction.length),mat,rotation,tint)

    def cylinder(self, start, end, radius, mat, sides=12, end_radius=None, tint=1):
        previous=self.begin_solid()
        a,b=Vector(start),Vector(end)
        delta=b-a
        rotation=delta.to_track_quat("Z","Y").to_matrix()
        r2=radius if end_radius is None else end_radius
        ring1=[a+rotation@Vector((radius*math.cos(t*math.tau/sides),radius*math.sin(t*math.tau/sides),0)) for t in range(sides)]
        ring2=[b+rotation@Vector((r2*math.cos(t*math.tau/sides),r2*math.sin(t*math.tau/sides),0)) for t in range(sides)]
        for i in range(sides):
            j=(i+1)%sides
            points=[ring1[i],ring1[j],ring2[j]] if r2==0 else [ring1[i],ring1[j],ring2[j],ring2[i]]
            uv=[(i/sides,0),((i+1)/sides,0),((i+1)/sides,delta.length),(i/sides,delta.length)]
            self.polygon(points,mat,uv[:len(points)],(tint,tint,tint,1))
        self.polygon(list(reversed(ring1)),mat)
        if r2>0:self.polygon(ring2,mat)
        self._active_group=previous

    def ring(self, center, radius, thickness, depth, mat, rotation=None, sides=32):
        previous=self.begin_solid()
        center=Vector(center)
        rot=rotation if rotation is not None else Matrix.Identity(3)
        rings=[]
        for z,r in [(-depth/2,radius-thickness/2),(-depth/2,radius+thickness/2),(depth/2,radius+thickness/2),(depth/2,radius-thickness/2)]:
            rings.append([center+rot@Vector((r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),z)) for i in range(sides)])
        for k in range(4):
            for i in range(sides):
                j=(i+1)%sides
                self.polygon([rings[k][i],rings[k][j],rings[(k+1)%4][j],rings[(k+1)%4][i]],mat)
        self._active_group=previous

    def finish(self, bevel=0, smooth=False):
        if not self.vertices:
            return None
        mesh=bpy.data.meshes.new(self.name)
        # Weld only within each solid. Merging touching planks into one topological
        # junction creates non-manifold bevel inputs and can crash Blender 5.1.
        unique,lookup,remap=[],{},[]
        for v,group in zip(self.vertices,self.vertex_groups):
            key=(group,)+tuple(round(c,6) for c in v)
            if key not in lookup:
                lookup[key]=len(unique)
                unique.append(v)
            remap.append(lookup[key])
        mesh.from_pydata(unique,[],[tuple(remap[i] for i in face) for face in self.faces])
        mesh.update()
        for mat in self.materials: mesh.materials.append(mat)
        uv=mesh.uv_layers.new(name="SurfaceUV")
        color=mesh.color_attributes.new(name="BoardTone",type="BYTE_COLOR",domain="CORNER")
        for poly,idx,coords,tone in zip(mesh.polygons,self.indices,self.uvs,self.colors):
            poly.material_index=idx
            poly.use_smooth=smooth
            for li,uvp in zip(poly.loop_indices,coords):
                uv.data[li].uv=uvp
                color.data[li].color=tone
        obj=bpy.data.objects.new(self.name,mesh)
        self.target.objects.link(obj)
        if bevel:
            mod=obj.modifiers.new("Worn edge highlights","BEVEL")
            mod.width=bevel
            mod.segments=1
            mod.limit_method="ANGLE"
        return obj


def curve(name, points, radius, material, target, matrix=None):
    data=bpy.data.curves.new(name,"CURVE")
    data.dimensions="3D"
    data.resolution_u=12
    data.bevel_depth=radius
    data.bevel_resolution=2
    spline=data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points):
        v=Vector(co)
        if matrix is not None: v=matrix@v
        point.co=(*v,1)
    obj=bpy.data.objects.new(name,data)
    target.objects.link(obj)
    data.materials.append(material)
    return obj


def text(name, body, position, width, size, mat, target, matrix=None, font=None, align="CENTER"):
    data=bpy.data.curves.new(name,"FONT")
    data.body=body
    data.align_x=align
    data.align_y="CENTER"
    data.size=size
    data.space_character=1.07
    data.extrude=.0008
    data.resolution_u=8
    if font: data.font=font
    obj=bpy.data.objects.new(name,data)
    target.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(math.pi/2,0,0)
    data.materials.append(mat)
    bpy.context.view_layer.update()
    if obj.dimensions.x>0: obj.scale.x*=min(1.35,width/obj.dimensions.x)
    bpy.context.view_layer.update()
    if matrix is not None: obj.matrix_world=matrix@obj.matrix_world
    return obj


def instance(source, name, position, target, scale=1, angle=0):
    obj=bpy.data.objects.new(name,source.data)
    target.objects.link(obj)
    obj.location=position
    obj.scale=(scale,scale,scale) if isinstance(scale,(int,float)) else scale
    obj.rotation_euler.z=angle
    for modifier in source.modifiers:
        if modifier.type=="BEVEL":
            mod=obj.modifiers.new(modifier.name,"BEVEL")
            mod.width=modifier.width
            mod.segments=modifier.segments
    return obj
