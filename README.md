# ProyekAnalisiData_MhdApriArami
Repository ini berisi proyek Analisis Data Kualitas Udara untuk Submission Proyek Akhir Modul Belajar Analisisi Data dengan Python pada Platform Dicoding
Adapun isinya terdiri dua bagian utama
1. Dashboard menggunakan streamlit
2. Notebook Analisis Data menggunakan Python

## Fitur Dashboard
Dashboard ini menyediakan fitur berikut:
- Visualisasi data kualitas udara dari berbagai stasiun.
- Statistik deskriptif untuk parameter kualitas udara.
- Korelasi antar parameter dalam bentuk heatmap.
- Visualisasi arah angin menggunakan windrose.
- Histogram dan time series untuk parameter tertentu.

## Cara Menjalankan Dashboard Streamlit

Ikuti langkah-langkah berikut untuk menjalankan dashboard:

1. **Clone Repository**
   ```bash
   git clone https://github.com/apriarami789/ProyekAnalisiData_MhdApriArami.git
   cd ProyekAnalisiData_MhdApriArami

2. Install Dependensi
pip install -r requirements.txt

3. Jalankan Dashboard
streamlit run dashboard/dashboard.py

setelah prmpt di atas di running, nanti akan muncul window baru yang akan memperlihatkan dashboard

### Catatan
Pastikan file station_data_days.xlsx berada di folder dashboard/ agar dashboard dapat memuat data dengan benar.
File data mentah (PRSA_Data_*.csv) berada di folder data/ untuk keperluan analisis tambahan.
