import time
import numpy as np
import glfw
from OpenGL import GL
import imgui
from imgui.integrations.glfw import GlfwRenderer

from modules.stream import IMUStream
from modules.plot import LineData2D #, LineData3D
from modules.data_rendering import LineRenderer2D, OpenGLApp #, LineRenderer3D

# Constants and Global Variables
TITLE = "Realtime IMU Data"
NUM_POINTS = 200
FPS = 0

def init_window():
    """Initializes and returns a GLFW window."""
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)

    window = glfw.create_window(800, 800, TITLE, None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window can't be created")
    glfw.make_context_current(window)

    #OpenGL Version Check
    opengl_version = GL.glGetString(GL.GL_VERSION)
    print(f"OpenGL version: {opengl_version.decode('utf-8')}")

    #OpenGL Line Width Check
    line_width_range = check_line_width_support()
    return window

def check_line_width_support():
    range = GL.glGetFloatv(GL.GL_LINE_WIDTH_RANGE)
    print(f"Supported line width range: {range[0]} to {range[1]}")
    return range

def main():
    if not glfw.init():
        raise Exception("GLFW can't be initialized")
    
    window = init_window()
    opengl_app = OpenGLApp(window)
    opengl_app.init_gl()

    # stream = Stream('/dev/cu.usbserial-0283D2D2', 1000000, record=False, read_file=False)
    stream = IMUStream('/dev/cu.usbserial-028574DD', 1000000, record=False, read_file=False)



    line_datas = [LineData2D(NUM_POINTS) for _ in range(6)]# + [LineData3D(NUM_POINTS)] #[LineData3D(NUM_POINTS)]
    line_renderers = [LineRenderer2D(NUM_POINTS) for _ in range(6)]# + [LineRenderer3D(NUM_POINTS)] #
    
    for renderer in line_renderers:
        opengl_app.add_line_renderer(renderer)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        data = None
        while not stream.data_queue.empty():
            data, FPS = stream.get_data()
            line_datas[0].update(data[0, 0])
            line_datas[1].update(data[0, 1])
            line_datas[2].update(data[0, 2])
            line_datas[3].update(data[1, 0])
            line_datas[4].update(data[1, 1])
            line_datas[5].update(data[1, 2])
            #line_datas[6].update(data[2])
            
            if FPS:
                glfw.set_window_title(window, TITLE + "   ---   " + f"FPS: {FPS:.2f}")

        if data is not None:
            for i, line_data in enumerate(line_datas):
                opengl_app.update_line_data(i, line_data.get_render_data())
            opengl_app.display()

    # Clean up
    stream.close()  # Close serial port
    glfw.terminate()  # Terminate GLFW

if __name__ == "__main__":
    main()