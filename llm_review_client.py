import os
import json
from pathlib import Path

try:
    from openai import OpenAI
except ModuleNotFoundError:
    OpenAI = None


SYSTEM_PROMPT = """Você é um especialista em análise de dados e conversão de dados para JSON.
Você receberá uma linha de texto que é uma resenha de um aplicativo em um marketplace online.
Eu quero que você analise essa resenha, e me retorne um JSON com as seguintes chaves:
- 'usuario': o nome do usuário que fez a resenha
- 'resenha_original': a resenha no idioma original que você recebeu
- 'resenha_pt': a resenha traduzida para o português, deve estar sempre na língua portuguesa
- 'avaliacao': uma avaliação se essa resenha foi 'Positiva', 'Negativa' ou 'Neutra' (apenas uma dessas opções)

Exemplo de entrada:
'879485937$Pedro Silva$This is a positive review for the app'
Exemplo de saída:
{
    "usuario": "Pedro Silva",
    "resenha_original": "This is a positive review for the app",
    "resenha_pt": "Esta é uma resenha positiva para o aplicativo",
    "avaliacao": "Positiva"
}

Exemplo de entrada:
'74398793$John Myers$Je n'aime pas cette application'
Exemplo de saída:
{
    "usuario": "John Myers",
    "resenha_original": "Je n'aime pas cette application",
    "resenha_pt": "Eu não gosto dessa aplicação",
    "avaliacao": "Negativa"
}

Regra importante: você deve retornar apenas o JSON, sem nenhum outro texto além do JSON.
"""


def load_local_env_file(env_file: str = ".env"):
    env_path = Path(env_file)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_local_env_file()

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY", "lm-studio")
GEMMA_BASE_URL = os.getenv("GEMMA_BASE_URL")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "google/gemma-3-4b")
DEMO_MODE = os.getenv("DEMO_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}
DEMO_MODE_FALLBACK = os.getenv("DEMO_MODE_FALLBACK", "true").strip().lower() in {"1", "true", "yes", "on"}

client_openai = None
if not DEMO_MODE:
    if OpenAI is None:
        raise ModuleNotFoundError(
            "Pacote 'openai' nao encontrado. Instale com 'pip install openai' "
            "ou ative DEMO_MODE=true no arquivo .env."
        )
    if not GEMMA_BASE_URL:
        raise ValueError("Define GEMMA_BASE_URL para usar o modo online com Gemma.")
    client_openai = OpenAI(base_url=GEMMA_BASE_URL, api_key=GEMMA_API_KEY)


def extract_review_fields(review_line):
    parts = review_line.split("$", 2)
    if len(parts) == 3:
        _, user_name, review_text = parts
        return user_name.strip() or "Usuario", review_text.strip()

    return "Usuario", review_line.strip()


def classify_sentiment_demo(review_text):
    text = review_text.lower()

    positive_words = [
        "good", "great", "excellent", "awesome", "love", "liked", "amazing", "best",
        "bom", "boa", "otimo", "ótimo", "excelente", "amei", "recomendo",
    ]
    negative_words = [
        "bad", "terrible", "awful", "hate", "worst", "bug", "broken", "slow", "crash",
        "ruim", "pessimo", "péssimo", "odiei", "horrivel", "horrível", "travando", "erro",
    ]

    positive_score = sum(1 for word in positive_words if word in text)
    negative_score = sum(1 for word in negative_words if word in text)

    if positive_score > negative_score:
        return "Positiva"
    if negative_score > positive_score:
        return "Negativa"
    return "Neutra"


def build_demo_json_response(review_line):
    user_name, review_text = extract_review_fields(review_line)
    payload = {
        "usuario": user_name,
        "resenha_original": review_text,
        "resenha_pt": review_text,
        "avaliacao": classify_sentiment_demo(review_text),
    }
    return json.dumps(payload, ensure_ascii=False)


def get_runtime_mode_label():
    if DEMO_MODE:
        return "DEMO_MODE (analise local)"
    return f"LLM online ({GEMMA_MODEL})"

def parse_review_line_to_json(review_line):
    if DEMO_MODE:
        demo_response = build_demo_json_response(review_line)
        print(demo_response)
        return demo_response

    try:
        llm_response = client_openai.chat.completions.create(
            model=GEMMA_MODEL,
            messages=[
                {"role":"system",
                "content": SYSTEM_PROMPT},

                {"role":"user",
                "content": f"Resenha: {review_line}"}
            ],
            temperature=0.0
        )

        response_content = llm_response.choices[0].message.content or ""
        cleaned_response = response_content.replace("```json", "").replace("```", "").strip()
        print(cleaned_response)
        return cleaned_response
    except Exception as exc:
        if not DEMO_MODE_FALLBACK:
            raise

        print(f"[WARN] Falha no LLM online ({exc}). Usando DEMO_MODE fallback.")
        demo_response = build_demo_json_response(review_line)
        print(demo_response)
        return demo_response