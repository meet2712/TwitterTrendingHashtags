import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import sqlite3
import time
import dash_bootstrap_components as dbc
import logging
import advertools as adv
from dash_table import DataTable
from dash_table.FormatTemplate import Format
from dash.exceptions import PreventUpdate
import threading
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots




external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css",
                "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]


external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js',
               'https://pythonprogramming.net/static/socialsentiment/googleanalytics.js']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s==%(funcName)s==%(message)s')

auth_params = {'app_key': 'y0QVTDJoOeYAYS3tT90AFhrlJ',
               'app_secret': 'OLtjU9A2262Xs1NyIE2WbSQuQr08FyCwfO8VlFlgObktigNumx',
               'oauth_token': '1277480095100231680-FX1yNiMFWVD29CAHCIfGcsNXr5BHRy',
               'oauth_token_secret': 'qT3OxDo571uE1NIoX0FqNyrbBsV3nQIbyhxkgATH4B2nq',}

adv.twitter.set_auth_params(**auth_params)

trend_locs = adv.twitter.get_available_trends()
locations = trend_locs['name'] + ', ' + trend_locs['country']

TABLE_COLS = ['Topic', 'Location', 'Tweet Volume',
              'Local Rank', 'Country', 'Time', 'Place Type']


app = dash.Dash(__name__,external_scripts=external_js,external_stylesheets=external_css)
server = app.server
  
import twitter

class thread(threading.Thread): 
    def __init__(self, thread_name, thread_ID): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 
    def run(self): 
        # print(str(self.thread_name) +"  "+ str(self.thread_ID)); 
        twitter.get_tweets()
  
thread1 = thread("", 1001)   
thread1.start() 

app.layout = html.Div(
    [html.Div(className='container-fluid', 
              children = [html.H2('Twitter Analysis Dashboard',
                                  style={'color':"#CECECE",'margin-top': '30px','font-size': '4rem'}),
                          html.H5('Search Country:',    
                                  style={'color':"#ffffff"}),
                          dcc.Input(id='term',
                                    value='twitter',
                                    type='text',
                                    style={'color':"#ffffff"}),],
              style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}),

    
    html.Div(className = 'row',
        children = [
        html.H5('Time Series Analysis',style={'color':"#CECECE",'margin-left':'44px','font-size': '2.25rem'}),
            html.H5('Sentimental Analysis',style={'color':"#CECECE",'margin-left':'441px','font-size': '2.25rem'})
             ]),
     html.Div(className = 'row',
              children = [html.Div(dcc.Graph(id = 'live-graph',animate = False),className='col s12 m6 l6',style={'top':'-23px'}),
                          html.Div(dcc.Graph(id = 'live-pie', animate = False),className='col s12 m6 l6',style={'top':'-23px'})

                          ]),

     html.Div(id = 'table', style={'margin-top':'30px'}),
     dcc.Interval(id = 'graph',interval=1000,n_intervals = 0),
dbc.Container([dcc.Location(id='url', refresh=False),
                       dbc.Row([
                           dbc.Col(lg=1),
                           dbc.Col([
                               dcc.Dropdown(id='locations',style={'height': '30px', 'width': '1200px','margin-left':'-60px','margin-top':'40px'},
                                            placeholder='Select location(s)',
                                            multi=True,
                                            options=[{'label': loc, 'value': i}
                                                     for i, loc in enumerate(locations)]),
                           ], lg=5),
                           dbc.Col([
                               dbc.Button(id='button', children='Submit',style={'margin-left':'465px','width':'33%','margin-top':'40px'},
                                          n_clicks=0, color='primary', className="mr-1"),
                           ]),
                       ], style={'position': 'relative', 'zIndex': 999}),

                   ] + [html.Br() for i in range(8)],
                   style={'background-color': '#000000', 'font-family': 'Source Sans Pro',
                          'zIndex': 999},
                   fluid=True),
dbc.Row([
                           dbc.Col(lg=1),
                           dbc.Col([
                               dcc.Loading([
                                   dcc.Graph(id='chart',style={'width':'123%','margin-left':'-161px','margin-top':'-187px'},
                                             figure=go.Figure({'layout':
                                                                   {'paper_bgcolor': '#000000',
                                                                    'plot_bgcolor': '#000000',
                                                                    'template': 'none'}},
                                                              {'config': {'displayModeBar': False}}),
                                             config={'displayModeBar': False})
                               ])
                           ], lg=10)
                       ]),
                       dbc.Row([
                           html.Br(),
                           dbc.Col(lg=1),
                           dbc.Col([
                               DataTable(id='table1',
                                         style_header={'textAlign': 'center'},
                                         style_cell={'font-family': 'Source Sans Pro',
                                                     'minWidth': 100,
                                                     'textAlign': 'left'
                                                     },
                                         style_cell_conditional=[
                                             {'if': {'column_id': 'Tweet Volume'},
                                              'textAlign': 'right'},
                                             {'if': {'column_id': 'Local Rank'},
                                              'textAlign': 'right'},
                                             {'if': {'column_id': 'Topic'},
                                              'textAlign': 'center'}
                                         ],
                                         columns=[{'name': i, 'id': i,
                                                   'type': 'numeric' if i == 'Tweet Volume' else None,
                                                   'format': Format(group=',')
                                                   if i == 'Tweet Volume' else None}
                                                  for i in TABLE_COLS],
                                         sort_action='native',
                                         export_headers='names',
                                         export_format='csv',
                                         page_action='none',
                                         style_table={'overflowX': 'scroll'},
                                         fixed_rows={'headers': True, 'data': 0},
                                         data=pd.DataFrame({
                                             k: ['' for i in range(10)] for k in TABLE_COLS
                                         }).to_dict('rows'))
                           ], lg=10),
                       ], style={'font-family': 'Source Sans Pro','width':'122%','margin-left':'-165px'}),
    ] ,style={'backgroundColor': "#000000", 'margin-top':'-30px', 'height':'2000px'},
)

old_term = ' '
@app.callback([Output(component_id='live-graph',component_property='figure'),
               Output(component_id='live-pie',component_property='figure'),
               Output(component_id='table',component_property='children')],
              [Input('term','value'),
               Input('graph','n_intervals')])
def update_graph(term,n):
    global old_term
    if term == '' : 
        term = old_term
    old_term = term
    conn = sqlite3.connect('twitter.db')
    # manage_data(conn)
    df = pd.read_sql("select * from sentiment where tweet like '%"+term+"%' order by unix desc limit 1000",conn)
        
    df['unix'] = pd.to_datetime(df['unix'],unit='ms')
    df.sort_values('unix',inplace=True)
    df.set_index('unix',inplace=True)
    df = df.iloc[-100:,:]
    tableData = df.iloc[-10:,:]
    
    positive = 0
    negative = 0
    neutral = 0
    for senti in df['sentiment']:
        if senti > 0:
            positive += 1
        if senti < 0:
            negative += 1
        else:
            neutral += 1
    
    df['smoothe_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
    
    df = df.resample('2s').mean()
    df.dropna(inplace=True)
            
    X = df.index
    Y = df.smoothe_sentiment.values
    
    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name = 'Scatter',
        mode = 'lines+markers'
    )
    
    layout = go.Layout(xaxis = dict(range=[min(X),max(X)]),
                       yaxis = dict(range=[min(Y),max(Y)]),
                       margin=dict(l=40,r=20,b=20,t=60,pad=0),
                       template = 'plotly_dark',
                       hovermode='x')
    
    
    pie = go.Pie(values=[positive,negative,neutral],
                 labels= ['Positive','Negative','Neutral'],
                 text=['Positive','Negative','Neutral'],
                 marker={'colors' :['green','red','blue']},
                 hole = 0.4)
    
    print(tableData.columns)
    return [{'data':[data],'layout':layout},
            {'data':[pie],'layout':layout},
            html.Table(className="responsive-table",
                       children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in tableData.columns.values],
                                  style={'color':app_colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':app_colors['text'],
                                                'background-color':quick_color(d[1])}
                                  )
                               for d in tableData.values.tolist()])
                          ]
    )]
    
    
def quick_color(s):
    # except return bg as app_colors['background']
    if s >= 0.1:
        # positive
        return "#002C0D"
    elif s <= -0.1:
        # negative:
        return "#270000"

    else:
        return app_colors['background']
    
app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}


def manage_data(conn):
    df = pd.read_sql("select * from sentiment",conn)
    # if len(df) > 100000:
    print(len(df))

@app.callback([Output('table1', 'data'),
               Output('url', 'search'),
               Output('chart', 'figure')],
              [Input('button', 'n_clicks')],
              [State('locations', 'value')])

def set_table_data(n_clicks, locations):
    if not n_clicks:
        raise PreventUpdate
    log_loc = trend_locs['name'][locations]
    logging.info(msg=list(log_loc))
    try:
        woeid = trend_locs['woeid'][locations]
        df = adv.twitter.get_place_trends(woeid)
        n_countries = df['country'].nunique()
        countries = df['country'].unique()
        fig = make_subplots(rows=n_countries, cols=1,
                            subplot_titles=['Worldwide' if not c else c
                                            for c in countries],
                            specs=[[{'type': 'treemap'}]
                                   for i in range(n_countries)],
                            vertical_spacing=0.05)
        for i, c in enumerate(countries):
            sub_fig_df = df[df['country'] == c]
            sub_fig = px.treemap(sub_fig_df,
                                 path=['country', 'location', 'name'],
                                 values='tweet_volume')
            sub_fig.layout.margin = {'b': 5, 't': 5}
            sub_fig.data[0]['hovertemplate'] = '<b>%{label}</b><br>Tweet volume: %{value}'
            last_line = '' if c == '' else '<br>%{percentRoot} of %{root}'
            sub_fig.data[0]['texttemplate'] = '<b>%{label}</b><br><br>Tweet volume: %{value}<br>%{percentParent} of %{parent}' + last_line
            fig.add_trace(sub_fig.to_dict()['data'][0], row=i+1, col=1)
        fig.layout.height = 400 * n_countries
        fig.layout.template = 'none'
        fig.layout.margin = {'t': 40, 'b': 40}
        fig.layout.paper_bgcolor = '#000000'
        fig.layout.plot_bgcolor = '#000000'

        final_df = df.drop(['promoted_content', 'woeid', 'parentid'], axis=1)
        final_df = final_df.rename(columns={'name': 'Topic'})
        final_df.columns = [x.title() for x in final_df.columns.str.replace('_', ' ')]
        url_search = '?q=' + '+'.join(log_loc)
        return final_df.to_dict('rows'), url_search, fig.to_dict()
    except Exception as e:
        return pd.DataFrame({'Name': ['Too many requests please '
                                      'try again in 15 minutes.']},
                            columns=df.columns).to_dict('rows')


if __name__ == "__main__":
    app.run_server(debug=True)
