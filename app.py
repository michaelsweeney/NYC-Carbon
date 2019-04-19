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
    dbc.Navbar(id='navbar', children=[
        dbc.Row([
            dbc.Col(id='nav_side_left', children=[
                html.A(

                    html.Img(id='logo', src='assets/logo.png'), href='http://akfgroup.com/')

            ], width=2),
            dbc.Col(id='nav_center', children=[
                html.H3("NYC Carbon Fine Calculator", id='title')
            ], width=8),

            dbc.Col(id='nav_side_right', children=[

                html.A(id='energy_performance_link', children=[html.Div('ENERGY'),
                                                               html.Div('+'),
                                                               html.Div('PERFORMANCE')],
                       href='https://www.akf-energyshift.com/'),
            ], width=2),
        ])
    ]),
    dbc.Row(id='titlerow', children=[
        dbc.Col([
            dbc.Button(html.Img(id='burg_svg', src='assets/burger.svg'), id='submit_btn'),
        ], width=1),
        dbc.Col(id='building_name', children=[html.H4('0000 Broadway')], width=10),
        dbc.Col(id='spacer', width=1), ]),
    dbc.Row(id='collapse_row', children=[
        dbc.Col([
            dbc.Collapse(id='collapse', is_open=True, children=[
                # dbc.Row(dbc.Col(html.H6('Input Project Information Below (todo: background colored differently)'))),
                dbc.Row([
                    dbc.Col(children=[html.Div("General Info"),
                                      html.Div(className='input-group-text bldg_type_header',
                                               children=['Building Type']),
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
                                           dbc.Input(id='area_input', value='135000')], id='bldg_area_group'), ],
                            width=4),

                    dbc.Col(children=[html.Div(children=["Annual Consumption"]),
                                      dbc.InputGroup(
                                          [dbc.InputGroupAddon("Elec (kWh)", addon_type="prepend"),
                                           dbc.Input(id='ann_kwh_input', value='1897217')]),
                                      dbc.InputGroup(
                                          [dbc.InputGroupAddon("Gas (Therms)", addon_type="prepend"),
                                           dbc.Input(id='ann_gas_input', value=32103)]),

                                      dbc.InputGroup(
                                          [dbc.InputGroupAddon("Steam (mLbs)", addon_type="prepend"),
                                           dbc.Input(id='ann_steam_input')]), ], width=4),

                    dbc.Col(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Div("Annual Rates")]),
                            dbc.Col([
                                dbc.Checklist(id='rate_toggle', options=[
                                    {'label': 'Use Default Rates', 'value': 'Y'}], values=['Y']), ]),
                        ]),

                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Elec ($/kWh)",
                                                 addon_type="prepend"),
                             dbc.Input(id='ann_kwh_cost_input')]),
                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Gas ($/Therm)",
                                                 addon_type="prepend"),
                             dbc.Input(id='ann_gas_cost_input')]),

                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Steam ($/mLbs)",
                                                 addon_type="prepend"),
                             dbc.Input(id='ann_steam_cost_input')]),

                    ], width=4), ]),

            ])
        ])
    ]),

    dbc.Row(id='bodyrow', children=[

            dbc.Col(id='bullet_col', width=5, children=[
                dcc.Graph(id='bullet_bar', config=config)
            ]),
            dbc.Col(id='pie_col', children=[

                dbc.Row(id='figrow1', children=[

                    dbc.Col([dcc.Graph(id='cost_pie', config=config), ], width=4, className='col_nopad', id='cost_pie_col'),
                    dbc.Col([dcc.Graph(id='carbon_pie', config=config), ], width=4, className='col_nopad', id='carbon_pie_col'),
                    dbc.Col([dcc.Graph(id='eui_pie', config=config), ], width=4, className='col_nopad', id='eui_pie_col'),
                ]),

                dbc.Row(id='figrow_toggle', children=[

                    dbc.Col([dbc.Checklist(options=[
                        {"label": "By Area", "value": 1},
                    ],
                        values=[], id='cost_toggle'), ], width=4, className='col_nopad', id='cost_toggle_col'),
                    dbc.Col([dcc.Checklist(options=[
                        {"label": "By Area1", "value": 1},
                    ],
                        values=[], id='carbon_toggle'), ], width=4, className='col_nopad', id='carbon_toggle_col'),
                    dbc.Col([
                        dcc.Checklist(options=[
                            {"label": "By Area", "value": 1},
                        ],
                            values=[], id='eui_toggle'), ], width=4, className='col_nopad', id='eui_toggle_col'),
                ]),

                dbc.Row(id='figrow2', children=[

                    dbc.Col(id='cost_col', children=[dcc.Graph(id='cost_bar', config=config)

                                                     ], width=12),
                ])
            ], width=5),

    ]),
    dbc.Row(id='bottom_row', children=[

        html.P('•	The above calculator is based on AKFs understanding and interpretation of the aged version of NYC Intro 1253'),

    html.P("•	The bill mandates an advisory board be established, who’s purpose will be to provide advice and recommendations to the commissioner and to the mayor’s office of long term planning and sustainability.  These recommendations may ultimately change the carbon limits and associated fines depicted above."),
  
html.P("•	The law as written also outlines a number of possible adjustments to the annual building emissions limit.  These adjustment may be granted if capital improvements required for compliance are not reasonably possible, do not allow for a reasonable financial return, are a result of special circumstances related to the use of the building, or apply specifically for not-for-profit hospitals and healthcare facilities.  However the department is responsible for determining if the adjustments apply for each covered building."),

    ]),

    dcc.Store(id='split_df_stores')
], fluid=False)


@app.callback(Output('collapse', 'is_open'),
              [Input('submit_btn', 'n_clicks')])
def toggle_collapse(nclicks):
    if (nclicks % 2) == 0:
        return True
    else:
        return False


@app.callback(
    [
        Output("cost_pie", "figure"),
        Output("carbon_pie", "figure"),
        Output("eui_pie", "figure"),
        Output("bullet_bar", "figure"),
        Output("cost_bar", "figure"),
    ],
    [
        Input("submit_btn", "n_clicks"),
        Input('bldg_type', 'value'),
        Input('area_input', 'value'),
        Input('ann_kwh_input', 'value'),
        Input('ann_gas_input', 'value'),
        Input('ann_steam_input', 'value'),
        Input('ann_kwh_cost_input', 'value'),
        Input('ann_gas_cost_input', 'value'),
        Input('ann_steam_cost_input', 'value'),
        Input('rate_toggle', 'values'),
        Input('cost_toggle', 'value'),
        Input('carbon_toggle', 'value'),
        Input('eui_toggle', 'value'),
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
               rate_toggle,
               cost_toggle,
               carbon_toggle,
               eui_toggle
               ):
    input_cons_dict = {
        'Elec': ann_kwh_input,
        'Gas': ann_gas_input,
        'Steam': ann_steam_input,
    }

    if rate_toggle == ["Y"]:
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

    cost_pie = parse.make_cost_pie(cost)
    carbon_pie = parse.make_carbon_pie(carbon)
    eui_pie = parse.make_eui_pie(eui)

    carbon_bullet = parse.make_carbon_bullet(carbon, co2limit, fine)
    cost_bar = parse.make_cost_bar(fine, cost)
    return cost_pie, carbon_pie, eui_pie, carbon_bullet, cost_bar


if __name__ == "__main__":
    port = 8880
    # open in chrome #todo why does this open each time
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # url = 'http://127.0.0.1:{0}'.format(port)
    # webbrowser.get(chrome_path).open(url)
    app.run_server(debug=True, port=port, dev_tools_hot_reload=True)
