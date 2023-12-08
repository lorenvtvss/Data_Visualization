#!/usr/bin/env python
# coding: utf-8

# In[37]:


import pandas as pd 
from math import pi
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange,CustomJS
#import bokeh.palettes as bp

 
### Task 1: Data Preprocessing
 
## T1.1 Read online .csv file into a dataframe using pandas
original_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/demographics_switzerland_bag.csv'
raw_url = 'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics_switzerland_bag.csv'
df = pd.read_csv(raw_url, index_col=0)

## T1.2 Prepare data for a grouped vbar_stack plot

# Filter out rows containing 'CH' 
df = df[(df.canton == 'CH')==False]

# Extract unique value lists of canton, age_group and sex
all_canton = df['canton'].tolist()
canton = pd.unique(all_canton)

all_age_group = df['age_group'].tolist()
age_group = pd.unique(all_age_group)

all_sex = df['sex'].tolist()
sex = pd.unique(all_sex)


# Create a list of categories in the form of [(canton1,age_group1), (canton2,age_group2), ...]
factors = [(c,ag) for c in canton for ag in age_group]

# Use genders as stack names
stacks = ['male','female']

# Calculate total population size as the value for each stack identified by canton,age_group and sex

# seperating male and female into two dataframes
male = df.loc[df['sex'] == 'Männlich']
female = df.loc[df['sex'] == 'Weiblich']

# grouping by canton and age
male_canton_age = male.groupby(['canton','age_group'])['pop_size'].sum()
female_canton_age = female.groupby(['canton','age_group'])['pop_size'].sum()

#Listing all sums grouped by canton and age
male_values = [v for v in male_canton_age]
female_values = [v for v in female_canton_age]

# Build a ColumnDataSource using above information
source = ColumnDataSource(data=dict(
    x = factors,
    male = male_values,
    female = female_values,))


### Task 2: Data Visualization

## T2.1: Visualize the data using bokeh plot functions
p=figure(x_range=FactorRange(*factors), plot_height=500, plot_width=800, title='Canton Population Visualization')
p.yaxis.axis_label = "Population Size"
p.xaxis.axis_label = "Canton"
p.sizing_mode = "stretch_both"
p.xgrid.grid_line_color = None
p.title.text_color = "black"
p.xaxis.major_label_orientation = pi/2
p.xaxis.major_label_text_font_size = '4pt'

p.background_fill_color = "whitesmoke"
p.background_fill_alpha = 0.9
p.outline_line_width = 3
p.outline_line_alpha = 0.3
p.outline_line_color = "black"

p.vbar_stack(stacks, x='x', width=0.5, alpha=0.5, color=['#41b6c4','#DD4968'], source=source, legend_label=stacks)

p.y_range.start = 0

p.legend.location = "top_left"
p.legend.border_line_width = 2
p.legend.border_line_color = "black"
p.legend.border_line_alpha = 0.3

## T2.2 Add the hovering tooltips to the plot using HoverTool
# To be specific, the hover tooltips should display “gender”, "canton, age group”, and “population” when hovering.
hover = HoverTool(tooltips=[
    ('gender','$name'),
    ('canton, age group','@x'),
    ('population','$y')])

p.add_tools(hover)
                  
show(p)

## T2.3 Save the plot as "dvc_ex1.html" using output_file
output_file("dvc_ex1.html")




# In[ ]:




