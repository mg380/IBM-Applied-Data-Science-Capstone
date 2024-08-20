# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value': 'ALL'}]+
                                                    [ {"label":site , "value":site} for site in pd.unique(spacex_df['Launch Site'])],
                                            value="ALL",
                                            placeholder="Select a Launch Site here",
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
                                                value=[int(min_payload), int(max_payload)]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = spacex_df.loc[spacex_df['Launch Site']==entered_site].groupby('class').count().reset_index()
        fig = px.pie(filtered_df, 
                     values='Launch Site', 
                     names='class', 
                     title='Total succesful Launches for site {}'.format(entered_site))
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value"))
def get_scatter_chart(entered_site, payload_range):
    print('Params: {} {}'.format(entered_site, payload_range))
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= int(payload_range[0])) &
                                (spacex_df['Payload Mass (kg)'] <= int(payload_range[1]))
                               ]
        mean_df = (filtered_df[['Booster Version Category','class']].groupby("Booster Version Category").mean()*100).round(1).reset_index()
        mean_df.rename(columns={"class":"success rate"},inplace=True)
        filtered_df = filtered_df.merge(mean_df,
                                        left_on='Booster Version Category',
                                        right_on='Booster Version Category')
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         symbol="success rate",
                         labels={'Booster Version Category':'Booster Version',
                                 "success rate":'Success rate'}, 
                         title='All sites - payload mass between {:8,d}kg and {:8,d}kg'.format(int(payload_range[0]),int(payload_range[1])))
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & 
                                (spacex_df['Payload Mass (kg)'] >= int(payload_range[0])) &
                                (spacex_df['Payload Mass (kg)'] <= int(payload_range[1]))
                               ]
        mean_df = (filtered_df[['Booster Version Category','class']].groupby("Booster Version Category").mean()*100).round(1).reset_index()
        mean_df.rename(columns={"class":"success rate"},inplace=True)        
        filtered_df = filtered_df.merge(mean_df,
                                        left_on='Booster Version Category',
                                        right_on='Booster Version Category')
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         symbol="success rate",
                         labels={'Booster Version Category':'Booster Version',
                                 "success rate":'Success rate'},
                         title='Site {} - payload mass between {:8,d}kg and {:8,d}kg'.format(entered_site,int(payload_range[0]),int(payload_range[1])))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
