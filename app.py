import pandas as pd
from dash import Dash, dcc, html
from scraper import get_all_this_season_stats
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
import re
import plotly.graph_objects as go

df = pd.read_csv('test.csv')

app = Dash(__name__, title='Football visualisations dashboard', external_stylesheets=[dbc.themes.CYBORG])

topbar = html.Div(
    children=[
        html.Div(id='links-container', children=[
            dcc.Link('Home', href='/', style={'margin-right': '20px'}),            
            dcc.Link('Player', href='/player-view', style={'margin-right': '20px'}),
            dcc.Link('Team stats', href='/team-stats', style={'margin-right': '20px'})
        ])
    ]
)

content = html.Div(children=[

    html.Div([
                          html.Div(style={'height': '40px'}),   
    # The following are the different options to filter the scatter graph
                          html.H6("Highlight a player...", style={'color': '#ffffff'}),
                          dcc.Dropdown(
                                      id='player-highlight',
                                      options=[{'label': player['player'] + ', ' + player['team'], 'value': player['player']} for index, player in df.iterrows()],
                                      placeholder='Highlight a player',
                                      multi=True
                                  ),

                        html.Div(style={'height': '30px'}),                    

                        # Change what the scatters are coloured with
                        html.H6("Colour option", style={'color': '#ffffff'}),
                        dcc.Dropdown(
                                      id='colour_option',
                                      options=[{'label': 'League', 'value': 'comp_level'},
                                               {'label': 'Position', 'value': 'position'}
                                               ],
                                      value='comp_level',  # Default selected value
                                      multi=False,
                                  ),

                          html.Div(style={'height': '30px'}),

                          html.Div([
                              html.H6("X and Y filters", style={'color': '#ffffff'}),
                              html.Div([
                                  dcc.Dropdown(
                                      id='x-axis-dropdown',
                                      options=[{'label': col, 'value': col} for col in df.columns],
                                      value='xg_assist_per90',  # Default selected value
                                      multi=False,
                                  ),
                              ]),

                              html.Div([
                                  dcc.Dropdown(
                                      id='y-axis-dropdown',
                                      options=[{'label': col, 'value': col} for col in df.columns],
                                      value='xg_per90',  # Default selected value
                                      multi=False,
                                  ),
                              ] ),

                            html.Div(style={'height': '30px'}),

                              html.Div([
                                    html.H6("Minimum threshold of 90s", style={'color': '#ffffff'}),
                                  dcc.Input(id='90s_input', type='text', value=str(int(max(df['minutes_90s']) * 0.75)),
                                            placeholder='Minimum number of 90s', pattern="[0-9]*"),
                              ]),

                            html.Div(style={'height': '30px'}),

                              html.Div([
                                  html.H6("Select positions", style={'color': '#ffffff'}),
                                  dcc.Dropdown(
                                      id='position_checklist',
                                      options=[
                                          {'label': 'Defenders', 'value': 'DF'},
                                          {'label': 'Midfielders', 'value': 'MF'},
                                          {'label': 'Forwards', 'value': 'FW'}
                                      ],
                                      multi=True,
                                      value=['DF','MF','FW'],
                                      style={'color': '#ffffff'}    
                                  ),
                                  html.H6("Select leagues", style={'color': '#ffffff'}),
                                dcc.Dropdown(
                                      id='league_filter',
                                      options=[
                                          {'label': 'Premier League', 'value': 'eng Premier League'},
                                          {'label': 'Ligue 1', 'value': 'fr Ligue 1'},
                                          {'label': 'Serie A', 'value': 'it Serie A'},
                                          {'label': 'Bundesliga', 'value': 'de Bundesliga'},
                                          {'label': 'La Liga', 'value': 'es La Liga'}
                                      ],
                                      multi=True,
                                      value=['eng Premier League','fr Ligue 1','it Serie A', 'de Bundesliga', 'es La Liga'],
                                  ),

                                  html.Div([
                                  html.Button('Other options', id='other-options', className='options-button', n_clicks=1),
                                  html.Div(id='other-options-container', children=[
                                        html.H6("Select x label", style={'color': '#ffffff'}, id='x-lab-head'),
                                        dcc.Input(id='x-input', type='text', placeholder='Enter X Label', value='xg_assist_per90'),

                                        html.H6("Select y label", style={'color': '#ffffff'}, id='y-lab-head'),
                                        dcc.Input(id='y-input', type='text', placeholder='Enter Y Label', value='xg_per90'),

                                        html.H6("Select title", style={'color': '#ffffff'}, id='title-lab-head'),
                                        dcc.Input(id='title-input', type='text', placeholder='Enter title', value=''),

                                        html.H6("Select legend label", style={'color': '#ffffff'}, id='legend-lab-head'),
                                        dcc.Input(id='legend-input', type='text', placeholder='Enter Legend', value='League')
                                  ])
                              ]),
                              ]),

                      ]) 
], style={'width': '20%', 'float': 'left'}) ,   

html.Div([
                              # Scatter graph
                          dcc.Graph(id='scatter-plot')
], style={'width': '80%', 'float': 'right'})

    ])




app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       topbar, 
                       content])

"""@app.callback(
        Output('links-container', 'children'),
        [Input('url', 'pathname')]
)"""

def update_page(pathname):
    if pathname == '/page-1':
        return 'page1_layout'
    elif pathname == '/page-2':
        return 'page2_layout'
    else:   
        return 'home_layout'
 

@app.callback(
    [Output('x-input', 'style'),
     Output('y-input', 'style'),
     Output('title-input', 'style'),
     Output('legend-input', 'style'),

     Output('x-lab-head', 'style'),
     Output('y-lab-head', 'style'),
     Output('title-lab-head', 'style'),
     Output('legend-lab-head', 'style')],

    [Input('other-options', 'n_clicks')]
)

def update_visibility(n_clicks):
    input_visibility = {'display': 'block'} if n_clicks % 2 == 0 else {'display': 'none'}
    return input_visibility, input_visibility, input_visibility, input_visibility, input_visibility, input_visibility, input_visibility, input_visibility
@app.callback(
        [Output('x-input', 'value'),
         Output('y-input', 'value')],
         [Input('x-axis-dropdown', 'value'),
          Input('y-axis-dropdown', 'value')]
 )

def update_input(x_var, y_var):
    return x_var, y_var

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('position_checklist', 'value'),
     Input('90s_input', 'value'),
     Input('colour_option', 'value'),
     Input('league_filter', 'value'),
     Input('player-highlight', 'value'),
     Input('x-input', 'value'),
     Input('y-input', 'value'),
     Input('title-input', 'value'),
     Input('legend-input', 'value'),
     ])

def update_scatter_plot(x_axis_variable, y_axis_variable, selected_positions, ninties_threshold, colour_option, league_filter, player_highlight, x_lab, y_lab, title, legend):
    if not ninties_threshold or not re.match("^[0-9]*$", ninties_threshold):
        return dash.no_update  

    plt = df[df['position'].apply(lambda x: any(option in x for option in selected_positions))]
    plt = plt[plt['comp_level'].apply(lambda x: any(option in x for option in league_filter))]
    plt = plt[plt['minutes_90s'] > float(ninties_threshold)]

    if player_highlight:
        highlighted_players = plt[plt['player'].isin(player_highlight)]
        plt['opacity'] = 0.15
    else:
        plt['opacity'] = 1

    fig = px.scatter(plt, x=x_axis_variable, y=y_axis_variable, opacity=plt['opacity'], color=plt[colour_option],
                     hover_data=['player', 'nationality', 'team', 'minutes_90s'], template='plotly_dark')
    
    fig.update_layout(
        xaxis_title = x_lab,
        yaxis_title = y_lab,
        legend_title = legend,
        title_text = title
    )

    fig.add_annotation(
        dict(
            text="From football viz dashboard<br>via @TCD",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=1,
            y=-0.1,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=8, color='grey')
        )
    )

    if player_highlight:
        player_trace = go.Scatter(
            x=highlighted_players[x_axis_variable],
            y=highlighted_players[y_axis_variable],
            mode='markers',
            text=highlighted_players[['player', x_axis_variable, y_axis_variable, 'nationality', 'team', 'minutes_90s']].astype(str).agg('<br>'.join, axis=1),
            hoverinfo='text',
            name='Highlighted Players',
            marker=dict(size=9)  # Set the size of the markers
        )

        for _, row in highlighted_players.iterrows():
            annotation = dict(
                x=row[x_axis_variable],
                y=row[y_axis_variable],  # Adjust the y-coordinate for the annotation
                text=row['player']
            )
            fig.add_annotation(annotation)

        fig.add_trace(player_trace)

        

    return fig

if __name__ == '__main__':
    app.run(debug=True)   