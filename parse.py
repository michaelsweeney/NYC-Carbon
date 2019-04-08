import glob as gb
import os
import re
import pandas as pd

import numpy as np
import bunch

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.offline as py
import plotly.graph_objs as go





piedims = 350
piecolors = ['rgb(56, 151, 170)', 'rgb(83, 224, 120)', 'rgb(242, 224, 109)']



class Bldg:
    def __init__(self, area, bldg_type, cons_dict, rate_dict, carbon_dict, limit_dict, fineval, energy_dict):

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
            'Elec': cons_dict['Elec'] * energy_dict['Elec'],
            'Gas': cons_dict['Gas'] * energy_dict['Gas'],
            'Steam': cons_dict['Steam'] * energy_dict['Steam'],
        }

        self.eui = {
            'Elec': (1000 * self.energy_norm['Elec']) / area,
            'Gas': (1000 * self.energy_norm['Gas']) / area,
            'Steam': (1000 * self.energy_norm['Steam']) / area,
        }

        self.area = area
        self.bldg_type = bldg_type
        self.limit_dict = {key: val * area for key, val in limit_dict[bldg_type].items()}
        self.fine = fineval
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








def make_pie_charts(cost, carbon, eui):

    # cost pie
    cost_pie = go.Pie(values=cost['Value'],
                      labels=cost['SubTable'],
                      hole=0.5,
                      text=carbon['SubTable'],
                      marker={'colors': piecolors},
                      showlegend=False
                      )

    layout = go.Layout(title='Annual Energy Cost by Fuel Type ($)',
                       font={'family': 'Futura LT BT'},
                       autosize=True,
                       height=piedims,
                       width=piedims
                       )
    cost_fig = go.Figure([cost_pie], layout)

    # carbon pie
    carbon_pie = go.Pie(values=carbon['Value'],
                        labels=carbon['SubTable'],
                        text=carbon['SubTable'],
                        hole=0.5,
                        marker={'colors': piecolors},
                        showlegend=False
                        )

    layout = go.Layout(title='Annual Carbon Emissions by Fuel Type (tCO2/yr)',
                       font={'family': 'Futura LT BT'},
        autosize=False,
        height=piedims,
        width=piedims
                       )
    carbon_fig = go.Figure([carbon_pie], layout)

    # eui
    eui_pie = go.Pie(values=eui['Value'],
                     labels=eui['SubTable'],
                     text=carbon['SubTable'],
                     hole=0.5,
                     marker={'colors': piecolors},
                     showlegend=False
                     )
    layout = go.Layout(title='Annual Energy Use Intensity by Fuel Type (kbtu/sf/yr)',
                       font={'family': 'Futura LT BT'},
    autosize=False,
    height=piedims,width=piedims)
    eui_fig = go.Figure([eui_pie], layout)

    return (cost_fig, eui_fig, carbon_fig)



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
                       width=700,
                       height=500,
                       title='Annual Building Energy Cost Over Time',
                       font={'family': 'Futura LT BT'},
                       legend={'orientation': 'h',
                               'x': 0.2,
                               'y': -0.1},
                       xaxis={'fixedrange': True},
                       yaxis={'fixedrange': True})
    fig = go.Figure(data, layout)
    return fig
