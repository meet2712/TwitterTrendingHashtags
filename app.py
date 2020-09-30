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
import dash_table

import threading 

dn = pd.read_csv('C:\\Users\\Nirmal\\Desktop\\BDAD Project\\TwitterTrendingHashtags-master\\my.csv')

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]


external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js',
               'https://pythonprogramming.net/static/socialsentiment/googleanalytics.js']


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
              children = [html.H2('Twitter Analytics Dashboard',className="card-panel teal lighten-3",
                                  style={'color':"Black"}),
                          html.H5('Search:',
                                  style={'color':"#ffffff"}),

                          html.Div(dcc.Input(id='term',
                                    value='twitter',
                                    type='text',
                                    style={'color':"#ffffff"}))],
              style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}),
    
    
     html.Div(className = 'row',
              children = [html.Div(dcc.Graph(id = 'live-graph',animate = False),style={'margin-left': '10px', 'width': '40%'},
                                 className='col s12 m6 l3'),
                          html.Div(dcc.Graph(id = 'live-pie', animate = False),style={'margin-left': '20px', 'width': '30%'},
                                 className='col s12 m6 l3'),
                          html.Div(className='col s12 m6 l3',
                                   children=[
                                    html.H5('Trending HashTag',className="blue-text text-darken-2"),

                                    html.Div(className="striped",
                                             children=[
                                        dash_table.DataTable(id='table1',
                                        data=dn.to_dict('records'),
                                        columns=[{"name": i, "id": i} for i in dn.columns],
                                        style_cell_conditional=[{'if': {'column_id': 'Trendung HashTag'},'width': '300px',
                                                                 'height':'30px'}],

                                        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                                        style_cell={
                                                'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white',
                                                'textAlign': 'left'}
                                        )])


                                             ]),]),

     html.Div(id = 'table'),
     dcc.Interval(id = 'graph',interval=1000,n_intervals = 0)
    ] ,style={'backgroundColor': "#000000", 'margin-top':'-30px', 'height':'2000px',},
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


if __name__ == "__main__":
    app.run_server(debug=True, port=4000)
