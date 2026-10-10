import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

TIMEOUT_S = 30
DEFAULT_HF_API_URL = "https://api-inference.huggingface.co/models"
MAX_INPUT_CHARS = int(os.getenv("HF_MAX_INPUT_CHARS", "900"))

CACHE = {}


class ApiError(Exception):
    pass


def cle(nom):
    valeur = os.getenv(nom)
    if not valeur:
        raise ApiError(f"{nom} manquante : ajoutez-la dans le fichier .env.")
    return valeur


def requete(methode, url, **kwargs):
    try:
        reponse = requests.request(methode, url, timeout=TIMEOUT_S, **kwargs)
    except requests.RequestException as exc:
        raise ApiError(f"Réseau indisponible ou délai dépassé : {exc}") from exc
    if reponse.status_code in (401, 403):
        detail = reponse.text[:250]
        raise ApiError(f"Clé API invalide, absente ou non autorisée (401/403). Détail: {detail}")
    if reponse.status_code == 429:
        raise ApiError("Quota gratuit dépassé (429) : réessayez plus tard ou utilisez le cache.")
    if reponse.status_code >= 400:
        raise ApiError(f"Erreur {reponse.status_code} : {reponse.text[:200]}")
    return reponse


def _normaliser_langue(langue):
    mapping = {
        "fr": "fr",
        "français": "fr",
        "francais": "fr",
        "french": "fr",
        "en": "en",
        "anglais": "en",
        "english": "en",
        "ar": "ar",
        "arabe": "ar",
        "arabic": "ar",
    }
    code = mapping.get((langue or "").strip().lower())
    if not code:
        raise ApiError(f"Langue non supportée : {langue}")
    return code


def _modele(source, cible):
    if source == "fr" and cible == "en":
        return os.getenv("HF_MODEL_FR_EN", "Helsinki-NLP/opus-mt-fr-en")
    if source == "en" and cible == "fr":
        return os.getenv("HF_MODEL_EN_FR", "Helsinki-NLP/opus-mt-en-fr")
    if source == "en" and cible == "ar":
        return os.getenv("HF_MODEL_EN_AR", "Helsinki-NLP/opus-mt-en-ar")
    if source == "ar" and cible == "en":
        return os.getenv("HF_MODEL_AR_EN", "Helsinki-NLP/opus-mt-ar-en")
    raise ApiError(f"Paire non supportée directement : {source} -> {cible}")


def _appel_modele(modele, texte):
    base_url = os.getenv("HF_API_URL", DEFAULT_HF_API_URL).rstrip("/")
    if base_url.endswith("/models"):
        url = f"{base_url}/{modele}"
    else:
        url = base_url

    data = requete(
        "POST",
        url,
        headers={"Authorization": f"Bearer {cle('HF_API_KEY')}"},
        json={"inputs": texte},
    ).json()

    if isinstance(data, dict) and data.get("error"):
        raise ApiError(f"Erreur Hugging Face : {data['error']}")

    if isinstance(data, list) and data and isinstance(data[0], dict):
        traduction = data[0].get("translation_text")
        if traduction:
            return traduction

    raise ApiError("Réponse Hugging Face inattendue.")


def detecter_langue(texte):
    texte_min = (texte or "").lower()
    if not texte_min.strip():
        raise ApiError("Le texte à traduire est vide.")
    if any("\u0600" <= caractere <= "\u06ff" for caractere in texte_min):
        return "ar"
    if any(mot in texte_min for mot in (" the ", " and ", " is ", " are ", " of ", " to ")):
        return "en"
    return "fr"


def _decouper_texte(texte, taille_max=None):
    if taille_max is None:
        taille_max = MAX_INPUT_CHARS
    if len(texte) <= taille_max:
        return [texte]

    morceaux = []
    courant = ""
    tokens = re.findall(r"\S+\s*", texte)

    for token in tokens:
        if len(token) > taille_max:
            if courant:
                morceaux.append(courant)
                courant = ""
            for index in range(0, len(token), taille_max):
                morceaux.append(token[index:index + taille_max])
            continue

        if len(courant) + len(token) > taille_max:
            morceaux.append(courant)
            courant = token
        else:
            courant += token

    if courant:
        morceaux.append(courant)

    return morceaux


def traduire(texte, langue_source, langue_cible):
    source = _normaliser_langue(langue_source)
    cible = _normaliser_langue(langue_cible)
    texte_normalise = (texte or "").strip()
    if not texte_normalise:
        raise ApiError("Le texte à traduire est vide.")
    if source == cible:
        return texte_normalise

    cle_cache = (source, cible, texte_normalise)
    if cle_cache in CACHE:
        return CACHE[cle_cache]

    segments = _decouper_texte(texte_normalise)
    if len(segments) > 1:
        resultat = "".join(traduire(segment, source, cible) for segment in segments)
        CACHE[cle_cache] = resultat
        return resultat

    if (source, cible) in (("fr", "ar"), ("ar", "fr")):
        intermediaire = traduire(texte_normalise, source, "en")
        resultat = traduire(intermediaire, "en", cible)
    else:
        modele = _modele(source, cible)
        resultat = _appel_modele(modele, texte_normalise)

    CACHE[cle_cache] = resultat
    return resultat


def vider_cache():
    CACHE.clear()
