import dash
from dash import dcc
from dash import html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from pandas.io.formats import style
#from pandas_datareader import data as pdr
import plotly.graph_objs as go
import plotly.express as px
from plotly.graph_objects import layout
# model
from model import prediction
from sklearn.svm import SVR
from plotly.validator_cache import ValidatorCache
app = dash.Dash()

def get_stock_price_fig(df):

    fig = px.line(df,x="Date",y=["Close", "Open"],title="Closing and Openning Price vs Date",markers=True)
    fig.update_layout(title_x=0.5)
    return fig

def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,x="Date",y="EWA_20",title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

# html layout of site
app.layout=html.Div([  
    html.Div([
        html.Div([
            html.H1(children="Welcome to the stock dash app")
        ],
        className='start',
        style={'padding-top':'1%'}
        ),
        html.Div([
            dcc.Input(id='input',type='text',style={'align':'center'}),
            html.Button('Submit',id='submit-name',n_clicks=0),
        ]),
        html.Div(
            #date range picker input
            ['Select a date range: ',
             dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=dt(1985,8,5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt.now(),
                            end_date=dt.now().date(),
                            style={'font-size':'18px','display':'inline-block','align':'center','border-radius':'2px','border':'1px #ccc','color':'#333'}
                        ),
            html.Div(id='output-container-date-picker-range',children='You have selected a date')        
            ]),
        html.Div([
            html.Button('Stock Price',id='submit-val',n_clicks=0,style={'float':'left','padding':'15px 32px','background-color':'red','display':'inline'}),
            html.Div(id='container-button-basic'),
            #Indicators button
            html.Button('Indicator',id='submit-ind',n_clicks=0),

            #number of days of forecast input
            html.Div([dcc.Input(id='Forecast_Input',type='text')]),
            html.Button('No of days to forecast',id='submit-forc',n_clicks=0),
            html.Div(id='forecast')
            #forecast button
        ])
    ],className='nav'),
    html.Div(
        [
            html.Div(
                [   html.Img(id='logo'),
                   html.H1(id='name')
                    #Company name
                ],
                className="header"),
            html.Div(#Description
                id="description",className="description_ticker"),
            html.Div([],
                     id="graphs-content"),
            html.Div([
                #indicator plot
            ],id="main-content"),
            html.Div([],id="forecast-content")],
            className="content")],
            className="container")

# callback for company info
@app.callback([
    Output('description', 'children'),
    Output('logo', 'src'),
    Output('name', 'children'),
    Output('submit-val', 'n_clicks'),
    Output('submit-ind', 'n_clicks'),
    Output('submit-forc', 'n_clicks'),
    Input('submit-name','n_clicks'),
    State('input','value')])

def update_data(n, val):
    if n == None:
        return "Hey there! Please enter a legitimate stock code to get details",None,"Stocks",None,None,None
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df = df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0], None, None, None

# callback for stocks graphs
@app.callback([
    Output('graphs-content', 'children'),
    Input('submit-val', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    State('input', 'value')])

def update_graph(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback([Output('main-content', 'children')], [
    Input('submit-ind', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State('input', 'value')])

def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback([
    Output("forecast-content", "children"),
    Input("submit-forc", "n_clicks"),
    State("Forecast_Input", "value"),
    State("input", "value")])

def forecast(n, n_days, val):
    if n == None:
        return [""]  # Return an empty list as the default value
    if val == None:
        raise PreventUpdate
    x=int(n_days)
    fig = prediction(val, x + 1)
    return [[dcc.Graph(figure=fig)]]  # Wrap the Graph component in a list



if __name__ == '__main__':
    app.run_server(debug=True)