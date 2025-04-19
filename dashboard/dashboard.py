import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Kualitas Udara & Cuaca", layout="wide")

st.title("🌤️ Dashboard Kualitas Udara & Cuaca Semua Statiun")
df_all = pd.read_excel('station_data_days.xlsx', sheet_name=None, parse_dates=True)
station_list = list(df_all.keys())

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
    if cat2 not in df['AQI_category'].cat.categories:
        df['AQI_category'] = df['AQI_category'].cat.add_categories([cat2])
    

# Tampilkan statistik deskriptif
st.subheader("📊 Statistik Deskriptif")
st.dataframe(df.describe().T)

numeric_cols = df.select_dtypes(include='number').columns.tolist()
obj_cols = df.select_dtypes(include='object').columns.tolist()
categorical_cols = df.select_dtypes(include='category').columns.tolist()

# Heatmap Korelasi
st.subheader("🔍 Korelasi Antar Parameter")
corr = df[numeric_cols].corr()
fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, vmin=-1, vmax=1, ax=ax_corr)
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

    fig_ts = px.line(df_filtered, x=df_filtered.index, y=selected_params, title=f"Time Series {selected_params}")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Histogram Plot
    st.subheader(f"📊 Histogram {selected_params}")
    fig_hist = px.histogram(df_filtered, x=selected_params, title=f"Histogram {selected_params}")
    fig_hist.update_traces(marker=dict(line=dict(width=1, color='black')))
    fig_hist.update_layout(bargap=0.2)
    st.plotly_chart(fig_hist, use_container_width=True)

    # Korelasi Dengan Feature Lain
    st.subheader("🔍 Korelasi Antar Parameter")
    corr = df_filtered[numeric_cols].corr()
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