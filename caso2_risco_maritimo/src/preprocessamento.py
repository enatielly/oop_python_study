"""Pré-processamento -- exemplo de COMPOSIÇÃO ("tem um") em vez de herança."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class PreProcessador:
    """
    COMPOSIÇÃO: PreProcessador não HERDA de ColumnTransformer -- ele TEM UM
    ColumnTransformer por dentro (self._transformador) e expõe uma interface
    própria, mais simples (.ajustar_transformar / .transformar). Isso é
    deliberado: "favoreça composição em vez de herança" quando a relação não
    é genuinamente um "é-um", e sim um "usa um".
    """

    def __init__(self) -> None:
        self._transformador: ColumnTransformer | None = None
        self._ajustado = False

    @staticmethod
    def _construir_transformador(X: pd.DataFrame) -> ColumnTransformer:
        colunas_categoricas = X.select_dtypes(include=["object", "string"]).columns.tolist()
        colunas_numericas = X.select_dtypes(exclude=["object", "string"]).columns.tolist()
        return ColumnTransformer(
            transformers=[
                ("categorica", OneHotEncoder(handle_unknown="ignore"), colunas_categoricas),
                ("numerica", StandardScaler(), colunas_numericas),
            ]
        )

    def ajustar_transformar(self, X: pd.DataFrame):
        self._transformador = self._construir_transformador(X)
        X_transformado = self._transformador.fit_transform(X)
        self._ajustado = True
        return X_transformado

    def transformar(self, X: pd.DataFrame):
        # ENCAPSULAMENTO: impede o erro clássico de chamar transformar()
        # antes de ajustar_transformar() (vazamento de dados de teste).
        if not self._ajustado or self._transformador is None:
            raise RuntimeError("Chame ajustar_transformar() no conjunto de treino antes de transformar().")
        return self._transformador.transform(X)
