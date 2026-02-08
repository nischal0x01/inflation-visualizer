from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import matplotlib.pyplot as plt
import glfw

# Global variables
shaderProgram = None
vertexBufferObject = None
indexBufferObject = None
framebufferObject = None
vertexArrayObject = None

# Strings containing shader programs written in GLSL
vertexShaderString = """
#version 330
layout(location = 0) in vec3 windowCoordinates;
layout(location = 1) in vec3 vertexColor;
smooth out vec3 fragmentColor;
uniform mat4 windowToClipMat;
void main()
{
    gl_Position = windowToClipMat * vec4(windowCoordinates, 1.0f);
    fragmentColor = vertexColor;
}
"""

fragmentShaderString = """
#version 330
smooth in vec3 fragmentColor;
out vec4 pixelColor;
void main()
{
    pixelColor = vec4(fragmentColor, 1.);
}
"""

def initializeShaders(shaderDict):
    """
    Compiles each shader defined in shaderDict, attaches them to a program object, and links them (i.e., creates executables that will be run on the vertex, geometry, and fragment processors on the GPU). This is more-or-less boilerplate.
    """
    shaderObjects = []
    global shaderProgram
    shaderProgram = glCreateProgram()
    
    for shaderType, shaderString in shaderDict.items():
        shaderObjects.append(glCreateShader(shaderType))
        glShaderSource(shaderObjects[-1], shaderString)
        
        glCompileShader(shaderObjects[-1])
        status = glGetShaderiv(shaderObjects[-1], GL_COMPILE_STATUS)
        if status == GL_FALSE:
            if shaderType is GL_VERTEX_SHADER:
                strShaderType = "vertex"
            elif shaderType is GL_GEOMETRY_SHADER:
                strShaderType = "geometry"
            elif shaderType is GL_FRAGMENT_SHADER:
                strShaderType = "fragment"
            raise RuntimeError("Compilation failure (" + strShaderType + " shader):\n" + glGetShaderInfoLog(shaderObjects[-1]).decode('utf-8'))
        
        glAttachShader(shaderProgram, shaderObjects[-1])
    
    glLinkProgram(shaderProgram)
    status = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
    
    if status == GL_FALSE:
        raise RuntimeError("Link failure:\n" + glGetProgramInfoLog(shaderProgram).decode('utf-8'))
        
    for shader in shaderObjects:
        glDetachShader(shaderProgram, shader)
        glDeleteShader(shader)

def windowToClip(width, height, zNear, zFar):
    """
    Creates elements for an OpenGL-style column-based homogenous transformation matrix that maps points from window space to clip space.
    """
    windowToClipMat = np.zeros(16, dtype = np.float32)
    windowToClipMat[0] = 2 / width
    windowToClipMat[3] = -1
    windowToClipMat[5] = 2 / height
    windowToClipMat[7] = -1
    windowToClipMat[10] = 2 / (zFar - zNear)
    windowToClipMat[11] = -(zFar + zNear) / (zFar - zNear)
    windowToClipMat[15] = 1
    
    return windowToClipMat

def configureShaders(var):
    """
    Modifies the window-to-clip space transform matrix in the vertex shader, but you can use this to configure your shaders however you'd like, of course.
    """
    # Grabs the handle for the uniform input from the shader
    windowToClipMatUnif = glGetUniformLocation(shaderProgram, "windowToClipMat")
    
    # Get input parameters to define a matrix that will be used as the uniform input
    width, height, zNear, zFar = var
    windowToClipMat = windowToClip(width, height, zNear, zFar)
    
    # Assign the matrix to the uniform input in our shader program. Note that GL_TRUE here transposes the matrix because of OpenGL conventions
    glUseProgram(shaderProgram)
    glUniformMatrix4fv(windowToClipMatUnif, 1, GL_TRUE, windowToClipMat)
    
    # We're finished modifying our shader, so we set the program to be used as null to be proper
    glUseProgram(0)

def initializeVertexBuffer():
    """
    Assign the triangular mesh data and the triplets of vertex indices that form the triangles (index data) to VBOs
    """
    # Create a handle and assign the VBO for the mesh data to it
    global vertexBufferObject
    vertexBufferObject = glGenBuffers(1)
    
    # Bind the VBO to the GL_ARRAY_BUFFER target in the OpenGL context
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    
    # Allocate enough memory for this VBO to contain the mesh data
    glBufferData(GL_ARRAY_BUFFER, meshData, GL_STATIC_DRAW)
    
    # Unbind the VBO from the target to be proper
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    # Similar to the above, but for the index data
    global indexBufferObject
    indexBufferObject = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexData, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

def initializeFramebufferObject():
    """
    Create an FBO and assign a texture buffer to it for the purpose of offscreen rendering to the texture buffer
    """
    # Create a handle and assign a texture buffer to it
    renderedTexture = glGenTextures(1)
    
    # Bind the texture buffer to the GL_TEXTURE_2D target in the OpenGL context
    glBindTexture(GL_TEXTURE_2D, renderedTexture)
    
    # Attach a texture 'img' (which should be of unsigned bytes) to the texture buffer. If you don't want a specific texture, you can just replace 'img' with 'None'.
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    
    # Does some filtering on the texture in the texture buffer
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
    # Unbind the texture buffer from the GL_TEXTURE_2D target in the OpenGL context
    glBindTexture(GL_TEXTURE_2D, 0)
    
    # Create a handle and assign a renderbuffer to it
    depthRenderbuffer = glGenRenderbuffers(1)
    
    # Bind the renderbuffer to the GL_RENDERBUFFER target in the OpenGL context
    glBindRenderbuffer(GL_RENDERBUFFER, depthRenderbuffer)
    
    # Allocate enough memory for the renderbuffer to hold depth values for the texture
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
    
    # Unbind the renderbuffer from the GL_RENDERBUFFER target in the OpenGL context
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    
    # Create a handle and assign the FBO to it
    global framebufferObject
    framebufferObject = glGenFramebuffers(1)
    
    # Use our initialized FBO instead of the default GLUT framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferObject)
    
    # Attaches the texture buffer created above to the GL_COLOR_ATTACHMENT0 attachment point of the FBO
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, renderedTexture, 0)
    
    # Attaches the renderbuffer created above to the GL_DEPTH_ATTACHMENT attachment point of the FBO
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRenderbuffer)
    
    # Sees if your GPU can handle the FBO configuration defined above
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError('Framebuffer binding failed, probably because your GPU does not support this FBO configuration.')
    
    # Unbind the FBO, relinquishing the GL_FRAMEBUFFER back to the window manager (i.e. GLUT)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

def resetFramebufferObject():

    glBindFramebuffer(GL_FRAMEBUFFER, framebufferObject)
    
    # Clears any color or depth information in the FBO
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Unbind the FBO, relinquishing the GL_FRAMEBUFFER back to the window manager (i.e. GLUT)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

def initializeVertexArray():
    """
    Creates the VAO to store the VBOs for the mesh data and the index data, 
    """
    # Create a handle and assign a VAO to it
    global vertexArrayObject
    vertexArrayObject = glGenVertexArrays(1)
    
    # Set the VAO as the currently used object in the OpenGL context
    glBindVertexArray(vertexArrayObject)
    
    # Bind the VBO for the mesh data to the GL_ARRAY_BUFFER target in the OpenGL context
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    
    # Specify the location indices for the types of inputs to the shaders
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    
    # Assign the first type of input (which is stored in the VBO beginning at the offset in the fifth argument) to the shaders
    glVertexAttribPointer(0, vertexDim, GL_FLOAT, GL_FALSE, 0, None)
    
    # Calculate the offset in the VBO for the second type of input, specified in bytes (because we used np.float32, each element is 4 bytes)
    colorOffset = c_void_p(vertexDim * numVertices * 4)
    
    # Assign the second type of input, beginning at the offset calculated above, to the shaders
    glVertexAttribPointer(1, vertexDim, GL_FLOAT, GL_FALSE, 0, colorOffset)
    
    # Bind the VBO for the index data to the GL_ELEMENT_ARRAY_BUFFER target in the OpenGL context
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
    
    # Unset the VAO as the current object in the OpenGL context
    glBindVertexArray(0)

def render():
    # Defines what shaders to use
    glUseProgram(shaderProgram)
    
    # Use our initialized FBO instead of the default GLUT framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferObject)
    
    # Set our initialized VAO as the currently used object in the OpenGL context
    glBindVertexArray(vertexArrayObject)
    
    # Draws the mesh triangles defined in the VBO of the VAO above according to the vertices defining the triangles in indexData, which is of unsigned shorts
    glDrawElements(GL_TRIANGLES, indexData.size, GL_UNSIGNED_SHORT, None)
    
    # Being proper
    glBindVertexArray(0)
    glUseProgram(0)


if __name__ == '__main__':
    # Predetermine the dimensions of the viewport/window for the rendering
    width = 100
    height = 100

    # Create a test 100x100 RGB image: all black and a red border.
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[[0, -1], :, 0] = 255
    img[:, [0, -1], 0] = 255
    img = img.tobytes()

    # Define a triangle in window space
    x = np.array([50, 40, 60]) - 1
    y = np.array([20, 40, 40]) - 1
    z = np.ones(x.size)
    vertexCoords = np.c_[x, y, z].astype(np.float32)

    indexData = np.array([[0, 1, 2]], dtype=np.uint16)
    vertexColors = np.eye(3, dtype=np.float32)
    meshData = np.r_[vertexCoords, vertexColors]

    vertexDim = 3
    numVertices = vertexCoords.shape[0]

    zNear = -10
    zFar = 10

    # Initialize GLFW
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    # Set OpenGL version hints (for core profile)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)  # Hidden window for offscreen rendering

    # Create a hidden window (this creates the OpenGL context)
    window = glfw.create_window(width, height, "Offscreen", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    # Make the context current
    glfw.make_context_current(window)

    # Now OpenGL context is valid - proceed with your existing code
    shaderDict = {GL_VERTEX_SHADER: vertexShaderString, GL_FRAGMENT_SHADER: fragmentShaderString}
    initializeShaders(shaderDict)
    configureShaders([width, height, zNear, zFar])

    glViewport(0, 0, width, height)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)

    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LEQUAL)
    glDepthRange(0.0, 1.0)

    initializeVertexBuffer()
    initializeFramebufferObject()
    initializeVertexArray()

    render()

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

    rendering = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    plt.imshow(rendering)
    plt.show()

    # Cleanup
    glfw.terminate()