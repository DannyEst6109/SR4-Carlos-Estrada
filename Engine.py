from gl import Renderer, V3, _color

from obj import Texture

width = 960
height = 540


rend = Renderer(width, height)

modelTexture = Texture("model.bmp")


rend.glLoadModel("model.obj", modelTexture, V3(width/2, height/2, 0), V3(200,200,200))

rend.glFinish("prueba.bmp")