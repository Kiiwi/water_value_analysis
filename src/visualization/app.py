import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [14, 6]

st.title('Water Value Analysis')

# Filling levels
df = pd.read_csv('/data/interim/fillinglevels.csv', index_col='acqdate')
df.index = pd.to_datetime(df.index)
df = df.resample('M').first()

# Model labels
mag_labels = np.array([1, 2, 0, 2, 0, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])


# Cluster
st.subheader('Cluster')

st.write('Cluster 1: Blåsjø, Storglomvatn')
st.write('Cluster 2: Strandevatn, Roskreppfjord, Vatnedalsvatn, Aursjøen, Nesjø, Akersvatn, Altevatn, Sisovatn, Styggevatnet, Nyhellervatn, Svartevatn')
st.write('Cluster 3: Bygdin, Møsvatn, Sysenvatn, Tyin, Songavatn')

cluster_selection = st.selectbox(
    'Select cluster',
    (1, 2 , 3)
)

cluster = mag_labels == (cluster_selection - 1)
df = df[df.columns[cluster]]

# Water usage
st.subheader('Water Usage')
month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
start_month, end_month = st.select_slider(
    'Select range for water usage',
    options=month_list,
    value=('October', 'December'))
st.write('You have selected water usage between end of', start_month, 'and end of', end_month)

df_start = df[df.index.month == month_list.index(start_month)]
df_end = df[df.index.month == month_list.index(end_month)]

df_start = df_start.mean(axis=1)
df_end = df_end.mean(axis=1)

water_used = df_start.values - df_end.values

df_water_usage = pd.DataFrame(index=df_start.index.year)
df_water_usage['Water Used'] = water_used

# System price
st.subheader('System Price')
df_price = pd.read_csv('/data/interim/system_price.csv', index_col='date')
df_price.index = pd.to_datetime(df_price.index)
df_price['year'] = df_price.index.year

week_list = list(range(1, 54))
start_week, end_week = st.select_slider(
    'Select system price range',
    options=week_list,
    value=(12, 16))
st.write('You have selected mean system price between week', start_week, 'and', end_week)

df_price = df_price[df_price.index.week.isin(list(range(start_week, end_week)))]
df_price = df_price.groupby('year').mean()

df_price.index = df_price.index + 1

# NVE
df_nve = pd.read_csv('/data/interim/nve.csv', index_col='dato_Id')
df_nve.index = pd.to_datetime(df_nve.index)
df_nve = df_nve.resample('M').first()
df_nve = df_nve['fyllingsgrad']
df_nve_start = df_nve[df_nve.index.month == month_list.index(start_month)]
df_nve_end = df_nve[df_nve.index.month == month_list.index(end_month)]
df_nve_difference = df_nve_start.values - df_nve_end.values
df_nve = pd.DataFrame(index=df_nve_start.index.year)
df_nve['NVE'] = df_nve_difference

# Final DataFrame
df_water_usage['Price'] = df_price
final = df_water_usage.copy()
final = final.dropna()

# Plot
st.subheader('Result')

nve_choice = st.radio('Include NVE?',
('No', 'Yes'))

if nve_choice == 'Yes':
    final['NVE'] = df_nve
    final = final.dropna()


fig,ax = plt.subplots()
ax.set_title("Cluster {} \nWater used from {} to {} vs System Price between weeks {} and {}".format(cluster_selection, start_month, end_month, start_week, end_week), fontsize=14)
ax.plot((final['Water Used']), color="red", marker="o")
if nve_choice == 'Yes':
    ax.plot((final['NVE']), color="green", marker="o")
ax.set_ylabel("water used",color="red",fontsize=14)
ax2=ax.twinx()
ax2.plot(final['Price'], color="blue",marker="o")
ax2.set_ylabel("price [EUR/MWh]",color="blue",fontsize=14)
st.pyplot(fig)



