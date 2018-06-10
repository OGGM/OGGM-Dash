import os
import pickle
import copy
import datetime as dt
import re

import pandas as pd
import xarray as xr
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
from server import server


app = dash.Dash(name='scenarios', sharing=True,
                server=server, url_base_pathname='/apps/scenarios')

app.title = 'GeoDataHack - Scenarios'

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

# Load data
package_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(package_directory, 'data')
df = pd.read_csv(os.path.join(data_directory, 'glacier_characteristics.csv'))
ds = xr.open_dataset(os.path.join(data_directory, 'run_output_00.nc'))

area_range = [int(np.floor(df.rgi_area_km2.min())), int(np.ceil(df.rgi_area_km2.max()))]

text = []
for rid, name, area in zip(df.rgi_id, df.name, df.rgi_area_km2):
    t = rid + ': {}'.format(name).replace('nan', '')
    t += '. Area: {:.2f}km2'.format(area)
    text.append(t)

df['text'] = text

map_lon = 10.4
map_lat = 46.1
map_zoom = 5

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiZm1hdXNzaW9uIiwiYSI6ImNqaTY0aGZsbzA0MDMzcHF1NWh0dWI4NmQifQ.TmioqTQp7R9zK5DTf5rmNA'

layout = dict(
    autosize=True,
    height=500,
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

glacier_properties= {
    'length': {
        'name':'Length',
        'units':'km',
        'multiplier': 1e-3
        },
    'area': {
        'name':'Area',
        'units':'km\u00b2',
        'multiplier': 1e-6
        },
    'volume': {
        'name':'Volume',
        'units':'km\u00b3',
        'multiplier': 1e-9
        },
    'temp': {
        'name':'Temperature',
        'units':'\u00b0C',
        'multiplier': 1
        },
    'prcp': {
        'name':'Precipitation',
        'units':'mm/year',
        'multiplier': 1
        },
    'prcp_sol': {
        'name':'Solid Precipitation',
        'units':'mm/year',
        'multiplier': 1
        },
    'ela': {
        'name':'Equilibrium Line Altitude',
        'units':'m above sea level',
        'multiplier': 1
        }
}


def run_selection_label(filename):
    """
    Returns the decriptive name to populate the drop-down menu for filename.
    """
    temperature = float(filename[-5:-3])/10
    return '%2.1f\u00b0C above pre-industrial levels' % temperature


# Locate temperature files
pattern = r'run_output_\d{2}.nc'
temperature_options = []

for file in os.listdir(data_directory):
    if re.match(pattern, file):
        label = run_selection_label(file)
        temperature_options.append({
            'label': label,
            'value': os.path.join(data_directory, file)
            }
        )

parameter_options = []
for prop in glacier_properties.keys():
    parameter_options.append(
        {
            'label': glacier_properties[prop]['name'],
            'value': prop
        }
    )

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    'OGGM Map demo',
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
                html.H5(
                    '',
                    id='glaciers_text',
                    className='two columns'
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.P('Filter by area:'),
                dcc.RangeSlider(
                    id='area_slider',
                    min=area_range[0],
                    max=area_range[1],
                    value=area_range
                ),
            ],
            style={'margin-top': '20'}
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.H5('Select temperature'),
                        dcc.Dropdown(
                            id='run_selection',
                            options=temperature_options,
                            value=temperature_options[0]['value'],
                            multi=True
                        ),
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        html.H5('Select plot'),
                        dcc.Dropdown(
                            id='param_selection',
                            options=parameter_options,
                            value=parameter_options[0]['value'],
                        ),
                    ],
                    className='four columns',
                    style={'margin-top': '20'}
                )
            ],
            className='row'
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='individual_graph')
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
                ),
            ],
            className='row'
        ),
    ],
    className='ten columns offset-by-one'
)


# Selectors -> glacier text
@app.callback(Output('glaciers_text', 'children'),
              [Input('area_slider', 'value')])
def update_glaciers_text(area_slider):

    dff = df.loc[(df.rgi_area_km2 >= area_slider[0]) &
                 (df.rgi_area_km2 <= area_slider[1])]
    return "No of Glaciers: {}".format(dff.shape[0])


# Selectors -> main graph
@app.callback(Output('main_graph', 'figure'),
              [Input('area_slider', 'value')],
              [State('main_graph', 'relayoutData')])
def make_main_figure(area_slider, main_graph_layout):

    dff = df.loc[(df.rgi_area_km2 >= area_slider[0]) &
                 (df.rgi_area_km2 <= area_slider[1])]

    traces = []
    trace = dict(
        type='scattermapbox',
        lon=dff['cenlon'],
        lat=dff['cenlat'],
        text=dff['text'],
        name=dff['rgi_id'],
        marker=dict(
            size=6,
            opacity=1,
            color='#FF0000'
        )
    )
    traces.append(trace)

    lon = map_lon
    lat = map_lat
    zoom = map_zoom

    layout['mapbox']['center']['lon'] = lon
    layout['mapbox']['center']['lat'] = lat
    layout['mapbox']['zoom'] = zoom

    figure = dict(data=traces, layout=layout)
    return figure


# Main graph -> individual graph
@app.callback(Output('individual_graph', 'figure'),
              [Input('main_graph', 'hoverData'),
              Input('run_selection','value'),
              Input('param_selection','value')])
def make_individual_figure(main_graph_hover, run_selection, param_selection):
    
    if main_graph_hover is None:
        main_graph_hover = {'points': [{'text': df.text.values[0]}]}
    
    # Get the properties of the selected parameter
    param_name = glacier_properties[param_selection]['name']
    param_units = glacier_properties[param_selection]['units']
    param_multiplier = glacier_properties[param_selection]['multiplier']

    t = main_graph_hover['points'][0]['text']
    dff = df.loc[df.text == t]
    rid = dff.rgi_id.values[0]

    # Make sure that the run selection is always formatted as a list
    if len(run_selection) == 0:
        run_selection = []
    elif type(run_selection) == str:
        run_selection = [run_selection]

    # Loop through each run  selected
    data = []
    for run in run_selection:

        ds = xr.open_dataset(run)

        
        sel = getattr(ds.sel(rgi_id=rid),param_selection) * param_multiplier
        data.append(
            go.Scatter(
                type='scatter',
                mode='lines+markers',
                name=run_selection_label(run),
                x=sel.time.data,
                y=sel.data,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1
                ),
                marker=dict(symbol='diamond-open')
            )
        )
        
    layout_graph = go.Layout(
        title=rid,
        xaxis=dict(title='Time (years)'),
        yaxis=dict(title='{} ({})'.format(param_name, param_units)),
        showlegend=True,
        legend=go.Legend(
                x=0,
                y=1.0
            ),
            margin=go.Margin(l=40, r=0, t=40, b=30)
    )
    
    figure = dict(data=data, layout=layout_graph)
    return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
