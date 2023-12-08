import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool, Select, FactorRange
from bokeh.plotting import figure, curdoc

# definition of the callback function that changes the source data and y range
def callback(attr, old, new):
    if dropdown.value == 'Mammalia':
        source.data = dict(source_mammalia.data)
        p.y_range.factors = source.data['species'].to_list()
    elif dropdown.value == 'Aves':
        source.data = dict(source_aves.data)
        p.y_range.factors = source.data['species'].to_list()
    else:
        source.data = dict(source_reptilia.data)
        p.y_range.factors = source.data['species'].to_list()

# reading data from .csv file
df = pd.read_csv('AZA_MLE_Jul2018_utf8.csv', encoding='utf-8')

# constructing list of indizes to remove unnecessary columns
cols = [1, 3]
cols.extend([i for i in range(7, 15)])
df.drop(df.columns[cols], axis=1, inplace=True)


### task 1

# renaming the columns of the data frame
df.rename(columns={'Species Common Name': 'species', 'TaxonClass': 'taxon_class', 'Overall CI - lower': 'ci_lower',
                    'Overall CI - upper': 'ci_upper', 'Overall MLE': 'mle', 'Male Data Deficient': 'male_deficient',
                    'Female Data Deficient': 'female_deficient'}, inplace=True)

# constructing three independent dataframes based taxon classes 'Mammalia', 'Aves', 'Reptilia' and removing the outliers
df_mammalia = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Mammalia')]
df_aves = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Aves')]
df_reptilia = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Reptilia')]

# removing data that has no 'mle' value
df_mammalia = df_mammalia.drop(df_mammalia[df_mammalia['mle'].isnull()].index)
df_aves = df_aves.drop(df_aves[df_aves['mle'].isnull()].index)
df_reptilia = df_reptilia.drop(df_reptilia[df_reptilia['mle'].isnull()].index)

# sorting the dataframes by 'mle' in descending order and reseting the index
df_mammalia = df_mammalia.sort_values('mle', ascending=False, na_position='last', ignore_index=True)
df_aves = df_aves.sort_values('mle', ascending=False, na_position='last', ignore_index=True)
df_reptilia = df_reptilia.sort_values('mle', ascending=False, na_position='last', ignore_index=True)

# reducing each dataframe to contain only the 10 species with the highest 'mle'
df_mammalia = df_mammalia.nlargest(10, ['mle'])
df_aves = df_aves.nlargest(10, ['mle'])
df_reptilia = df_reptilia.nlargest(10, ['mle'])

# sorting the dataframes in ascending order and reseting the index
df_mammalia = df_mammalia.sort_values('mle', ascending=True, ignore_index=True)
df_aves = df_aves.sort_values('mle', ascending=True, ignore_index=True)
df_reptilia = df_reptilia.sort_values('mle', ascending=True, ignore_index=True)

# renaming the species'Penguin, Northern & Southern Rockhopper (combined)' in the aves dataframe
df_aves['species'] = df_aves['species'].replace({'Penguin, Northern & Southern Rockhopper (combined)': 'Penguin, Rockhopper'})

# constructing a ColumDataSource for each of the dataframes
source_mammalia = ColumnDataSource(data=dict(
    species=df_mammalia['species'],
    mle=df_mammalia['mle'],
    ci_lower=df_mammalia['ci_lower'],
    ci_upper=df_mammalia['ci_upper']))

source_aves = ColumnDataSource(data=dict(
    species=df_aves['species'],
    mle=df_aves['mle'],
    ci_lower=df_aves['ci_lower'],
    ci_upper=df_aves['ci_upper']))

source_reptilia = ColumnDataSource(data=dict(
    species=df_reptilia['species'],
    mle=df_reptilia['mle'],
    ci_lower=df_reptilia['ci_lower'],
    ci_upper=df_reptilia['ci_upper']))

# constructing a fourth ColumDataSource that is used as input for the plot with initial value 'Mammalia'
source = ColumnDataSource(data=dict(
    species=df_mammalia['species'],
    mle=df_mammalia['mle'],
    ci_lower=df_mammalia['ci_lower'],
    ci_upper=df_mammalia['ci_upper']))


### task 2:
# configuring a mouse hover tool
hover = HoverTool(tooltips=[('low', '@ci_lower'),('high', '@ci_upper')])

# constructing a figure with axis label, hovertools and disabled toolbar
p = figure(x_range=(0, 51), y_range=FactorRange(factors=source.data['species'].to_list()), plot_height=500, plot_width=800,
           title='Medium Life Expectancy of Animals in Zoos',)
p.yaxis.axis_label = 'Species'
p.xaxis.axis_label = 'Medium Life Expectancy [Years]'
p.toolbar.logo = None
p.toolbar_location = None
p.add_tools(hover)
p.sizing_mode = "stretch_both"

# adding the horizontal bar chart to the figure
p.hbar(y='species', left='ci_lower', right='ci_upper', height=0.4, source=source)

# creating a Select dropdown tool and configuring its 'on_change' callback (default visualization is 'Mammalia')
dropdown = Select(value='Mammalia', options=['Mammalia', 'Aves', 'Reptilia'], title="Select Taxon Class")
dropdown.on_change('value', callback)

# visualization
curdoc().add_root(row(p, dropdown))
curdoc().title = 'dva_ex1_Lorena_Tassone_18700237'

# I was only able to run it with this command: python -m bokeh serve --show dva_ex1_Lorena_Tassone_18700237.py


