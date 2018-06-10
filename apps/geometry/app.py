import os
import pickle
import copy
import datetime as dt
import re

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import salem
from oggm import utils, cfg, workflow
from oggm.core import flowline

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from server import server

# Init data
cfg.initialize()

# Local working directory (where OGGM will write its output)
package_directory = os.path.dirname(os.path.abspath(__file__))
cfg.PATHS['working_dir'] = os.path.join(package_directory, 'data')

# Acc
ds = xr.open_dataset(os.path.join(package_directory, 'data', 'run_output_08.nc'))

# Go - initialize working directories
gdirs = workflow.init_glacier_regions()

models = []
point_lons = []
point_lats = []
for gdir in gdirs:
    model = flowline.FileModel(gdir.get_filepath('model_run',
                                        filesuffix='_08'))
    coords = []
    for fl in model.fls:
        x, y = fl.line.coords.xy
        lon, lat = gdir.grid.ij_to_crs(x, y, salem.wgs84)
        point_lons = np.append(point_lons, lon)
        point_lats = np.append(point_lats, lat)
        coords.append((lon, lat))
    model.coords = coords
    models.append(model)

time_range = [0, 300]

map_lon = 10.87
map_lat = 46.85
map_zoom = 10

app = dash.Dash(name='geometry', sharing=True,
                server=server, url_base_pathname='/apps/geometry')

app.title = 'GeoDataHack - Geometry'

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiZm1hdXNzaW9uIiwiYSI6ImNqaTY0aGZsbzA0MDMzcHF1NWh0dWI4NmQifQ.TmioqTQp7R9zK5DTf5rmNA'

layout = dict(
    autosize=True,
    height=700,
    # font=dict(color='#CCCCCC'),
    # titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    # plot_bgcolor="#191A1A",
    # paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Map Overview',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="satellite",
        center=dict(
            lon=map_lon,
            lat=map_lat
        ),
        zoom=map_zoom,
    )
)

marks = dict()
steps = np.arange(11) * 10
for s in steps:
    marks['{}'.format(s)] = {'label': '{}'.format(s)}

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    'OGGM Glacier geometry demo',
                    className='eight columns',
                ),
                html.Img(
                    src="https://raw.githubusercontent.com/OGGM/oggm/master/docs/_static/logos/oggm_s_alpha.png",
                    className='one columns',
                    style={
                        'height': '100',
                        'width': '225',
                        'float': 'right',
                        'position': 'relative',
                    },
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.P('Time:'),
                dcc.Slider(
                    id='time_slider',
                    min=0,
                    max=100,
                    step=1,
                    value=0,
                    marks=marks
                ),
                html.Div(id='slider-output-container')
            ],
            style={'margin-top': '20'}
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='ten columns',
                    style={'margin-top': '20'}
                ),
                # html.Div(
                #     [
                #         dcc.Graph(id='individual_graph')
                #     ],
                #     className='four columns',
                #     style={'margin-top': '20'}
                # ),
            ],
            className='row'
        ),
    ],
    className='ten columns offset-by-one',
)


# Selectors -> main graph
@app.callback(Output('main_graph', 'figure'),
              [Input('time_slider', 'value')],
              [State('main_graph', 'relayoutData')])
def make_main_figure(time_slider, main_graph_layout):

    if time_slider is not None:
        for model in models:
            model.run_until(time_slider)

    toplot_th = []
    for model in models:
        for l in model.fls:
            toplot_th = np.append(toplot_th, l.thick)

    toplot_size = np.where(toplot_th == 0, 0, 10)

    traces = []
    trace = dict(
        type='scattermapbox',
        lon=point_lons,
        lat=point_lats,
        name='glacier geom',
        marker=dict(
            size=toplot_size,
            opacity=0.8,
            colorscale='Viridis',
            color=toplot_th,
            cmin=0,
            cmax=200,
            colorbar=dict(
                title="Thickness (m)"
            )
        )
    )
    traces.append(trace)

    if (main_graph_layout is not None):
        try:
            lon = float(main_graph_layout['mapbox']['center']['lon'])
            lat = float(main_graph_layout['mapbox']['center']['lat'])
            zoom = float(main_graph_layout['mapbox']['zoom'])
            layout['mapbox']['center']['lon'] = lon
            layout['mapbox']['center']['lat'] = lat
            layout['mapbox']['zoom'] = zoom
        except KeyError:
            lon = map_lon
            lat = map_lat
            zoom = map_zoom
    else:
        lon = map_lon
        lat = map_lat
        zoom = map_zoom

    layout['mapbox']['center']['lon'] = lon
    layout['mapbox']['center']['lat'] = lat
    layout['mapbox']['zoom'] = zoom

    figure = dict(data=traces, layout=layout)
    return figure


# # Main graph -> individual graph
# @app.callback(Output('individual_graph', 'figure'),
#               [Input('time_slider', 'value')])
# def make_individual_figure(time_slider):
#
#     _layout = copy.deepcopy(layout)
#
#     if True:
#         annotation = dict(
#             text='No data available',
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper"
#         )
#         _layout['annotations'] = [annotation]
#         data = []
#     else:
#         rid = dff.rgi_id.values[0]
#         sel = ds.sel(rgi_id=rid).area * 1e-6
#         data = [
#             dict(
#                 type='scatter',
#                 mode='lines+markers',
#                 name='Gas Produced (mcf)',
#                 x=sel.time.data,
#                 y=sel.data,
#                 line=dict(
#                     shape="spline",
#                     smoothing=2,
#                     width=1,
#                     color='#fac1b7'
#                 ),
#                 marker=dict(symbol='diamond-open')
#             ),
#         ]
#         _layout['title'] = rid + ': Area (km2)'
#
#     figure = dict(data=data, layout=_layout)
#     return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
