import streamlit as st
import pandas as pd
import requests
from PIL import Image

# Konfigurasi Halaman Utama
st.set_page_config(page_title="AI Business Suite Pro", page_icon="🚀", layout="wide")

# ==========================================
# 1. FUNGSI UTAMA INTEGRASI API HUGGING FACE
# ==========================================
# Kita menggunakan model Llama-3 milik Meta yang di-host gratis oleh Hugging Face
API_URL = "https://huggingface.co"

# CARI FUNGSI INI DI STREAMLIT_APP.PY ANDA DAN GANTI DENGAN KODE BERIKUT:

API_URL = "https://huggingface.co"

def panggil_huggingface_api(prompt_teks):
    """Fungsi final mengirim request aman dengan validasi Content-Type & Token"""
    try:
        hf_token = st.secrets["HF_TOKEN"]
        # PERBAIKAN UTAMA: Wajib menyertakan Content-Type dan Token secara eksplisit
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
    except Exception:
        return "Error: Kode token HF_TOKEN belum dimasukkan ke menu Advanced Settings -> Secrets di Streamlit Cloud."
        
    payload = {
        "inputs": prompt_teks,
        "parameters": {
            "max_new_tokens": 200, 
            "temperature": 0.7,
            "return_full_text": False  # Mencegah teks prompt asli ikut terulang di jawaban
        }
    }
    
    try:
        # Kirim request post ke server Hugging Face
        response = requests.post(API_URL, json=payload, headers=headers)
        
        # Skenario jika model sedang tidur / loading di server HF
        if response.status_code == 503:
            return "Model AI di server Hugging Face sedang dibangunkan dari mode tidur. Mohon tunggu 15 detik lalu klik kembali tombolnya."
            
        # Skenario jika akses ditolak atau token salah
        if response.status_code in [401, 403]:
            return "Akses Ditolak! Pastikan Token 'Read' dari Hugging Face yang Anda masukkan di menu Secrets sudah benar dan aktif."

        # Membaca isi respons teks mentah terlebih dahulu untuk memastikan keamanan data
        teks_mentah = response.text.strip()
        if not teks_mentah:
            return "Menerima respons kosong dari server. Silakan coba kirim ulang chat Anda."

        # Konversi teks ke data JSON
        hasil_json = response.json()
        
        # Ekstrak hasil teks (Skenario Format List)
        if isinstance(hasil_json, list) and len(hasil_json) > 0:
            item = hasil_json[0]
            if isinstance(item, dict) and 'generated_text' in item:
                return item['generated_text'].strip()
                
        # Ekstrak hasil teks (Skenario Format Dictionary)
        elif isinstance(hasil_json, dict):
            if 'generated_text' in hasil_json:
                return hasil_json['generated_text'].strip()
            elif "error" in hasil_json:
                return f"Pesan Server Hugging Face: {hasil_json['error']}"
                
        return f"Format data tidak dikenali. Respons mentah: {teks_mentah[:200]}"
        
    except Exception as e:
        return f"Koneksi ke Hugging Face terputus: {str(e)}"

# Placeholder Gambar Layout
def generate_gambar_konten():
    return Image.new('RGB', (400, 250), color = (41, 128, 185))

# ==========================================
# 2. TAMPILAN ANTARMUKA DASBOR (UI)
# ==========================================
st.title("🚀 AI Business Suite Multi-Fungsi (Versi Cloud API)")
st.caption("Solusi AI Hemat RAM Berbasis Serverless Hugging Face API — 100% Stabil & Mendukung Bahasa Indonesia")

tab1, tab2, tab3 = st.tabs(["🏪 1. AI Copilot Admin Toko", "✍️ 2. Agregator Konten", "📊 3. Premium: Analisis Ulasan"])

# --- TAB 1: AI COPILOT ADMIN ---
with tab1:
    st.header("Auto-Reply Chat Berdasarkan SOP Toko")
    col1, col2 = st.columns(2)
    
    with col1:
        faq_input = st.text_area(
            "Dokumen Kebijakan & FAQ Toko (SOP)", 
            value="Nama Toko: HijabChic.\nKebijakan Retur: Garansi ganti baru jika robek/cacat dalam 3 hari setelah barang sampai. Ongkir retur ditanggung toko.\nHarga Gamis Aisyah: Rp 150.000, sisa stok 5 pcs.\nJadwal pengiriman: Setiap jam 3 sore menggunakan ekspedisi J&T.",
            height=180
        )
        pertanyaan_input = st.text_input("Chat Masuk dari Pembeli", placeholder="Contoh: Sis, kalau gamis aisyah harganya berapa dan dikirim kapan?")
        tombol_admin = st.button("Rekomendasikan Balasan Chat", type="primary", key="btn_admin")
        
    with col2:
        st.subheader("Draf Jawaban Otomatis")
        if tombol_admin:
            if faq_input.strip() and pertanyaan_input.strip():
                with st.spinner("Menghubungi Server Hugging Face..."):
                    # Menyusun prompt instruksi khusus untuk model LLM
                    prompt = f"<|im_start|>system\nAnda adalah admin toko online yang ramah dan profesional. Jawab pertanyaan pembeli HANYA berdasarkan SOP Toko berikut:\n{faq_input}<|im_end|>\n<|im_start|>user\n{pertanyaan_input}<|im_end|>\n<|im_start|>assistant\n"
                    jawaban_ai = panggil_huggingface_api(prompt)
                    st.success(jawaban_ai)
            else:
                st.warning("Mohon lengkapi data SOP dan pertanyaan pembeli.")

# --- TAB 2: AGREGATOR KONTEN ---
with tab2:
    st.header("Input Tren/Berita -> Hasil Skrip Konten Sosmed")
    col3, col4 = st.columns(2)
    
    with col3:
        berita_input = st.text_area("Tempel Artikel Tren/Berita Asing atau Lokal", placeholder="Tempel bahan berita di sini...", height=180)
        tombol_konten = st.button("Generate Konsep Konten", type="primary", key="btn_konten")
        
    with col4:
        if tombol_konten:
            if berita_input.strip():
                with st.spinner("AI sedang merangkum konsep konten..."):
                    prompt = f"<|im_start|>system\nAnda adalah seorang Content Creator ahli. Buatlah ringkasan singkat dalam bentuk poin-poin penting serta draf skrip video TikTok/Reels yang menarik berdasarkan artikel berikut:\n{berita_input}<|im_end|>\n<|im_start|>assistant\n"
                    hasil_konten = panggil_huggingface_api(prompt)
                    st.subheader("Rekomendasi Skrip & Konsep")
                    st.write(hasil_konten)
                    
                    st.subheader("Rekomendasi Visual Banner")
                    st.image(generate_gambar_konten(), caption="Layout Visual Promosi")
            else:
                st.warning("Masukkan teks berita terlebih dahulu.")

# --- TAB 3: FITUR PREMIUM ---
with tab3:
    st.header("Analisis Ulasan Massal (Max 5 Baris untuk Demo)")
    file_upload = st.file_uploader("Unggah File .csv atau .xlsx (Wajib kolom bernama 'ulasan')", type=["csv", "xlsx"])
    tombol_analisis = st.button("Mulai Analisis Massal", type="primary", key="btn_analisis")
    
    if tombol_analisis and file_upload:
        with st.spinner("Memproses data via Hugging Face API..."):
            try:
                df = pd.read_csv(file_upload) if file_upload.name.endswith('.csv') else pd.read_excel(file_upload)
                
                kolom_target = next((col for col in df.columns if any(kw in col.lower() for kw in ['ulasan', 'text', 'review'])), None)
                
                if not kolom_target:
                    st.error("Error: File harus memiliki kolom bernama 'ulasan', 'text', atau 'review'.")
                else:
                    df_hasil = df.head(5).copy()
                    kesimpulan_list = []
                    
                    for index, teks in enumerate(df_hasil[kolom_target]):
                        prompt = f"<|im_start|>system\nAnalisis ulasan produk berikut. Berikan kategori emosi (POSITIF/NEGATIF) dan 3 kata inti kesimpulannya. Contoh format output: [POSITIF] Produk sangat bagus.\nUlasan: {str(teks)}<|im_end|>\n<|im_start|>assistant\n"
                        res = panggil_huggingface_api(prompt)
                        kesimpulan_list.append(res)
                    
                    df_hasil['Analisis Kepuasan AI'] = kesimpulan_list
                    st.success("Analisis Massal Selesai!")
                    st.dataframe(df_hasil)
                    
                    csv_data = df_hasil.to_csv(index=False).encode('utf-8')
                    st.download_button("Unduh Hasil (.csv)", data=csv_data, file_name="hasil_analisis_api.csv", mime="text/csv")
            except Exception as e:
                st.error(f"Gagal memproses file: {str(e)}")
