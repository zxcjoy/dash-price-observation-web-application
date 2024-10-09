"""
Application for entering pricing data and displaying basic analytics
"""
# Built-ins
import datetime
# 3rd-party
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State
from dash import callback_context, no_update
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
                     value='USDA Grade-A eggs (Dozen)', id='item-input'),
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
        html.Div(id='error-message-save', style={'color': 'red'}),  # Display error messages
        html.Br(),
        html.Br(),

        html.Label('Number of Matching Observations to delete'),
        dcc.Input(value=1, id='delete-n-observations'),
        html.Br(),
        html.Label('Delete Most Recent First?'),
        dcc.Checklist(['Yes'], ['Yes'], id='delete-most-recent-toggle'), # (list of available options in the checklist, initial value of the checklist) -> a list containing the selected options
        html.Br(),
        html.Button('Delete Matching Observations', id='delete-button'),
        html.Div(id='error-message-delete', style={'color': 'red'}),  # Display error messages

    ], style={'padding': 10, 'flex': 1}),
    html.Div(children=[
        html.Label('Graph Type'),
        dcc.Dropdown(options=['Item Prices Over Time', 'Average Item Price by City'],
                     value='Item Prices Over Time', id='graph-type'),
        # dcc.Graph(figure=px.scatter(Observation.table_df(), x='Date', y='Price', color='Item'), id='observation-graph'),
        dcc.Graph(figure={}, id='observation-graph'),
        dash_table.DataTable(Observation.table_df().to_dict('records'), id='observation-table')
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
    Output(component_id='observation-table', component_property='data'),
    Output(component_id='observation-graph', component_property='figure'),
    Output(component_id='error-message-save',component_property='children'),
    Output(component_id='error-message-delete',component_property='children'),
    Input(component_id='save-button', component_property='n_clicks'),
    Input(component_id='delete-button', component_property='n_clicks'),
    Input(component_id='graph-type', component_property='value'),
    State(component_id='date-input', component_property='date'),
    State(component_id='category-input', component_property='value'),
    State(component_id='item-input', component_property='value'),
    State(component_id='price-input', component_property='value'),
    State(component_id='state-input', component_property='value'),
    State(component_id='city-input', component_property='value'),
    State(component_id='delete-n-observations', component_property='value'),
    State(component_id='delete-most-recent-toggle', component_property='value'),
)
def update_observation_and_graph(save_clicks: float, delete_clicks: float, graph_type: str,
                    date: str, category: str, item: str, 
                    price: str, state: str, city: str, n_to_delete: int, delete_most_recent: list):
    ctx = callback_context
    # Deal with the save button or delete button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] # component id
    if button_id == 'save-button' and save_clicks >= 1:
        print('save button clicked')
        # if price is None or price == '':
        #     return no_update, no_update, 'Error: Price cannot be empty.'  # Return error message if price is empty
        
        # Through error handling for entered price, only support valid numeric values
        try:
            price_rounded = round(float(price), 4)
        except (ValueError, TypeError):
            return no_update, no_update, 'Error: Please enter a valid numeric value for Price.', ''

        obj = Observation(Date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                          Category=category, Item=item, Price=price_rounded, State=state, City=city)
        obj.write()
    elif button_id == 'delete-button' and delete_clicks >= 1:
        print('delete button clicked')
        if price:
            try:
                price_rounded = round(float(price), 4)
            except (ValueError, TypeError):
                return no_update, no_update, '', 'Error: Please enter a valid numeric value for Price.'
        order_to_delete_in = {'AddedOn': False} if delete_most_recent else None  # Addedon Date DESC if chose delete most recent
        Observation().delete_matching(
            n_to_delete=int(n_to_delete),
            order_to_delete_in=order_to_delete_in,
            Date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
            Category=category, Item=item, 
            Price=float(price) if price else None,
            State=state, City=city
        )

    df = Observation.table_df() # update the df to display the latest data

    # Deal with the graph
    # https://plotly.com/python-api-reference/generated/plotly.express.scatter.html
    # https://plotly.com/python/px-arguments/
    if graph_type == 'Item Prices Over Time':
        # Group by 'Item' and 'Price', count occurrences of each price for each item
        # Normalize the count so that the miniimum point size is at least 3 ( 1 & 2 are too small in my screen!)
        df['Count'] = df.groupby(['Item', 'Price'])['Price'].transform('count')
        min_size, max_size = 3, 15
        df['Mapped_Count'] = ((df['Count'] - df['Count'].min()) / (df['Count'].max() - df['Count'].min())) * (max_size - min_size) + min_size

        fig = px.scatter(
            df, 
            x='Date',
            y='Price', 
            color='Item',
            size='Mapped_Count',
            hover_name='Item',
            hover_data={'Price': True, 'Date': True,'Item': False,'Mapped_Count': False},
            size_max=15,
        )
        df.drop('Count', axis=1, inplace=True) # Drop the Count column
        df.drop('Mapped_Count', axis=1, inplace=True) # Drop the Mapped_Count column
        
    return df.to_dict('records'), fig, '', ''


if __name__ == '__main__':
    app.run_server(debug=True)  # Runs at localhost:8050 by default
