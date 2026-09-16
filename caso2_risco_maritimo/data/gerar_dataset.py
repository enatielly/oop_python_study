"""
Gera um dataset sintético de risco de mar agitado/ressaca, com seed fixa
para ser 100% reprodutível sem depender de download externo. As variáveis
usam os mesmos tipos de grandeza que a Rede de Monitoramento do Caso 1
coleta (vento, temperatura de superfície, pressão), somadas a variáveis
oceanográficas adicionais (altura de onda, amplitude de maré). A relação
com o alvo foi desenhada pra imitar sinais físicos plausíveis (vento forte,
ondas altas e queda de pressão aumentam o risco) -- inclusive o
desbalanceamento natural da classe (mar perigoso é a minoria), igual ao que
se vê na prática de previsão de condições marítimas.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_AMOSTRAS = 2000


def gerar_dataset(n: int = N_AMOSTRAS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    velocidade_vento = rng.gamma(shape=2.0, scale=4.0, size=n)
    altura_onda = rng.gamma(shape=2.0, scale=0.6, size=n) + 0.3
    pressao_atmosferica = rng.normal(1013, 8, size=n).clip(980, 1032)
    temperatura_superficie = rng.normal(24, 3, size=n).clip(15, 32)
    amplitude_mare = rng.gamma(shape=2.0, scale=0.5, size=n) + 0.2
    estacao_do_ano = rng.choice(
        ["verao", "outono", "inverno", "primavera"], size=n, p=[0.25, 0.25, 0.25, 0.25]
    )

    peso_estacao = np.select(
        [estacao_do_ano == "inverno", estacao_do_ano == "outono",
         estacao_do_ano == "primavera", estacao_do_ano == "verao"],
        [0.6, 0.4, 0.0, -0.3],
    )

    logit = (
        -5.7
        + 0.18 * velocidade_vento
        + 1.1 * altura_onda
        - 0.04 * (pressao_atmosferica - 1013)
        + 0.35 * amplitude_mare
        + peso_estacao
        + rng.normal(0, 0.5, size=n)
    )
    probabilidade_perigo = 1 / (1 + np.exp(-logit))
    condicao_perigosa = rng.binomial(1, probabilidade_perigo)

    df = pd.DataFrame(
        {
            "velocidade_vento": velocidade_vento.round(1),
            "altura_onda": altura_onda.round(2),
            "pressao_atmosferica": pressao_atmosferica.round(1),
            "temperatura_superficie": temperatura_superficie.round(1),
            "amplitude_mare": amplitude_mare.round(2),
            "estacao_do_ano": estacao_do_ano,
            "condicao_perigosa": condicao_perigosa,
        }
    )
    return df


if __name__ == "__main__":
    df = gerar_dataset()
    saida = Path(__file__).parent / "condicao_mar_sintetico.csv"
    df.to_csv(saida, index=False)
    print(f"Gerado {saida} com {len(df)} linhas")
    print(df["condicao_perigosa"].value_counts(normalize=True).rename("proporcao"))
