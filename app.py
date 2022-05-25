# run the following from the command line
# pip install -r requirements.txt
import os

from flask import Flask, render_template, Markup, request

import requests, json
from datetime import datetime
import folium

import pandas, plotly
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px


import station
#import virus

#resp = requests.get('https://pomber.github.io/covid19/timeseries.json').json()
#resp['United States'] = resp.pop('US')


iss=station.iss()
#covid=virus.covid()

app=Flask(__name__,static_url_path='/static')
@app.route('/iss')
def station():
	now = datetime.now()
	now = str(now.strftime('%Y-%m-%d %H:%M'))
	map, pass_data = iss.query()
	return render_template('iss.html',**pass_data, now=now, map=map)

@app.route('/')
def index():
	return render_template('index.html')
	
#The Covid analysis elements of this Flask have been removed due to the loss of the data source

@app.route('/covid')
def covtracker(div_placeholder = None):
	options = ['Zero Day Scatter', 'Choropleth', 'Daily Cases', 'Deaths per Million Population', 'Choropleth']
	return render_template('covid.html', options = options, div_placeholder=div_placeholder)


@app.route('/covid', methods = ['POST'])
def choices():
	#countryList = request.form['list'].split(',')
	countryList = [x.lstrip().rstrip().title() for x in request.form['list'].split(',')]
	choice = request.form['options']
	
	if choice == "Zero Day Scatter":
		dfZeroDay = covid.zero_day_init(resp, countryList)
		data = covid.zero_scatter(dfZeroDay, countryList)
		data = plot(data,output_type = 'div')
		div_placeholder=Markup(data)
		
	if choice == "Daily Cases":
		data = covid.daily_cases_bar(resp,countryList)
		data = plot(data,output_type = 'div')
		div_placeholder=Markup(data)
	
	if choice == "Deaths per Million Population":
		data = covid.wiki_pop(resp, countryList)
		data = plot(data,output_type = 'div')
		div_placeholder=Markup(data)
	
	if choice == "Choropleth":
		data = covid.total_choropleth(resp)
		data = plot(data, output_type = 'div')
		div_placeholder=Markup(data)
	
	return covtracker(div_placeholder)
	
if __name__ == '__main__':
	app.run(debug=True,port=80,host='0.0.0.0')
