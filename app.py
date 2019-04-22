'''todo
fix first column of inputs-  padding or whatever - make them flush


line up donuts
bottom bar graph y axis - title choking ticks
do donuts have enough space for callouts to swirl around?
figure out print (maybe button?) and why it doesn't print NAV automatically)
donuts are crowding titles or vice versa

#can i line up first line of pie / bars with 'annual consumption', and last line of pie / bars with middle of 'annual rates'?
line up  'NYC Carbon Fine Calculator' with building title (or vice versa)

'<1000' exception
clickable links: new tabs
'''

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
import dash_daq as daq
from parse import input_std_dict_rates

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True


config = {'showLink': False,
          'displayModeBar': False}
app.title = "NYC 80x50 Energy + Performance estimator"

app.layout = dbc.Container([
    dbc.Navbar(id='navbar', children=[
        dbc.Row([
            dbc.Col(id='nav_side_left', children=[
                html.A(
                    html.Img(id='logo', src='assets/logo.png'), href='http://akfgroup.com/', target="_blank"
                ),

            ], width=2),
            dbc.Col(id='nav_center', children=[
                html.H3("NYC Carbon Fine Calculator", id='title')
            ], width=8),

            dbc.Col(id='nav_side_right', children=[

                html.A(id='energy_performance_link', children=[html.Div('ENERGY'),
                                                               html.Div('+'),
                                                               html.Div('PERFORMANCE')],
                       href='https://www.akf-energyshift.com/',
                       target="_blank"),
            ], width=2),
        ])
    ]),
    dbc.Row(id='titlerow', children=[
        dbc.Col([
            dbc.Button('Print', className = 'print')

        ], width=1, id='print_col'),
        dbc.Col(id='building_name', children=[
            # html.H4('0000 Broadway'),
            dbc.Input(id='building_name_input', placeholder='Enter Building Name (optional)')

        ], width=10),

        dbc.Col(id='spacer', width=1, children=[

            # html.A("Print", href='Print'),

        ]), ]),
    dbc.Row(id='collapse_row', children=[
        dbc.Col([
            dbc.Collapse(id='collapse', is_open=True, children=[
                # dbc.Row(dbc.Col(html.H6('Input Project Information Below (todo: background colored differently)'))),

                dbc.Row([
                    dbc.Col(children=[html.Div("General Info", className='form_header'),
                                      html.Div(className='input-group-text bldg_type_header',
                                               children=[html.Div('Building Type'),
                                                         html.A(html.Div("?", id='bldg_type_question'),
                                                                href='https://up.codes/viewer/new_york_city/nyc-building-code-2014/chapter/3/use-and-occupancy-classification#3',
                                                                target="_blank")]
                                               ),
                                      dcc.Dropdown(className='form-control',
                                                   id='bldg_type',
                                                   options=[

                                                       {'label': 'A (Assembly)', 'value': 'A'},
                                                       {'label': 'B (Business)', 'value': 'B (normal)'},
                                                       {'label': 'B (Other)', 'value': 'B (healthcare)'},
                                                       # todo footnote
                                                       {'label': 'E (Educational)', 'value': 'E'},
                                                       {'label': 'F (Factory/Industrial)', 'value': 'F'},
                                                       {'label': '(H High Hazard)', 'value': 'H'},
                                                       {'label': 'I-1 (Institutional)', 'value': 'I-1'},
                                                       {'label': 'I-2 (Institutional)', 'value': 'I-2'},
                                                       {'label': 'I-3 (Institutional)', 'value': 'I-3'},
                                                       {'label': 'I-4 (Institutional)', 'value': 'I-4'},
                                                       {'label': 'M (Mercantile)', 'value': 'M'},
                                                       {'label': 'R-1 (Residential)', 'value': 'R-1'},
                                                       {'label': 'R-2 (Residential)', 'value': 'R-2'},
                                                       {'label': 'S (Storage)', 'value': 'S'},
                                                       {'label': 'U (Utility/Miscellaneous)', 'value': 'U'},

                                                   ],
                                                   value='R-2',
                                                   placeholder='Building Type',
                                                   clearable=False),
                                      dbc.InputGroup(
                                          [dbc.InputGroupAddon("Bldg Area", addon_type="prepend"),
                                           dbc.Input(id='area_input', value='135000')], id='bldg_area_group'), ],
                            width=4),

                    dbc.Col(children=[html.Div(children=["Annual Consumption"], className='form_header'),
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
                                html.Div("Blended Utility Rates", className='form_header')]),

                        ]),

                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Elec ($/kWh)",
                                                 addon_type="prepend"),

                             dbc.Input(id='ann_kwh_cost_input', value=input_std_dict_rates['Elec'])]),
                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Gas ($/Therm)",
                                                 addon_type="prepend"),

                             dbc.Input(id='ann_gas_cost_input', value=input_std_dict_rates['Gas'])]),

                        dbc.InputGroup(
                            [dbc.InputGroupAddon("Steam ($/mLbs)",
                                                 addon_type="prepend"),
                             dbc.Input(id='ann_steam_cost_input', value=input_std_dict_rates['Steam'])]),

                    ], width=4), ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Calculate', id='submit_btn'),

                    ], width=4, id='submit_col'),
                    dbc.Col([], width=4),
                    dbc.Col([

                        daq.BooleanSwitch(
                            id='rate_bool',
                            on=True),
                        html.Div("Use Typical Rates for Commercial Office Buildings", id='typ_rate_text'),

                    ], width=4, id='inp_bot_right_col'),

                ])
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
                dbc.Col([dcc.Graph(id='carbon_pie', config=config), ], width=4, className='col_nopad',
                        id='carbon_pie_col'),
                dbc.Col([dcc.Graph(id='eui_pie', config=config), ], width=4, className='col_nopad', id='eui_pie_col'),
            ]),

            dbc.Row(id='figrow_toggle', children=[

                dbc.Col([
                    html.Div("Normalize by Area", className='norm_tag'),
                    daq.BooleanSwitch(  # todo callbacks and format
                        id='norm_bool',
                        on=False)],
                    width=12, className='col_nopad', id='norm_toggle_col'

                ),

            ]),

            # dbc.Col([
            #     daq.BooleanSwitch(  # todo callbacks and format
            #         id='cost_bool',
            #         on=False)], width=4, className='col_nopad', id='cost_toggle_col'),
            #
            # dbc.Col([
            #
            #     daq.BooleanSwitch(  # todo callbacks and format
            #         id='carbon_bool',
            #         on=False
            #     )
            #     , ], width=4, className='col_nopad', id='carbon_toggle_col'),
            # dbc.Col([
            #     daq.BooleanSwitch(  # todo callbacks and format
            #         id='eui_bool',
            #         on=True
            #     )], width=4, className='col_nopad', id='eui_toggle_col'),

            dbc.Row(id='figrow2', children=[

                dbc.Col(id='cost_col', children=[dcc.Graph(id='cost_bar', config=config)

                                                 ], width=12),
            ])
        ], width=5),

    ], style={'visibility': 'hidden'}, ),
    dbc.Row(id='bottom_row', children=[
        html.H6("Notes and Clarifications"),

        html.P(
            "•	The above calculator is based on AKFs understanding and interpretation of the aged version of NYC Intro 1253c (This calculator provides an approximation of the impact of the new law and should not be relied on as actual results may vary) "),
        html.P(
            "•	Emission limits for 2035 – 2050 are not yet itemized for each individual occupancy group.  The fine identified here is based on the average value for all covered buildings that is identified in the law, and is subject to change."),
        html.P(
            "•	The bill mandates an advisory board be established, who’s purpose will be to provide advice and recommendations to the commissioner and to the mayor’s office of long term planning and sustainability.  These recommendations may ultimately change the carbon limits and associated fines depicted above."),
        html.P(
            "•	The law as written also outlines a number of possible adjustments to the annual building emissions limit.  These adjustment may be granted if capital improvements required for compliance are not reasonably possible, do not allow for a reasonable financial return, are a result of special circumstances related to the use of the building, or apply specifically for not-for-profit hospitals and healthcare facilities.  However the department is responsible for determining if the adjustments apply for each covered building."),
        html.P(
            '•	This tool currently only includes Electricity, Natural Gas, and Steam as fuel source inputs. Future versions will include Fuel Oil and will continue to provide updates alongside revisions to NYC Intro 1253c.'),

    ]),
    dcc.Store(id='split_df_stores')
], fluid=False)


@app.callback(
    [
        Output('ann_kwh_cost_input', 'value'),
        Output('ann_gas_cost_input', 'value'),
        Output('ann_steam_cost_input', 'value'),
    ],
    [
        Input('rate_bool', 'on'),
    ]
)
def populate_rates(stdbool):
    if stdbool:
        return (input_std_dict_rates['Elec'], input_std_dict_rates['Gas'], input_std_dict_rates['Steam'])
    else:
        return ('', '', '')


@app.callback(
    [
        Output('bodyrow', "style"),
        Output("cost_pie", "figure"),
        Output("carbon_pie", "figure"),
        Output("eui_pie", "figure"),
        Output("bullet_bar", "figure"),
        Output("cost_bar", "figure"),
    ],
    [
        Input("submit_btn", "n_clicks"),
        Input('norm_bool', 'on'),
        # Input('cost_bool', 'on'),
        # Input('carbon_bool', 'on'),
        # Input('eui_bool', 'on'),
    ],
    [
        State('bldg_type', 'value'),
        State('area_input', 'value'),
        State('ann_kwh_input', 'value'),
        State('ann_gas_input', 'value'),
        State('ann_steam_input', 'value'),
        State('ann_kwh_cost_input', 'value'),
        State('ann_gas_cost_input', 'value'),
        State('ann_steam_cost_input', 'value'),
    ],

)
def make_frame(n_clicks,
               norm_toggle,
               # cost_toggle,
               # carbon_toggle,
               # eui_toggle,
               bldg_type,
               area_input,
               ann_kwh_input,
               ann_gas_input,
               ann_steam_input,
               ann_kwh_cost_input,
               ann_gas_cost_input,
               ann_steam_cost_input,

               ):
    input_cons_dict = {
        'Elec': ann_kwh_input,
        'Gas': ann_gas_input,
        'Steam': ann_steam_input
    }
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

    cost_pie = parse.make_cost_pie(cost, float(area_input), norm=norm_toggle)
    carbon_pie = parse.make_carbon_pie(carbon, float(area_input), norm=norm_toggle)
    eui_pie = parse.make_eui_pie(eui, float(area_input), norm=norm_toggle)

    carbon_bullet = parse.make_carbon_bullet(carbon, co2limit, fine)
    cost_bar = parse.make_cost_bar(fine, cost)

    body_display = {'visibility': 'visible'}
    return body_display, cost_pie, carbon_pie, eui_pie, carbon_bullet, cost_bar


if __name__ == "__main__":
    port = 8880
    # open in chrome #todo why does this open each time
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # url = 'http://127.0.0.1:{0}'.format(port)
    # webbrowser.get(chrome_path).open(url)
    app.run_server(debug=True, port=port, dev_tools_hot_reload=True)
