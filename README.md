# Équipe 10 — TradLingo

Application minimaliste de traduction pour documents administratifs (FR / EN / AR).
API utilisée : **Hugging Face Inference Providers** avec modèles Helsinki-NLP.
Authentification locale sécurisée avec SQLite + hachage PBKDF2-SHA256.

## Démarrer

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux / macOS : source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Linux / macOS : cp .env.example .env
# ouvrez .env et collez votre clé HF_API_KEY=hf_...
pytest                           # les tests utilisent des mocks : ils passent sans clé
streamlit run app.py
```

## Authentification

- Connexion et inscription via l'écran d'accueil Streamlit.
- Les comptes sont stockés dans une base SQLite locale `users.db`.
- Les mots de passe sont hachés avec un sel unique avant stockage.
- Le bouton `Logout` est disponible dans la barre latérale après connexion.

## Contenu

| Fichier | Rôle |
|---|---|
| `api_client.py` | Traduction Hugging Face, passage FR↔AR via EN, cache en mémoire. |
| `app.py` | Interface Streamlit avec authentification, langues, texte/fichier `.txt`, historique de session. |
| `auth.py` | Création de comptes, connexion et hachage sécurisé des mots de passe. |
| `test_api_client.py` | Tests pytest avec mocks (traduction directe, en 2 étapes, cache). |
| `test_auth.py` | Tests pytest de la création de compte et de l'authentification. |
| `.env.example` | Modèle du fichier `.env`. **Ne versionnez jamais `.env`.** |

## Variables `.env`

- `HF_API_KEY` : token Hugging Face (`hf_...`)
- `HF_API_URL` : base URL de l'inférence (par défaut `https://api-inference.huggingface.co/models`)
- `HF_MODEL_FR_EN`, `HF_MODEL_EN_FR`, `HF_MODEL_EN_AR`, `HF_MODEL_AR_EN`

> Aucun package supplémentaire n'est requis pour l'authentification : la solution utilise uniquement la bibliothèque standard Python.

Si un modèle change de nom, modifiez-le dans `.env` sans toucher au code.
