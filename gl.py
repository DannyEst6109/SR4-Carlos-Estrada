import struct
from collections import namedtuple
from obj import Obj

from mate import pPunto, pCruz, restaVect, dividir, normalizar

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def char(c):
    # utiliza 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # utiliza 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # utiliza 4 bytes
    return struct.pack('=l', d)

def _color(r, g, b):
    # Acepta valores de 0 a 1 empleando solo 3 bytes
    return bytes([ int(b * 255), int(g * 255), int(r * 255)])

BLACK = _color(0, 0, 0)
WHITE = _color(1, 1, 1)

def baryCoords(A, B, C, P):
    try:
        u = (((B.y - C.y) * (P.x - C.x) + (C.x - B.x) * (P.y - C.y)) /
            ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))

        v = (((C.y - A.y) * (P.x - C.x) + (A.x - C.x) * (P.y - C.y)) /
             ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))

        w = 1 - u - v

    except:
        return -1, -1, -1

    return u, v, w

class Renderer(object):
    def __init__(self, width, height):
        self.curr_color = WHITE
        self.clear_color = BLACK
        self.glCreateWindow(width, height)

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewport(0, 0, width, height)

    def glViewport(self, x, y, width, height):
        #Definicion de Viewport
        self.vpx = x
        self.vpy = y
        self.vpwidth = width
        self.vpheight = height

    def glClearColor(self, r, g, b):
        self.clear_color = _color(r, g, b)

    def glClear(self):
        self.pixels = [[self.clear_color for y in range(self.height)] for x in range(self.width)]

        self.zbuffer = [[ -float('inf')for y in range(self.height)]
                        for x in range(self.width)]

    def glColor(self, r, g, b):
        self.curr_color = _color(r, g, b)

    def glPoint(self, x, y, color = None):
        if x < self.vpx or x >= self.vpx + self.vpwidth or y < self.vpy or y >= self.vpy + self.vpheight:
            return

        if (0 < x < self.width) and (0 < y < self.height):
            self.pixels[int(x)][int(y)] = color or self.curr_color

    def glLine(self, v0, v1, color = None):
        x0 = v0.x
        x1 = v1.x
        y0 = v0.y
        y1 = v1.y

        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y1, color)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.5
        m = dy/dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x, color)
            else:
                self.glPoint(x, y, color)

            offset += m
            if offset >= limit:
                y += 1 if y0 < y1 else -1
                limit += 1


    def glLine_NDC(self, v0, v1, color = None):

        x0 = int((v0.x + 1) * (self.vpwidth/2) + self.vpx)
        x1 = int((v1.x + 1) * (self.vpwidth/2) + self.vpx)
        y0 = int((v0.y + 1) * (self.vpheight/2) + self.vpy)
        y1 = int((v1.y + 1) * (self.vpheight/2) + self.vpy)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        steep = dy > dx

        if steep:

            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:

            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        offset = 0
        limit = 0.5
        m = dy/dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x, color)
            else:
                self.glPoint(x, y, color)

            offset += m
            if offset >= limit:
                y += 1 if y0 < y1 else -1
                limit += 1


    def glPoint_NDC(self, x, y, color = None):

        x = int((x+1) * (self.vpwidth/2) + self.vpx)
        y = int((y+1) * (self.vpheight/2) + self.vpy)

        if x < self.vpx or x >= self.vpx + self.vpwidth or y < self.vpy or y >= self.vpy + self.vpheight:
            return

        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[int(x)][int(y)] = color or self.curr_color


    def glLoadModel(self, filename, texture = None, translate= V3(0,0,0), scale=V3(1,1,1)):

        model = Obj(filename)

        light = V3(0, 0, 1)


        light = dividir(light, normalizar(light))

        for face in model.faces:
            vertConteo = len(face)

            vert0 = model.vertices[face[0][0] - 1]
            vert1 = model.vertices[face[1][0] - 1]
            vert2 = model.vertices[face[2][0] - 1]

            vt0 = model.texcoords[face[0][1] - 1]
            vt1 = model.texcoords[face[1][1] - 1]
            vt2 = model.texcoords[face[2][1] - 1]

            a = self.glTransform(vert0, translate, scale)
            b = self.glTransform(vert1, translate, scale)
            c = self.glTransform(vert2, translate, scale)

            if vertConteo == 4:
                vert3 = model.vertices[face[3][0] - 1]
                vt3 = model.texcoords[face[3][1] - 1]
                d = self.glTransform(vert3, translate, scale)


            normal = pCruz(restaVect(vert1, vert0), restaVect(vert2, vert0))
            normal = dividir(normal, normalizar(normal))
            intensity = pPunto(normal, light)

            if intensity > 1:
                intensity = 1
            elif intensity < 0:
                intensity = 0
                
            self.glTriangle_bc(a, b, c, texCoords=(vt0, vt1, vt2), texture = texture, intensity=intensity)

            if vertConteo == 4:
                self.glTriangle_bc(a, c, d, texCoords=(vt0, vt2, vt3), texture = texture, intensity=intensity)


    def glTriangle(self, A, B, C, color = None):

        self.glLine(A,B,color)
        self.glLine(B,C,color)
        self.glLine(C,A,color)

        if A.y < B.y:
            A, B = B, A
        if A.y < C.y:
            A, C = C, A
        if B.y < C.y:
            B, C = C, B

        def flatBottomTriangle(v1, v2, v3):
            d_21 = (v2.x - v1.x) / (v2.y - v1.y)
            d_31 = (v3.x - v1.x) / (v3.y - v1.y)

            x1 = v2.x
            x2 = v3.x

            for y in range(v2.y, v1.y + 1):
                self.glLine(V2(int(x1), y), V2(int(x2), y), color)
                x1 += d_21
                x2 += d_31

        def flatTopTriangle(v1, v2, v3):
            d_31 = (v3.x - v1.x) / (v3.y - v1.y)
            d_32 = (v3.x - v2.x) / (v3.y - v2.y)

            x1 = v3.x
            x2 = v3.x

            for y in range(v3.y, v1.y + 1):
                self.glLine(V2(int(x1), y), V2(int(x2), y), color)
                x1 += d_31
                x2 += d_32


        if B.y == C.y:
            flatBottomTriangle(A, B, C)
        elif A.y == B.y:
            flatTopTriangle(A, B, C)
        else:
            D = V2(A.x + ((B.y - A.y) / (C.y - A.y)) * (C.x - A.x), B.y)

            flatBottomTriangle(A, B, D)

            flatTopTriangle(B, D, C)


    def glTriangle_bc(self, A, B, C, texCoords = (), texture = None, color = None, intensity = 1):

        minX = round(min(A.x, B.x, C.x))
        minY = round(min(A.y, B.y, C.y))
        maxX = round(max(A.x, B.x, C.x))
        maxY = round(max(A.y, B.y, C.y))

        for x in range(minX, maxX + 1):
            for y in range(minY, maxY + 1):

                u, v, w = baryCoords(A, B, C, V2(x, y))

                if u >= 0 and v >= 0 and w >= 0:
                    z = A.z * u + B.z * v + C.z * w

                    if texture:
                        tA, tB, tC = texCoords
                        tx = tA[0] * u + tB[0] * v + tC[0] * w
                        ty = tA[1] * u + tB[1] * v + tC[1] * w
                        color = texture.getColor(tx, ty)
                        
                    if z > self.zbuffer[x][y]:
                        
                        self.glPoint(x, y, _color( color[2] * intensity/255,
                                                  color[1] * intensity/255,
                                                  color[0] * intensity/255))
                        self.zbuffer[x][y] = z

    def glTransform(self, vertex, translate=V3(0,0,0), scale=V3(1,1,1)):
        return V3(vertex[0] * scale.x + translate.x,
                  vertex[1] * scale.y + translate.y,
                  vertex[2] * scale.z + translate.z)


    def glFinish(self, filename):
        with open(filename, "wb") as file:

            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write((dword(14 + 40)))

            # InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color Table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])