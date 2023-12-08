import pandas as pd
from math import pi
import numpy as np
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, FactorRange
import bokeh.palettes as bp


### Task 1: Data Preprocessing

## T1.1: Reading data into a dataframe, setting column "Date" to be the index
original_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid19_cases_switzerland_openzh-phase2.csv'
url = original_url+'?raw=true'
raw = pd.read_csv(url, index_col='Date')

# Initializing the first row with zeros, and removing the last unnecessary columns incl. 'CH'
raw.iloc[0, :] = 0
raw = raw[raw.columns[:26]]

# Filling null with the value of previous date from same canton
raw = raw.fillna(method='ffill')


## T1.2: Calculating and smoothing daily case changes
# Computing daily new cases for each canton and filling null with zeros
dnc = raw.diff(axis=0)
dnc = dnc.fillna(0)

# Smoothing daily new case by the average value in a rolling window, and the window size is defined by step
step = 3
dnc_avg = dnc.rolling(step).mean()
dnc_avg = dnc_avg.fillna(0)
dnc_avg = dnc_avg.round()


## T1.3: Building a ColumnDataSource
# Extracting all canton names and dates, and converting dates to datetime
cantons = dnc_avg.columns.tolist()
date = dnc_avg.index.values.tolist()
date = pd.to_datetime(date)

# Creating a color list to represent different cantons in the plot
color_palette = bp.turbo(26)

# Building a dictionary with date and each canton name as a key, i.e., {'date':[], 'AG':[], ..., 'ZH':[]}
# For each canton, the value is a list containing the averaged daily new cases
source_dict = {'date': date}
for canton in cantons:
    source_dict[canton] = dnc_avg[canton].tolist()

source = ColumnDataSource(data=source_dict)


### Task 2: Data Visualization

## T2.1: Drawing a group of lines, each line represents a canton, using date, dnc_avg as x,y and adding a legend
p = figure(plot_width=1000, plot_height=800, x_axis_type="datetime")
p.title.text = 'Daily New Cases in Switzerland'
p.sizing_mode = "stretch_both"

for canton, color in zip(cantons, color_palette):
    p.line(x='date', y=canton, line_color=color, source=source, legend_label=canton, name=canton)

# Making the legend of the plot clickable, and setting the click_policy to be "hide"
p.legend.location = "top_left"
p.legend.click_policy = "hide"

## T2.2: Adding hovering tooltips to correctly display date, canton and averaged daily new case
hover = HoverTool(tooltips=[("date", "@date{%F}"),
                            ("canton", "$name"),
                            ("cases", "@$name")],
                  formatters={'@date': 'datetime'})

p.add_tools(hover)

show(p)
output_file("dvc_ex2.html")
save(p)