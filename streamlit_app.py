import streamlit as st
import pandas as pd
from transformers import pipeline
from PIL import Image

# Pengaturan Judul Halaman
st.set_page_config(page_title="AI Business Suite", page_icon="🚀", layout="wide")

# ==========================================
# 1. LOAD MODEL AI RINGAN (HEMAT RAM SERVER)
# ==========================================
@st.cache_resource
def load_models():
    # Model Tanya Jawab (QA) - Hanya ~200MB
    qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    # Model Ringkasan - Hanya ~300MB
    ringkas = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    # Model Analisis Sentimen - Hanya ~50MB
    sentimen = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    return qa, ringkas, sentimen

qa_pipeline, ringkas_pipeline, sentimen_pipeline = load_models()

# Fungsi Generator Gambar Demo
def generate_gambar_konten():
    img = Image.new('RGB', (400, 300), color = (73, 109, 137))
    return img

# ==========================================
# 2. TAMPILAN ANTARMUKA (UI DASBOR)
# ==========================================
st.title("🚀 AI Business Suite Multi-Fungsi")
st.caption("Solusi AI Otomatis untuk Manajemen Toko Online & Kreator Konten")

# Membuat 3 Tab Menu Bisnis
tab1, tab2, tab3 = st.tabs(["🏪 AI Copilot Admin Toko", "✍️ Agregator Konten", "📊 Premium: Analisis Massal"])

# --- TAB 1: AI COPILOT ADMIN ---
with tab1:
    st.header("Auto-Reply Chat Berdasarkan SOP Toko")
    col1, col2 = st.columns(2)
    
    with col1:
        faq_input = st.text_area(
            "Dokumen Kebijakan & FAQ Toko (SOP)", 
            value="Nama Toko: HijabChic. Kebijakan Retur: Garansi ganti baru jika robek dalam 3 hari. Ongkir retur ditanggung toko. Harga Gamis Aisyah: Rp 150.000, stok sisa 5 pcs. Jadwal pengiriman: Setiap jam 3 sore menggunakan J&T.",
            height=200
        )
        pertanyaan_input = st.text_input("Chat Masuk dari Pembeli", placeholder="Contoh: sis kalau barangnya cacat gimana?")
        tombol_admin = st.button("Rekomendasikan Balasan Chat", type="primary")
        
    with col2:
        st.subheader("Draf Jawaban Otomatis")
        if tombol_admin:
            if faq_input and pertanyaan_input:
                with st.spinner("AI sedang memikirkan jawaban..."):
                    hasil = qa_pipeline(question=pertanyaan_input, context=faq_input)
                    st.success(f"👉 \"{hasil['answer']}\"")
                    st.info(f"Tingkat Akurasi: {hasil['score']:.2f}")
            else:
                st.warning("Mohon isi SOP Toko dan pertanyaan pembeli terlebih dahulu.")

# --- TAB 2: AGREGATOR KONTEN ---
with tab2:
    st.header("Input Tren -> Hasil Skrip Konten & Ide Gambar")
    col3, col4 = st.columns(2)
    
    with col3:
        berita_input = st.text_area("Tempel Teks Berita/Tren Asing", placeholder="Tempel artikel tren di sini...", height=200)
        tombol_konten = st.button("Generate Konsep Konten", type="primary")
        
    with col4:
        if tombol_konten:
            if berita_input:
                with st.spinner("Menganalisis tren..."):
                    panjang = len(berita_input.split())
                    max_len = min(60, panjang) if panjang > 10 else 10
                    ringkasan = ringkas_pipeline(berita_input, max_length=max_len, min_length=5, do_sample=False)[0]['summary_text']
                    
                    st.subheader("Rangkuman Inti untuk Skrip Video")
                    st.write(ringkasan)
                    
                    st.subheader("Rekomendasi Visual Banner")
                    gambar = generate_gambar_konten()
                    st.image(gambar, caption="Layout Dasar Promosi")
            else:
                st.warning("Masukkan teks berita terlebih dahulu.")

# --- TAB 3: FITUR PREMIUM ---
with tab3:
    st.header("Analisis Ulasan Massal dari Excel / CSV")
    file_upload = st.file_uploader("Unggah File .csv atau .xlsx (Pastikan ada kolom bernama 'ulasan')", type=["csv", "xlsx"])
    tombol_analisis = st.button("Mulai Analisis Massal", type="primary")
    
    if tombol_analisis and file_upload:
        with st.spinner("Sedang memproses data massal..."):
            try:
                if file_upload.name.endswith('.csv'):
                    df = pd.read_csv(file_upload)
                else:
                    df = pd.read_excel(file_upload)
                
                kolom_target = None
                for col in df.columns:
                    if 'ulasan' in col.lower() or 'text' in col.lower() or 'review' in col.lower():
                        kolom_target = col
                        break
                
                if not kolom_target:
                    st.error("Error: File harus memiliki kolom bernama 'ulasan', 'text', atau 'review'.")
                else:
                    # Proses 5 baris data teratas untuk efisiensi server gratisan
                    df_hasil = df.head(5).copy()
                    hasil_ringkas = []
                    hasil_sentimen = []
                    
                    for teks in df_hasil[kolom_target]:
                        teks_str = str(teks)
                        # Hitung sentimen
                        res_s = sentimen_pipeline(teks_str)[0]
                        hasil_sentimen.append(f"{res_s['label']} ({res_s['score']:.2f})")
                        # Hitung ringkasan pendek
                        res_r = ringkas_pipeline(teks_str, max_length=15, min_length=2, do_sample=False)[0]['summary_text']
                        hasil_ringkas.append(res_r)
                    
                    df_hasil['Kesimpulan AI'] = hasil_ringkas
                    df_hasil['Kategori Emosi'] = hasil_sentimen
                    
                    st.success("Analisis Berhasil Selesai!")
                    st.dataframe(df_hasil)
                    
                    # Konversi hasil ke CSV untuk didownload
                    csv_data = df_hasil.to_csv(index=False).encode('utf-8')
                    st.download_button("Unduh File Hasil Analisis (.csv)", data=csv_data, file_name="hasil_analisis_ai.csv", mime="text/csv")
            except Exception as e:
                st.error(f"Gagal memproses file: {str(e)}")
