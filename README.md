# Équipe 10 — TradLingo

Application minimaliste de traduction pour documents administratifs (FR / EN / AR).
API utilisée : **Hugging Face Inference Providers** avec modèles Helsinki-NLP.

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

## Contenu

| Fichier | Rôle |
|---|---|
| `api_client.py` | Traduction Hugging Face, passage FR↔AR via EN, cache en mémoire. |
| `app.py` | Interface Streamlit minimale : langues, texte/fichier `.txt`, historique de session. |
| `test_api_client.py` | Tests pytest avec mocks (traduction directe, en 2 étapes, cache). |
| `.env.example` | Modèle du fichier `.env`. **Ne versionnez jamais `.env`.** |

## Variables `.env`

- `HF_API_KEY` : token Hugging Face (`hf_...`)
- `HF_API_URL` : base URL de l'inférence (par défaut `https://api-inference.huggingface.co/models`)
- `HF_MODEL_FR_EN`, `HF_MODEL_EN_FR`, `HF_MODEL_EN_AR`, `HF_MODEL_AR_EN`

Si un modèle change de nom, modifiez-le dans `.env` sans toucher au code.
