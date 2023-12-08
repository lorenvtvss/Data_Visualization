import numpy as np
import os
import bokeh


from bokeh.layouts import layout, row
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker
from colorcet import CET_L16, __version__

print(__version__)
from colorsys import hsv_to_rgb

output_file('DVA_ex4.html')
color = CET_L16

def to_bokeh_image(rgba_uint8):
    if  len(rgba_uint8.shape) > 2 \
            and int(bokeh.__version__.split(".")[0]) >= 2 \
            and int(bokeh.__version__.split(".")[1]) >= 2:

        np_img2d = np.zeros((rgba_uint8.shape[0], rgba_uint8.shape[1]), dtype=np.uint32)
        view = np_img2d.view(dtype=np.uint8).reshape(rgba_uint8.shape)
        view[:] = rgba_uint8[:]
    else:
        np_img2d = rgba_uint8
    return [np_img2d]

def get_divergence(vx_wind, vy_wind):
    # np.gradient returns a set of arrays with the same shape as the input array. The number of returned arrays corres-
    # ponds to the number of dimensions of the input array. I.e. the gradient is calculated along all axes.
    vx_grad = np.gradient(vx_wind[:,:,20])
    vx_grad_test = np.gradient(vx_wind[:,:,20], axis=0)
    print(vx_grad[0] == vx_grad_test)
    vy_grad = np.gradient(vy_wind[:,:,20])

    # The divergence is the sum of the derivatives of all axis with respect to themselfs.
    div_v = vx_grad[0] + vy_grad[1]
    return  div_v

def get_vorticity(vx_wind, vy_wind):
    # np.gradient returns a set of arrays with the same shape as the input array. The number of returned arrays corres-
    # ponds to the number of dimensions of the input array. I.e. the gradient is calculated along all axes.
    vx_grad = np.gradient(vx_wind[:, :, 20])
    vy_grad = np.gradient(vy_wind[:, :, 20])

    # vorticity the z-component is 0 and vx and vy are constant with respect to z, which leads to the first two compo-
    # nents of the vorticity being 0
    vort_v = vy_grad[0] - vx_grad[1]

    return  vort_v

# calculates the HSV colors of the xy-windspeed vectors and maps them to RGBA colors
def vector_color_coding(vx_wind, vy_wind):
    # calculate the hue as the angle between the vector and the positive x-axis
    rgba_colors = np.zeros((500, 500, 4))
    y_coord = vy_wind[:, :, 20].flatten()
    x_coord = vx_wind[:, :, 20].flatten()
    hue = np.arctan2(y_coord, x_coord)
    hue[hue < 0] = hue[hue < 0] + 2 * np.pi
    hue = np.reshape(hue, (500, 500))
    hue = hue * 180 / np.pi

    # Saturation (S) can be set to 1
    S = 1

    impl = 0
    if impl == 0:
        # The brightness value (V) is set on the normalized magnitude of the vector
        # Calculate a matrix of all vector norms
        print('Fast V implementation')
        vxy_wind = np.concatenate((vx_wind[:, :, 20][..., np.newaxis], vy_wind[:, :, 20][..., np.newaxis]), axis=2)
        V_norm = np.linalg.norm(vxy_wind, axis=2)
        n_max = np.amax(V_norm)
        n_min = np.amin(V_norm)
        V = (V_norm - n_min) / (n_max - n_min)
    elif impl == 1:
        # alt implementation
        print('alt V implementation')
        vx_sq = np.square(vx_wind[:, :, 20])
        vy_sq = np.square(vy_wind[:, :, 20])
        vxy_sum = vx_sq + vy_sq
        sum_root = np.sqrt(vxy_sum)
        n_max = np.amax(sum_root)
        n_min = np.amin(sum_root)
        V = (sum_root - n_min) / (n_max - n_min)
    else:
        print('constant V=1 implementation')
        V=np.ones((500,500))


    # Algorithm for the HSV to RGB conversion see https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    C = V * S
    m = V - C
    X = C * (1 - np.abs(np.mod(hue/60, 2) - 1))

    for i in range(500):
        for j in range(500):
            # Either use hsv_to_rgb
            rgba_colors[i, j] = 255 * np.array([*hsv_to_rgb(hue[i, j] / 360.0, S, V[i, j]), 1.0])

            # Or your own implementation

            # if hue[i, j] < 60:
            #     rgba_colors[i, j] = 255 * np.array([C[i, j] + m[i, j], X[i, j] + m[i, j], 0 + m[i, j], 1])
            # elif hue[i, j] < 120:
            #     rgba_colors[i, j] = 255 * np.array([X[i, j] + m[i, j], C[i, j] + m[i, j], 0 + m[i, j], 1])
            # elif hue[i, j] < 180:
            #     rgba_colors[i, j] = 255 * np.array([0 + m[i, j], C[i, j] + m[i, j], X[i, j] + m[i, j], 1])
            # elif hue[i, j] < 240:
            #     rgba_colors[i, j] = 255 * np.array([0 + m[i, j], X[i, j] + m[i, j], C[i, j] + m[i, j], 1])
            # elif hue[i, j] < 300:
            #     rgba_colors[i, j] = 255 * np.array([X[i, j] + m[i, j], 0 + m[i, j], C[i, j] + m[i, j], 1])
            # else:
            #     rgba_colors[i, j] = 255 * np.array([C[i, j] + m[i, j], 0 + m[i, j], X[i, j] + m[i, j], 1])

    # The RGBA colors have to be saved as uint8 for the bokeh plot to properly work
    return rgba_colors


# load and process the required data
print('processing data')
xWind_file = 'Uf24.bin'
xWind_path = os.path.abspath(os.path.dirname(xWind_file))
xWind_data = np.fromfile(os.path.join(xWind_path, xWind_file), dtype=np.dtype('>f'))
xWind_data = np.reshape(xWind_data, [500, 500, 100], order='F')
xWind_data = np.flipud(xWind_data)

# replace the missing "no data" values with the average of the dataset
filtered_average = np.average(xWind_data[xWind_data < 1e35])
xWind_data[xWind_data == 1e35] = filtered_average

yWind_file = 'Vf24.bin'
yWind_path = os.path.abspath(os.path.dirname(yWind_file))
yWind_data = np.fromfile(os.path.join(yWind_path, yWind_file), dtype=np.dtype('>f'))
yWind_data = np.reshape(yWind_data, [500, 500, 100], order='F')
yWind_data = np.flipud(yWind_data)

# replace the missing "no data" values with the average of the dataset
filtered_average = np.average(yWind_data[yWind_data < 1e35])
yWind_data[yWind_data == 1e35] = filtered_average

wind_vcc = vector_color_coding(xWind_data, yWind_data)
print(np.shape(wind_vcc))
wind_divergence = get_divergence(xWind_data, yWind_data)
wind_vorticity = get_vorticity(xWind_data, yWind_data)
print('data processing completed')


fig_args = {'x_range': (0,500), 'y_range': (0,500), 'width': 500, 'height': 400, 'toolbar_location': None, 'active_scroll': 'wheel_zoom'}
img_args = {'dh': 500, 'dw': 500, 'x': 0, 'y': 0}
cb_args = {'ticker': BasicTicker(), 'label_standoff': 12, 'border_line_color': None, 'location': (0,0)}

# create x wind speed plot
color_mapper_xWind = LinearColorMapper(palette=CET_L16, low=np.amin(xWind_data), high=np.amax(xWind_data))
xWind_plot = figure(title="x-Wind speed (West - East)", **fig_args)
xWind_plot.image(image=to_bokeh_image(xWind_data[:,:,20]), color_mapper=color_mapper_xWind, **img_args)
xWind_color_bar = ColorBar(color_mapper=color_mapper_xWind, **cb_args)
xWind_plot.add_layout(xWind_color_bar, 'right')

# create y wind speed plot
color_mapper_yWind = LinearColorMapper(palette=CET_L16, low=np.amin(yWind_data), high=np.amax(yWind_data))
yWind_plot = figure(title="y-Wind speed South - North", **fig_args)
yWind_plot.image(image=to_bokeh_image(yWind_data[:,:,20]), color_mapper=color_mapper_yWind, **img_args)
yWind_color_bar = ColorBar(color_mapper=color_mapper_yWind, **cb_args)
yWind_plot.add_layout(yWind_color_bar, 'right')

# # create divergence plot
color_mapper_divergence = LinearColorMapper(palette=CET_L16, low=np.amin(wind_divergence), high=np.amax(wind_divergence))
divergence_plot = figure(title="Divergence", **fig_args)
divergence_plot.image(image=to_bokeh_image(wind_divergence), color_mapper=color_mapper_divergence, **img_args)
divergence_color_bar = ColorBar(color_mapper=color_mapper_divergence, **cb_args)
divergence_plot.add_layout(divergence_color_bar, 'right')

# create vorticity plot
color_mapper_vorticity = LinearColorMapper(palette=CET_L16, low=np.amin(wind_vorticity), high=np.amax(wind_vorticity))
vorticity_plot = figure(title="Vorticity", **fig_args)
vorticity_plot.image(image=to_bokeh_image(wind_vorticity), color_mapper=color_mapper_vorticity, **img_args)
vorticity_color_bar = ColorBar(color_mapper=color_mapper_vorticity, **cb_args)
vorticity_plot.add_layout(vorticity_color_bar, 'right')

# create vector color coding plot
vcc_plot = figure(title="Vector Color Coding", **fig_args)
vcc_plot.image_rgba(image=to_bokeh_image(wind_vcc), **img_args)

# create and show plot layout
final_layout = layout(row(xWind_plot, yWind_plot), row(divergence_plot, vorticity_plot, vcc_plot))# vcc_plot, vorticity_plot,
show(final_layout)
