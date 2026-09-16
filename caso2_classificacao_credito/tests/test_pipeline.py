import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from modelos import ComparadorModelos, ModeloClassificacao, ModeloRandomForest, ModeloRegressaoLogistica, ModeloXGBoost
from preprocessamento import PreProcessador


@pytest.fixture(scope="module")
def dataset_pequeno():
    rng = np.random.default_rng(0)
    n = 300
    X = pd.DataFrame(
        {
            "idade": rng.integers(18, 70, n),
            "renda_mensal": rng.gamma(4, 800, n),
            "historico_credito": rng.choice(["bom", "regular", "ruim"], n),
        }
    )
    y = pd.Series(rng.choice([0, 1], n, p=[0.8, 0.2]), name="inadimplente")
    return train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)


def test_preprocessador_exige_ajuste_antes_de_transformar():
    pre = PreProcessador()
    with pytest.raises(RuntimeError):
        pre.transformar(pd.DataFrame({"a": [1, 2]}))


def test_preprocessador_ajusta_e_transforma(dataset_pequeno):
    X_treino, X_teste, _, _ = dataset_pequeno
    pre = PreProcessador()
    X_treino_proc = pre.ajustar_transformar(X_treino)
    X_teste_proc = pre.transformar(X_teste)
    assert X_treino_proc.shape[0] == len(X_treino)
    assert X_teste_proc.shape[0] == len(X_teste)
    assert X_treino_proc.shape[1] == X_teste_proc.shape[1]


def test_nao_pode_instanciar_modelo_abstrato_diretamente():
    with pytest.raises(TypeError):
        ModeloClassificacao("X")  # type: ignore[abstract]


@pytest.mark.parametrize("Modelo", [ModeloXGBoost, ModeloRandomForest, ModeloRegressaoLogistica])
def test_cada_modelo_treina_e_avalia(dataset_pequeno, Modelo):
    X_treino, X_teste, y_treino, y_teste = dataset_pequeno
    pre = PreProcessador()
    X_treino_proc = pre.ajustar_transformar(X_treino)
    X_teste_proc = pre.transformar(X_teste)

    modelo = Modelo()
    modelo.treinar(X_treino_proc, y_treino)
    resultado = modelo.avaliar(X_teste_proc, y_teste)

    assert 0.0 <= resultado.acuracia <= 1.0
    assert 0.0 <= resultado.roc_auc <= 1.0


def test_comparador_modelos_funciona_polimorficamente(dataset_pequeno):
    """
    O teste mais importante do case: ComparadorModelos não sabe (nem
    precisa saber) que por baixo tem XGBoost, sklearn RandomForest e
    LogisticRegression -- três bibliotecas diferentes, uma interface só.
    """
    X_treino, X_teste, y_treino, y_teste = dataset_pequeno
    pre = PreProcessador()
    X_treino_proc = pre.ajustar_transformar(X_treino)
    X_teste_proc = pre.transformar(X_teste)

    comparador = ComparadorModelos([ModeloXGBoost(), ModeloRandomForest(), ModeloRegressaoLogistica()])
    tabela = comparador.rodar(X_treino_proc, y_treino, X_teste_proc, y_teste)

    assert len(tabela) == 3
    assert list(tabela.columns) == ["nome_modelo", "acuracia", "precisao", "recall", "f1", "roc_auc"]
    # a tabela deve estar ordenada por roc_auc decrescente
    assert tabela["roc_auc"].is_monotonic_decreasing
