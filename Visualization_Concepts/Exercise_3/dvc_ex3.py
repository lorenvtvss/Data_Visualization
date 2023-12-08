import pandas as pd
import numpy as np
import bokeh.palettes as bp
from bokeh.plotting import figure
from bokeh.io import output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, ColorBar, RangeTool
from bokeh.transform import linear_cmap
from bokeh.layouts import gridplot


### Task1: Data Preprocessing

## T1.1 Read the data to the dataframe "raw" from provided data (update Nov.3, 2020)
raw = pd.read_csv('covid19_tests_switzerland_bag.csv', index_col=0)

## T1.2 Create a ColumnDataSource containing: date, positive number, positive rate, total tests
dates = pd.to_datetime(raw['date'].tolist())
pos_num = raw['n_positive']
pos_rate = raw['frac_positive']
test_num = raw['n_tests']

source = ColumnDataSource(data=dict(dates=dates, positive_number=pos_num, positive_rate=pos_rate, total_tests=test_num))

## T1.3 Map the range of positive rate to a colormap using module "linear_cmap"
mapper = linear_cmap(field_name='positive_rate', palette=bp.inferno(256), low=min(pos_rate), high=max(pos_rate))


### Task2: Data Visualization

## T2.1 Covid-19 Total Tests Scatter Plot
# initial x_range first 30 days.
TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p = figure(plot_height=400, plot_width=1000, tools=TOOLS, x_axis_type="datetime", x_range=(dates[0], dates[29]))
p.scatter(x='dates', y='total_tests', source=source, size=11, line_color='black', fill_color=mapper, fill_alpha=0.5)
p.toolbar.logo = None
p.toolbar_location = None

p.title.text = 'Covid-19 Tests in Switzerland'
p.yaxis.axis_label = "Total Tests"
p.xaxis.axis_label = "Date"
p.sizing_mode = "stretch_both"

# Add a hovertool to display date, total test number
hover = HoverTool(tooltips=[("date", "@dates{%F}"),
                            ('total tests', '@total_tests')],
                  formatters={'@dates': 'datetime'})
p.add_tools(hover)


## T2.2 Add a colorbar to the above scatter plot, and encode positve rate values with colors; please use the color mapper defined in T1.3
color_bar = ColorBar(color_mapper=mapper['transform'], width=10, location=(0, 0), title='P_Rate')
p.add_layout(color_bar, 'right')

## T2.3 Covid-19 Positive Number Plot using RangeTool
TOOLS = ''
select = figure(plot_height=350, plot_width=1000, tools=TOOLS, x_axis_type="datetime")
select.title.text = 'Drag the middle and edges of the selection box to change the range above'
select.yaxis.axis_label = "Positive Cases"
select.xaxis.axis_label = "Date"

# Define a RangeTool to link with x_range in the scatter plot
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "green"
range_tool.overlay.fill_alpha = 0.2
select.add_tools(range_tool)

# Draw a line plot and add the RangeTool to the plot
select.line(x='dates', y='positive_number', source=source)
select.yaxis.axis_label = "Positive Cases"
select.xaxis.axis_label = "Date"

# Add a hovertool to the range plot and display date, positive test number
hover2 = HoverTool(tooltips=[("date", "@dates{%F}"),
                             ('positive tests', '@positive_number')],
                   formatters={'@dates': 'datetime'})
select.add_tools(hover2)


## T2.4 Layout arrangement and display
linked_p = gridplot([[p],
                     [select]],
                    sizing_mode='stretch_width')

show(linked_p)
output_file("dvc_ex3.html")
save(linked_p)
