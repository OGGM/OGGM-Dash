import dash
import dash_html_components as html
from server import server


app = dash.Dash(name='index', sharing=True, server=server, url_base_pathname='/')

app.title = 'GeoDataHack - dashboards'

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

app.layout = html.Div([

    html.Div(
        [
            html.H1(
                'OpenDataHack #2018: Dashboards',
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
            html.P("""
            This website was created during the 24hrs long
            hackathon organized by the ECMWF in June 2018.
            """),
            html.A("Click here for more information", href="http://oggm.org/OpenDataHack2018-Glaciers"),
            html.Br(),
            html.Br(),
            html.P("""
            Here are the three apps we came up with:
            """),
            html.Br(),
            html.A("Explore the world glaciers", href="/apps/explore"),
            html.Br(),
            html.Br(),
            html.A("Glacier change under various scenarios",
                   href="/apps/scenarios"),
            html.Br(),
            html.Br(),
            html.A("Glacier geometry and change", href="/apps/geometry")
        ],
        className='row'
    ),

],
    className='ten columns offset-by-one',
    style={
        "width": "1200px",
    }
)

# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)

