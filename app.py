import glob as gb
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import parse
import webbrowser


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True



# todo allow manual rates (and handle 'inactive', fix and check conversions, stabilize viewports/divs. longer-term: consider sliding left sidenav
config = {'showLink': False,
          'displayModeBar': False}

app.title = "NYC 80x50 energy + performance estimator"

app.layout = dbc.Container([
    dbc.Navbar([
        dbc.Row(dbc.Col(html.H4("AKF Energy + Analytics NYC Carbon Fine Calculator", id='title'), width=12)),
    ]),

dbc.Row(dbc.Col(id='body', children=[dbc.Row(children=[
        dbc.Col(id = 'sidenav',children=[
            html.Div("General Info"),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Bldg Area", addon_type="prepend"),
                 dbc.Input(id='area_input', value='135000')]),

            html.Div(className = 'input-group-text bldg_type_header', children=['Building Type']),
            dcc.Dropdown(className = 'form-control',
                         id='bldg_type',
                         options=[
                             {'label': "A, Assembly", 'value': 'A'},
                             {'label': "E, Education", 'value': 'E'},
                             {'label': "H, High Hazard", 'value': 'H'},
                             {'label': "U, Utility & Misc.", 'value': 'U'},
                             {'label': "B, Business", 'value': 'B'},
                             {'label': "I, Institutional", 'value': 'I'},
                             {'label': "M, Mercantile", 'value': 'M'},
                             {'label': "F, Factory & Industrial", 'value': 'F'},
                             {'label': "S, Storage", 'value': 'S'},
                             {'label': "R, Residential", 'value': 'R'}
                         ],
                         value='R',
                         placeholder='Building Type',
                         clearable=False),
            html.Br(),

            html.Div(children=["Annual Consumption"]),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Elec (kWh)", addon_type="prepend"),
                 dbc.Input(id='ann_kwh_input', value='1897217')]),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Gas (Therms)", addon_type="prepend"),
                 dbc.Input(id='ann_gas_input', value=32103)]),

            dbc.InputGroup(
                [dbc.InputGroupAddon("Steam (MMBtu)", addon_type="prepend"), dbc.Input(id='ann_steam_input')]),
            html.Br(),

            html.Div("Annual Cost"),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Elec ($)",
                                     addon_type="prepend"),
                 dbc.Input(id='ann_kwh_cost_input')]),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Gas ($)",
                                     addon_type="prepend"),
                 dbc.Input(id='ann_gas_cost_input')]),

            dbc.InputGroup(
                [dbc.InputGroupAddon("Steam ($)",
                                     addon_type="prepend"),
                 dbc.Input(id='ann_steam_cost_input')]),

            dbc.Checklist(id='cost_toggle', options=[
                {'label': 'Use Default Rates', 'value': 'Y'}
            ],
                          values=['Y']
                          ),
            html.Br(),
            dbc.Button('Submit', id='submit_btn')

        ], width=2),

        dbc.Col(width=2, children=[
            dbc.Col([dcc.Graph(id='bullet_bar', config=config)
                                            ], width=12), ]),

        dbc.Col([

            dbc.Row(id='figrow1', children=[
                dbc.Col([dcc.Graph(id='pie_summaries', config=config)
            ], width=12),]),

            dbc.Row(id='figrow2', children=[

                dbc.Col([dcc.Graph(id='cost_bar', config=config)

                         ], width=12),
            ])
        ], width=8),

    ]),], width=12)),



dcc.Store(id='split_df_stores')
], fluid=True)




# @app.callback(
# Output("summary_donut_eui", "figure"),
# Input('cost_toggle', 'values'))
# def cost_inactive(cost_toggle, value):
#     print (value)

@app.callback(
[
    Output("pie_summaries", "figure"),
    Output("bullet_bar", "figure"),
    Output("cost_bar", "figure"),
],
[
    Input("submit_btn", "n_clicks"),
    Input('bldg_type', 'value'),
],
[
        State('area_input', 'value'),
        State('ann_kwh_input', 'value'),
        State('ann_gas_input', 'value'),
        State('ann_steam_input', 'value'),
        State('ann_kwh_cost_input', 'value'),
        State('ann_gas_cost_input', 'value'),
        State('ann_steam_cost_input', 'value'),
        State('cost_toggle', 'values'),
 ])

def make_frame(n_clicks,
               bldg_type,
               area_input,
               ann_kwh_input,
               ann_gas_input,
               ann_steam_input,
               ann_kwh_cost_input,
               ann_gas_cost_input,
               ann_steam_cost_input,
               cost_toggle):

    input_cons_dict = {
        'Elec': ann_kwh_input,
        'Gas': ann_gas_input,
        'Steam': ann_steam_input,
    }

    if cost_toggle == ["Y"]:
        bldg = parse.Bldg(area_input,
                          bldg_type,
                          input_cons_dict).to_frame()

    else:
        input_rate_dict = {
            'Elec': ann_kwh_cost_input,  # $ / kWh
            'Gas': ann_gas_cost_input,  # $ / Therm
            'Steam': ann_steam_cost_input,  # $ / MMBtu
        }
        bldg = parse.Bldg(area_input,
                          bldg_type,
                          input_cons_dict,
                          input_rate_dict).to_frame()

    cost = bldg[(bldg['Table'] == 'Cost') & (bldg['Value'] != 0)]
    carbon = bldg[(bldg['Table'] == 'Carbon') & (bldg['Value'] != 0)]
    eui = bldg[(bldg['Table'] == 'EUI') & (bldg['Value'] != 0)]
    co2limit = bldg[bldg['Table'] == 'CO2 Limit']
    fine = bldg[bldg['Table'] == 'Annual Fine']
    pie_charts = parse.make_pie_subplots(cost, carbon, eui)
    carbon_bullet = parse.make_carbon_bullet(carbon, co2limit)
    cost_bar = parse.make_cost_bar(fine, cost)
    return pie_charts, carbon_bullet, cost_bar


if __name__ == "__main__":
    port = 8881
    # open in chrome #todo why does this open each time
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # url = 'http://127.0.0.1:{0}'.format(port)
    # webbrowser.get(chrome_path).open(url)
    app.run_server(debug=True, port=port, dev_tools_hot_reload=True)
