from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from OpenGL.GLU import *
from PyQt5.QtWidgets import *
from src.SMD import SMD
from PyQt5.QtOpenGL import *
import numpy as np
import ctypes


def flatten_triangle_data(triangles):
    # careful here, the order of points could invert face normals
    # no vertex optimization for now
    verts = []  # flat array of vertex data (pos, norm, and tex coord)
    inds = []
    ind = 0
    for traingle in triangles:
        for vert in traingle.verts:
            tx = vert.texCoord
            p = vert.pos
            n = vert.norm
            verts.append([p[0], p[1], p[2], n[0], n[1], n[2], tx[0], tx[1]]) #
            inds.append(ind)
            ind += 1

    return np.array(verts, dtype='float32'), np.array(inds, dtype='uint32')


class SimpleVBO:
    def __init__(self, verts: np.array, inds: np.array, shader=None):
        self.verts = verts.copy()
        self.inds = inds.copy()
        self.count = len(self.inds)
        self.vao = GLuint(0)
        self.vbo = GLuint(0)
        self.ebo = GLuint(0)

        glGenVertexArrays(1, self.vao) # main vao
        glGenBuffers(1, self.vbo) # vertex data vbo
        glGenBuffers(1, self.ebo) # index data buffer object (ebo)

        glBindVertexArray(self.vao) # bind the vao we want to load with data

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.inds, GL_STATIC_DRAW)
        float_size = ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*float_size, ctypes.c_void_p(0))  # our vertex pos is at index 0
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8*float_size, ctypes.c_void_p(3*float_size))  # normal at index 1
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8*float_size, ctypes.c_void_p(6*float_size))  # texcoord at index 2
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)

        # clean up opengl stuff
        glBindVertexArray(0) # always unbind the VAO first, it records unbind calls otherwise
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def get_count(self):
        return self.count

    def bind(self):
        glBindVertexArray(self.vao)
        # glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # glEnableVertexAttribArray(0)
        # glEnableVertexAttribArray(1)
        # glEnableVertexAttribArray(2)
        # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)  # our vertex pos is at index 0
        # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3, None)  # normal at index 1
        # glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 6, None)  # texcoord at index 2

    def unbind(self):
        glBindVertexArray(0)
        #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        #glBindBuffer(GL_ARRAY_BUFFER, 0)


class TexturedSMD:
    def __init__(self, smd):
        self.mesh_tri_dict = dict()
        for triangle in smd.triangles:
            if triangle.matName in self.mesh_tri_dict:
                self.mesh_tri_dict[triangle.matName].append(triangle)
            else:
                self.mesh_tri_dict[triangle.matName] = [triangle]

        self.shaded_vbos = dict()
        for k, v in self.mesh_tri_dict.items():
            verts, inds = flatten_triangle_data(v)
            self.shaded_vbos[k] = SimpleVBO(verts, inds)

    def draw(self):
        pass

    def drawWireframe(self, fallback_shader=None):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # enable wireframe drawing mode
        for _, vbo in self.shaded_vbos.items():
            glUseProgram(fallback_shader)
            vbo.bind()  # bind the buffer
            #glDrawArrays(GL_TRIANGLES, 0, vbo.count)
            glDrawElements(GL_TRIANGLES, vbo.count, GL_UNSIGNED_INT, None)  # last parameter must be None
            vbo.unbind()


class SMDPreviewWindow(QGLWidget):
    def __init__(self, *args, **kwargs):
        SMDs = kwargs.pop('SMDs')
        QGLWidget.__init__(self, *args, **kwargs)
        self.setMinimumSize(640, 480)
        self.raw_smds = SMDs
        self.render_objects = list()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the color buffer and depth buffer (blank canvas)

        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.0)
        for object in self.render_objects:
            object.drawWireframe(self.default_shader_program)

        glPopMatrix()
        # we'll render a wireframe for now, since we can't import textures yet

    def resizeGL(self, width, height):
        glViewport(0,0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width/float(height)

        gluPerspective(45.0, aspect, 0.1, 100.0)
        gluLookAt(50.0,50.0,50.0,0.0,0.0,0.0,0.0,1.0,0.0)
        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)  # backface full
        self.render_objects = [TexturedSMD(smd) for smd in self.raw_smds]
        self.default_vert = shaders.compileShader(
            """
            layout (location = 0) in vec3 aPos;
            layout (location = 1) in vec3 aNorm;
            layout (location = 2) in vec2 aTexCoord;

            out vec2 tCord;
    
            void main()
            {
                gl_Position = gl_ModelViewProjectionMatrix  * vec4(aPos, 1.0f);
                tCord = aTexCoord;
            }
            """, GL_VERTEX_SHADER)

        self.default_frag = shaders.compileShader(
            """
            void main() {
                gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f); // plain red
            }
            """, GL_FRAGMENT_SHADER)

        self.default_shader_program = shaders.compileProgram(self.default_vert, self.default_frag)