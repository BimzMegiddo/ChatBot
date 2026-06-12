import streamlit as st
import google.generativeai as genai

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Aplikasi gagal berjalan: API Key tidak ditemukan di Streamlit Secrets!")
    st.stop()

system_instruction = (
    "Anda adalah 'Do-It Bot', seorang asisten produktivitas pribadi yang santai, cerdas, dan suportif. "
    "Tugas Anda adalah membantu pengguna mengelola To-Do List mereka."
)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=system_instruction
)

if "todo_list" not in st.session_state:
    st.session_state.todo_list = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Do-It Bot: AI Productivity Assistant", layout="wide")
st.title("🤖 Do-It Bot: Personal To-Do & AI Assistant")
st.write("Kelola tugasmu dan dapatkan insights cerdas dari AI untuk menyelesaikannya!")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Daftar Tugasmu")
    
    new_task = st.text_input("Tambah tugas baru baru di sini:", placeholder="Misal: Belajar materi presentasi Machine Learning")
    if st.button("Tambah Tugas"):
        if new_task:
            st.session_state.todo_list.append({"task": new_task, "status": "Belum Selesai"})
            st.success(f"Tugas '{new_task}' berhasil ditambahkan!")
            
            prompt_ai = f"Saya baru saja menambahkan tugas: '{new_task}'. Berikan tips singkat atau estimasi waktu untuk menyelesaikannya!"
            
            try:
                response = model.generate_content(prompt_ai)
                st.session_state.chat_history.append({"role": "user", "content": prompt_ai})
                st.session_state.chat_history.append({"role": "model", "content": response.text})
            except Exception as e:
                st.warning("⏳ Tips AI otomatis gagal dimuat karena kuota API sedang penuh. Tugasmu tetap berhasil disimpan! Coba lagi dalam 1 menit.")
            
            st.rerun()

    st.write("---")
    for idx, item in enumerate(st.session_state.todo_list):
        status_emoji = "✅" if item["status"] == "Selesai" else "⏳"
        cols_task = st.columns([0.1, 0.7, 0.2])
        cols_task[0].write(status_emoji)
        cols_task[1].write(item["task"])
        if item["status"] == "Belum Selesai":
            if cols_task[2].button("Selesai", key=f"btn_{idx}"):
                st.session_state.todo_list[idx]["status"] = "Selesai"
                st.rerun()

with col2:
    st.header("💬 Konsultasi AI Productivity")
    
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])
            
    if user_query := st.chat_input("Tanyakan tips produktivitas atau analisis tugasmu..."):
        with st.chat_message("user"):
            st.write(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        context = f"\n\n[Konteks To-Do List Saat Ini: {st.session_state.todo_list}]"
        full_prompt = user_query + context
        
        with st.chat_message("model"):
            try:
                response = model.generate_content(full_prompt)
                st.write(response.text)
                st.session_state.chat_history.append({"role": "model", "content": response.text})
            except Exception as e:
                error_msg = "⚠️ Maaf, permintaan terlalu padat (Rate Limit). Kuota Gemini API gratisan sedang habis. Silakan tunggu 1 menit lalu coba kirim pesan lagi."
                st.write(error_msg)
                st.session_state.chat_history.append({"role": "model", "content": error_msg})
