# ⚡ Predictive Maintenance SUTM Dashboard
**PT PLN UP3 Bandung — 2026**

Dashboard interaktif untuk analisis data inspeksi SUTM (Saluran Udara Tegangan Menengah) dengan pembaruan otomatis setiap kali data Excel diperbarui.

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Siapkan File Excel
Letakkan dua file Excel di folder yang sama dengan `app.py`:
- `1__INSPEKSI_SUTM_T1_2026.xlsx` — Data inspeksi visual (SUTMT1)
- `2__INSPEKSI_SUTM_T2_-_2026.xlsx` — Data inspeksi thermal (SUTMT2)

### 3. Jalankan Dashboard
```bash
streamlit run app.py
```

Dashboard akan terbuka otomatis di browser: `http://localhost:8501`

---

## 🔄 Update Data Otomatis

Dashboard akan **refresh otomatis setiap 30 detik**.

Caranya:
1. Aktifkan toggle **"Auto-refresh (30s)"** di sidebar
2. Tambahkan data baru ke file Excel
3. Dashboard akan memuat data terbaru secara otomatis

Atau: Upload file Excel baru langsung dari sidebar menggunakan **"Upload new Excel files"**

---

## 🌐 Deploy ke Streamlit Cloud (Gratis)

### Langkah 1 — Upload ke GitHub
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

### Langkah 2 — Connect ke Streamlit Cloud
1. Buka [streamlit.io/cloud](https://streamlit.io/cloud)
2. Login dengan akun GitHub
3. Klik **"New app"**
4. Pilih repository → pilih `app.py` sebagai main file
5. Klik **"Deploy!"**

Selesai! Dalam ~2 menit dashboard online dan bisa diakses siapa saja.

---

## 📁 Struktur File

```
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .streamlit/
│   └── config.toml                 # Dark theme config
├── 1__INSPEKSI_SUTM_T1_2026.xlsx  # Visual inspection data
└── 2__INSPEKSI_SUTM_T2_-_2026.xlsx # Thermal inspection data
```

> ⚠️ **Penting**: Jangan upload file Excel ke GitHub jika datanya sensitif.
> Gunakan fitur **Upload** di sidebar untuk upload data secara langsung.

---

## 📊 Fitur Dashboard

| Tab | Isi |
|-----|-----|
| 📊 Overview | KPI cards, donut chart, distribusi per ULP, histogram risk score, monthly progress |
| ⚠️ Risk Analysis | Treemap, top penyulang, tabel summary per ULP |
| 🔬 Health Index | Stacked bar 12 komponen, heatmap per ULP, ranking BURUK |
| 🌡️ Thermal | Distribusi ΔT, HI-1 chart, summary per ULP |
| 🤖 ML Results | F1-Score comparison, fold stability, grouped metrics |
| 🎯 Priority List | Tabel sortir + download CSV |

---

## ⚙️ Konfigurasi

Edit baris ini di `app.py` untuk mengubah path default file Excel:
```python
t1_path = "1__INSPEKSI_SUTM_T1_2026.xlsx"
t2_path = "2__INSPEKSI_SUTM_T2_-_2026.xlsx"
```

---

*Developed for PT PLN UP3 Bandung Predictive Maintenance Program 2026*
