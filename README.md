# datavizproject

### What is that ?

A project I did from september to october 2021 for my Data visualization class in Efrei Paris. The theme was to visualize our own data. I did a jointure of my maps data and spotify.

###  Requirement for it to run

1. Have python and pip installed.

2. All the dependencies are in requirements.txt.
To install : `pip install -r requirements.txt`

3. It is advised to create a virtual environment for this

### How to use it

This is a streamlit app, so to run it, simply go to the root of the directory and tap `streamlit run app.py`. Then follow the instruction in the how to section if you want to visualize your own data. In a nutshell :

- I gathered the spotify data with a bot I created for the occasion, to do the same check out my repository : [spothistbot](https://github.com/ktazi/spothistbot)
- I transformed the google maps from kml format to csv with the script `kml_to_csv.py`. To do the same, put the path to your kml and future path to your csv in the configure.json file
- I put the path of the 2 csv in my configure.csv file. It is important, as the app refers to these paths to open the data


