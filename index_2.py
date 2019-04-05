import glob as gb
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app
import parse
import dash_dual_listbox as ddl




import dash_dual_listbox as dll
import dash
from dash.dependencies import Input, Output
import dash_html_components as html

app = dash.Dash('')

app.layout = html.Div([
    dll.DualList(id='DualList', available=[{'label': 'sdf', 'value': 'AL'},
                                       {'label': 'Alassdfsdfka', 'value': 'AK'},
                                       {'label': 'Arizona', 'value': 'AZ'},
                                       {'label': 'Arkansas', 'value': 'AR'},
                                       {'label': 'California', 'value': 'CA'},
                                       {'label': 'Colorado', 'value': 'CO'},
                                       {'label': 'sdfg', 'value': 'CT'},
                                       {'label': 'Delaware', 'value': 'DE'},
                                       {'label': 'Florida', 'value': 'FL'},
                                       {'label': 'Georgia', 'value': 'GA'}
                                           ],
                 selected=['AL']
                 ),
    html.Div(id='display')



])

@app.callback(Output('display', 'children'),
              [Input('DualList', 'available'),
               ])
def display_output(c):
    print (c)
    return c

if __name__ == "__main__":
    app.run_server(debug=True, port=8880)
