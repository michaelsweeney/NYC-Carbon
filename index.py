import glob as gb
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app
import parse

# todo allow manual rates (and handle 'inactive', fix and check conversions, stabilize viewports/divs. longer-term: consider sliding left sidenav

limits = pd.read_csv('nyc_carbon_limits.csv')
limit_dict = limits
limit_dict.index = limits['DOB Occupancy groups']
limit_dict = limits[['2022-2023', '2024-2029', '2030-2049', '2050']]
limit_dict = limit_dict.T.to_dict()

config = {'showLink': False,
          'displayModeBar': False}

# static dictionaries/lookups
carbon_dict = {
    'Elec': 0.000288962,  # tCO2 / kWh
    'Gas': 0.005311,  # tCO2 / Therm
    'Steam': 66.4,  # kg/MMBtu
}
energy_dict = {
    'Elec': 3.412,
    'Gas': 100,
    'Steam': .01,
}

input_std_dict_rates = {
    'Elec': 0.18866,  # $ / kWh
    'Gas': 0.997,  # $ / Therm
    'Steam': 2.36,  # $ / MMBtu
}

fine_per_tCO2 = 268

app.title = "NYC 80x50 energy + performance estimator"

app.layout = dbc.Container([

    dbc.Navbar([
        dbc.Row(dbc.Col(html.H4("AKF Energy + Analytics NYC Carbon Fine Calculator"), width=12)),
    ]),

    dbc.Row([
        dbc.Col([
            html.Div("General Info"),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Bldg Area", addon_type="prepend"),
                 dbc.Input(id='area_input', value='135000')]),

            html.Br(),

            dcc.Dropdown(id='bldg_type',
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
                         placeholder='Building Type'),

            html.Br(),
            html.Div("Annual Consumption"),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Elec (kWh)", addon_type="prepend"),
                 dbc.Input(id='ann_kwh_input', value='1897217')]),
            dbc.InputGroup(
                [dbc.InputGroupAddon("Gas (Therms)", addon_type="prepend"),
                 dbc.Input(id='ann_gas_input', value=32103)]),

            dbc.InputGroup(
                [dbc.InputGroupAddon("Steam (MMBtu)", addon_type="prepend"), dbc.Input(id='ann_steam_input')]),
            html.Br(),

            dbc.Checklist(id='cost_toggle', options=[
                {'label': 'Use Default Rates', 'value': 'Y'}
            ],
                          values=['Y']
                          ),

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

            html.Br(),
            dbc.Button('Submit', id='submit_btn')

        ], width=2),


        dbc.Col(width=2, children=[dbc.Col([dcc.Graph(id='bullet_bar', config=config)
                         ], width=12),]),
        dbc.Col([

            dbc.Row(id='figrow1', children=[
                dbc.Col([dcc.Graph(id='summary_donut_eui', config=config)
                         ], width=4),
                dbc.Col([dcc.Graph(id='summary_donut_cost', config=config)
                         ], width=4),
                dbc.Col([dcc.Graph(id='summary_donut_carbon', config=config)
                         ], width=4),
            ]),
            dbc.Row(id='figrow2', children=[

                dbc.Col([dcc.Graph(id='cost_bar', config=config)

                         ], width=12),
            ])
        ], width=8),

    ]),
    dcc.Store(id='split_df_stores')

], fluid=True)


# @app.callback(
#     Output("cost_collapse", "is_open"),
#     [Input("cost_toggle", "values")],
#     [State("cost_collapse", "is_open")]
# )
# def toggle_collapse(values, is_open):
#     if values == ['Y']:
#         return True
#     else:
#         return False


# @app.callback(
# Output("summary_donut_eui", "figure"),
# Input('cost_toggle', 'values'))
# def cost_inactive(cost_toggle, value):
#     print (value)


@app.callback([
    Output("summary_donut_eui", "figure"),
    Output("summary_donut_cost", "figure"),
    Output("summary_donut_carbon", "figure"),
    Output("bullet_bar", "figure"),
    Output("cost_bar", "figure"),
],
    [Input("submit_btn", "n_clicks")],
    [
        State('bldg_type', 'value'),
        State('area_input', 'value'),
        State('ann_kwh_input', 'value'),
        State('ann_gas_input', 'value'),
        State('ann_steam_input', 'value'),

        State('ann_kwh_cost_input', 'value'),
        State('ann_gas_cost_input', 'value'),
        State('ann_steam_cost_input', 'value'),
        State('cost_toggle', 'values')
    ])
def make_frame(n_clicks, bldg_type, area_input, ann_kwh_input, ann_gas_input, ann_steam_input,
               ann_kwh_cost_input, ann_gas_cost_input, ann_steam_cost_input, cost_toggle):
    def try_float(num):
        '''returns float, else returns 0'''
        try:
            return float(num)
        except:
            return 0

    input_cons_dict = {
        'Elec': try_float(ann_kwh_input),
        'Gas': try_float(ann_gas_input),
        'Steam': try_float(ann_steam_input),
    }

    fineval = 268
    if cost_toggle == ["Y"]:
        input_rate_dict = input_std_dict_rates

    else:
        input_rate_dict = {
            'Elec': ann_kwh_cost_input,  # $ / kWh
            'Gas': ann_gas_cost_input,  # $ / Therm
            'Steam': ann_steam_cost_input,  # $ / MMBtu
        }

    bldg = parse.Bldg(try_float(area_input),
                      bldg_type,
                      input_cons_dict,
                      input_rate_dict,
                      carbon_dict,
                      limit_dict,
                      fineval,
                      energy_dict).to_frame()

    cost = bldg[(bldg['Table'] == 'Cost') & (bldg['Value'] != 0)]
    carbon = bldg[(bldg['Table'] == 'Carbon') & (bldg['Value'] != 0)]
    eui = bldg[(bldg['Table'] == 'EUI') & (bldg['Value'] != 0)]
    co2limit = bldg[bldg['Table'] == 'CO2 Limit']
    fine = bldg[bldg['Table'] == 'Annual Fine']
    pie_charts = parse.make_pie_charts(cost, carbon, eui)
    carbon_bullet = parse.make_carbon_bullet(carbon, co2limit)
    cost_bar = parse.make_cost_bar(fine, cost)
    return pie_charts[0], pie_charts[1], pie_charts[2], carbon_bullet, cost_bar


if __name__ == "__main__":
    app.run_server(debug=True, port=8881)
