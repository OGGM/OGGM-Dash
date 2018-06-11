import dash
import dash_html_components as html
from server import server
import dash_core_components as dcc
from textwrap import dedent

app = dash.Dash(name='index', server=server, url_base_pathname='/')

app.title = 'GeoDataHack - dashboards'

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

app.layout = html.Div([
    html.Div(
        [
            html.H1(
                ' #OpenDataHack2018: Dashboards',
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
        dcc.Markdown(dedent('''
            This website was created during the 24 hours long
            [hackathon](https://events.ecmwf.int/event/79/overview) 
            organized by the ECMWF in June 2018.
            
            Here are the three apps we came up with:
            
            1. [Explore the world glaciers](/apps/explore)
            2. [Glacier change under various scenarios](/apps/scenarios)
            3. [Glacier geometry and change](/apps/geometry)
            
            Given the context, the apps probably have some rough edges: we plan to 
            make them better soon!
            
            Read our [blog post](http://oggm.org/2018/06/11/opendatahack2018/) for 
            more information, and [let us know](http://oggm.org) if you have comments!
            
            The code and data behind the apps is available [here](https://github.com/OGGM/OGGM-Dash). 
            ''')
        ),
        className='row'
    ),
    ],
    className='ten columns offset-by-one'
)

