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

# todo handle 'inactive', fix and check conversions, stabilize viewports/divs. longer-term: consider sliding left sidenav
config = {'showLink': False,
          'displayModeBar': False}

app.title = "NYC 80x50 Energy + Performance estimator"


app.layout = dbc.Container([
    dbc.Navbar([
        dbc.Row(dbc.Col(html.H4("AKF Energy + Performance NYC Carbon Fine Calculator", id='title'), width=12)),
    ]),

    dbc.Row(dbc.Col(id='body', children=[dbc.Row(children=[
        dbc.Col(id='sidenav', children=[
            html.Div("General Info"),

            html.Div(className='input-group-text bldg_type_header', children=['Building Type']),
            dcc.Dropdown(className='form-control',
                         id='bldg_type',
                         options=[

                             {'label': 'A', 'value': 'A'},
                             {'label': 'B, (healthcare)', 'value': 'B (healthcare)'},
                             {'label': 'B, (normal)', 'value': 'B (normal)'},
                             {'label': 'E', 'value': 'E'},
                             {'label': 'F', 'value': 'F'},
                             {'label': 'H', 'value': 'H'},
                             {'label': 'I-1', 'value': 'I-1'},
                             {'label': 'I-2', 'value': 'I-2'},
                             {'label': 'I-3', 'value': 'I-3'},
                             {'label': 'I-4', 'value': 'I-4'},
                             {'label': 'M', 'value': 'M'},
                             {'label': 'R-1', 'value': 'R-1'},
                             {'label': 'R-2', 'value': 'R-2'},
                             {'label': 'S', 'value': 'S'},
                             {'label': 'U', 'value': 'U'},

                         ],
                         value='B (normal)',
                         placeholder='Building Type',
                         clearable=False),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Bldg Area", addon_type="prepend"),
                 dbc.Input(id='area_input', value='135000')], id='bldg_area_group'),
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

            html.Div("Annual Rates"),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Elec ($/kWh)",
                                     addon_type="prepend"),
                 dbc.Input(id='ann_kwh_cost_input')]),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Gas ($/Therm)",
                                     addon_type="prepend"),
                 dbc.Input(id='ann_gas_cost_input')]),

            dbc.InputGroup(
                [dbc.InputGroupAddon("Steam ($/MMBtu)",
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

        dbc.Col(id='bullet_col', width=3, children=
        [dcc.Graph(id='bullet_bar', config=config)
         ]),
        dbc.Col(id='cost_pie_col', children=[

            dbc.Row(id='figrow1', children=[
                dbc.Col(id='pie_col', children=[dcc.Graph(id='pie_summaries', config=config)
                                                ], width=12), ]),

            dbc.Row(id='figrow2', children=[

                dbc.Col(id='cost_col', children=[dcc.Graph(id='cost_bar', config=config)

                                                 ], width=12),
            ])
        ], width=7),

    ]), ], width=12), id='bodyrow'),
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
    carbon_bullet = parse.make_carbon_bullet(carbon, co2limit, fine)
    cost_bar = parse.make_cost_bar(fine, cost)
    return pie_charts, carbon_bullet, cost_bar


if __name__ == "__main__":
    port = 8881
    # open in chrome #todo why does this open each time
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # url = 'http://127.0.0.1:{0}'.format(port)
    # webbrowser.get(chrome_path).open(url)
    app.run_server(debug=True, port=port, dev_tools_hot_reload=True)

