from os.path import dirname, join

import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.sampledata.movies_data import movie_path
from bokeh.charts import Histogram, output_file, show
import bokeh

import pandas as pd

wages_plot_data = pd.read_csv("wage_plot_data.csv", index_col= 0)
hist, edges = np.histogram(wages_plot_data.percent_time_idle, bins=50)

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
reviews = Slider(title="Percent Idle Time", value=15, start=5, end=100, step=10)
source = bokeh.models.ColumnDataSource(wages_plot_data)

#Attempt at a histogram
p = figure(plot_height=600,
           min_border=10, min_border_left=50)
hh1 = p.quad(bottom=0, left=edges[:-1], right=edges[1:], top=hist)#, color="white", line_color="#3A5785")
p.quad(bottom=0, left=edges[:-1], right=edges[1:])#, top=hzeros, alpha=0.5, **LINE_ARGS)


def select_data():
    selected = wages_plot_data[ (wages_plot_data.percent_time_idle >= reviews.value)]
    hist, edges = np.histogram(selected.percent_time_idle, bins=50)
    return hist, edges, selected

def update():
    hist, edges, df  = select_movies()

    x_name = "percent_time_idle"
    y_name = "hourly_wage"
    hh1.data_source.data["top"]   =  hist

    p.title.text = "%d Taxi drivers" % len(df.index)

controls = [reviews]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Movies"
