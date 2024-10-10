"""
Application for entering pricing data and displaying basic analytics
"""
# Built-ins
import datetime
# 3rd-party
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State
from dash import callback_context, no_update
import pandas as pd
import dash_bootstrap_components as dbc
# Internal
from cpi import Observation

# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
app = Dash(__name__, external_stylesheets=[dbc.themes.YETI, dbc.icons.BOOTSTRAP]) 

def create_row(label, component, label_width=3, component_width=9):
    return dbc.Row([
        dbc.Col(dbc.Label(label), width=label_width),  # left column for label name
        dbc.Col(component, width=component_width)      # right column for Input/drop down 
    ], className="mb-3")  # Add some bottom margin for spacing

# Layout using Bootstrap's grid system (Container, Row, Col)
# https://dash-bootstrap-components.opensource.faculty.ai/docs/
# Layout with dcc.Loading wrapper

dbc_Container = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Price Observation Data Entry", className="text-center text-primary")),
                dbc.CardBody([
                    # Observation input section
                    create_row("Date", dcc.DatePickerSingle(date=datetime.date.today(), id='date-input')),
                    create_row("Category", dcc.Dropdown(options=Observation.available_categories(), value='Food', id='category-input')),
                    create_row("Item", dcc.Dropdown(id='item-input')),
                    
                    # Price input with popover for information
                    dbc.Row([
                        dbc.Col(dbc.Label("Price"), width=3),
                        dbc.Col(dcc.Input(id='price-input'), width=6),
                        # dbc.Col(html.Span("!", id="popover-target", style={'color': 'red', 'cursor': 'pointer'}), width=1)
                        dbc.Col(html.I(className="bi bi-info-circle-fill", id="popover-target", 
                                       style={'color': 'grey', 'cursor': 'pointer'}), width=1)
                    ], className="mb-3"),
                    
                    # Popover for Price Input explanation
                    dbc.Popover(
                        dbc.PopoverBody("Please enter a valid number within 4 decimal places."),
                        target="popover-target",  # Target the "!" span
                        trigger="hover",  # Popover appears on hover (can also use 'click')
                        placement="right"
                    ),

                    create_row("State", dcc.Dropdown(options=Observation.available_states(), value='Texas', id='state-input')),
                    create_row("City", dcc.Dropdown(id='city-input')),
                    html.Hr(), 
                    
                    # Delete functionality section
                    dbc.Row([
                        dbc.Col(dbc.Label("Number of Matching Records to Delete"), width=9),  # Label Column
                        dbc.Col(dcc.Input(value=1, id='delete-n-observations', style={'width': '100%', 'maxWidth': '150px'}), width=3)         # Input/Component Column
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Col(dbc.Label("Delete Most Recent Record First?"), width=9),  # Label Column
                        dbc.Col(dcc.Checklist(['Yes'], ['Yes'], id='delete-most-recent-toggle'), width=3)          # Input/Component Column
                    ], className="mb-3"),
            
                    # Buttons for save and delete
                    html.Div([
                        dbc.Button('Save Observation', id='save-button', color='primary', className='mr-2'),
                        dbc.Button('Delete Observation', id='delete-button', color='danger')
                    ], className="d-flex justify-content-between mt-3"),
                    
                    # # Error messages
                    # html.Div(id='error-message-save', className="text-danger mt-2"),  
                    # html.Div(id='error-message-delete', className="text-danger mt-2"),

                    # Notification messages (alerts) container
                    html.Hr(), 
                    html.Div(id='notification-container')
                ])
            ], className="shadow mb-4")
        ], width=4, style={'max-height': '800px', 'overflow-y': 'scroll'}),
        # ], width=4, style = {'position': 'sticky', 'top': '10px', 'zIndex': '1'}),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Analytics Dashboard", className="text-center text-success")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            html.Label("Graph Type", style={'textAlign': 'right', 'verticalAlign': 'middle'}),
                            width='auto', 
                            # className="d-flex align-items-center" # Center the text vertically
                        ),
                        dbc.Col(dcc.Dropdown(options=['Item Prices Over Time', 'Average Item Price by City'], 
                                             value='Item Prices Over Time', id='graph-type'), width=5)
                    ]),
                    dcc.Graph(figure={}, id='observation-graph', style={'height': '400px'}),
                    dash_table.DataTable(
                        Observation.table_df().to_dict('records'),
                        id='observation-table',
                        page_size=20,
                        sort_action='native',
                        sort_mode='multi',
                        style_table={'height': '700px', 'overflowY': 'auto', 'maxWidth': '100%'},  
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'font-size': '12px'  # Reduced font size for table data
                        },
                        style_header={
                            'font-size': '14px',  # Reduced font size for header
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold'
                        }
                    ),
                ])
            ], className="shadow mb-4")
        ], width=8, style={'max-height': '800px', 'overflow-y': 'scroll'})
    ])
], fluid=True)  # `fluid=True` makes the container responsive and full-width

app.layout = dbc_Container

# Callback to update Item based on selected Category
@app.callback(
    [Output('item-input', 'options'), Output('item-input', 'value')], 
    Input('category-input', 'value')
)
def set_items_options(selected_category):
    """
    Set the options and default value for the item dropdown based on the selected category.
    """
    if selected_category is None:
        # Return an empty list if no category is selected, avoid try to access None key in the dict -> BUG #1
        return [], None
    items = Observation.category_item_map[selected_category]
    options = [{'label': item, 'value': item} for item in items]
    default_value = items[0] if items else None # Set the default value to the first item if available
    return options, default_value

# Callback to update City based on selected State
@app.callback(
    [Output('city-input', 'options'), Output('city-input', 'value')],
    Input('state-input', 'value')
)
def set_cities_options(selected_state):
    """
    Set the options and default value for the city dropdown based on the selected state.
    """
    if selected_state is None:
        # Return an empty list if no state is selected, avoid try to access None key in the dict -> BUG #1
        return [], None
    cities = Observation.state_city_map[selected_state]
    options = [{'label': city, 'value': city} for city in cities]
    default_value = cities[0] if cities else None   # Set the default value to the first city if available
    
    return options, default_value

# Callback to update graph or add/delete observations
@app.callback(
    Output(component_id='observation-table', component_property='data'),
    Output(component_id='observation-graph', component_property='figure'),
    Output(component_id='notification-container', component_property='children'),
    Input(component_id='save-button', component_property='n_clicks'),
    Input(component_id='delete-button', component_property='n_clicks'),
    Input(component_id='date-input', component_property='date'),
    Input(component_id='graph-type', component_property='value'),
    State(component_id='category-input', component_property='value'),
    State(component_id='item-input', component_property='value'),
    State(component_id='price-input', component_property='value'),
    State(component_id='state-input', component_property='value'),
    State(component_id='city-input', component_property='value'),
    State(component_id='delete-n-observations', component_property='value'),
    State(component_id='delete-most-recent-toggle', component_property='value'),
)
def update_observation_and_graph(save_clicks: float, delete_clicks: float, date: str, graph_type: str,
                    category: str, item: str, price: str, state: str, city: str,
                     n_to_delete: int, delete_most_recent: list):
    """
    Callback function to add/delete observations or update the graph based on trigged component.
    Returns: 
        - Updated table data
        - Updated graph figure
        - Notification message
    """
    ctx = callback_context
    message_add, message_delete = '', ''
    alert = None
    fig = None # fix BUG #1
    # Deal with the save button or delete button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] # component id
    if button_id == 'save-button' and save_clicks >= 1:
        # Through error handling for entered price, only support valid numeric values
        try:
            price_rounded = round(float(price), 4)
        except (ValueError, TypeError):
            alert = dbc.Alert(
                [
                    html.I(className="bi bi-x-octagon-fill me-2"),  # danger icon for error
                    "Invalid price format. Please enter a valid number."
                ],
                color="danger",
                className="d-flex align-items-center"
            )
            return no_update, no_update, alert

        obj = Observation(Date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                          Category=category, Item=item, Price=price_rounded, State=state, City=city)
        flag, message_add = obj.write()
        if flag: # True if success
            alert = dbc.Alert(
                [
                    html.I(className="bi bi-check-circle-fill me-2"),  # Checkmark icon for success
                    message_add
                ],
                color="success",
                className="d-flex align-items-center"
            )
        else: # False if fail
            alert = dbc.Alert(
                [
                    html.I(className="bi bi-x-octagon-fill me-2"),  # danger icon for unknown system error
                    message_add
                ],
                color="danger",
                className="d-flex align-items-center"
            )

    elif button_id == 'delete-button' and delete_clicks >= 1:
        # Error handling for price
        if price:
            try:
                price_rounded = round(float(price), 4)
            except (ValueError, TypeError):
                alert = dbc.Alert(
                    [
                        html.I(className="bi bi-x-octagon-fill me-2"),  # Danger icon for error
                        "Error: Please enter a valid numeric value for Price."
                    ],
                    color="danger",
                    className="d-flex align-items-center"
                )
                return no_update, no_update, alert
        order_to_delete_in = {'AddedOn': False} if delete_most_recent else None  # Addedon Date DESC if chose delete most recent
        num_deleted, message_delete = Observation().delete_matching(
            n_to_delete=int(n_to_delete),
            order_to_delete_in=order_to_delete_in,
            Date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
            Category=category, Item=item, 
            Price=float(price) if price else None,
            State=state, City=city
        )
        if num_deleted: 
            # if num_deleted > 0, then delete successfully -> display success message
            message_delete = f'{num_deleted} {message_delete}.' # e.g. '1 Observation deleted.'
            alert = dbc.Alert(
                [
                    html.I(className="bi bi-check-circle-fill me-2"),  # Checkmark icon for success
                    message_delete
                ],
                color="success",
                className="d-flex align-items-center"
            )
        else:
            # if num_deleted == 0, then delete failed -> display warning message
            alert = dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),  # Warning icon for no matching
                    message_delete
                ],
                color="warning",
                className="d-flex align-items-center"
            )


    df = Observation.table_df() # update the df to display the latest data
    df['Date'] = pd.to_datetime(df['Date']).dt.date # Convert pandas object to datetime, allow comparing to select date

    # Deal with the graphs
    # https://plotly.com/python-api-reference/generated/plotly.express.scatter.html
    # https://plotly.com/python/px-arguments/
    if graph_type == 'Item Prices Over Time':
        # Group by 'Item' and 'Price', count occurrences of each price for each item
        # Normalize the count so that the minimum point size is at least 3 ( 1 & 2 are too small in my screen!)
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
            size_max=15, # px scatter does not allow to set a min_size, this variable becomes optional as I have manullay mapped the count value to [3, 15]
        )
        df.drop('Count', axis=1, inplace=True) # Drop the Count column
        df.drop('Mapped_Count', axis=1, inplace=True) # Drop the Mapped_Count column

    elif graph_type == 'Average Item Price by City':
        selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date() # The date in the Date field
        print('Average Item Price by City, selected_date:', selected_date)
        df_filtered = df[df['Date'] == selected_date]
        avg_df = df_filtered.groupby(['Item', 'City'])['Price'].mean().reset_index()
        fig = px.bar(
            avg_df, 
            x='Item',  # The bars should be grouped together by item type 
            y='Price', 
            color='City', # The color of each bar should correspond to the city -> same city, same color
            barmode='group',
            labels={'Price': 'Average Price'},
            title=f'Average Item Price by City on {selected_date}'
        )

    return df.to_dict('records'), fig, alert

if __name__ == '__main__':
    app.run_server(debug=True)  # Runs at localhost:8050 by default
