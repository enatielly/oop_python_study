"""
Caso 2 - POO aplicada a um problema de classificação (risco de crédito)
=========================================================================

Executa o pipeline completo: carrega dados -> pré-processa -> treina e
compara 3 modelos (XGBoost, Random Forest, Regressão Logística) através da
mesma interface polimórfica -> imprime a tabela comparativa.

Rode com: python src/pipeline.py  (a partir da pasta caso2_classificacao_credito)
"""

from __future__ import annotations

from sklearn.model_selection import train_test_split

from dados import CarregadorDados
from modelos import ComparadorModelos, ModeloRandomForest, ModeloRegressaoLogistica, ModeloXGBoost
from preprocessamento import PreProcessador


def executar_pipeline() -> None:
    X, y = CarregadorDados.dataset_padrao().carregar()

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    preprocessador = PreProcessador()
    X_treino_proc = preprocessador.ajustar_transformar(X_treino)
    X_teste_proc = preprocessador.transformar(X_teste)

    modelos = [
        ModeloXGBoost(),
        ModeloRandomForest(),
        ModeloRegressaoLogistica(),
    ]

    comparador = ComparadorModelos(modelos)
    tabela = comparador.rodar(X_treino_proc, y_treino, X_teste_proc, y_teste)

    print(f"Treino: {X_treino.shape[0]} amostras | Teste: {X_teste.shape[0]} amostras")
    print(f"Proporção de inadimplentes no treino: {y_treino.mean():.1%}\n")
    print(tabela.to_string(index=False))


if __name__ == "__main__":
    executar_pipeline()
