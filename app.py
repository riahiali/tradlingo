import streamlit as st
from pypdf import PdfReader

import api_client
import auth


st.set_page_config(page_title="TradLingo", page_icon="🌍", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --surface-border: color-mix(in srgb, var(--text-color), transparent 88%);
        --surface-bg: color-mix(in srgb, var(--background-color), var(--secondary-background-color) 60%);
        --surface-bg-strong: color-mix(in srgb, var(--background-color), var(--primary-color) 6%);
        --accent-bg: color-mix(in srgb, var(--primary-color), transparent 88%);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, color-mix(in srgb, var(--primary-color), transparent 82%) 0%, transparent 28%),
            radial-gradient(circle at top right, color-mix(in srgb, var(--secondary-background-color), transparent 35%) 0%, transparent 24%),
            linear-gradient(180deg, color-mix(in srgb, var(--background-color), white 1%) 0%, var(--background-color) 100%);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.75rem;
        padding-bottom: 2.5rem;
    }

    .hero {
        border: 1px solid var(--surface-border);
        border-radius: 24px;
        padding: 1.4rem 1.4rem 1.2rem 1.4rem;
        margin-bottom: 1rem;
        background:
            linear-gradient(135deg, color-mix(in srgb, var(--primary-color), transparent 90%) 0%, transparent 45%),
            var(--surface-bg-strong);
        box-shadow: 0 18px 45px color-mix(in srgb, black, transparent 90%);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.4rem;
        line-height: 1.05;
    }

    .hero p {
        margin: 0.45rem 0 0 0;
        opacity: 0.82;
        font-size: 1.02rem;
    }

    .section-card {
        border: 1px solid var(--surface-border);
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.9rem;
        background: var(--surface-bg);
        box-shadow: 0 10px 30px color-mix(in srgb, black, transparent 94%);
    }

    .panel-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.8rem;
    }

    .panel-title h2,
    .panel-title h3 {
        margin: 0;
    }

    .panel-subtitle {
        margin: 0.1rem 0 0 0;
        opacity: 0.75;
        font-size: 0.95rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        border: 1px solid var(--surface-border);
        background: color-mix(in srgb, var(--primary-color), transparent 92%);
        font-size: 0.85rem;
        font-weight: 600;
    }

    .mini-card {
        border: 1px solid var(--surface-border);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        background: color-mix(in srgb, var(--background-color), var(--primary-color) 4%);
    }

    .auth-shell {
        max-width: 760px;
        margin: 0 auto;
    }

    .auth-layout {
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 1rem;
        align-items: start;
    }

    .auth-feature {
        border: 1px solid var(--surface-border);
        border-radius: 22px;
        padding: 1.2rem;
        background: linear-gradient(180deg, color-mix(in srgb, var(--primary-color), transparent 90%) 0%, var(--surface-bg) 100%);
        box-shadow: 0 18px 45px color-mix(in srgb, black, transparent 92%);
    }

    .feature-list {
        display: grid;
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.8rem 0.9rem;
        border-radius: 16px;
        border: 1px solid var(--surface-border);
        background: color-mix(in srgb, var(--background-color), var(--secondary-background-color) 50%);
    }

    .feature-icon {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 999px;
        display: grid;
        place-items: center;
        background: var(--accent-bg);
        font-size: 1.1rem;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        border: 1px solid var(--surface-border);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        background: var(--surface-bg);
        box-shadow: 0 10px 24px color-mix(in srgb, black, transparent 95%);
    }

    .metric-card .label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.68;
        margin-bottom: 0.35rem;
    }

    .metric-card .value {
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-card .hint {
        margin-top: 0.25rem;
        font-size: 0.88rem;
        opacity: 0.75;
    }

    .translation-card {
        border: 1px solid var(--surface-border);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        background: linear-gradient(180deg, color-mix(in srgb, var(--primary-color), transparent 92%) 0%, var(--surface-bg) 100%);
        box-shadow: 0 10px 24px color-mix(in srgb, black, transparent 95%);
    }

    div.stButton > button {
        border-radius: 14px;
        font-weight: 700;
        padding: 0.7rem 1rem;
        border: 1px solid color-mix(in srgb, var(--primary-color), transparent 30%);
        box-shadow: 0 10px 20px color-mix(in srgb, black, transparent 92%);
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, color-mix(in srgb, var(--background-color), var(--primary-color) 4%) 0%, var(--background-color) 100%);
        border-right: 1px solid var(--surface-border);
    }

    div[data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


auth.init_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "historique" not in st.session_state:
    st.session_state.historique = []


def _logout() -> None:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()


def render_auth_screen() -> None:
    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    left, right = st.columns([1.25, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="hero">
              <div class="badge">🌍 TradLingo • Secure Workspace</div>
              <h1>Traduisez avec une interface plus nette, plus spacieuse et plus fluide.</h1>
              <p>Connectez-vous ou créez un compte pour accéder à votre espace de traduction.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="auth-feature">
              <div class="panel-title">
                <div>
                  <h3>Ce que vous obtenez</h3>
                  <p class="panel-subtitle">Une expérience plus confortable sur desktop et mobile.</p>
                </div>
              </div>
              <div class="feature-list">
                <div class="feature-item"><div class="feature-icon">🔒</div><div><strong>Auth sécurisée</strong><br/>Comptes locaux hachés dans SQLite.</div></div>
                <div class="feature-item"><div class="feature-icon">✨</div><div><strong>UI premium</strong><br/>Cartes, espacements, ombres et dégradés modernisés.</div></div>
                <div class="feature-item"><div class="feature-icon">🚀</div><div><strong>Flux rapide</strong><br/>Login, traduction et historique sans friction.</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

        with login_tab:
            with st.form("login_form"):
                st.markdown('<div class="mini-card">', unsafe_allow_html=True)
                login_username = st.text_input("Nom d'utilisateur", key="login_username")
                login_password = st.text_input("Mot de passe", type="password", key="login_password")
                login_submitted = st.form_submit_button("Se connecter", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if login_submitted:
                try:
                    if auth.authenticate_user(login_username, login_password):
                        st.session_state.authenticated = True
                        st.session_state.username = login_username.strip().lower()
                        st.success("Connexion réussie.")
                        st.rerun()
                    else:
                        st.error("Nom d'utilisateur ou mot de passe incorrect.")
                except ValueError as exc:
                    st.error(exc)

        with signup_tab:
            with st.form("signup_form"):
                st.markdown('<div class="mini-card">', unsafe_allow_html=True)
                signup_username = st.text_input("Nom d'utilisateur", key="signup_username")
                signup_password = st.text_input("Mot de passe", type="password", key="signup_password")
                signup_confirm = st.text_input("Confirmer le mot de passe", type="password", key="signup_confirm")
                signup_submitted = st.form_submit_button("Créer le compte", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if signup_submitted:
                if signup_password != signup_confirm:
                    st.error("Les mots de passe ne correspondent pas.")
                    return

                try:
                    auth.create_user(signup_username, signup_password)
                    st.session_state.authenticated = True
                    st.session_state.username = signup_username.strip().lower()
                    st.success("Compte créé avec succès.")
                    st.rerun()
                except ValueError as exc:
                    st.error(exc)

    st.markdown("</div>", unsafe_allow_html=True)


def render_main_app() -> None:
    st.sidebar.markdown(
        f"""
        <div class="mini-card" style="margin-bottom: 1rem;">
          <div class="badge">✅ Session active</div>
          <h3 style="margin: 0.7rem 0 0.25rem 0;">{st.session_state.username}</h3>
          <div style="opacity: 0.75;">Bienvenue dans votre espace TradLingo.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.button("Logout", use_container_width=True, on_click=_logout)

    st.markdown(
        f"""
        <div class="hero">
          <div class="badge">🌍 TradLingo Workspace</div>
          <h1>Bienvenue, {st.session_state.username}.</h1>
          <p>Traduction FR / EN / AR avec une interface plus premium, plus lisible et plus confortable.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    translations_count = len(st.session_state.historique)
    last_translation = st.session_state.historique[0]["cible"] if st.session_state.historique else "—"
    history_state = "Actif" if st.session_state.historique else "Vide"

    st.markdown(
        f"""
        <div class="metrics-grid">
          <div class="metric-card"><div class="label">Historique</div><div class="value">{translations_count}</div><div class="hint">Traductions de la session</div></div>
          <div class="metric-card"><div class="label">Dernière cible</div><div class="value">{last_translation}</div><div class="hint">Langue récemment utilisée</div></div>
          <div class="metric-card"><div class="label">Statut</div><div class="value">{history_state}</div><div class="hint">Session prête à l'emploi</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    langues = ["fr", "en", "ar"]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col_source, col_cible, col_mode = st.columns([1, 1, 1.05])
    with col_source:
        source = st.selectbox("Langue source", langues, index=0)
    with col_cible:
        cible = st.selectbox("Langue cible", langues, index=1)
    with col_mode:
        auto_detect = st.checkbox("Détection automatique", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

    input_col, preview_col = st.columns([1.2, 0.8], gap="large")
    with input_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-title">
              <div>
                <h3>Votre texte</h3>
                <p class="panel-subtitle">Saisissez du contenu ou importez un fichier pour le traduire.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        texte = st.text_area("Texte à traduire", height=240, placeholder="Entrez votre texte ici...")
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

        translate_clicked = st.button("Traduire maintenant", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with preview_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-title">
              <div>
                <h3>Aperçu</h3>
                <p class="panel-subtitle">Conçu pour garder votre flux de travail propre et lisible.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="translation-card">
              <div class="badge">⚡ Rapid workflow</div>
              <p style="margin: 0.9rem 0 0 0; line-height: 1.6; opacity: 0.85;">
                Une interface plus large, avec des composants mieux espacés pour la lecture,
                l'import de fichiers et l'historique des traductions.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if translate_clicked:
        try:
            source_effective = api_client.detecter_langue(texte) if auto_detect else source
            traduction = api_client.traduire(texte, source_effective, cible)
            st.markdown('<div class="translation-card">', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="panel-title">
                  <div>
                    <h3>Résultat</h3>
                    <p class="panel-subtitle">Traduction générée avec succès.</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(traduction)
            st.markdown("</div>", unsafe_allow_html=True)

            st.session_state.historique.insert(0, {
                "source": source_effective,
                "cible": cible,
                "texte": texte,
                "traduction": traduction,
            })
            st.toast("Traduction ajoutée à l'historique.")
        except api_client.ApiError as exc:
            st.error(exc)

    history_header, history_action = st.columns([3, 1])
    with history_header:
        st.markdown(
            """
            <div class="panel-title">
              <div>
                <h3>Historique de session</h3>
                <p class="panel-subtitle">Retrouvez vos dernières traductions dans un espace plus lisible.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with history_action:
        if st.button("Vider l'historique", use_container_width=True):
            st.session_state.historique = []

    if st.session_state.historique:
        for item in st.session_state.historique:
            st.markdown('<div class="translation-card">', unsafe_allow_html=True)
            row1, row2 = st.columns([1, 1])
            with row1:
                st.markdown(f"<span class='badge'>{item['source']} → {item['cible']}</span>", unsafe_allow_html=True)
            with row2:
                st.caption("Session")
            st.write(item["texte"])
            st.markdown(f"**Résultat :** {item['traduction']}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Aucune traduction pour le moment.")


if st.session_state.authenticated:
    render_main_app()
else:
    render_auth_screen()
