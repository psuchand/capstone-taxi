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
percent_idle_selector = Slider(title="Percent Idle Time", value=15, start=5, end=50, step=5)

#Attempt at a histogram
p = figure(plot_height=600, # plot_width=p.plot_width,  #x_range=p.x_range,
           min_border=10, min_border_left=50, title ="Hourly Wage")
p.quad(bottom=0, left=edges[:-1], right=edges[1:])#, top=hzeros, alpha=0.5, **LINE_ARGS)
hh1 = p.quad(bottom=0, left=edges[:-1], right=edges[1:], top=hist)#, color="white", line_color="#3A5785")

def select_data():
    selected = wages_plot_data[ wages_plot_data.percent_time_idle >= percent_idle_selector.value]
    hist, edges = np.histogram(selected.hourly_wage.values, bins=50)
    return hist, edges, selected

def update():
    hist, edges, df  = select_data()
    hh1.data_source.data["top"] =  hist
    p.title.text = "%d Taxi drivers" % len(df.index)

controls = [percent_idle_selector]#, boxoffice, genre, min_year, max_year, oscars, director, cast, x_axis, y_axis]
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