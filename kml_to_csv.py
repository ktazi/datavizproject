from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json

with open("configure.json") as conf:
    data2 = json.load(conf)

with open(data2['maps_kml'], 'r') as f:
    data = f.read()
Bs_data = BeautifulSoup(data, "xml")

dates = np.array(Bs_data.find_all('when'))

a = np.vectorize(lambda x : int(x[:4]))
years = a(dates)
a = np.vectorize(lambda x : int(x[5:7]))
months = a(dates)
a = np.vectorize(lambda x : int(x[8:10]))
day = a(dates)
a = np.vectorize(lambda x : int(x[11:13]))
hour = a(dates)
a = np.vectorize(lambda x : int(x[14:16]))
minute = a(dates)
a = np.vectorize(lambda x : int(x[17:19]))
sec = a(dates)
df = pd.DataFrame(years, columns=["yr"])
df["mn"]=months
df["dy"]=day
df["hr"]=hour
df["mi"]=minute
df["sc"]=sec

coord = np.array(Bs_data.find_all('gx:coord'))
a = np.vectorize(lambda x : float(x.split(" ")[0]))
df["lon"] = a(coord)
a = np.vectorize(lambda x : float(x.split(" ")[1]))
df["lat"] = a(coord)
a = np.vectorize(lambda x : float(x.split(" ")[2]))
df["haut"] = a(coord)


from math import cos,sqrt, asin, pi
def harv(la1,lo1,la2,lo2):
    earth_radius = 6378
    p = pi/180
    a = 0.5 - cos((la2-la1)*p)/2 + cos(la1*p)*cos(la2*p) * (1-cos((lo2-lo1)*p)) / 2
    return 2*earth_radius*asin(sqrt(a))

distances = [0]
for i in range(0, len(df)-1) :
    distances.append(harv(df["lat"][i],df["lon"][i], df["lat"][i+1],df["lon"][i+1]))
df["dist"] = distances
df.to_csv(data2['maps'], index=False)