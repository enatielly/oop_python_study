"""
Núcleo do case: hierarquia de modelos de classificação com POLIMORFISMO.

A ideia central: ComparadorModelos treina e avalia XGBoost, Random Forest e
Regressão Logística com o MESMO código, porque todos implementam a mesma
interface (ModeloClassificacao). Isso é exatamente o que torna fácil trocar
ou adicionar um quarto modelo sem tocar no código de comparação -- o mesmo
princípio por trás do comparador A/B de embeddings que eu uso no meu
trabalho de pesquisa (lá, comparo modelos de embedding; aqui, modelos de
classificação -- mesma ideia de design).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from xgboost import XGBClassifier


@dataclass
class ResultadoAvaliacao:
    """@dataclass: value object simples para carregar as métricas de um modelo."""

    nome_modelo: str
    acuracia: float
    precisao: float
    recall: float
    f1: float
    roc_auc: float

    def __str__(self) -> str:
        return (
            f"{self.nome_modelo:<22} "
            f"acc={self.acuracia:.3f}  "
            f"precisao={self.precisao:.3f}  "
            f"recall={self.recall:.3f}  "
            f"f1={self.f1:.3f}  "
            f"roc_auc={self.roc_auc:.3f}"
        )


class ModeloClassificacao(ABC):
    """
    ABSTRAÇÃO: define O CONTRATO que todo modelo precisa cumprir
    (treinar/prever/prever_proba), sem se importar com qual biblioteca
    cada subclasse usa por baixo.
    """

    def __init__(self, nome: str) -> None:
        self.nome = nome
        # ENCAPSULAMENTO: o estimador real fica "protegido" -- quem usa a
        # classe interage só com treinar()/prever(), nunca com o objeto
        # sklearn/xgboost por dentro.
        self._estimador = None

    @abstractmethod
    def treinar(self, X_treino, y_treino) -> None:
        raise NotImplementedError

    @abstractmethod
    def prever(self, X):
        raise NotImplementedError

    @abstractmethod
    def prever_proba(self, X):
        raise NotImplementedError

    def avaliar(self, X_teste, y_teste) -> ResultadoAvaliacao:
        """
        Método concreto, herdado por TODAS as subclasses -- e que funciona
        para qualquer uma delas graças ao polimorfismo de prever()/prever_proba().
        """
        y_pred = self.prever(X_teste)
        y_proba = self.prever_proba(X_teste)
        return ResultadoAvaliacao(
            nome_modelo=self.nome,
            acuracia=accuracy_score(y_teste, y_pred),
            precisao=precision_score(y_teste, y_pred, zero_division=0),
            recall=recall_score(y_teste, y_pred, zero_division=0),
            f1=f1_score(y_teste, y_pred, zero_division=0),
            roc_auc=roc_auc_score(y_teste, y_proba),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nome={self.nome!r})"


class ModeloXGBoost(ModeloClassificacao):
    """
    Usa scale_pos_weight para lidar com o desbalanceamento da classe
    (dias de mar perigoso são raros) -- a mesma técnica que vale mencionar
    em entrevista quando perguntarem "o que fazer com variável desbalanceada".
    """

    def __init__(self, nome: str = "XGBoost", **kwargs) -> None:
        super().__init__(nome)
        self._kwargs = kwargs

    def treinar(self, X_treino, y_treino) -> None:
        proporcao_negativa_positiva = (y_treino == 0).sum() / max((y_treino == 1).sum(), 1)
        self._estimador = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.08,
            eval_metric="logloss",
            scale_pos_weight=proporcao_negativa_positiva,
            random_state=42,
            **self._kwargs,
        )
        self._estimador.fit(X_treino, y_treino)

    def prever(self, X):
        return self._estimador.predict(X)

    def prever_proba(self, X):
        return self._estimador.predict_proba(X)[:, 1]


class ModeloRandomForest(ModeloClassificacao):
    def __init__(self, nome: str = "Random Forest", **kwargs) -> None:
        super().__init__(nome)
        self._kwargs = kwargs

    def treinar(self, X_treino, y_treino) -> None:
        self._estimador = RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            class_weight="balanced",
            random_state=42,
            **self._kwargs,
        )
        self._estimador.fit(X_treino, y_treino)

    def prever(self, X):
        return self._estimador.predict(X)

    def prever_proba(self, X):
        return self._estimador.predict_proba(X)[:, 1]


class ModeloRegressaoLogistica(ModeloClassificacao):
    """Modelo simples, usado aqui como baseline interpretável."""

    def __init__(self, nome: str = "Regressão Logística", **kwargs) -> None:
        super().__init__(nome)
        self._kwargs = kwargs

    def treinar(self, X_treino, y_treino) -> None:
        self._estimador = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
            **self._kwargs,
        )
        self._estimador.fit(X_treino, y_treino)

    def prever(self, X):
        return self._estimador.predict(X)

    def prever_proba(self, X):
        return self._estimador.predict_proba(X)[:, 1]


class ComparadorModelos:
    """
    Recebe uma LISTA de ModeloClassificacao -- não importa quais nem quantos
    -- treina e avalia todos com o mesmo laço, e devolve uma tabela ordenada.
    Adicionar um quarto modelo (ex.: LightGBM) não muda uma linha desta classe.
    """

    def __init__(self, modelos: list[ModeloClassificacao]) -> None:
        self._modelos = modelos

    def rodar(self, X_treino, y_treino, X_teste, y_teste, ordenar_por: str = "roc_auc") -> pd.DataFrame:
        resultados: list[ResultadoAvaliacao] = []
        for modelo in self._modelos:
            modelo.treinar(X_treino, y_treino)
            resultados.append(modelo.avaliar(X_teste, y_teste))

        df = pd.DataFrame([r.__dict__ for r in resultados])
        return df.sort_values(ordenar_por, ascending=False).reset_index(drop=True)
