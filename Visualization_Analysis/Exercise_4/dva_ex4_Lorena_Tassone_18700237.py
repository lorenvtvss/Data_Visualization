import numpy as np
import os

import bokeh
from bokeh.layouts import layout, row
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker
from colorcet import CET_L16

from colorsys import hsv_to_rgb


# scale values for colors not normalize it!!

output_file('DVA_ex4.html')
color = CET_L16

def to_bokeh_image(rgba_uint8):
    if len(rgba_uint8.shape) > 2 \
            and int(bokeh.__version__.split(".")[0]) >= 2 \
            and int(bokeh.__version__.split(".")[1]) >= 2:
        np_img2d = np.zeros(shape=rgba_uint8.shape[:2], dtype=np.uint32)
        view = np_img2d.view(dtype=np.uint8).reshape(rgba_uint8.shape)
        view[:] = rgba_uint8[:]
    else:
        np_img2d = rgba_uint8
    return [np_img2d]

def get_divergence(vx_wind, vy_wind):
    # Use np.gradient to calculate the gradient of a vector field. Find out what exactly the return values represent and
    # use the appropriate elements for your calculations

    div_v = 0
        # your code
    n_vx = len(vx_wind)
    n_vy = len(vy_wind)
    np.ufunc.reduce(np.add, [np.gradient(f[i], axis=i) for i in range(num_dims)])

    return div_v

def get_vorticity(vx_wind, vy_wind):
    # Calculate the gradient again and use the appropriate results to calculate the vorticity. Think about what happens
    # to the z-component and the derivatives with respect to z for a two dimensional vector field.
    # (You can save the gradient in the divergence calculations or recalculate it here. Since the gradient function is
    # fast and we have rather small data slices the impact of recalculating it is negligible.)

    vort_v = 0
        # your code

    return vort_v

# Calculates the HSV colors of the xy-windspeed vectors and maps them to RGBA colors
def vector_color_coding(vx_wind, vy_wind):
    # Calculate the hue (H) as the angle between the vector and the positive x-axis
        # your code

    # Saturation (S) can be set to 1
    S = 1

    # The brightness value (V) is set on the normalized magnitude of the vector

    # Either use colorsys.hsv_to_rgb or implement the color conversion yourself using the
    # algorithm for the HSV to RGB conversion, see https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    rgba_colors = np.array(0)
        # your code

    # The RGBA colors have to be saved as uint8 for the bokeh plot to properly work
    return rgba_colors.astype('uint8')


# Load and process the required data
print('processing data')
xWind_file = 'Uf24.bin'
xWind_path = os.path.abspath(os.path.dirname(xWind_file))
xWind_data = np.fromfile(os.path.join(xWind_path, xWind_file), dtype=np.dtype('>f'))
xWind_data = np.reshape(xWind_data, [500, 500, 100], order='F')
xWind_data = np.flipud(xWind_data)

print(xWind_data)

# Replace the missing "no data" values with the average of the dataset
filtered_average = np.average(xWind_data[xWind_data < 1e35])
xWind_data[xWind_data == 1e35] = filtered_average

yWind_file = 'Vf24.bin'
yWind_path = os.path.abspath(os.path.dirname(yWind_file))
yWind_data = np.fromfile(os.path.join(yWind_path, yWind_file), dtype=np.dtype('>f'))
yWind_data = np.reshape(yWind_data, [500, 500, 100], order='F')
yWind_data = np.flipud(yWind_data)

# Replace the missing "no data" values with the average of the dataset
filtered_average = np.average(yWind_data[yWind_data < 1e35])
yWind_data[yWind_data == 1e35] = filtered_average

wind_vcc = vector_color_coding(xWind_data, yWind_data)
wind_divergence = get_divergence(xWind_data, yWind_data)
wind_vorticity = get_vorticity(xWind_data, yWind_data)
print('data processing completed')


fig_args = {'x_range': (0,500), 'y_range': (0,500), 'width': 500, 'height': 400, 'toolbar_location': None, 'active_scroll': 'wheel_zoom'}
img_args = {'dh': 500, 'dw': 500, 'x': 0, 'y': 0}
cb_args = {'ticker': BasicTicker(), 'label_standoff': 12, 'border_line_color': None, 'location': (0,0)}

# Create x wind speed plot
color_mapper_xWind = LinearColorMapper(palette=CET_L16, low=np.amin(xWind_data), high=np.amax(xWind_data))
xWind_plot = figure(title="x-Wind speed (West - East)", **fig_args)
xWind_plot.image(image=to_bokeh_image(xWind_data[:,:,20]), color_mapper=color_mapper_xWind, **img_args)
xWind_color_bar = ColorBar(color_mapper=color_mapper_xWind, **cb_args)
xWind_plot.add_layout(xWind_color_bar, 'right')

# Create y wind speed plot
color_mapper_yWind = LinearColorMapper(palette=CET_L16, low=np.amin(yWind_data), high=np.amax(yWind_data))
yWind_plot = figure(title="y-Wind speed South - North", **fig_args)
yWind_plot.image(image=to_bokeh_image(yWind_data[:,:,20]), color_mapper=color_mapper_yWind, **img_args)
yWind_color_bar = ColorBar(color_mapper=color_mapper_yWind, **cb_args)
yWind_plot.add_layout(yWind_color_bar, 'right')


# Create divergence plot
    # your code

# Create vorticity plot
    # your code

# Create vector color coding plot
# Use the bokeh image_rgba function for the plotting (no color mapper)
    # your code


# Create and show plot layout
# Use the second line when you've created all plots (and delete the first one)
final_layout = layout(row(xWind_plot, yWind_plot))
# final_layout = layout(row(xWind_plot, yWind_plot), row(divergence_plot, vorticity_plot, vcc_plot))
show(final_layout)