"""
Application for entering pricing data and displaying basic analytics
"""
# Built-ins
import datetime
# 3rd-party
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State
# Internal
from cpi import Observation


app = Dash(__name__)


app.layout = html.Div([
    html.Div(children=[
        html.H1('Price Observation Data Entry'),
        html.Br(),

        html.Label('Date'),
        dcc.DatePickerSingle(date=datetime.date.today(), id='date-input'),
        html.Br(),

        html.Label('Category'),
        dcc.Dropdown(options=Observation.available_categories(), value='Food', id='category-input'),
        html.Br(),

        html.Label('Item'),
        dcc.Dropdown(options=Observation.available_items(),
                     value='USDA Grade-A eggs', id='item-input'),
        html.Br(),

        html.Label('Price'),
        dcc.Input(id='price-input'),
        html.Br(),

        html.Label('State'),
        dcc.Dropdown(options=Observation.available_states(),
                     value='Texas', id='state-input'),
        html.Br(),

        html.Label('City'),
        dcc.Dropdown(options=Observation.available_cities(),
                     value='Dallas', id='city-input'),
        html.Br(),

        html.Button('Save Observation', id='save-button', n_clicks=0),
        html.Br(),
        html.Br(),

        html.Label('Number of Matching Observations to delete'),
        dcc.Input(value=1, id='delete-n-observations'),
        html.Br(),
        html.Label('Delete Most Recent First?'),
        dcc.Checklist(['Yes'], ['Yes'], id='delete-most-recent-toggle'),
        html.Br(),
        html.Button('Delete Matching Observations', id='delete-button'),

    ], style={'padding': 10, 'flex': 1}),
    html.Div(children=[
        html.Label('Graph Type'),
        dcc.Dropdown(options=['Item Prices Over Time', 'Average Item Price by City'],
                     value='Item Prices Over Time', id='graph-type'),
        dcc.Graph(figure=px.scatter(Observation.table_df(), x='Date', y='Price', color='Item'), id='observation-graph'),
        dash_table.DataTable(Observation.table_df().to_dict('records'), id='observation-table')
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
    Output(component_id='observation-table', component_property='data'),
    Output(component_id='observation-graph', component_property='figure'),
    Input(component_id='save-button', component_property='n_clicks'),
    State(component_id='date-input', component_property='date'),
    State(component_id='category-input', component_property='value'),
    State(component_id='item-input', component_property='value'),
    State(component_id='price-input', component_property='value'),
    State(component_id='state-input', component_property='value'),
    State(component_id='city-input', component_property='value')
)
def update_observation(n_clicks: float, date: str, category: str, item: str, price: str,
                       state: str, city: str):
    if n_clicks >= 1:
        obj = Observation(Date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                          Category=category, Item=item, Price=float(price), State=state, City=city)
        obj.write()
    df = Observation.table_df()
    return df.to_dict('records'), px.scatter(df, x='Date', y='Price', color='Item')


if __name__ == '__main__':
    app.run_server(debug=True)  # Runs at localhost:8050 by default
