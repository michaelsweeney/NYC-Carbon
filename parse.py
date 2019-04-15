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
limit_dict = limits[['2022-2023', '2024-2029', '2030-2049', '2050']]
limit_dict = limit_dict.T.to_dict()

piedims = 350
piecolors = ['rgb(56, 151, 170)', 'rgb(83, 224, 120)', 'rgb(242, 224, 109)']

# static dictionaries/lookups
carbon_dict = {
    'Elec': 0.000288962,  # tCO2 / kWh
    'Gas': 0.005311,  # tCO2 / Therm
    'Steam': 0.0064,  # tCO2/MMBtu (from 66.4 kg/MMBtu)
}
kbtu_dict = {  # convert to kbtu
    'Elec': 3.412,
    'Gas': 100,
    'Steam': 1000,
}

input_std_dict_rates = {
    'Elec': 0.18866,  # $ / kWh
    'Gas': 0.997,  # $ / Therm
    'Steam': 2.36,  # $ / MMBtu
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


def make_pie_subplots(cost, carbon, eui):
    cost_trace = go.Pie(values=cost['Value'],
                        labels=cost['SubTable'],
                        hole=0.5,
                        domain={'x': [0.0, 0.3],
                                'y': [0, 1]},
                        text=carbon['SubTable'],
                        marker={'colors': piecolors},
                        showlegend=False,
                        )
    carbon_trace = go.Pie(values=carbon['Value'],
                          labels=carbon['SubTable'],
                          text=carbon['SubTable'],
                          hole=0.5,
                          domain={'x': [0.33, 0.63],
                                  'y': [0, 1]},
                          marker={'colors': piecolors},
                          showlegend=False,
                          )

    eui_trace = go.Pie(values=eui['Value'],
                       labels=cost['SubTable'],
                       text=carbon['SubTable'],
                       hole=0.5,
                       domain={'x': [0.66, 0.97],
                               'y': [0, 1]},

                       marker={'colors': piecolors},
                       showlegend=False,
                       )

    layout = go.Layout(
                       font={'family': 'Futura LT BT'},
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       autosize=False,
                       width=700,
                       height=300,

                       xaxis={'showgrid': False},
                       yaxis={'showgrid': False},
                       annotations=[
                           {
                               'x': 0.1,
                               'y': 1.555,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': 'Cost ($)',
                               'showarrow': False,
                               'font': {'size': 17, 'color': 'rgb(60, 60, 60)'},
                               'align': 'left',
                           },
                           {
                               'x': 0.47,
                               'y': 1.555,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': 'Carbon (tCO2)',
                               'showarrow': False,
                               'font': {'size': 17, 'color': 'rgb(60, 60, 60)'},
                               'align': 'left',
                           },
                           {
                               'x': 0.88,
                               'y': 1.555,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': 'EUI (kbtu/sf/yr)',
                               'showarrow': False,
                               'font': {'size': 17, 'color': 'rgb(60, 60, 60)'},
                               'align': 'left',
                           },
                       ]
                       )

    # height=piedims,
    # width=piedims

    fig = go.Figure([cost_trace, carbon_trace, eui_trace], layout)

    # fig = tools.make_subplots(1, 3, subplot_titles=['Annual Energy Use Intensity by Fuel Type (kbtu/sf/yr)',
    #                                                 'Annual Energy Cost by Fuel Type ($)',
    #                                                 'Annual Carbon Emissions by Fuel Type (tCO2/yr)',
    #                                                 ])
    # fig.add_trace(eui_trace, 1, 1)
    # fig.add_trace(cost_trace, 1, 2)
    # fig.add_trace(carbon_trace, 1, 3)
    return fig


#
# def make_pie_charts(cost, carbon, eui):
#
#     # cost pie
#     cost_pie = go.Pie(values=cost['Value'],
#                       labels=cost['SubTable'],
#                       hole=0.5,
#                       text=carbon['SubTable'],
#                       marker={'colors': piecolors},
#                       showlegend=False
#                       )
#
#     layout = go.Layout(title='Annual Energy Cost by Fuel Type ($)',
#                        font={'family': 'Futura LT BT'},
#                        autosize=False,
#                        height=piedims,
#                        width=piedims,
#                        paper_bgcolor='rgba(0,0,0,0)',
#                        plot_bgcolor='rgba(0,0,0,0)',
#                        )
#     cost_fig = go.Figure([cost_pie], layout)
#
#     # carbon pie
#     carbon_pie = go.Pie(values=carbon['Value'],
#                         labels=carbon['SubTable'],
#                         text=carbon['SubTable'],
#                         hole=0.5,
#                         marker={'colors': piecolors},
#                         showlegend=False
#                         )
#
#     layout = go.Layout(title='Annual Carbon Emissions by Fuel Type (tCO2/yr)',
#                        font={'family': 'Futura LT BT'},
#                        paper_bgcolor='rgba(0,0,0,0)',
#                        plot_bgcolor='rgba(0,0,0,0)',
#         autosize=False,
#         height=piedims,
#         width=piedims
#                        )
#     carbon_fig = go.Figure([carbon_pie], layout)
#
#     # eui
#     eui_pie = go.Pie(values=eui['Value'],
#                      labels=eui['SubTable'],
#                      text=carbon['SubTable'],
#                      hole=0.5,
#                      marker={'colors': piecolors},
#                      showlegend=False,
#
#
#                      )
#     layout = go.Layout(title='Annual Energy Use Intensity by Fuel Type (kbtu/sf/yr)',
#                        font={'family': 'Futura LT BT'},
#                        paper_bgcolor='rgba(0,0,0,0)',
#                        plot_bgcolor='rgba(0,0,0,0)',
#                        autosize=False,
#                        height=piedims,
#                        width=piedims
#                        )
#
#     eui_fig = go.Figure([eui_pie], layout)
#     return (cost_fig, eui_fig, carbon_fig)


def make_carbon_bullet(carbon, co2limit):
    carbon_traces = [
        go.Bar(x=[1],
               y=[carbon['Value'].sum()],
               name='Carbon',
               width=0.75,
               opacity=1.0,
               marker={'color': 'rgb(50, 160, 180)'},
               showlegend=False)]
    data = carbon_traces

    layout = go.Layout(barmode='overlay',
                       font={'family': 'Futura LT BT'},
                       legend={'x': 1.07},
                       autosize=False,
                       width=400,
                       height=700,
                       xaxis={'showticklabels': False,
                              'showgrid': False,
                              'fixedrange': True},

                       title='Annual Building CO2 Intensity vs. NYC Fine Thresholds',
                       yaxis={'showgrid': False,
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
            'text': co2limit.reset_index()['SubTable'][0],
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][1],
            'text': co2limit.reset_index()['SubTable'][1],
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][2],
            'text': co2limit.reset_index()['SubTable'][2],
            'showarrow': False,
            'align': 'left',
            'width': 100,
        },
        {
            'x': 3,
            'y': co2limit.reset_index()['Value'][3],
            'text': co2limit.reset_index()['SubTable'][3],
            'showarrow': False,
            'align': 'left',
            'width': 100,
        }
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

        {
            'type': 'rect',
            'x0': 0,
            'y0': 0,
            'x1': 2,
            'y1': co2limit.reset_index()['Value'][3],
            'opacity': 0.2,
            'layer': 'below',
            'line': {
                'color': 'rgba(128, 128, 128, 1)',
                'width': 1,
            },
            'fillcolor': 'rgba(255, 0, 0, 1)', }, ]
    })

    figure = go.Figure(data, layout)
    return figure


def make_cost_bar(fine, cost):
    data = []

    try:
        elec_costs = cost.iloc[0, :]['Value']
        elec_traces = go.Bar(x=fine.SubTable,
                             y=[elec_costs] * len(fine.SubTable),
                             name='Elec ($)',
                             marker={'color': piecolors[0]})
        data.append(elec_traces)
    except:
        pass

    try:
        gas_costs = cost.iloc[1, :]['Value']
        gas_traces = go.Bar(x=fine.SubTable,
                            y=[gas_costs] * len(fine.SubTable),
                            name='Gas ($)',
                            marker={'color': piecolors[1]})
        data.append(gas_traces)
    except:
        pass

    try:
        steam_costs = cost.iloc[2, :]['Value']
        steam_traces = go.Bar(x=fine.SubTable,
                              y=[steam_costs] * len(fine.SubTable),
                              name='Steam ($)',
                              marker={'color': piecolors[2]})
        data.append(steam_traces)
    except:
        pass

    fine_traces = go.Bar(x=fine.SubTable,
                         y=fine.Value,
                         name='Carbon Fine ($)',
                         marker={'color': 'rgb(200, 83, 94)'}
                         )

    data.append(fine_traces)

    layout = go.Layout(barmode='stack',
                       autosize=False,
                       width=700,
                       height=400,
                       title='Annual Building Energy Cost Over Time',
                       font={'family': 'Futura LT BT'},
                       legend={'orientation': 'h',
                               'x': 0.2,
                               'y': -0.1},
                       xaxis={'fixedrange': True},
                       yaxis={'fixedrange': True},
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       )
    fig = go.Figure(data, layout)
    return fig
