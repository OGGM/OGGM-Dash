import dash
import dash_html_components as html
from server import server


app = dash.Dash(name='index', sharing=True, server=server, url_base_pathname='/')

app.layout = html.Div([
    html.A("Geometry", href="/apps/geometry"),
    html.Br(),
    html.A("Explore", href="/apps/explore")
])
