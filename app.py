import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import altair as alt
import folium
import branca
from streamlit_folium import folium_static
import json

with open("configure.json") as conf:
    data = json.load(conf)


def load_spotify_data(conf):
    dfs = pd.read_csv(conf['spotify'])
    dfs['day'] = dfs['dat'].apply(day)
    dfs['month'] = dfs['dat'].apply(month)
    dfs['year'] = dfs['dat'].apply(year)
    dfs['dat'] = pd.to_datetime(dfs['dat'])
    return dfs


def load_maps_data(conf):
    df = pd.read_csv(conf['maps'])
    df.rename(columns={'yr': 'year', "mn": "month", "dy": "day"}, inplace=True)
    df.rename(columns={'sc': 'second', "hr": "hour", "mi": "minute"}, inplace=True)
    df["dat"] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
    return df


st.title("Data visualization of spotify and google maps data")
st.sidebar.header("Input : ")
st.sidebar.markdown("Use these to delimiter the time window for the visualisation")
st.sidebar.subheader("From")
date_b = st.sidebar.date_input('day beginning', datetime(2021, 9, 28))
hour_b = st.sidebar.slider('hour beginning', 0, 23, 1)
st.sidebar.subheader("To")
date_e = st.sidebar.date_input('day end', datetime(2021, 10, 2))
hour_e = st.sidebar.slider('hour end', 0, 23, 1)
st.markdown(
    "For this project, my goal was to visualise how I listen to music using my spotify data and my google maps history.")
st.header("How to collect the data ?")
st.subheader("Google maps")
st.markdown(
    "Very simple ! All you have to do is go to the google takeout website and check the google maps history ! Pick kml as file type [link to google takeout](https://takeout.google.com/settings/takeout). Now all you have to do is put the path to the kml file in the section `maps_kml` of the configure.json file and the path to the future csv in the section `maps` run the kml_to_csv.py and you're good to go !")
st.subheader("Spotify")
st.markdown(
    "Not that simple ! Spotify actually don't let the user have access to their entire history, even through the API ! However said API allows us to access the 'recently played' section, which contains the 50 last songs. In order to do this project, I created a bot that gathers this info for myself and puts it in a .csv ! For those who are interested in it, I put it on my github : [spothistbot](https://github.com/ktazi/spothistbot) <br /> Once it is done, put the path of your csv in the section `spotify` of configure.json")
st.header("Let's begin !")


# import the spotify data
def day(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M").day if d.find('.') == -1 else datetime.strptime(d,
                                                                                                  "%Y-%m-%d %H:%M:%S.%f").day


def month(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M").month if d.find('.') == -1 else datetime.strptime(d,
                                                                                                    "%Y-%m-%d %H:%M:%S.%f").month


def year(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M").year if d.find('.') == -1 else datetime.strptime(d,
                                                                                                   "%Y-%m-%d %H:%M:%S.%f").year


dfs = load_spotify_data(data)
dfp = load_maps_data(data)

dfs = dfs[:][dfs['dat'] < datetime(date_e.year, date_e.month, date_e.day, hour_e)]
dfs = dfs[:][dfs['dat'] > datetime(date_b.year, date_b.month, date_b.day, hour_b)]

# Number of musics I listen to in a day

st.markdown("This is a simple plot of how many tracks are listened to per day. Library used : `matplotlib`")

plt.style.use('dark_background')

ax1 = plt.subplot(2, 1, 1)
plt.figure(1)
d = dfs.groupby(by=['year', 'month', 'day'], as_index=False).count()[['track', 'day', 'month', 'year']]
d['dat'] = d.apply(lambda x: datetime(x.year, x.month, x.day), axis=1)
plt.plot_date(d['dat'], d['track'], linestyle='solid', fmt='go--', tz=None, xdate=True, ydate=False, data=None)
plt.tick_params(axis='x', which='major', labelsize=10)
plt.tight_layout()
plt.gcf().autofmt_xdate()
plt.title("Number of tracks listened per day", fontname='Ubuntu', fontsize=20, fontweight='bold')
plt.xlabel("day", fontname='Ubuntu', fontsize=15)
plt.ylabel("number of tracks", fontname='Ubuntu', fontsize=15)
fig = plt.figure(1)

st.pyplot(fig)
st.markdown("This is a word cloud of the music genres of the tracks that were played during the time window. The size of a genre is related to its frequency ! Library used : `matplotlib`, `wordcloud`")

plt.figure(2)
wordcloud = WordCloud(background_color="black").generate(" ".join(list(dfs["genre"][dfs["genre"] != "none"])))
plt.imshow(wordcloud, interpolation='bilinear')
plt.title("Word cloud of music genre", fontname='Ubuntu', fontsize=20, fontweight='bold')

plt.axis("off")
fig2 = plt.figure(2)

st.pyplot(fig2)
st.markdown("The following 2 plots are histograms representing one of the most basic spotify statistics : most listened to. The first graph shows the most popular artists, and the second the most popular tunes ! Library used : `altair`")

art = dfs.groupby(by="nam", as_index=False).count()[['track', 'nam']]
art = pd.DataFrame(art).sort_values(by="track", ascending=False).head(20)

st.write(alt.Chart(art, title="20 most popular artists").mark_bar().encode(
    alt.X('nam:N', title='name of artists'),
    alt.Y('track:Q', title='number of track listened')).properties(
    width=800,
    height=600
).configure_axis(
    labelFontSize=15,
    titleFontSize=15
))

art2 = dfs.groupby(by=["nam", "track", 'imag'], as_index=False).count()[['track', 'nam', "genre", 'imag']]
art2 = pd.DataFrame(art2).sort_values(by="genre", ascending=False).head(20)
st.write(alt.Chart(art2, title="20 most popular songs").mark_image().encode(
    alt.X('track:N', title='name of artists'),
    alt.Y('genre:Q', title='number of track listened'),
    url="imag"
).properties(
    width=800,
    height=600
).configure_axis(
    labelFontSize=15,
    titleFontSize=15
))

# Number of music listened to ploted against the distance walked in the day
st.markdown("This scatter plot represents the number of music listened against the distance walked in the day. Since maps gives coordinates, the distance was computed using the harversine formula. Library used : `matplotlib`")

st.code("""def harv(la1,lo1,la2,lo2):
    earth_radius = 6378
    p = pi/180
    a = 0.5 - cos((la2-la1)*p)/2 + cos(la1*p)*cos(la2*p) * (1-cos((lo2-lo1)*p)) / 2
    return 2*earth_radius*asin(sqrt(a))""")

dist_day = dfp[["year", "month", "day", "dist"]].groupby(by=["year", "month", "day"]).sum()["dist"]
nb_ecoutes = dfs.groupby(by=["year", "month", "day"]).count()['track']
melange = pd.DataFrame(nb_ecoutes).join(pd.DataFrame(dist_day))
plt.figure(3)
plt.scatter(melange["track"], melange["dist"], marker='v', c="g")
fig3 = plt.figure(3)
plt.title("Number of tracks against the distance travelled per day", fontname='Ubuntu', fontsize=20, fontweight='bold')
plt.xlabel("number of tracks", fontname='Ubuntu', fontsize=15)
plt.ylabel("distance travelled (km)", fontname='Ubuntu', fontsize=15)
st.pyplot(fig3)

st.markdown("Last but not least, it's time for the ")
# Map of music
st.subheader("Musical map !")

st.markdown("click on markers to see which song was listened at this place. library used : `folium`")

def dat_to_lon(dat, dfp):
    res = dfp[["lon"]][dfp["dat"] > dat].head(1)
    if res.shape[0] == 0:
        return dfp[["lon"]].tail(1).values[0][0]
    return res.values[0][0]


def dat_to_lat(dat, dfp):
    res = dfp[["lat"]][dfp["dat"] > dat].head(1)
    if res.shape[0] == 0:
        return dfp[["lat"]].tail(1).values[0][0]
    return res.values[0][0]


res = pd.DataFrame(dfs.apply(lambda x: dat_to_lon(x.dat, dfp), axis=1))
dfs["lat"] = res

res = pd.DataFrame(dfs.apply(lambda x: dat_to_lat(x.dat, dfp), axis=1))
dfs["lon"] = res

m = folium.Map(location=[48.828669, 2.365653], tiles='openstreetmap', zoom_start=13, control_scale=True)
for i in range(dfs.shape[0]):
    html = "<h5>Name of the song</h5><p>" + dfs.iloc[i]['track'] + "</p><h5>Name of the artist</h5><p>" + dfs.iloc[i][
        'nam'] + "</p><img src=" + dfs.iloc[i]['imag'] + " alt='album image'>"
    iframe = branca.element.IFrame(html=html, width=500, height=300)
    popup = folium.Popup(iframe, max_width=500)
    folium.Marker(
        location=[dfs.iloc[i]['lon'], dfs.iloc[i]['lat']],
        popup=popup,
    ).add_to(m)
folium_static(m)
