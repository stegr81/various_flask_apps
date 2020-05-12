import os
#sudo pip install plotly===4.6.0
# ! pip install plotly-geo
#os._exit(00)

from flask import Flask, render_template, Markup, request
import requests, pandas, plotly, json
from datetime import datetime
import folium
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px

resp = requests.get('https://pomber.github.io/covid19/timeseries.json').json()
resp['United States'] = resp.pop('US')

class covid():

    def wiki_pop(self, resp, countryList):
        url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
        response = requests.get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')#view this variable to inspect the structure of the HTML
        countries = html_soup.find_all('table', class_ = "wikitable sortable")#pull out an instance of table with unique WS
#table could be DIV with a unique div class in place of wikitable sortable. This is found by inspecting the HTML
        popDF = pandas.read_html(str(countries))[0]#read countries into a string and read into pandas
        popDF.rename(columns={1:'Country',2:'Population'}, inplace = True)
        #popDF.drop(columns=[0,3,4,5], inplace = True)
        try:
            popDF.drop(index=0, inplace = True)
        except:
            pass
    
        #remove [] notation from wiki data
        popDF['Country'] = popDF['Country'].map(lambda x: x.split('[')[0])

        #extract each country from covid data along with number of deaths per country
        countryDict = {}
        for country in resp:
            deaths = resp[country][-1]['deaths']
            countryDict[country]=deaths
    
        FinalDF = pandas.DataFrame.from_dict(countryDict, orient='index')
        FinalDF.reset_index(inplace=True)
        FinalDF.rename(columns={'index':'Country',0:'Deaths'}, inplace=True)

        popDF = pandas.merge(FinalDF, popDF, how='outer', on='Country')
        
        popDF.fillna(1, inplace=True)
        
        #popDF['Deaths per 1M Population'] = ''
        x=0
        while x < len(popDF):
            deaths = popDF.at[x,'Deaths']
            popDF.at[x,'Deaths_1M_Population']=float(deaths/(int(popDF.at[x,'Population'])/1000000))
            x+=1
        
        fig = go.Figure()
        for country in countryList:
            idx = popDF.index[popDF['Country'] == country]
            fig.add_trace(go.Bar(x=[popDF.at[idx[0],'Country']],
                                 y=[popDF.at[idx[0],'Deaths_1M_Population']],
                                 name=country))
        fig.update_layout(
            title='Deaths per Million Population by Country',
            xaxis_title='Country',
            xaxis_tickfont_size=14,
            yaxis=dict(
                title='Deaths/1M Pop',
                titlefont_size=16,
                tickfont_size=14,
            ),
        )
        
        return(fig)
        
    def init_df(self, data, country):
        df = pandas.DataFrame(data.get(country.title()))
        df.drop(columns='recovered', inplace=True)
        df.rename(columns={'confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
        df = df[['date', country+'_Confirmed', country+'_Deaths']]
        finalDF = df
        return finalDF
    
    def add_to_df(self, data, country, FinalDF):
        df = pandas.DataFrame(data.get(country))
        df.drop(columns='recovered', inplace=True)
        df.rename(columns={'confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
        df = df[['date', country+'_Confirmed', country+'_Deaths']]
        finalDF = pandas.merge(FinalDF, df, how = 'inner', on = 'date')
        return finalDF
    
    def zero_day_init(self, data, countryList):
        for country in countryList:
            if country in countryList[0]:
                df = pandas.DataFrame(data.get(country))
                try:
                    df.drop(columns='recovered', inplace=True)
                except:
                    pass
                df.rename(columns={'date':country+'_Date','confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
                df = df[[country+'_Date', country+'_Confirmed', country+'_Deaths']]
                dayZero = df[df[country+'_Confirmed'].gt(0)].index[0]
                x=0
                while x<dayZero:
                    df.drop([df.index[0]], inplace=True)
                    x+=1
                df.reset_index(inplace=True, drop=True)
                df.reset_index(inplace=True)
                df.rename(columns={'index':'DayZero'}, inplace=True)
                dfZeroDay = df
            else:
                subdf = pandas.DataFrame(data.get(country))
                try:
                    subdf.drop(columns='recovered', inplace=True)
                except:
                    pass
                subdf.rename(columns={'date':country+'_Date','confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
                subdf = subdf[[country+'_Date', country+'_Confirmed', country+'_Deaths']]
                dayZero = subdf[subdf[country+'_Confirmed'].gt(0)].index[0]
                x=0
                while x<dayZero:
                    subdf.drop([subdf.index[0]], inplace=True)
                    x+=1
                subdf.reset_index(inplace=True, drop=True)
                subdf.reset_index(inplace=True)
                subdf.rename(columns={'index':'DayZero'}, inplace=True)
                dfZeroDay = pandas.merge(dfZeroDay, subdf, how = 'outer', on = 'DayZero')
        return dfZeroDay
    

    def zero_scatter(self, dfZeroDay, countryList):
        countriesPlotData = []
        for country in countryList:
            coly = country+'_Confirmed'
            country = go.Scatter(x = dfZeroDay.DayZero,
                                y = dfZeroDay[coly],
                                name = country)
            data = [country]
            countriesPlotData.append(country)
        #fig = iplot(data)
        #data = [countriesPlotData]
        return(countriesPlotData)
    
    def total_choropleth(self, resp):
        countryDict = {}
        countries = requests.get('https://raw.github.com/stegrieve/gps-folium-test/master/custom.geo.json').json()
        for country in resp:
            deaths = resp[country][-1]['deaths']
            countryDict[country]= deaths
        
        #the name of the column in the data has to match the name the feature you use in the geo_json    
        totalDF = pandas.DataFrame.from_dict(countryDict, orient='index')
        totalDF.reset_index(drop=False, inplace = True)
        totalDF.rename(columns={0:'Deaths', 'index':'name'}, inplace=True)
    
        fig  = px.choropleth(totalDF, geojson=countries, locations='name', featureidkey='properties.name',color='Deaths',
                               color_continuous_scale="Viridis",
                               scope="world",
                               labels={'Deaths':'Number of Deaths'}
                              )
        return(fig)
    
    def daily_cases_bar(self, data, countryList):
        
        for country in countryList:
            if country in countryList[0]:
                df = pandas.DataFrame(data.get(country))
                df.rename(columns={'recovered':country+'_recovered','confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
                df[country+'_Daily_Cases']=''
                x=1
                y=0
                while x < len(df):
                    df.at[x, country+'_Daily_Cases'] = df.at[x, country+'_Confirmed'] - df.at[y, country+'_Confirmed']
                    x+=1
                    y+=1
                #df = df[[country+'_Date', country+'_Confirmed', country+'_Deaths']]
                #dayZero = df[df[country+'_Confirmed'].gt(0)].index[0]
            else:
                subdf = pandas.DataFrame(data.get(country))
                subdf.rename(columns={'recovered':country+'_recovered','confirmed':country+'_Confirmed', 'deaths':country+'_Deaths'}, inplace=True)
                subdf[country+'_Daily_Cases']=''
                x=1
                y=0
                while x < len(subdf):
                    subdf.at[x, country+'_Daily_Cases'] = subdf.at[x, country+'_Confirmed'] - subdf.at[y, country+'_Confirmed']
                    x+=1
                    y+=1
                df = pandas.merge(df, subdf, how = 'outer', on = 'date')
        #fig = px.bar(df, x = 'date', y='Daily Cases')
        dailyDF = df
        
        fig = go.Figure()
        for country in countryList:
            fig.add_trace(go.Bar(x=df.date,
                    y=df[country+'_Daily_Cases'],
                    name=country))
        return(fig)

class iss():
	def user_location(self):
		userLocation = requests.get('http://ip-api.com/json/?fields = status,lat,reverse,ip').json()
		userLat = userLocation.get('lat')
		userLon = userLocation.get('lon')
		return userLat,userLon

	def iss_location(self):
		issLocation = requests.get('http://api.open-notify.org/iss-now.json').json()
		issLat = issLocation.get('iss_position').get('latitude')
		issLon = issLocation.get('iss_position').get('longitude')
		return str(issLat),str(issLon)

	def iss_pass(self,userLat,userLon):
		params =f'?lat={userLat}&lon={userLon}'
		issPasses = requests.get('http://api.Open-Notify.org/iss-pass.json'+params).json().get('response')
		passes = [datetime.fromtimestamp(x.get('risetime')).strftime('%A %d-%m-%Y  at %H:%M:%S') for x in issPasses]
		passes = 'The ISS will transit your location at the following times: ' + ', '.join(passes)
		return passes

	def map_maker(self, issLat, issLon, userLat, userLon):
		map = folium.Map(location=[15, 0],zoom_start=1.5)
		folium.Marker([issLat,issLon], icon=folium.Icon(icon='cloud')).add_to(map)
		folium.Marker([userLat,userLon]).add_to(map)
		return map._repr_html_()

	def weather(self, userLat, userLon):
		weatherparams = f'weather?lat={userLat}&lon={userLon}&appid=d328775d7b9b02737e5b7ce8eeead070'
		query = requests.get('http://api.openweathermap.org/data/2.5/'+weatherparams).json()
		description = query.get('weather')[0].get('description')
		temp = round(query.get('main').get('temp')-273.15,1)
		return description, temp

	def query(self):
		userLat,userLon = self.user_location()
		issLat, issLon = self.iss_location()
		passes = self.iss_pass(userLat,userLon)
		description, temp = self.weather(userLat, userLon)
		map = self.map_maker(issLat,issLon, userLat, userLon)
		pass_data={
			'userLat':userLat,
			'userLon':userLon,
 			'issLat':issLat,
 			'issLon':issLon,
 			'passes':passes,
			'description':description,
			'temp':temp
 			}
		return map,pass_data
        	#print(issLat,issLon,passes,userLat,userLon)
        	#display(map._repr_html_())
	
iss=iss()
covid=covid()
app=Flask(__name__,static_url_path='/static')
@app.route('/iss')
def station():
	now = datetime.now()
	now = str(now.strftime('%Y-%m-%d %H:%M'))
	map, pass_data = iss.query()
	return render_template('iss.html',**pass_data, now=now, map=map)

@app.route('/index')
def index():
	return render_template('index.html')
	
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
