"""
Gera um dataset sintético de risco de crédito, com seed fixa para ser
100% reprodutível sem depender de download externo (dataset público real
como o German Credit exige acesso a UCI/OpenML, que nem sempre está
disponível). As variáveis e a relação com o alvo foram desenhadas pra
imitar um cenário real de concessão de crédito -- inclusive o desbalanceamento
natural da classe (poucos inadimplentes), igual ao que se vê na prática.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_AMOSTRAS = 2000


def gerar_dataset(n: int = N_AMOSTRAS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    idade = rng.integers(18, 71, n)
    renda_mensal = rng.gamma(shape=4.0, scale=800, size=n) + 1200
    valor_solicitado = rng.gamma(shape=2.5, scale=2500, size=n) + 500
    duracao_meses = rng.choice([6, 12, 18, 24, 36, 48, 60], size=n)
    tempo_emprego_anos = rng.gamma(shape=2.0, scale=2.5, size=n)
    historico_credito = rng.choice(["bom", "regular", "ruim"], size=n, p=[0.5, 0.35, 0.15])
    finalidade = rng.choice(["veiculo", "imovel", "educacao", "outros"], size=n, p=[0.3, 0.25, 0.2, 0.25])
    possui_imovel_proprio = rng.choice([0, 1], size=n, p=[0.55, 0.45])
    num_dependentes = rng.poisson(1.1, size=n)
    score_externo = rng.normal(650, 90, size=n).clip(300, 850)

    comprometimento_renda = valor_solicitado / (renda_mensal * duracao_meses / 6 + 1)

    peso_historico = np.select(
        [historico_credito == "bom", historico_credito == "regular", historico_credito == "ruim"],
        [-1.2, 0.0, 1.4],
    )

    logit = (
        -2.4
        + 1.8 * comprometimento_renda
        + peso_historico
        - 0.015 * (score_externo - 650) / 10
        - 0.05 * tempo_emprego_anos
        + 0.10 * num_dependentes
        - 0.35 * possui_imovel_proprio
        + rng.normal(0, 0.6, size=n)
    )
    probabilidade_inadimplencia = 1 / (1 + np.exp(-logit))
    inadimplente = rng.binomial(1, probabilidade_inadimplencia)

    df = pd.DataFrame(
        {
            "idade": idade,
            "renda_mensal": renda_mensal.round(2),
            "valor_solicitado": valor_solicitado.round(2),
            "duracao_meses": duracao_meses,
            "tempo_emprego_anos": tempo_emprego_anos.round(1),
            "historico_credito": historico_credito,
            "finalidade": finalidade,
            "possui_imovel_proprio": possui_imovel_proprio,
            "num_dependentes": num_dependentes,
            "score_externo": score_externo.round(0),
            "inadimplente": inadimplente,
        }
    )
    return df


if __name__ == "__main__":
    df = gerar_dataset()
    saida = Path(__file__).parent / "credito_sintetico.csv"
    df.to_csv(saida, index=False)
    print(f"Gerado {saida} com {len(df)} linhas")
    print(df["inadimplente"].value_counts(normalize=True).rename("proporcao"))
