import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout

# You might want to implement a helper function for the update function below or you can do all the calculations in the
# update callback function.
def channel_hist_data_for_selection(selection=None) -> dict:
    """
    Creates a channel histogram for all selected indices.

    :param selection: An list of selected indices in the dataset, if None the complete dataset is returned
    :return: A dict to pass into the ColumnDataSource
    """
    if not selection:
        selection = [*range(N)]

    ys = np.sum(channel_histograms[selection, ...], axis=0)
    ys /= len(selection)
    ys /= np.amax(ys)

    xs = np.arange(N_BINS_CHANNEL)

    return dict(r=ys[0, :], g=ys[1, :], b=ys[2, :], xs=xs)

# Only do this once you've followed the rest of the instructions below and you actually reach the part where you have to
# configure the callback of the lasso select tool. The ColumnDataSource containing the data from the dimensionality
# reduction has an on_change callback routine that is triggered when certain parts of it are selected with the lasso
# tool. More specifically, a ColumnDataSource has a property named selected, which has an on_change routine that can be
# set to react to its "indices" attribute and will call a user defined callback function. Connect the on_change routine
# to the "indices" attribute and an update function you implement here. (This is similar to the last exercise but this
# time we use the on_change function of the "selected" attribute of the ColumnDataSource instead of the on_change
# function of the select widget).
# In simpler terms, each time you select a subset of image glyphs with the lasso tool, you want to adjust the source
# of the channel histogram plot based on this selection.
# Useful information:
# https://docs.bokeh.org/en/latest/docs/reference/models/sources.html
# https://docs.bokeh.org/en/latest/docs/reference/models/tools.html
# https://docs.bokeh.org/en/latest/docs/reference/models/selections.html#bokeh.models.selections.Selection
def update(attr, old, new):
    hist_source.data = channel_hist_data_for_selection(new)


# Fetch the number of images using glob or some other path analyzer
N = len(glob.glob("static/*.jpg"))

# Find the root directory of your app to generate the image URL for the bokeh server
ROOT = os.path.split(os.path.abspath("."))[1] + "/"

# Number of bins per color for the 3D histograms
N_BINS_COLOR = 16
# Number of bins per channel for the channel histograms
N_BINS_CHANNEL = 50

# Define an array containing the 3D color histograms. We have one histogram per image each having N_BINS_COLOR^3 bins.
# i.e. an N * N_BINS_COLOR^3 array
color_histograms = np.zeros((N, N_BINS_COLOR**3))

# Define an array containing the channel histograms, there is one per image each having 3 channel and N_BINS_CHANNEL
# bins i.e an N x 3 x N_BINS_CHANNEL array
channel_histograms = np.zeros((N, 3, N_BINS_CHANNEL))

# initialize an empty list for the image file paths
img_paths = []

# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):
    # open image using PILs Image package
    img = Image.open(f)
    # Convert the image into a numpy array and reshape it such that we have an array with the dimensions (N_Pixel, 3)
    a = np.asarray(img)
    pixels = np.reshape(a, (a.shape[0]*a.shape[1], 3))

    # Compute a multi dimensional histogram for the pixels, which returns a cube
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html
    hist_col, _ = np.histogramdd(pixels, (N_BINS_COLOR, N_BINS_COLOR, N_BINS_COLOR), ((0, 255), (0, 255), (0, 255)))

    print(hist_col.shape)
    # However, later used methods do not accept multi dimensional arrays, so reshape it to only have columns and rows
    # (N_Images, N_BINS^3) and add it to the color_histograms array you defined earlier
    color_histograms[idx] = np.reshape(hist_col, (N_BINS_COLOR**3))

    # Append the image url to the list for the server
    url = ROOT + f
    img_paths.append(url)

    # Compute a "normal" histogram for each color channel (rgb)
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    hist_r, _ = np.histogram(pixels[:, 0], bins=N_BINS_CHANNEL, range=(0, 255))
    hist_g, _ = np.histogram(pixels[:, 1], bins=N_BINS_CHANNEL, range=(0, 255))
    hist_b, _ = np.histogram(pixels[:, 2], bins=N_BINS_CHANNEL, range=(0, 255))
    # and add them to the channel_histograms
    channel_histograms[idx] = [hist_r, hist_g, hist_b]

# Calculate the indicated dimensionality reductions
# references:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
coords_tsne = TSNE().fit_transform(color_histograms)
coords_pca = PCA().fit_transform(color_histograms)


# Construct a data source containing the dimensional reduction result for both the t-SNE and the PCA and the image paths
dimred_source = ColumnDataSource(dict(
    xs_tsne=coords_tsne[:, 0], ys_tsne=coords_tsne[:, 1],
    xs_pca=coords_pca[:, 0], ys_pca=coords_pca[:, 1],
    paths=img_paths
))

# Create a first figure for the t-SNE data. Add the lasso_select, wheel_zoom, pan and reset tools to it.
p1 = figure(title="t-SNE", x_axis_label='x', y_axis_label='y', tools=["lasso_select", "wheel_zoom", "pan", "reset"])

# And use bokehs image_url to plot the images as glyphs
# reference: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_url.html
g1 = p1.image_url(url="paths", x="xs_tsne", y="ys_tsne", h_units="screen", w_units="screen",
                  w=32, h=20, anchor="center", source=dimred_source)

# Since the lasso tool isn't working with the image_url glyph you have to add a second renderer (for example a circle
# glyph) and set it to be completely transparent. If you use the same source for this renderer and the image_url,
# the selection will also be reflected in the image_url source and the circle plot will be completely invisible.
p1.circle(x="xs_tsne", y="ys_tsne", fill_alpha=0.0, line_alpha=0.0, source=dimred_source)

# Create a second plot for the PCA result. As before, you need a second glyph renderer for the lasso tool.
# Add the same tools as in figure 1
p2 = figure(title="PCA", x_axis_label='x', y_axis_label='y', tools=["lasso_select", "wheel_zoom", "pan", "reset"])
p2.circle(x="xs_pca", y="ys_pca", fill_alpha=0.0, line_alpha=0.0, source=dimred_source)
p2.image_url(url="paths", x="xs_pca", y="ys_pca", h_units="screen", w_units="screen",
             w=32, h=20, anchor="center", source=dimred_source)

# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
hist_source = ColumnDataSource(channel_hist_data_for_selection())

# Construct a histogram plot with three lines.
# First define a figure and then make three line plots on it, one for each color channel.
# Add the wheel_zoom, pan and reset tools to it.
p3 = figure(title="Channel Histogram", x_axis_label='bin', y_axis_label='Frequency', tools=["wheel_zoom", "pan", "reset"])
p3.line("xs", "r", color="red", width=4, source=hist_source)
p3.line("xs", "g", color="green", width=4, source=hist_source)
p3.line("xs", "b", color="blue", width=4, source=hist_source)

# Connect the on_change routine of the selected attribute of the dimensionality reduction ColumnDataSource with a
# callback/update function to recompute the channel histogram. Also read the topmost comment for more information.
dimred_source.selected.on_change("indices", update)

# Construct a layout and use curdoc() to add it to your document.
curdoc().add_root(layout([[p1, p2, p3]], sizing_mode="scale_width"))

# You can use the command below in the folder of your python file to start a bokeh directory app.
# Be aware that your python file must be named main.py and that your images have to be in a subfolder name "static"

# bokeh serve --show .
# python -m bokeh serve --show .

# dev option:
# bokeh serve --dev --show .
# python -m bokeh serve --dev --show .
