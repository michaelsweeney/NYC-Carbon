import glob as gb
import os
import re
import pandas as pd

import numpy as np
import bunch

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import tools
import plotly.offline as py

import plotly.graph_objs as go

limits = pd.read_csv('nyc_carbon_limits.csv')
limit_dict = limits
limit_dict.index = limits['DOB Occupancy groups']
limit_dict = limits[['2024-2029', '2030-2034', '2035-2050 (est)']].astype(float)
limit_dict = limit_dict.T.to_dict()

piedims = 200
piemargins = {'t': 40,
              'b': 40,
              'l': 40,
              'r': 40
              }

# default 80
piecolors = ['rgb(56, 151, 170)', 'rgb(83, 224, 120)', 'rgb(242, 224, 109)']



# static dictionaries/lookups
carbon_dict = {
    'Elec': 0.000288962,  # tCO2 / kWh
    'Gas': 0.005311,  # tCO2 / Therm
    'Steam': 0.053646,  # tCO2/MMBtu (from 66.4 kg/MMBtu)
}
kbtu_dict = {  # convert to kbtu
    'Elec': 3.412,
    'Gas': 100,
    'Steam': 1194,
}

input_std_dict_rates = {
    'Elec': 0.22,  # $ / kWh
    'Gas': 0.997,  # $ / Therm
    'Steam': 35,  # $ / mLb
}


def try_float(num):
    '''returns float, else returns 0'''
    try:
        return float(num)
    except:
        return 0


fine_per_tCO2 = 268


class Bldg:
    def __init__(self, area, bldg_type, cons_dict, rate_dict=input_std_dict_rates):

        area = try_float(area)
        cons_dict = {key: try_float(val) for key, val in cons_dict.items()}
        rate_dict = {key: try_float(val) for key, val in rate_dict.items()}

        self.cons_dict = cons_dict

        self.cost_dict = {
            'Elec': cons_dict['Elec'] * rate_dict['Elec'],
            'Gas': cons_dict['Gas'] * rate_dict['Gas'],
            'Steam': cons_dict['Steam'] * rate_dict['Steam'],
        }
        self.carbon_dict = {
            'Elec': cons_dict['Elec'] * carbon_dict['Elec'],
            'Gas': cons_dict['Gas'] * carbon_dict['Gas'],
            'Steam': cons_dict['Steam'] * carbon_dict['Steam'],
        }
        self.energy_norm = {
            'Elec': cons_dict['Elec'] * kbtu_dict['Elec'],
            'Gas': cons_dict['Gas'] * kbtu_dict['Gas'],
            'Steam': cons_dict['Steam'] * kbtu_dict['Steam'],
        }

        self.eui = {
            'Elec': (self.energy_norm['Elec']) / area,
            'Gas': (self.energy_norm['Gas']) / area,
            'Steam': (self.energy_norm['Steam']) / area,
        }

        self.area = area
        self.bldg_type = bldg_type
        self.limit_dict = {key: val * area for key, val in limit_dict[bldg_type].items()}
        self.fine = fine_per_tCO2
        self.carbon_total = sum(self.carbon_dict.values())

        def fines(carbon_total, limit_dict, fine):
            fine_dict = {}
            for period, limit in limit_dict.items():
                if limit > carbon_total:
                    annual_fine = 0
                else:
                    annual_fine = (carbon_total - limit) * fine
                fine_dict[period] = annual_fine
            return fine_dict

        self.fine_dict = fines(self.carbon_total, self.limit_dict, self.fine)

    def to_frame(self):
        '''returns summary dataframe for plotting / exploring'''

        # by enduse
        cost_dict = self.cost_dict
        carbon_dict = self.carbon_dict
        cons_dict = self.cons_dict

        energy_dict = self.energy_norm
        eui_dict = self.eui

        # by time
        limit_dict = self.limit_dict
        fine_dict = self.fine_dict
        time = pd.DataFrame([limit_dict, fine_dict])
        time.index = ['CO2 Limit', 'Annual Fine']
        utilities = pd.DataFrame([cost_dict, carbon_dict, energy_dict, eui_dict])

        utilities.index = ['Cost', 'Carbon', 'Consumption', 'EUI']

        summary = pd.concat([utilities.unstack().reset_index(), time.unstack().reset_index()])
        summary = summary[['level_1', 'level_0', 0]]
        unitdict = {
            'Cost': '$',
            'Carbon': 'tC02',
            'Consumption': 'MMBtu',
            'CO2 Limit': 'tC02',
            'Annual Fine': '$',
            'EUI': 'kBtu/sf/yr'
        }
        summary['units'] = summary['level_1'].apply(lambda x: unitdict[x])
        summary.columns = ['Table', 'SubTable', 'Value', 'Units']
        summary = summary[['Table', 'SubTable', 'Units', 'Value']]
        return summary





def make_cost_pie(cost):
    cost_trace = go.Pie(values=cost['Value'].round(0),
                        labels=cost['SubTable'],
                        hole=0.5,
                        text=cost['SubTable'],
                        marker={'colors': piecolors},
                        showlegend=False,
                        hoverinfo='label+value+percent',
                        )
    cost_layout = go.Layout(dict(
                       font={'family': 'Futura LT BT'},
                       title='Cost ($)',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       width=piedims,
                       height=piedims,
                       xaxis={'showgrid': False},
                       yaxis={'showgrid': False},
        margin=piemargins
    ))
    cost_fig = go.Figure([cost_trace], cost_layout)
    return cost_fig



def make_carbon_pie(carbon):
    carbon_trace = go.Pie(values=carbon['Value'].round(0),
                          labels=carbon['SubTable'],
                          text=carbon['SubTable'],
                          hole=0.5,
                          marker={'colors': piecolors},
                          showlegend=False,
                          hoverinfo='label+value+percent'
                          )
    carbon_layout = go.Layout(dict(
        font={'family': 'Futura LT BT'},
        title='Carbon (tCO2)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=piedims,
        height=piedims,
        xaxis={'showgrid': False},
        yaxis={'showgrid': False},
        margin=piemargins
    ))
    carbon_fig = go.Figure([carbon_trace], carbon_layout)
    return carbon_fig


def make_eui_pie(eui):
    eui_trace = go.Pie(values=eui['Value'].round(0),
                       labels=eui['SubTable'],
                       text=eui['SubTable'],
                       hole=0.5,
                       marker={'colors': piecolors},
                       showlegend=False,
                       hoverinfo='label+value+percent'
                       )

    eui_layout = go.Layout(dict(
        font={'family': 'Futura LT BT'},
        title='EUI (kBtu/sf/Yr)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=piedims,
        height=piedims,
        xaxis={'showgrid': False},
        yaxis={'showgrid': False},
        margin=piemargins
    ))
    eui_fig = go.Figure([eui_trace], eui_layout)
    return eui_fig






def make_carbon_bullet(carbon, co2limit, fine):
    carbon_traces = [
        go.Bar(x=[1],
               y=[round(carbon['Value'].sum())],
               name='Carbon (tCO2)',
               width=0.75,
               opacity=1.0,
               marker={'color': 'rgb(100, 100, 100)'},
               showlegend=False,
               hoverinfo='name+y'
               )]
    data = carbon_traces

    layout = go.Layout(barmode='overlay',
                       font={'family': 'Futura LT BT'},
                       legend={'x': 1.07},
                       width=300,
                       height=600,
                       margin={'l': 45,
                               'r': 40,
                               't': 80,
                               'b': 40,
                               },
                       xaxis={'showticklabels': False,
                              'showgrid': False,
                              'fixedrange': True},

                       title=go.layout.Title(text='Building CO2 Intensity vs.<br>NYC Fine Thresholds over Time',
                                             x=0.38,
                                             y=0.95,
                                             xref='container',
                                             xanchor='center'),

                       yaxis={'showgrid': False,
                              'showline': False,
                              'zeroline': False,
                              'title': "Metric Tons CO2",
                              'fixedrange': True},
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',

                       )

    # add annotations
    layout.update({'annotations': [
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][0],
            'text': "{0}<br>${1}/yr".format(co2limit.reset_index()['SubTable'][0], "{:,}".format(round(list(fine['Value'])[0]))),
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][1],
            'text': "{0}<br>${1}/yr".format(co2limit.reset_index()['SubTable'][1], "{:,}".format(round(list(fine['Value'])[1]))),
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][2],
            'text': "{0}<br>${1}/yr".format(co2limit.reset_index()['SubTable'][2], "{:,}".format(round(list(fine['Value'])[2]))),
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        # {
        #     'x': 3,
        #     'y': co2limit.reset_index()['Value'][3],
        #     'text': co2limit.reset_index()['SubTable'][3],
        #     'showarrow': False,
        #     'align': 'left',
        #     'width': 100,
        # }
    ]

    })

    # add rectangles
    layout.update({'shapes': [
        {
            'type': 'rect',
            'x0': 0,
            'y0': 0,
            'x1': 2,
            'y1': co2limit.reset_index()['Value'][0],
            'opacity': 0.2,
            'layer': 'below',
            'line': {
                'color': 'rgba(128, 128, 128, 1)',
                'width': 1,
            },
            'fillcolor': 'rgba(255, 100, 0, 1)', },

        {
            'type': 'rect',
            'x0': 0,
            'y0': 0,
            'x1': 2,
            'y1': co2limit.reset_index()['Value'][1],
            'opacity': 0.2,
            'layer': 'below',
            'line': {
                'color': 'rgba(128, 128, 128, 1)',
                'width': 1,
            },
            'fillcolor': 'rgba(255, 75, 0, 1)', },

        {
            'type': 'rect',
            'x0': 0,
            'y0': 0,
            'x1': 2,
            'y1': co2limit.reset_index()['Value'][2],
            'opacity': 0.2,
            'layer': 'below',
            'line': {
                'color': 'rgba(128, 128, 128, 1)',
                'width': 1,
            },
            'fillcolor': 'rgba(255, 25, 0, 1)', },


        ]
    })

    figure = go.Figure(data, layout)
    return figure


def make_cost_bar(fine, cost):
    data = []

    try:
        elec_costs = round(cost.iloc[0, :]['Value'].round())
        elec_traces = go.Bar(x=fine.SubTable,
                             y=[round(elec_costs)] * len(fine.SubTable),
                             name='Elec ($)',
                             marker={'color': piecolors[0]})
        data.append(elec_traces)
    except:
        pass

    try:
        gas_costs = round(cost.iloc[1, :]['Value'].round())
        gas_traces = go.Bar(x=fine.SubTable,
                            y=[round(gas_costs)] * len(fine.SubTable),
                            name='Gas ($)',
                            marker={'color': piecolors[1]})
        data.append(gas_traces)
    except:
        pass

    try:
        steam_costs = round(cost.iloc[2, :]['Value'].round())
        steam_traces = go.Bar(x=fine.SubTable,
                              y=[round(steam_costs)] * len(fine.SubTable),
                              name='Steam ($)',
                              marker={'color': piecolors[2]})
        data.append(steam_traces)
    except:
        pass




    fine_traces = go.Bar(x=fine.SubTable,
                         y=round(fine.Value),
                         name='Carbon Fine ($)',
                         marker={'color': 'rgb(200, 83, 94)'}
                         )

    data.append(fine_traces)

    layout = go.Layout(barmode='stack',
                       width=600,
                       height=400,
                       title=go.layout.Title(text='Annual Building Utility Cost + Carbon Fines per Year',
                                       y=0.9),
                       font={'family': 'Futura LT BT'},
                       legend={'orientation': 'h',
                               'x': 0.2,
                               'y': -0.2},
                       margin={'l': 45,
                               'r': 40,
                               't': 80,
                               'b': 40,
                               },
                       xaxis={'fixedrange': True,
                              'showgrid': False,
                              'showline': False
                              },

                       yaxis={'fixedrange': True,
                              'showgrid': False,
                              'title': 'Cost per Year ($)',
                              'zerolinecolor': 'rgb(153,153,153)',

                              },



                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       )



    y_modifier = .05* (cost['Value'].sum() + fine['Value'].max())
    layout.update({'annotations': [
        {
            'x': 0,
            'y': list(fine['Value'])[0] + cost['Value'].sum() + y_modifier,
            'text': "${0}/yr".format("{:,}".format(round(list(fine['Value'])[0]))),
            'showarrow': False,
            'align': 'center',
            'width': 100,
        },
        {
            'x': 1,
            'y': list(fine['Value'])[1] + cost['Value'].sum() + y_modifier,
            'text': "${0}/yr".format("{:,}".format(round(list(fine['Value'])[1]))),
            'showarrow': False,
            'align': 'center',
            'width': 100,
        },
        {
            'x': 2,
            'y': list(fine['Value'])[2] + cost['Value'].sum() + y_modifier,
            'text': "${0}/yr".format("{:,}".format(round(list(fine['Value'])[2]))),
            'showarrow': False,
            'align': 'center',
            'width': 100,
        }
        ]
    }
    )

    fig = go.Figure(data, layout)
    return fig
