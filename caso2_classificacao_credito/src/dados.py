"""Carregamento de dados -- responsabilidade única e isolada do resto do pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

COLUNA_ALVO = "inadimplente"


class CarregadorDados:
    """
    ENCAPSULAMENTO: concentra numa única classe a lógica de "de onde vêm os
    dados e como separá-los em X/y". O resto do pipeline não precisa saber
    que existe um arquivo CSV -- só chama .carregar().
    """

    def __init__(self, caminho_csv: str | Path) -> None:
        self._caminho_csv = Path(caminho_csv)

    def carregar(self) -> tuple[pd.DataFrame, pd.Series]:
        if not self._caminho_csv.exists():
            raise FileNotFoundError(
                f"{self._caminho_csv} não encontrado. Rode `python data/gerar_dataset.py` primeiro."
            )
        df = pd.read_csv(self._caminho_csv)
        X = df.drop(columns=[COLUNA_ALVO])
        y = df[COLUNA_ALVO]
        return X, y

    @classmethod
    def dataset_padrao(cls) -> "CarregadorDados":
        """@classmethod: construtor alternativo apontando pro CSV padrão do
        projeto, sem quem chama precisar saber o caminho de cor."""
        caminho_padrao = Path(__file__).resolve().parents[1] / "data" / "credito_sintetico.csv"
        return cls(caminho_padrao)
