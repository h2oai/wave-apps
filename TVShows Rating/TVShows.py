from h2o_wave import Q, main, site, app, ui, data
import pandas as pd


def load_data():
    data =  pd.read_csv('tv_shows.csv')
    return data

df = load_data()

page = site['/TVshows']

card = page.add('header',ui.header_card(
    box='4 1 5 2 ',
    title= "  TV Shows On Netflix Data Visualtsation",
    subtitle ='by Ujjwal Mahar',
    icon = 'TVMonitor',
))

#bar plot
df_bar = df.loc[:20,['Title','IMDb','Rotten Tomatoes']]
v = page.add('bar_plot',ui.plot_card(
    box = '5 4 4 4',
    title='Bar Plot',
    data= data(fields=df_bar.columns.tolist(),rows = df_bar.values.tolist() ),
    plot=ui.plot(marks=[ui.mark(type='interval',x='=Title',y='=IMDb',color='=Rotten Tomatoes',dodge='auto')])
))

page.save()