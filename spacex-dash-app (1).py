# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Prepare dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Dropdown for Launch Site selection
    html.Div(dcc.Dropdown(id='site-dropdown',
                          options=dropdown_options,
                          value='ALL',
                          placeholder="Select a Launch Site here",
                          searchable=True
                          )),
    html.Br(),

    # TASK 2: Pie chart output
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'left'}),
    
    # TASK 3: Range Slider for Payload selection
    html.Div(dcc.RangeSlider(id='payload-slider',
                             min=0, max=10000, step=1000,
                             marks={i: f'{i} kg' for i in range(0, 10001, 2500)},
                             value=[min_payload, max_payload]
                             )),
    html.Br(),

    # TASK 4: Scatter chart output
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ----------------------------------------------------------------------
# TASK 2: Callback function to render success-pie-chart (CORRECTED LOGIC)
# ----------------------------------------------------------------------
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter for successful launches (class=1) across all sites
        success_df = spacex_df[spacex_df['class'] == 1]
        
        # Count total successful launches for each site
        site_success_counts = success_df.groupby('Launch Site')['class'].count().reset_index()
        site_success_counts.rename(columns={'class': 'Success Count'}, inplace=True)
        
        # Create pie chart showing success count per site
        fig = px.pie(site_success_counts, 
                     values='Success Count', 
                     names='Launch Site', 
                     title='Total Successful Launches By Site')
        return fig
    else:
        # Filter for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Calculate the count of success (1) and failure (0) outcomes
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['class'] = site_counts['class'].map({1: 'Success', 0: 'Failure'}) # Map for better labels

        # Create pie chart showing success vs. failed counts for the specific site
        fig = px.pie(site_counts, 
                     values='count', 
                     names='class',
                     title=f'Success vs. Failure Counts for Site {entered_site}')
        return fig

# ----------------------------------------------------------------------
# TASK 4: Callback function to render success-payload-scatter-chart
# ----------------------------------------------------------------------
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Filter the entire dataframe by the payload range first
    payload_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                                    (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        # Scatter plot for all sites within the payload range
        title = 'Payload vs. Mission Outcome for All Sites (Colored by Booster Version)'
        fig = px.scatter(payload_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class',
                         color='Booster Version Category',
                         title=title)
        return fig
    else:
        # Filter by both site and payload range
        site_payload_filtered_df = payload_filtered_df[payload_filtered_df['Launch Site'] == entered_site]
        
        # Scatter plot for the selected site within the payload range
        title = f'Payload vs. Mission Outcome for Site {entered_site} (Colored by Booster Version)'
        fig = px.scatter(site_payload_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class',
                         color='Booster Version Category',
                         title=title)
        return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)