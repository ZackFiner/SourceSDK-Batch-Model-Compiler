from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from OpenGL.GLU import *
import glm
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
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
            verts.append([p[0], p[2], p[1], n[0], n[2], n[1], tx[0], tx[1]]) #
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

    def set_transform(self, shader, transform):
        uniform_location = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(uniform_location, 1, GL_FALSE, glm.value_ptr(transform))

    def drawWireframe(self, fallback_shader=None, transform=glm.identity(glm.mat4)):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # enable wireframe drawing mode
        for _, vbo in self.shaded_vbos.items():
            glUseProgram(fallback_shader)
            self.set_transform(fallback_shader, transform)
            vbo.bind()  # bind the buffer
            #glDrawArrays(GL_TRIANGLES, 0, vbo.count)
            glDrawElements(GL_TRIANGLES, vbo.count, GL_UNSIGNED_INT, None)  # last parameter must be None
            vbo.unbind()


class RenderContainer:
    def __init__(self, smd, transforms=None, instances=None,  render=True):
        self.smd = smd
        self.render = render
        self.transforms = transforms
        self.instances = instances

    def draw(self):
        pass


class SMDPreviewWindow(QGLWidget):
    def __init__(self, *args, **kwargs):
        SMDs = kwargs.pop('SMDs')
        QGLWidget.__init__(self, *args, **kwargs)
        self.setMinimumSize(640, 480)
        self.raw_smds = SMDs
        self.render_objects = list()
        self.render_dict = dict() # this will be used to determine which objects should be rendered/what transformations

        self.viewport_transform = dict()
        self.setMouseTracking(True)  # we need this for drag, zoom, and pan

        self.camera_lookdir = glm.vec3(1.0,0.0,0.0)
        self.camera_up = glm.vec3(0.0,1.0,0.0)
        self.camera_zoom = 50.0
        self.center_pos = glm.vec3(0.0)


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the color buffer and depth buffer (blank canvas)

        for idx, object in enumerate(self.render_objects):
            if self.render_dict[idx].render:
                object.drawWireframe(self.default_shader_program, self.viewport_transform['state'])

        # we'll render a wireframe for now, since we can't import textures yet

    def resizeGL(self, width, height):
        glViewport(0,0, width, height)
        aspect = width / float(height)
        identity = glm.mat4()
        perspective = glm.perspective(45.0, aspect, 0.1, 10000.0)
        camera = glm.lookAt(self.camera_lookdir*self.camera_zoom + self.center_pos, self.center_pos, self.camera_up)

        self.viewport_transform['identity'] = identity
        self.viewport_transform['camera'] = camera
        self.viewport_transform['projection'] = perspective
        self.viewport_transform['state'] = perspective*camera*identity
        self.dragging = set()
        self.mouse_x = -1
        self.mouse_y = -1

    def mousePressEvent(self, event):
        lbutton = event.buttons() & QtCore.Qt.LeftButton
        mbutton = event.buttons() & QtCore.Qt.MiddleButton
        if lbutton and 1 not in self.dragging:
            self.dragging.add(1)

        if mbutton and 2 not in self.dragging:
            self.dragging.add(2)

        self.mouse_x = event.globalPos().x()
        self.mouse_y = event.globalPos().y()


    def mouseReleaseEvent(self, event):
        lbutton = event.buttons() & QtCore.Qt.LeftButton
        mbutton = event.buttons() & QtCore.Qt.MiddleButton

        if not lbutton:
            self.dragging.discard(1)

        if not mbutton:
            self.dragging.discard(2)

    def refresh_camera_matrix(self):
        self.viewport_transform['camera'] = glm.lookAt(self.camera_lookdir * self.camera_zoom + self.center_pos,
                                                       self.center_pos,
                                                       self.camera_up)

    def refresh_state_matrix(self):
        self.refresh_camera_matrix()
        self.viewport_transform['state'] = self.viewport_transform['projection'] * \
                                           self.viewport_transform['camera'] * \
                                           self.viewport_transform['identity']

    def rotate_camera(self, dX, dY):
        right = glm.normalize(glm.cross(self.camera_lookdir, self.camera_up))
        rotation = glm.rotate(glm.rotate(glm.mat4(), dY, right), dX, glm.vec3(0,1,0))
        self.camera_lookdir = glm.vec3(glm.vec4(self.camera_lookdir, 1.0) * rotation)
        self.camera_up = glm.vec3(glm.vec4(self.camera_up, 1.0) * rotation)

        self.refresh_state_matrix()

    def pan_camera(self, dX, dY):
        right = glm.normalize(glm.cross(self.camera_lookdir, self.camera_up))
        self.center_pos += self.camera_up*dY + right*dX
        self.refresh_state_matrix()

    def zoom_camera(self, dZ):
        self.camera_zoom = glm.max(self.camera_zoom + dZ, 0)
        self.refresh_state_matrix()

    def mouseMoveEvent(self, event):
        if len(self.dragging):
            nX = event.globalPos().x()
            nY = event.globalPos().y()
            dX = nX - self.mouse_x
            dY = nY - self.mouse_y
            self.mouse_x = nX
            self.mouse_y = nY
            mbutton = event.buttons() & QtCore.Qt.MiddleButton
            lbutton = event.buttons() & QtCore.Qt.LeftButton
            if mbutton:
                self.pan_camera(dX*0.5, dY*0.5)
            else:
                self.rotate_camera(dX*0.05, -dY*0.05)
            self.update()

    def wheelEvent(self, event):

        dz = event.angleDelta()
        self.zoom_camera(-dz.y()*0.1)
        self.update()

    def toggle_render(self, idx, value):
        self.render_dict[idx].render = value
        self.update()

    def initializeGL(self):
        glClearColor(0.0, 0.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)  # backface full


        for idx, smd in enumerate(self.raw_smds):
            built_smd = TexturedSMD(smd)
            self.render_objects.append(built_smd)
            self.render_dict[idx] = RenderContainer(built_smd)

        self.default_vert = shaders.compileShader(
            """
            #version 430 core
            
            layout (location = 0) in vec3 aPos;
            layout (location = 1) in vec3 aNorm;
            layout (location = 2) in vec2 aTexCoord;
            
            uniform mat4 transform;
            out vec2 tCord;
    
            void main()
            {
                gl_Position = transform  * vec4(aPos, 1.0f);
                tCord = aTexCoord;
            }
            """, GL_VERTEX_SHADER)



        self.default_frag = shaders.compileShader(
            """
            #version 430 core
            void main() {
                gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f); // plain red
            }
            """, GL_FRAGMENT_SHADER)

        self.default_shader_program = shaders.compileProgram(self.default_vert, self.default_frag)



class SMDRenderWindow(QWidget):
    def __init__(self, *args, **kwargs):
        SMDs = kwargs.pop('SMDs')
        SMD_names = kwargs.pop('SMD_names')
        QWidget.__init__(self, *args, **kwargs)

        self.render_window = SMDPreviewWindow(SMDs = SMDs)
        layout = QVBoxLayout()
        self.smd_render_selector = QWidget()
        selector_layout = QVBoxLayout()

        def build_render_func(idx):
            def func(state):
                self.render_window.toggle_render(idx, state)
            return func

        for idx, name in enumerate(SMD_names):
            selector = QCheckBox(name)
            selector.setChecked(True)
            selector.stateChanged.connect(build_render_func(idx))
            selector_layout.addWidget(selector)

        self.smd_render_selector.setLayout(selector_layout)

        layout.addWidget(self.render_window)
        layout.addWidget(self.smd_render_selector)

        self.setLayout(layout)

