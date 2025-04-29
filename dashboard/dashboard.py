import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# Fungsi dekomposisi, memishakan trend, musiman, dan residual
def decompose(series,period=7):
  data = series
  df_decomp = pd.DataFrame()
  decomp = seasonal_decompose(data, model='additive', period=period)  # disarankan periode sesuai dengan yang terlihat di graph line
  df_decomp['original'] = data
  df_decomp['trend'] = decomp.trend
  df_decomp['seasonal'] = decomp.seasonal
  df_decomp['residual'] = decomp.resid

  return df_decomp

def categorize_level_aqi(skor_aci):
    if skor_aci < 2:
        return 'Baik'
    elif skor_aci < 3:
        return 'Moderate'
    elif skor_aci < 4:
        return 'Tidak Sehat untuk Grup Senitive'
    elif skor_aci < 5:
        return 'Tidak Sehat'
    elif skor_aci < 6:
        return 'Sangat Tidak Sehat'
    else :
        return 'Berbahaya'

    
st.set_page_config(page_title="Dashboard Kualitas Udara & Cuaca", layout="wide")

# Halaman Utama
st.title("🌤️ Dashboard Kualitas Udara & Cuaca Semua Statiun")

@st.cache_data
def load_data(path):
    # Read the Excel file from the URL
    data = pd.read_excel(path,sheet_name=None, parse_dates=True, engine='openpyxl')
    return data

df_all = load_data('station_data_days.xlsx')
station_list = list(df_all.keys())

# Peringkat Stasiun berdasarkakan Level AQI
st.subheader("🏆 Peringkat Stasiun Berdasarkan Level AQI")
st.write("Peringkat stasiun berdasarkan level AQI harian dari yang terendah ke tertinggi.")
st.write("Level AQI:")
st.write("Level 1. Baik (0-50)")
st.write("Level 2. Moderate (51-100)")
st.write("Level 3. TTidak Sehat untuk Grup Senitive (101-150)")
st.write("Level 4. Tidak Sehat (151-200)")
st.write("Level 5. Sangat Tidak Sehat (201-300)")
st.write("Level 6. Berbahaya (301-500)")

ACI_skor = []
ACI_station = []
pm25_mean = []

for i,station in enumerate(df_all.keys()):
  pm25_skor = pd.DataFrame()
  data = df_all[station]
  data_pm25 = data[data['AQI_category_max'] == 'PM2.5']
  pm25_mean.append(data_pm25['PM2.5'].mean())

  # membuat dataframe perhitungan
  pm25_skor['pm25_nDays'] = data_pm25.groupby('AQI_category')['PM2.5'].count()
  pm25_skor['Indeks'] = [1,2,3,4,5,6]

  # Average Category Index (ACI)
  aci = pm25_skor['Indeks'] * pm25_skor['pm25_nDays']
  ACI = (aci.sum()) / pm25_skor['pm25_nDays'].sum()
  ACI_skor.append(ACI)
  ACI_station.append(station)

# Skor ACI dan Rankingnya
aci_skor = pd.Series(ACI_skor,index=ACI_station,name='Score')

df_aci_skor = pd.DataFrame({'ACI':aci_skor,
                            'PM2.5_mean':pm25_mean,
                            'Kategori': aci_skor.apply(lambda x : categorize_level_aqi(x)),
                            'Rank':aci_skor.rank(ascending=False)})

# menampilkan data frame Score Level AQI
st.dataframe(df_aci_skor.sort_values('ACI',ascending=False))

col01,col02 = st.columns(2)
with col01:
    MEAN_conc = aci_skor.mean()
    st.metric("Rata-Rata Level AQI", value=round(MEAN_conc,2))
    st.write(f'Kategori {categorize_level_aqi(MEAN_conc)}')

fig_bar_01, ax_bar_01 = plt.subplots(1,1,figsize=(15,5))
df_aci_skor.sort_values('ACI',ascending=True).plot(kind='barh',y='ACI',legend=False,ax=ax_bar_01)
ax_bar_01.bar_label(ax_bar_01.containers[0], fontsize=10)
st.pyplot(fig_bar_01)

select_station = st.selectbox("Pilih Stasiun", df_all.keys(), index=0)

# Tampilkan preview data
st.subheader("📄 Preview Data")
st.dataframe(df_all[select_station].head(10))
df = df_all[select_station]

# Konversi kolom datetime (asumsi ada kolom waktu)
if 'Time' in df.columns:
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
elif df.index.dtype != 'datetime64[ns]':
    df.index = pd.to_datetime(df.index)
else:
    st.error("Tidak ada kolom waktu yang dapat digunakan sebagai index.")

# Konversi tipe data kolom
# 1. AQI_category_max
label_cat_1 = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
df['AQI_category_max'] = df['AQI_category_max'].astype('category')

# 2. AQI_category
label_cat_2 = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6']
df['AQI_category'] = df['AQI_category'].astype('category')

for cat1,cat2 in zip(label_cat_1,label_cat_2):
    if cat1 not in df['AQI_category_max'].cat.categories:
        df['AQI_category_max'] = df['AQI_category_max'].cat.add_categories([cat1])
    elif cat2 not in df['AQI_category'].cat.categories:
        df['AQI_category'] = df['AQI_category'].cat.add_categories([cat2])
    else:
        break

# Tampilkan statistik deskriptif
st.subheader("📊 Statistik Deskriptif")
st.dataframe(df.describe().T)

# Distribusi parameter IAQI yang mempengaruhi AQI
st.subheader("📊 Distribusi Parameter IAQI")
fig_aqi01,ax_aqi01 = plt.subplots(figsize=(10, 5))
sns.countplot(data=df,x='AQI_category_max',order=label_cat_1,ax=ax_aqi01)
ax_aqi01.bar_label(ax_aqi01.containers[0], fontsize=10)
ax_aqi01.set_title("Distribusi parameter IAQI")
ax_aqi01.set_xlabel("Parameter IAQI")
ax_aqi01.set_ylabel("Jumlah Hari")
st.pyplot(fig_aqi01)

max_features = df['AQI_category_max'].value_counts().idxmax()
max_count = df['AQI_category_max'].value_counts().max()
st.write(f"{max_features} menjadi parameter IAQI yang paling banyak mempengaruhi " \
f"nilai AQI harian sebanyak {max_count} hari di stasiun {select_station}.")

# Distribusi Level AQI untuk kategori PM2.5
data = df_all[station].copy()
# data_pm25 merupakan dataframe yang hanya berisi data dari pengelompokam PM2.5 pada kolom AQI_category_max
data_pm25 = data[data['AQI_category_max'] == 'PM2.5']
mean_pm25 = data_pm25['PM2.5'].mean()

# visualisasi distribusinya
st.subheader("📊 Distribusi Level AQI Kategori PM2.5")
fig_aqi02,ax_aqi02 = plt.subplots(figsize=(10,5))
sns.countplot(data=data_pm25,x='AQI_category',order=label_cat_2,ax=ax_aqi02)
ax_aqi02.bar_label(ax_aqi02.containers[0], fontsize=10)
ax_aqi02.set_title(f'Distribusi Level AQI pada kategori PM2.5 di {station}')
ax_aqi02.set_xlabel('Konsentrasi yang menentukan nilai AQI')
ax_aqi02.set_ylabel('Jumlah hari')
st.pyplot(fig_aqi02)

# Mapping kategori AQI ke label
numeric_cols = df.select_dtypes(include='number').columns.tolist()
obj_cols = df.select_dtypes(include='object').columns.tolist()
categorical_cols = df.select_dtypes(include='category').columns.tolist()

# Heatmap Korelasi
trend_df = pd.DataFrame()
for feature in numeric_cols:
    trend = decompose(df[feature],period=365)
    trend_df[feature] = trend['trend']

st.subheader("🔍 Korelasi Antar Parameter")
corr = trend_df.corr()
fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax_corr)
st.pyplot(fig_corr)

# Pilih parameter untuk diplot
list_cols = df.columns.tolist()

selected_params = st.selectbox("Pilih satu kolom untuk divisualisasikan", list_cols)
time_range = st.slider("Pilih rentang waktu",
                       min_value=df.index.min().to_pydatetime(),
                       max_value=df.index.max().to_pydatetime(),
                       value=(df.index.min().to_pydatetime(), df.index.max().to_pydatetime()))
df_filtered = df.loc[time_range[0]:time_range[-1]]

if selected_params in numeric_cols:

    # Time Series Plot
    st.subheader(f"📈 Time Series {selected_params}")
    col1, col2, col3, = st.columns(3)
    
    with col1:
        Min_conc = df_filtered[selected_params].min()
        st.metric("Min Value", value=round(Min_conc,2))
        st.write('on', df_filtered[selected_params].idxmin().strftime('%d %b %Y'))
    
    with col2:
        Max_conc = df_filtered[selected_params].max()
        st.metric("Max Value", value=round(Max_conc,2))
        st.write('on', df_filtered[selected_params].idxmax().strftime('%d %b %Y'))
 
    with col3:
        Mean_conc = df_filtered[selected_params].mean()
        st.metric("Mean Value", value=round(Mean_conc,2))

    trend_df_filtered = pd.DataFrame()
    for feature in numeric_cols:
        trend = decompose(df_filtered[feature],period=365)
        trend_df_filtered[feature] = trend['trend']
    
    # Observasi Data Plot
    fig_ts = px.line(df_filtered, x=df_filtered.index, y=selected_params, title=f"Time Series {selected_params}")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Trend Data Plot
    fig_trend = px.line(trend_df_filtered, x=trend_df_filtered.index, y=selected_params, title=f"Trend {selected_params}")
    fig_trend.update_traces(line=dict(width=2))
    fig_trend.update_layout(yaxis_title="Trend")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Histogram Plot
    st.subheader(f"📊 Histogram {selected_params}")
    fig_hist = px.histogram(df_filtered, x=selected_params, title=f"Histogram {selected_params}")
    fig_hist.update_traces(marker=dict(line=dict(width=1, color='black')))
    fig_hist.update_layout(bargap=0.2)
    st.plotly_chart(fig_hist, use_container_width=True)

    # Korelasi Dengan Feature Lain
    st.subheader("🔍 Korelasi Antar Parameter")
    corr = trend_df_filtered.corr()
    fig_corr_param, ax_corr_param = plt.subplots()
    sns.barplot(corr[selected_params], ax=ax_corr_param)
    ax_corr_param.set_ylim(-1, 1)
    ax_corr_param.bar_label(ax_corr_param.containers[0], fontsize=5)
    st.pyplot(fig_corr_param)

elif selected_params in obj_cols:
    wind = df_filtered.copy()
    st.dataframe(wind['wd'].describe())

    # Mapping arah angin ke sudut (0–360°) ===
    wind_dir_map = {'N': 0,'NNE': 22.5,'NE': 45,'ENE': 67.5,
                    'E': 90,'ESE': 112.5,'SE': 135,'SSE': 157.5,
                    'S': 180,'SSW': 202.5,'SW': 225,'WSW': 247.5,
                    'W': 270,'WNW': 292.5,'NW': 315,'NNW': 337.5
                    }
        
    wind['wind_direction_deg'] = wind['wd'].map(wind_dir_map)

    # Visualisasi Windrose dengan Plotly ===
    fig = px.bar_polar(
    wind,
    r='WSPM',
    theta='wind_direction_deg',
    color='wd',
    color_discrete_sequence=px.colors.sequential.Plasma_r,
    title='🌬️ Visualisasi Windrose'
    )

    fig.update_layout(
        polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90)  # Kompas style
        )
    )
    st.plotly_chart(fig, use_container_width=True)

elif selected_params in categorical_cols:
    if selected_params == 'AQI_category_max':
        # Visualisasi IAQI Category MAX
        fig_aqi1,ax_aqi1 = plt.subplots(figsize=(10, 5))
        sns.countplot(data=df_filtered,x='AQI_category_max',order=label_cat_1,ax=ax_aqi1)
        ax_aqi1.bar_label(ax_aqi1.containers[0], fontsize=10)
        ax_aqi1.set_title("Distribusi parameter IAQI yang mempengaruhi AQI")
        st.pyplot(fig_aqi1)
    
    elif selected_params == 'AQI_category':
        # Visualisasi AQI Category
        fig_aqi2,ax_aqi2 = plt.subplots(figsize=(10, 5))
        sns.countplot(data=df_filtered,x='AQI_category',order=label_cat_2,ax=ax_aqi2)
        ax_aqi2.bar_label(ax_aqi2.containers[0], fontsize=10)
        ax_aqi2.set_title("Distribusi AQI Level")
        st.pyplot(fig_aqi2)

    else:
        st.warning("Parameter yang dipilih bukan parameter numerik atau tidak valid untuk analisis.")

else:
    st.warning("Parameter yang dipilih bukan parameter numerik, category atau tidak valid untuk analisis.")