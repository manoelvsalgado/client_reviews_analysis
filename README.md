# Client Reviews Analysis

Aplicação em Python + Streamlit para analisar avaliações de aplicativos, identificar idioma, traduzir para português, classificar sentimento e gerar uma síntese geral das reviews.

## Funcionalidades

- Upload de arquivo `.txt` com reviews no formato `ID$Usuario$Texto`
- Identificação do idioma da review
- Tradução da review para português
- Classificação de sentimento: `Positiva`, `Negativa` ou `Neutra`
- Síntese geral das avaliações com sentimento predominante
- Gráficos de pizza por sentimento e por idioma
- Filtro por sentimento e por idioma
- Fallback local automático quando o provedor online falha ou a cota é atingida

## Estrutura do projeto

- `app.py`: interface Streamlit
- `llm_review_client.py`: integração com LLM e fallback local
- `review_analysis_pipeline.py`: pipeline de leitura e agregação das reviews
- `app_reviews.txt`: arquivo de exemplo
- `requirements.txt`: dependências

## Requisitos

- Python 3.12+
- Ambiente virtual recomendado

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Crie ou ajuste o arquivo `.env`.

Exemplo usando Groq:

```env
GROQ_API_KEY=sua_chave_groq
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant
DEMO_MODE=false
DEMO_MODE_FALLBACK=true
```

### Significado das variáveis

- `GROQ_API_KEY`: chave da API do Groq
- `GROQ_BASE_URL`: endpoint OpenAI-compatible do Groq
- `GROQ_MODEL`: modelo usado na análise
- `DEMO_MODE=true`: força o uso do fallback local
- `DEMO_MODE_FALLBACK=true`: usa fallback local quando o provedor online falha

## Como executar

### Interface web

Use o Streamlit:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

Importante: não execute `python app.py`. O arquivo deve ser iniciado com `streamlit run`.

### Pipeline no terminal

```bash
source .venv/bin/activate
python review_analysis_pipeline.py
```

## Formato do arquivo de entrada

Cada linha do arquivo deve seguir este formato:

```text
879485937$Pedro Silva$This is a positive review for the app
74398793$John Myers$Je n'aime pas cette application
```

## Como o sistema funciona

### Modo online

Quando `DEMO_MODE=false` e o provedor está configurado corretamente, o sistema usa o LLM online para:

- detectar idioma
- traduzir para português
- classificar sentimento
- gerar síntese geral

### Fallback local

Quando o provedor online falha, a aplicação cai automaticamente para o modo local se `DEMO_MODE_FALLBACK=true`.

Nesse modo:

- a aplicação continua funcionando
- a tradução pode não ser ideal
- a classificação de sentimento pode ser menos precisa
- a interface mostra um aviso quando houve fallback

## Aviso sobre cota

Se a cota do provedor online for atingida, a aplicação mostra um aviso na interface informando que parte dos resultados pode não refletir o resultado ideal.

## Deploy

### Streamlit Community Cloud

1. Suba o repositório para o GitHub
2. Conecte o repositório no Streamlit Cloud
3. Defina `app.py` como arquivo principal
4. Adicione as variáveis de ambiente em `Secrets`

Exemplo de secrets:

```toml
GROQ_API_KEY = "sua_chave_groq"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.1-8b-instant"
DEMO_MODE = "false"
DEMO_MODE_FALLBACK = "true"
```

## Observações

- O arquivo `.env` está no `.gitignore` e não deve ser commitado
- Se quiser uma demo estável sem depender de API, use `DEMO_MODE=true`
- Para melhor qualidade de tradução e sentimento, use um provedor online com cota disponível