from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import pandas as pd
import plotly.express as px
import io
import base64
import matplotlib.pyplot as plt
from plotly import io as pio
import plotly.figure_factory as ff


df = pd.read_csv('data/iraste_nxt_cas.csv')
df1 = pd.read_csv('data/iraste_nxt_casdms.csv')
df = pd.concat([df, df1], axis = 0)
df = df.drop_duplicates()
df = df.dropna()
df = df.sample(frac=0.01, random_state=42)




# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)


@on('#intro')
async def page_intro(q: Q):
    q.page['sidebar'].value = '#intro'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Create a heatmap of alert occurrences
    fig = px.density_mapbox(df, lat='Lat', lon='Long', radius=10, zoom=5, mapbox_style='carto-positron',
                        title='Spatial Distribution of Alert Occurrences')

# Update map layout
    fig.update_layout(mapbox_center={'lat': df['Lat'].mean(), 'lon': df['Long'].mean()})
    

    config = {
        'scrollZoom': True,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'spatia1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='1000px', width='1300px')]))
    
@on('#data-frame-analysis')
async def page_df(q: Q):
    q.page['sidebar'].value = '#data-frame-analysis'
    clear_cards(q)
    
    # Add description dictionary
    descriptions = {
        'cas_ldw': "Lane Departure Warning (LDW) - A system that alerts the driver when the vehicle is unintentionally drifting out of its lane without a turn signal.",
        'cas_hmw': "Headway Monitoring and Warning (HMW) - A system that monitors the distance between the driver's vehicle and the vehicle in front and alerts the driver if the distance becomes dangerously short.",
        'hard_brake': "Hard Brake - An event recorded when the driver applies the brakes abruptly and significantly, often indicating an emergency or sudden deceleration.",
        'cas_pcw': "Pedestrian Collision Warning (PCW) - A system that detects pedestrians in the vehicle's path and alerts the driver to avoid collisions.",
        'cas_fcw': "Forward Collision Warning (FCW) - A system that detects vehicles or obstacles in the vehicle's path and alerts the driver to potential collisions.",
        'dms_distracted': "Driver Monitoring System (DMS) - Distracted - An event recorded when the driver is distracted, such as by using a mobile phone or engaging in other activities instead of focusing on driving.",
        'dms_noseatbelt': "Driver Monitoring System (DMS) - No Seatbelt - An event recorded when the driver is not wearing a seatbelt.",
        'dms_smoking': "Driver Monitoring System (DMS) - Smoking - An event recorded when the driver is smoking while driving."
    }
    
    table_rows = []
    df_temp = df.copy()
    df_temp['Date'] = df_temp['Date'].astype(str)  # Convert datetime to string for display
    df_temp['Speed'] = df_temp['Speed'].astype(str)  # Convert speed to string for display
    for index, row in df_temp.iterrows():
        if index == 10000:
            break
        table_rows.append(ui.table_row(
            name=row['Date'],
            cells=[row['Date'], row['Alert'], descriptions.get(row['Alert'], ''), row['Speed']]  # Adjust these indices based on your CSV columns
        ))
        
    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='Date', label='Date', searchable=True, min_width='200'),
            ui.table_column(name='Alert', label='Alert', filterable=True, min_width='200', cell_type=ui.tag_table_cell_type(name='tags', tags=[
                ui.tag(label='RUNNING', color='#D2E3F8'),
                ui.tag(label='DONE', color='$red'),
                ui.tag(label='SUCCESS', color='$mint'),
            ])),
            ui.table_column(name='Description', label='Description', searchable=True, min_width='800'),
            ui.table_column(name='Speed', label='Speed', searchable=True, min_width='200'),
        ],
        events=[''],
        rows=table_rows)]
    ))


@on('table')
async def handle_table_click(q: Q):
    table_rows = []
    for index, row in df.iterrows():
        table_rows.append(ui.table_row(
            name=row['Date'],
            cells=[row['Date'], row['Alert'], row['Speed']]  # Adjust these indices based on your CSV columns
        ))
    print(q.args.table)
    if q.args.table:
        q.client.selected_actor = q.args.table[0]
        q.args['#'] = 'data-frame-analysis'
        await page_df(q)

@on('#alert-frequency-analysis')
async def pageca(q: Q):
    print('Handling page4')

    q.page['sidebar'].value = '#alert-frequency-analysis'
    clear_cards(q)


    # Assuming df is your DataFrame containing the dataset

    # Convert 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Extract day of the week and hour of the day from the 'Date' column
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['HourOfDay'] = df['Date'].dt.hour

    # Alert Frequency Analysis by Day of Week
    fig1 = px.histogram(df, x='DayOfWeek', color='Alert', title='Alert Frequency by Day of Week')
    fig1.update_layout(xaxis={'categoryorder':'total descending'},width = 1300)

    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig1, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'bar1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1300px')]))

    fig3 = px.scatter(df, x='Speed', color='Alert', title='Alert Frequency Comparison Across Different Vehicles')
    fig3.update_layout(xaxis_title='Speed', yaxis_title='Alert Frequency', width = 1300)
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig3, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'bar2', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1300px')]))
   

@on('#speed-analysis')
async def page_ind(q: Q):
    q.page['sidebar'].value = '#speed-analysis'
    clear_cards(q)
    
    # Convert 'Speed' column to float
    df['Speed'] = df['Speed'].astype(float)
    
    # Sort DataFrame by 'Time'
    df_sorted = df.sort_values(by='Time')
    df_sorted['Time'] = pd.to_datetime(df_sorted['Time'], errors='coerce')
    
    # Create a new column for speed category
    def categorize_speed(speed):
        if speed < 60:
            return 'Low'
        elif 60 <= speed < 80:
            return 'Medium'
        else:
            return 'High'
    
    df_sorted['Speed_Category'] = df_sorted['Speed'].apply(categorize_speed)
    
    # Scatter plot of Speed vs. Time with Alert Events
    fig1 = px.scatter(df_sorted, x='Time', y='Speed', color='Alert', title='Speed vs. Time with Alert Events')
    fig1.update_layout(xaxis_title='Time', yaxis_title='Speed')
    
    # Convert plot to HTML
    html1 = pio.to_html(fig1, validate=False, include_plotlyjs='cdn', config={'scrollZoom': False, 'showLink': False, 'displayModeBar': False})
    
    # Add the plot to a card
    add_card(q, 'speed1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html1, height='650px', width='1500px')
    ]))
    
    # Histogram of Speed Distribution
    fig2 = px.histogram(df_sorted, x='Speed', nbins=20, title='Distribution of Speed')
    fig2.update_layout(xaxis_title='Speed', yaxis_title='Frequency')
    
    # Convert plot to HTML
    html2 = pio.to_html(fig2, validate=False, include_plotlyjs='cdn', config={'scrollZoom': False, 'showLink': False, 'displayModeBar': False})
    
    # Add the plot to a card
    add_card(q, 'speed2', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html2, height='650px', width='1500px')
    ]))
    grouped_data = df_sorted.groupby(['Speed_Category', 'Alert']).size().reset_index(name='Count')
    
    # Create grouped bar plot
    fig3 = px.bar(grouped_data, x='Speed_Category', y='Count', color='Alert', barmode='group',
                  title='Alerts Count by Speed Category')
    fig3.update_layout(xaxis_title='Speed Category', yaxis_title='Count')
    
    # Convert plot to HTML
    html3 = pio.to_html(fig3, validate=False, include_plotlyjs='cdn', config={'scrollZoom': False, 'showLink': False, 'displayModeBar': False})
    
    # Add the plot to a card
    add_card(q, 'speed3', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html3, height='650px', width='1500px')
    ]))

    

    

@on('#correlation-analysis')
async def page_temporal(q: Q):
    q.page['sidebar'].value = '#correlation-analysis'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    
    df1 = df.copy()
    
    df1['Alert'] = df1['Alert'].astype('category').cat.codes
    df1['Date'] = pd.to_datetime(df1['Date'])
    df1['DayOfWeek'] = df1['Date'].dt.day_name()
    df1['HourOfDay'] = df1['Date'].dt.hour
    df1['Date'] = df1['Date'].astype('category').cat.codes
    df1['Time'] = pd.to_datetime(df1['Time'], errors='coerce')
    df1['DayOfWeek'] = df1['DayOfWeek'].astype('category').cat.codes
    df1['HourOfDay'] = df1['HourOfDay'].astype('category').cat.codes
    df1.drop(['HourOfDay'], axis=1, inplace=True)

    correlation_matrix = df1.corr()

    # Create a heatmap of the correlation matrix
    fig2 = ff.create_annotated_heatmap(z=correlation_matrix.values,
    x=list(correlation_matrix.columns),
    y=list(correlation_matrix.index),
    colorscale='Viridis')

    # Update plot layout
    fig2.update_layout(title='Correlation Between Alert Occurrence and Road Conditions')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig2, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'corr1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1500px')]))
    


    

    






@on('#driver-behaviour-analysis')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#driver-behaviour-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # Now df_expanded has each industry on a separate row

    # Group the data by alert type and count the occurrences of each alert
    
    df_temp = df.copy()
    alert_counts = df_temp['Alert'].value_counts().reset_index()
    alert_counts.columns = ['Alert', 'Frequency']


    # Create a pie chart of alert frequencies
    fig = px.pie(alert_counts, values='Frequency', names='Alert', title='Distribution of Driver Alerts')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'corr1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1500px')]))

@on('#safety-impact-analysis')
async def page_target_aud(q: Q):
    q.page['sidebar'].value = '#safety-impact-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    


    safety_df = df[(df['Alert'] == 'cas_ldw') | (df['Alert'] == 'cas_hmw') | (df['Alert'] == 'hard_brake') |
               (df['Alert'] == 'cas_pcw') | (df['Alert'] == 'cas_fcw')]

    fig1 = px.scatter(safety_df.groupby('Speed')['Alert'].count().reset_index(), x='Speed', y='Alert',
                    title='Speed vs. Frequency of Safety-Related Alerts', trendline='ols')
    fig1.update_layout(xaxis_title='Speed', yaxis_title='Frequency of Safety Alerts')

    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig1, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'safe1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1500px')]))
    # Box plot comparing speeds during safety-related alert events vs non-alert events
    fig2 = px.box(safety_df, x='Alert', y='Speed', title='Speed Distribution During Safety Alerts')
    fig2.update_layout(xaxis_title='Alert Type', yaxis_title='Speed')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig2, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'safe2', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1500px')]))
    









@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]


@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='300px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', direction=ui.ZoneDirection.ROW,),
                    ui.zone('zone2',direction=ui.ZoneDirection.ROW ),
                    ui.zone('vertical'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
                    ui.zone(name='zone1', direction=ui.ZoneDirection.ROW),
                    ui.zone(name='zone3',direction=ui.ZoneDirection.COLUMN)
                ]),
            ]),
        ])
    ])])
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title = 'Advanced Driver Assistance System', subtitle="",
        value=f'#{q.args["#"]}' if q.args['#'] else '#intro',
        image='', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#intro', label='Spatial Analysis'),
                ui.nav_item(name='#data-frame-analysis', label='Data Frame Analysis'),
                ui.nav_item(name='#alert-frequency-analysis', label='Alert Freuency Analysis'),
                ui.nav_item(name='#speed-analysis', label='Speed Analysis'),
                ui.nav_item(name='#correlation-analysis', label='Correlation Analysis'),
                ui.nav_item(name='#driver-behaviour-analysis', label='Driver Behaviour Analysis'),
                ui.nav_item(name='#safety-impact-analysis',label='Safety Impact Analysis'),
                
            ]),
        ],
    )
    q.page['header'] = ui.header_card(
        box='header', title='', subtitle='',
    )

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page_intro(q)


@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)
    await q.page.save()
