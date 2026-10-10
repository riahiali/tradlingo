import streamlit as st
from pypdf import PdfReader

import api_client

st.set_page_config(page_title="TradLingo", page_icon="🌍")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 920px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero {
        border: 1px solid color-mix(in srgb, var(--text-color), transparent 85%);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        margin-bottom: 1rem;
        background: color-mix(in srgb, var(--background-color), var(--primary-color) 6%);
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: 0.35rem 0 0 0;
        opacity: 0.85;
    }
    .section-card {
        border: 1px solid color-mix(in srgb, var(--text-color), transparent 86%);
        border-radius: 14px;
        padding: 0.85rem 0.9rem;
        margin-bottom: 0.85rem;
        background: color-mix(in srgb, var(--background-color), var(--secondary-background-color) 35%);
    }
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🌍 TradLingo</h1>
      <p>Traduction FR / EN / AR, simple et rapide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

LANGUES = ["fr", "en", "ar"]

if "historique" not in st.session_state:
    st.session_state.historique = []

st.markdown('<div class="section-card">', unsafe_allow_html=True)
col_source, col_cible = st.columns(2)
with col_source:
    source = st.selectbox("Langue source", LANGUES, index=0)
with col_cible:
    cible = st.selectbox("Langue cible", LANGUES, index=1)
auto_detect = st.checkbox("Détecter automatiquement la langue source", value=False)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
texte = st.text_area("Texte à traduire", height=160, placeholder="Entrez votre texte ici...")
fichier = st.file_uploader("Importer un fichier (.txt ou .pdf)", type=["txt", "pdf"])
if fichier is not None:
    if fichier.name.lower().endswith(".txt"):
        try:
            texte = fichier.read().decode("utf-8")
        except UnicodeDecodeError:
            st.error("Le fichier texte doit être encodé en UTF-8.")
            texte = ""
    elif fichier.name.lower().endswith(".pdf"):
        try:
            reader = PdfReader(fichier)
            texte = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
            if not texte:
                st.error("Aucun texte lisible trouvé dans ce PDF.")
        except Exception:
            st.error("Impossible de lire ce PDF.")
            texte = ""
st.markdown("</div>", unsafe_allow_html=True)

if st.button("Traduire", use_container_width=True):
    try:
        if auto_detect:
            source_effective = api_client.detecter_langue(texte)
        else:
            source_effective = source

        traduction = api_client.traduire(texte, source_effective, cible)
        st.subheader("Résultat")
        st.write(traduction)

        st.session_state.historique.insert(0, {
            "source": source_effective,
            "cible": cible,
            "texte": texte,
            "traduction": traduction,
        })
    except api_client.ApiError as exc:
        st.error(exc)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.subheader("Historique de session")
with col_h2:
    if st.button("Vider", use_container_width=True):
        st.session_state.historique = []

if st.session_state.historique:
    for item in st.session_state.historique:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"**{item['source']} → {item['cible']}**")
        st.write(item["texte"])
        st.write("→", item["traduction"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()
else:
    st.caption("Aucune traduction pour le moment.")