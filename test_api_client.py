from unittest.mock import MagicMock, patch

import pytest

import api_client


def fausse_reponse(json_data, status=200):
    r = MagicMock(status_code=status, text=str(json_data))
    r.json.return_value = json_data
    return r


@pytest.fixture(autouse=True)
def variables_env(monkeypatch):
    monkeypatch.setenv("HF_API_KEY", "hf_test")
    monkeypatch.setenv("HF_API_URL", "https://api-inference.huggingface.co/models")
    monkeypatch.setenv("HF_MODEL_FR_EN", "Helsinki-NLP/opus-mt-fr-en")
    monkeypatch.setenv("HF_MODEL_EN_FR", "Helsinki-NLP/opus-mt-en-fr")
    monkeypatch.setenv("HF_MODEL_EN_AR", "Helsinki-NLP/opus-mt-en-ar")
    monkeypatch.setenv("HF_MODEL_AR_EN", "Helsinki-NLP/opus-mt-ar-en")
    api_client.vider_cache()


def test_quota_depasse_donne_une_erreur_claire():
    with patch("api_client.requests.request", return_value=fausse_reponse({}, 429)):
        with pytest.raises(api_client.ApiError, match="429"):
            api_client.traduire("bonjour", "fr", "en")


def test_traduction_directe_fr_en():
    reponse = [{"translation_text": "hello"}]
    with patch("api_client.requests.request", return_value=fausse_reponse(reponse)) as mock_request:
        resultat = api_client.traduire("bonjour", "fr", "en")
    assert resultat == "hello"
    assert mock_request.call_count == 1


def test_traduction_fr_vers_ar_via_anglais():
    def _side_effect(*_args, **kwargs):
        url = kwargs.get("url") if "url" in kwargs else _args[1]
        if "opus-mt-fr-en" in url:
            return fausse_reponse([{"translation_text": "hello"}])
        if "opus-mt-en-ar" in url:
            return fausse_reponse([{"translation_text": "مرحبا"}])
        return fausse_reponse({}, 400)

    with patch("api_client.requests.request", side_effect=_side_effect) as mock_request:
        resultat = api_client.traduire("bonjour", "fr", "ar")

    assert resultat == "مرحبا"
    assert mock_request.call_count == 2


def test_cache_evite_un_second_appel_api():
    reponse = [{"translation_text": "hello"}]
    with patch("api_client.requests.request", return_value=fausse_reponse(reponse)) as mock_request:
        premier = api_client.traduire("bonjour", "fr", "en")
        second = api_client.traduire("bonjour", "fr", "en")

    assert premier == "hello"
    assert second == "hello"
    assert mock_request.call_count == 1


def test_detection_auto_langue_arabe():
    assert api_client.detecter_langue("مرحبا بكم") == "ar"


def test_long_texte_est_decoupe_en_plusieurs_appels(monkeypatch):
    monkeypatch.setattr(api_client, "MAX_INPUT_CHARS", 20)
    reponse = [{"translation_text": "X"}]
    texte_long = " ".join(f"mot{i}" for i in range(80))

    with patch("api_client.requests.request", return_value=fausse_reponse(reponse)) as mock_request:
        resultat = api_client.traduire(texte_long, "fr", "en")

    assert resultat
    assert mock_request.call_count > 1
