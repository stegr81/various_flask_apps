import requests, json
from datetime import datetime
import folium

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
