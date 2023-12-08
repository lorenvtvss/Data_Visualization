import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta

import bokeh.palettes as bp
from bokeh.plotting import figure, curdoc
from bokeh.transform import linear_cmap
from bokeh.layouts import column, row
from bokeh.models import (CDSView,
                        HoverTool,ColorBar,
                        GeoJSONDataSource,
                        Patches,
                        RadioButtonGroup,
                        DateSlider,
                        Button)


### Task 1: Data Preprocessing

## T1.1 Read and filter data

demo_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/demographics.csv'
local_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid_19_cases_switzerland_standard_format.csv'
case_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid19_cases_switzerland_openzh-phase2.csv'
shape_dir = 'data/gadm36_CHE_1.shp'


# Read from demo_url into a dataframe using pandas
d_url = demo_url+'?raw=true'
demo_raw = pd.read_csv(d_url, index_col=0)
demo_raw = demo_raw[demo_raw.index != 'CH']
demo_raw = demo_raw.sort_values('Canton')

# Read from local_url into a dataframe using pandas
l_url = local_url+'?raw=true'
local_raw = pd.read_csv(l_url)

# Extract unique 'abbreviation_canton','lat','long' combinations from local_raw
canton_point = local_raw[['abbreviation_canton', 'lat', 'long']].drop_duplicates()
canton_point = canton_point.sort_values('abbreviation_canton')

# Read from case_url into a dataframe using pandas
c_url = case_url+'?raw=true'
case_raw = pd.read_csv(c_url, index_col=0)

# Create a date list from case_raw and convert to datatime form
dates_raw = case_raw.index.tolist()
dates = pd.to_datetime(dates_raw)

# Read shape file from shape_dir unsing geopandas
shape_raw = gpd.read_file('data/gadm36_CHE_1.shp')


# Extract canton name abbreviations from the attribute 'HASC_1', e.g. CH.AG --> AG, CH.ZH --> ZH
# And save into a new column named 'Canton'
shape_raw['Canton'] = [c[3:] for c in shape_raw['HASC_1']]
shape_raw = shape_raw.sort_values('Canton')

canton_poly = shape_raw[['geometry', 'Canton']]
canton_poly = canton_poly.sort_values('Canton')


## T1.2 Merge data and build a GeoJSONDataSource

# Merge canton_poly with demo_raw on attribute name 'Canton' into dataframe merged,
# then merge the result with canton_point on 'Canton' and 'abbreviation_canton' respectively
merged = canton_poly.merge(demo_raw, left_on='Canton', right_on='Canton')
merged = merged.merge(canton_point, left_on='Canton', right_on='abbreviation_canton')


# For each date, extract a list of daily new cases per capita from all cantons(e.g. 'AG_diff_pc', 'AI_diff_pc', etc.), and add as a new column in merged
for i, d in enumerate(dates_raw):
    nc = []
    for c in canton_point['abbreviation_canton']:
        x = c+'_diff_pc'
        nc.append(case_raw.at[d, x])
    merged[d] = nc


# Calculate circle sizes that are proportional to dnc per capita
# Set the latest dnc as default
merged['size'] = merged.iloc[:, -1]*1e5/5+10
merged['dnc'] = merged.iloc[:, -2]

merged.fillna(0, inplace=True)


# Build a GeoJSONDataSource from merged
geosource = GeoJSONDataSource(geojson=merged.to_json())


# Task 2: Data Visualization

# T2.1 Create linear color mappers for 2 attributes in demo_raw: population density, hospital beds per capita
# Map their maximum values to the high, and mimimum to the low
labels = ['Density', 'BedsPerCapita']

mappers = {}
mappers['Density'] = linear_cmap(field_name='Density', palette=bp.inferno(256)[::-1], low=min(demo_raw['Density']), high=max(demo_raw['Density']))
mappers['BedsPerCapita'] = linear_cmap(field_name='BedsPerCapita', palette=bp.inferno(256)[::-1], low=min(demo_raw['BedsPerCapita']), high=max(demo_raw['BedsPerCapita']))


# T2.2 Draw a Switzerland Map on canton level

# Define a figure
p1 = figure(title='Demographics in Switzerland', plot_height=600, plot_width=950, toolbar_location='above', tools="pan, wheel_zoom, box_zoom, reset")
p1.xgrid.grid_line_color = None
p1.ygrid.grid_line_color = None

# Plot the map using patches, set the fill_color as mappers['Density']
cantons = p1.patches('xs', 'ys', source=geosource, fill_color=mappers['Density'], line_color='gray', line_width=0.25, fill_alpha=0.5)

# Create a colorbar with mapper['Density'] and add it to above figure
color_bar = ColorBar(color_mapper=mappers['Density']['transform'], width=10, location=(0, 0), title='Density', title_text_font='3')
p1.add_layout(color_bar, 'right')

# Add a hovertool to display canton, density, bedspercapita and dnc
hover = HoverTool(tooltips=[('Canton', '@Canton'),
                            ('Population Density', '@Density{int}'),
                            ('Beds Per Capita', '@BedsPerCapita'),
                            ('Daily New Cases per Capita', '@dnc')],
                  renderers=[cantons])

p1.add_tools(hover)


# T2.3 Add circles at the locations of capital cities for each canton, and the sizes are proportional to daily new cases per capita
sites = p1.circle('long', 'lat', source=geosource, fill_color='blue', fill_alpha=0.5, size='size')


# T2.4 Create a radio button group with labels 'Density', and 'BedsPerCapita'
buttons = RadioButtonGroup(labels=['Density', 'BedsPerCapita'], active=0)

# Define a function to update color mapper used in both patches and colorbar
def update_bar(new):
    for i,d in enumerate(labels):
        if i == new:
            color_bar.color_mapper = mappers[d]["transform"]
            color_bar.title = d
            cantons.glyph.fill_color = mappers[d]


buttons.on_click(update_bar)


# T2.5 Add a dateslider to control which per capita daily new cases information to display

# Define a dateslider using maximum and mimimum dates, set value to be the latest date
timeslider = DateSlider(start=min(dates), end=max(dates), value=max(dates), step=1, title='Date')

# Callback function
def callback(attr,old,new):
    # Convert timestamp to datetime
    date = datetime.fromtimestamp(timeslider.value / 1e3)

    # convert the timestamp value from the slider to datetime and format it in the form of '%Y-%m-%d'
    i = date.strftime('%Y-%m-%d')

    # update columns 'size', 'dnc' with the column named '%Y-%m-%d' in merged
    merged.size = merged[i]*1e5/5+10
    merged.dnc = merged[i]

    # update geosource with new merged
    geosource.geojson = merged.to_json()


# Circles change on mouse move
timeslider.on_change('value', callback)


# T2.6 Add a play button to change slider value and update the map plot dynamically

# Update the slider value with one day before current date
def animate_update_slider():
    # Extract date from slider's current value
    date = datetime.fromtimestamp(timeslider.value / 1e3)

    # stringify date so that it can be compared in if-loop
    s_d = date.strftime('%Y-%m-%d')
    min_d = min(dates).strftime('%Y-%m-%d')

    # Subtract one day from date
    day = date - timedelta(days=1)

    # if first date of list is reached jump to current date
    if s_d == min_d:
        day = max(dates)

    timeslider.value = day


# Define the callback function of button
def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update_slider, 500)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)


button = Button(label='► Play', width=80, height=40)
button.on_click(animate)


curdoc().add_root(column(p1, buttons, row(timeslider, button)))

# python -m bokeh serve --dev --show dvc_ex4.py
