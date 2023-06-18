import json
import pandas as pd
from pandas.io.json import json_normalize
import requests
from tabulate import tabulate
from sklearn.cluster import KMeans
import random
import numpy as np
import pandas as pd
import folium
from sklearn.cluster import DBSCAN


# Fetching data form HERE API for IIT-Bombay
url = 'https://discover.search.hereapi.com/v1/discover?in=circle:19.1334,72.9133;r=10000&q=apartment&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'
data = requests.get(url).json()
d = json_normalize(data['items'])
d.to_csv('api-data/apartment.csv')


# Cleaning API data
d2 = d[['title', 'address.label', 'distance', 'access', 'position.lat',
        'position.lng', 'address.postalCode', 'contacts', 'id']]
d2.to_csv('api-data/cleaned_apartment.csv')


# Counting no. of cafes, department stores and gyms near apartments around IIT Bombay
df_final = d2[['position.lat', 'position.lng']]

CafeList = []
StoList = []
GymList = []
latitudes = list(d2['position.lat'])
longitudes = list(d2['position.lng'])
for lat, lng in zip(latitudes, longitudes):
    radius = '500'  # Set the radius to 500 metres
    latitude = lat
    longitude = lng

    search_query = 'cafe'  # Search for any cafes
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        latitude, longitude, radius, search_query)
    results = requests.get(url).json()
    venues = json_normalize(results['items'])
    CafeList.append(venues['title'].count())

    search_query = 'gym'  # Search for any gyms
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        latitude, longitude, radius, search_query)
    results = requests.get(url).json()
    venues = json_normalize(results['items'])
    GymList.append(venues['title'].count())

    search_query = 'general+stores'  # search for supermarkets
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        latitude, longitude, radius, search_query)
    results = requests.get(url).json()
    venues = json_normalize(results['items'])
    StoList.append(venues['title'].count())

df_final['Cafes'] = CafeList
df_final['Stores'] = StoList
df_final['Gyms'] = GymList

print(tabulate(df_final, headers='keys', tablefmt='github'))

model = DBSCAN(eps=5, min_samples=4).fit(df_final)
print(model.labels_)
df_final['Cluster_dbscan'] = model.labels_
df_final['Cluster_dbscan'] = df_final['Cluster_dbscan'].apply(str)

# # Run K-means clustering on dataframe
kclusters = 3
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_final)
# y_cluster = kmeans.predict(X_pca)
# print(kmeans.labels_)
df_final['Cluster'] = kmeans.labels_
df_final['Cluster'] = df_final['Cluster'].apply(str)


print(tabulate(df_final, headers='keys', tablefmt='github'))

# Plotting clustered locations on map using Folium

# define coordinates of the college
map_bom = folium.Map(location=[19.1334, 72.9133], zoom_start=12)

# instantiate a feature group for the incidents in the dataframe
locations = folium.map.FeatureGroup()

# set color scheme for the clusters

# 0 --> best , -1 --> worst , 1 --> orange.


def color_producer(cluster):
    if cluster == '0':
        return 'blue'
    elif cluster == '-1':
        return 'black'
    else:
        return 'orange'


latitudes = list(df_final['position.lat'])
longitudes = list(df_final['position.lng'])
labels = list(df_final['Cluster_dbscan'])
names = list(d2['title'])
for lat, lng, label, names in zip(latitudes, longitudes, labels, names):
    folium.CircleMarker(
        [lat, lng],
        fill=True,
        fill_opacity=0.4,
        popup=folium.Popup(names, max_width=300),
        radius=25,
        color=color_producer(label)
    ).add_to(map_bom)

# add locations to map
map_bom.add_child(locations)
folium.Marker([19.1334, 72.9133], popup='IIT Bombay').add_to(map_bom)

# saving the map
map_bom.save("map-IITBombay.html")

print(kmeans.labels_)
print(metrics.accuracy_score(y, y_cluster))