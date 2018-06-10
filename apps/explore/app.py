import os
import pickle
import copy
import datetime as dt

import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from server import server

app = dash.Dash(name='explore', sharing=True,
                server=server, url_base_pathname='/apps/explore')

app.title = 'GeoDataHack - Explore'

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

# Load data
package_directory = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(package_directory, 'data',
                              'glacier_characteristics.csv'))
df = df.sort_values(by='rgi_area_km2')

area_range = [int(np.floor(df.rgi_area_km2.min())), int(np.ceil(df.rgi_area_km2.max()))]

df['text'] = ['Id: {} - Area: {:.2f} km2 - N Glaciers: {}'.format(i, a, n) for i, (a, n) in enumerate(zip(df.rgi_area_km2, df.n_glaciers))]

df = df.set_index('text')

map_lon = 0
map_lat = 0
map_zoom = 0

col_all_p = '#85c1e9'
col_sel_p = '#2e86c1'
col_all_t = '#f1948a'
col_sel_t = '#cb4335'
col_lat = '#7d3c98'

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiZm1hdXNzaW9uIiwiYSI6ImNqaTY0aGZsbzA0MDMzcHF1NWh0dWI4NmQifQ.TmioqTQp7R9zK5DTf5rmNA'

layout = dict(
    autosize=True,
    height=400,
    title='',
    dragmode='select',
)

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    'World glaciers explorer',
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
                html.P(
                    'Box-select on each plot, double click on the same plot to reset.',
                    className='eight columns',
                ),
                html.H6(
                    '',
                    id='glaciers_text',
                ),
            ],
            className='row'
        ),
        # html.Div(
        #     [
        #         html.P('Select ranges of data on each plot to '
        #                 'discover under which climate glaciers '
        #                 'are located.'),
        #     ],
        #     className='row'
        # ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            '',
                        ),
                    ],
                    className='four columns',
                    style={
                        'float': 'left',
                        'position': 'relative',
                        'margin-top': '0',
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='eight columns',
                    style={'margin-top': '0'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='lat_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '0'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='temp_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '0'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='precip_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '0'}
                ),
            ],
            className='row'
        ),
    ],
    className='ten columns offset-by-one',

style={
       "width": "1400px",
       }

)


def point_selector(dff, points):
    return dff.loc[[p['text'] for p in points]]

# Selectors -> glacier text
@app.callback(Output('glaciers_text', 'children'),
              [Input('lat_graph', 'selectedData'),
               Input('main_graph', 'selectedData'),
               Input('precip_graph', 'selectedData'),
               Input('temp_graph', 'selectedData'),
               ])
def update_glaciers_text(selected_lat, selected_map, selected_p, selected_t):

    dff = df.copy()
    if selected_lat is not None:
        dff = point_selector(dff, selected_lat['points'])
    if selected_map is not None:
        dff = point_selector(dff, selected_map['points'])
    if selected_p is not None:
        pmin, pmax = selected_p['range']['x']
        dff = dff.loc[(dff.tstar_avg_prcp <= pmax) &
                      (dff.tstar_avg_prcp >= pmin)]
    if selected_t is not None:
        pmin, pmax = selected_t['range']['x']
        dff = dff.loc[(dff.tstar_avg_temp_mean_elev <= pmax) &
                      (dff.tstar_avg_temp_mean_elev >= pmin)]
    return "No of Glaciers: {}".format(dff.n_glaciers.sum())


# Selectors -> main graph
@app.callback(Output('main_graph', 'figure'),
              [Input('lat_graph', 'selectedData'),
               Input('main_graph', 'selectedData'),
               Input('precip_graph', 'selectedData'),
               Input('temp_graph', 'selectedData'),
               ]
              )
def make_main_figure(selected_lat, selected_map, selected_p, selected_t):

    dff = df.copy()
    if selected_lat is not None:
        dff = point_selector(dff, selected_lat['points'])
    if selected_map is not None:
        dff = point_selector(dff, selected_map['points'])
    if selected_p is not None:
        pmin, pmax = selected_p['range']['x']
        dff = dff.loc[(dff.tstar_avg_prcp <= pmax) &
                      (dff.tstar_avg_prcp >= pmin)]
    if selected_t is not None:
        pmin, pmax = selected_t['range']['x']
        dff = dff.loc[(dff.tstar_avg_temp_mean_elev <= pmax) &
                      (dff.tstar_avg_temp_mean_elev >= pmin)]

    traces = []
    trace = dict(
        type='scattergeo',
        lon=dff['cenlon'],
        lat=dff['cenlat'],
        text=dff.index,
        mode='markers',
        marker=dict(
            size=4,
            opacity=0.8,
            colorscale='Viridis',
            color=dff['rgi_area_km2'],
            cmin=0,
            cmax=3200,
            colorbar=dict(
                title="Area (km<sup>2</sup>)"
            )
        ),
    )
    traces.append(trace)

    _layout = copy.deepcopy(layout)
    _layout['geo'] = dict(
        scope='world',
        projection=dict(type='natural earth'),
        showland=True,
        margin=go.Margin(
        l=-20,
        r=-20,
        b=-20,
        t=-20,
        ),
        landcolor="rgb(250, 250, 250)",
        subunitcolor="rgb(217, 217, 217)",
        countrycolor="rgb(217, 217, 217)",
        countrywidth=0.5,
        subunitwidth=0.5,
    )

    figure = dict(data=traces, layout=_layout)
    return figure


# Selectors -> count graph
@app.callback(Output('lat_graph', 'figure'),
              [Input('main_graph', 'selectedData'),
               Input('precip_graph', 'selectedData'),
               Input('temp_graph', 'selectedData'),
               ],
              )
def make_lat_figure(selected_map, selected_p, selected_t):

    dff = df.copy()
    if selected_map is not None:
        dff = point_selector(dff, selected_map['points'])
    if selected_p is not None:
        pmin, pmax = selected_p['range']['x']
        dff = dff.loc[(dff.tstar_avg_prcp <= pmax) &
                      (dff.tstar_avg_prcp >= pmin)]
    if selected_t is not None:
        pmin, pmax = selected_t['range']['x']
        dff = dff.loc[(dff.tstar_avg_temp_mean_elev <= pmax) &
                      (dff.tstar_avg_temp_mean_elev >= pmin)]

    data = [
        dict(
            type='scatter',
            mode='markers',
            x=dff.dem_mean_elev,
            y=dff.cenlat,
            text=dff.index,
            hoverinfo='skip',
            marker=dict(
                size=4,
                opacity=1,
                color=col_lat
            )
        ),
    ]

    _layout = copy.deepcopy(layout)
    _layout['showlegend'] = False
    _layout['xaxis'] = dict(range=[0, 6200], title='Altitude (m)')
    _layout['yaxis'] = dict(range=[-90, 90], title='Latidude')

    figure = dict(data=data, layout=_layout)
    return figure


# Selectors -> count graph
@app.callback(Output('precip_graph', 'figure'),
              [Input('lat_graph', 'selectedData'),
               Input('main_graph', 'selectedData'),
               Input('precip_graph', 'selectedData'),
               Input('temp_graph', 'selectedData'),
               ])
def make_precip_figure(selected_lat, selected_map, selected_p, selected_t):

    dff = df.copy()
    if selected_map is not None:
        dff = point_selector(dff, selected_map['points'])
    if selected_lat is not None:
        dff = point_selector(dff, selected_lat['points'])
    if selected_p is not None:
        pmin, pmax = selected_p['range']['x']
        dff = dff.loc[(dff.tstar_avg_prcp <= pmax) &
                      (dff.tstar_avg_prcp >= pmin)]
    if selected_t is not None:
        pmin, pmax = selected_t['range']['x']
        dff = dff.loc[(dff.tstar_avg_temp_mean_elev <= pmax) &
                      (dff.tstar_avg_temp_mean_elev >= pmin)]

    bins = np.arange(41) * 100

    pcp = df.tstar_avg_prcp.copy()
    pcp[~np.isfinite(pcp)] = 0
    hist1, edges1 = np.histogram(pcp, bins)
    scale = np.sum(hist1)
    hist1 = hist1 / scale

    pcp = dff.tstar_avg_prcp.copy()
    pcp[~np.isfinite(pcp)] = 0
    hist2, edges2 = np.histogram(pcp, bins)
    hist2 = hist2 / scale

    data = [
        dict(
            type='bar',
            x=(edges1[1:] + edges1[0:-1])/2,
            y=hist1,
            name='All',
            hoverinfo='skip',
            marker=dict(
                color=col_all_p
            ),
        ),
        dict(
            type='bar',
            x=(edges1[1:] + edges1[0:-1])/2,
            y=hist2,
            name='Selection',
            hoverinfo='skip',
            marker=dict(
                color=col_sel_p
            ),
        ),
    ]

    _layout = copy.deepcopy(layout)
    _layout['showlegend'] = True
    _layout['xaxis'] = dict(range=[0, 4100], title='Annual precipitation (mm yr<sup>-1</sup>)')
    _layout['yaxis'] = dict(title='Frequency')

    figure = dict(data=data, layout=_layout)
    return figure

# Selectors -> count graph
@app.callback(Output('temp_graph', 'figure'),
              [Input('lat_graph', 'selectedData'),
               Input('main_graph', 'selectedData'),
               Input('precip_graph', 'selectedData'),
               Input('temp_graph', 'selectedData'),
               ])
def make_temp_figure(selected_lat, selected_map, selected_p, selected_t):

    dff = df.copy()
    if selected_map is not None:
        dff = point_selector(dff, selected_map['points'])
    if selected_lat is not None:
        dff = point_selector(dff, selected_lat['points'])
    if selected_p is not None:
        pmin, pmax = selected_p['range']['x']
        dff = dff.loc[(dff.tstar_avg_prcp <= pmax) &
                      (dff.tstar_avg_prcp >= pmin)]
    if selected_t is not None:
        pmin, pmax = selected_t['range']['x']
        dff = dff.loc[(dff.tstar_avg_temp_mean_elev <= pmax) &
                      (dff.tstar_avg_temp_mean_elev >= pmin)]

    bins = np.arange(35) - 27

    pcp = df.tstar_avg_temp_mean_elev.copy()
    pcp[~np.isfinite(pcp)] = 0
    hist1, edges1 = np.histogram(pcp, bins)
    scale = np.sum(hist1)
    hist1 = hist1 / scale

    pcp = dff.tstar_avg_temp_mean_elev.copy()
    pcp[~np.isfinite(pcp)] = 0
    hist2, edges2 = np.histogram(pcp, bins)
    hist2 = hist2 / scale

    data = [
        dict(
            type='bar',
            x=(edges1[1:] + edges1[0:-1])/2,
            y=hist1,
            name='All',
            hoverinfo='skip',
            marker=dict(
                color=col_all_t
            ),
        ),
        dict(
            type='bar',
            x=(edges1[1:] + edges1[0:-1])/2,
            y=hist2,
            name='Selection',
            hoverinfo='skip',
            marker=dict(
                color=col_sel_t
            ),
        ),
    ]

    _layout = copy.deepcopy(layout)
    _layout['showlegend'] = True
    _layout['xaxis'] = dict(range=[-27, 7], title='Annual Temperature at avg. altitude (°C)')
    _layout['yaxis'] = dict(title='Frequency')

    figure = dict(data=data, layout=_layout)
    return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)

