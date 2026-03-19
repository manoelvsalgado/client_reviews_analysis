import os

from openai import OpenAI


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


def _is_online_demo_mode():
    return os.getenv("LLM_MODE", "local").strip().lower() == "online"


def _build_client_and_model():
    if _is_online_demo_mode():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Define OPENAI_API_KEY para usar LLM_MODE=online.")

        base_url = os.getenv("ONLINE_API_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("ONLINE_CHAT_MODEL", "gpt-4o-mini")
        client = OpenAI(base_url=base_url, api_key=api_key)
        return client, model

    base_url = os.getenv("LOCAL_API_BASE_URL", "http://127.0.0.1:1234/v1")
    api_key = os.getenv("LOCAL_API_KEY", "lm-studio")
    model = os.getenv("LOCAL_CHAT_MODEL", "google/gemma-3-4b")
    client = OpenAI(base_url=base_url, api_key=api_key)
    return client, model


client_openai, configured_model = _build_client_and_model()

def parse_review_line_to_json(review_line):
    llm_response = client_openai.chat.completions.create(
        model=configured_model,
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