import os
import pickle
import copy
import datetime as dt

import pandas as pd
import xarray as xr
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

# Load data
df = pd.read_csv('./data/glacier_characteristics.csv')
ds = xr.open_dataset('./data/run_output_rdn_tstar.nc')

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
                        dcc.Graph(id='main_graph')
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='individual_graph')
                    ],
                    className='four columns',
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
              [Input('main_graph', 'hoverData')])
def make_individual_figure(main_graph_hover):

    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {'points': [{'text': df.text.values[0]}]}

    t = main_graph_hover['points'][0]['text']
    dff = df.loc[df.text == t]

    if len(dff) == 0:
        annotation = dict(
            text='No data available',
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        layout_individual['annotations'] = [annotation]
        data = []
    else:
        rid = dff.rgi_id.values[0]
        sel = ds.sel(rgi_id=rid).area * 1e-6
        data = [
            dict(
                type='scatter',
                mode='lines+markers',
                name='Gas Produced (mcf)',
                x=sel.time.data,
                y=sel.data,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#fac1b7'
                ),
                marker=dict(symbol='diamond-open')
            ),
        ]
        layout_individual['title'] = rid + ': Area (km2)'

    figure = dict(data=data, layout=layout_individual)
    return figure

# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
