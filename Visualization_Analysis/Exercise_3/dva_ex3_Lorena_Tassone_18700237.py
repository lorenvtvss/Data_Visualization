import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row


def get_distance(p,m):
    distance = abs(sepal_length[p]-sepal_length[m]) + abs(sepal_width[p]-sepal_width[m]) + abs(petal_length[p]-petal_length[m]) + abs(petal_width[p]-petal_width[m])
    return distance


def get_cost(meds):
    dist_array = []
    for m in meds:
        distance_array = np.add(np.add(np.abs(sepal_length-sepal_length[m]), np.abs(sepal_width-sepal_width[m])), np.add(np.abs(petal_length-petal_length[m]), np.abs(petal_width-petal_width[m])))
        dist_array.append(distance_array)

    sum = 0
    for p in data.index:
        arr = np.array([dist_array[0][p], dist_array[1][p], dist_array[2][p]])
        sum += min(arr)

    return sum


def k_medoids():
    # number of clusters:
    k = 3

    if data_select.value == 'False':
        medoids = [24, 74, 124]
    else:
        indexes = np.random.randint(0, len(data)-1, k)
        medoids = [m for m in indexes]

    # calculation cost
    original_cost = get_cost(medoids)

    new_cost = original_cost
    old_cost = original_cost
    smaller = True

    # calc best medoids
    best_combo = (None, None)
    new_medoids = [m for m in medoids]

    while smaller:
        for m in range(0, k):
            for p in data.index:
                if new_medoids[m] == p:
                    continue
                tmp = new_medoids[m]
                new_medoids[m] = p
                new_cost = get_cost(new_medoids)
                if new_cost < old_cost:
                    old_cost = new_cost
                    best_combo = (m, p)
                new_medoids[m] = tmp
        if not best_combo == (None, None):
            new_medoids[best_combo[0]] = best_combo[1]
            new_cost = get_cost(new_medoids)
            best_combo = (None, None)
        else:
            new_cost = old_cost
            smaller = False

    # setting colors of clusters
    for p in data.index:
        curr_d = []
        for m in new_medoids:
            dist = get_distance(p, m)
            curr_d.append(dist)
        if min(curr_d) == curr_d[0]:
            color[p] = 'red'
        elif min(curr_d) == curr_d[1]:
            color[p] = 'green'
        else:
            color[p] = 'blue'

    source.data['Color'] = color

    # changing costs in div
    div.text = 'The final cost is: {:.2f}'.format(new_cost)


# read and store the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)

sepal_length = np.array(data['sepal_length'])
sepal_width = np.array(data['sepal_width'])
petal_length = np.array(data['petal_length'])
petal_width = np.array(data['petal_width'])

# create a color column in your dataframe and set it to gray on startup
data['color'] = 'gray'
color = np.array(data['color'])

# Create a ColumnDataSource from the data
source = ColumnDataSource(data=dict(Sepal_length=sepal_length,
                                    Sepal_width=sepal_width,
                                    Petal_length=petal_length,
                                    Petal_width=petal_width,
                                    Color=color))

# Creating figures
p1 = figure(plot_height=400, plot_width=400)
p1.scatter('Petal_length', 'Sepal_length', color='Color', source=source, alpha=0.5)
p1.title.text = 'Scatterplot of flower distribution by petal length and sepal length'
p1.yaxis.axis_label = "Sepal length"
p1.xaxis.axis_label = "Petal length"
p1.sizing_mode = 'stretch_both'

p2 = figure(plot_height=400, plot_width=400)
p2.scatter('Petal_width', 'Petal_length', color='Color', source=source, alpha=0.5)
p2.title.text = 'Scatterplot of flower distribution by petal width and petal length'
p2.yaxis.axis_label = "Petal length"
p2.xaxis.axis_label = "Petal width"
p2.sizing_mode = 'stretch_both'

# Create a select widget, a button, a DIV to show the final clustering cost and two figures for the scatter plots.
data_select = Select(title='Random Medoids', value='False', options=['False', 'True'])
button = Button(label='Cluster data', button_type='success')
button.on_click(k_medoids)
div = Div(text="The final cost is: ")

# use curdoc to add your widgets to the document
curdoc().add_root(row(column(data_select, button, div), p1, p2))
curdoc().title = "DVA_ex_3"


# use on of the commands below to start your application
# bokeh serve --show dva_ex3_Lorena_Tassone_18700237.py
# python -m bokeh serve --show dva_ex3_Lorena_Tassone_18700237.py
# bokeh serve --dev --show dva_ex3_Lorena_Tassone_18700237.py
# python -m bokeh serve --dev --show dva_ex3_Lorena_Tassone_18700237.py