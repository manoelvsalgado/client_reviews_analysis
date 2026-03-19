from urllib.request import Request, urlopen

import pandas as pd


URL_ARQUIVO = "https://cdn3.gnarususercontent.com.br/4790-python/Resenhas_App_ChatGPT.txt"


def carregar_linhas_do_arquivo(url: str) -> list[str]:
    """Baixa um arquivo .txt de uma URL e retorna suas linhas em uma lista."""
    requisicao = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(requisicao) as resposta:
        conteudo = resposta.read().decode("utf-8")

    # O pandas facilita manipulação posterior das linhas antes de enviar ao LLM.
    df_resenhas = pd.DataFrame({"linha": conteudo.splitlines()})
    return df_resenhas["linha"].tolist()


if __name__ == "__main__":
    linhas = carregar_linhas_do_arquivo(URL_ARQUIVO)

    print(f"Total de linhas carregadas: {len(linhas)}")
    print("Primeiras 2 linhas da lista:")
    print(f"[0] {linhas[0]}")
    print(f"[1] {linhas[1]}")