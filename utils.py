#utils.py
import math
from scipy.spatial import distance as sp_distance
from entidades import Aluno, Monitor
import random
import numpy as np


def calcular_limite_distancia(aluno, escola_x, escola_y, delta_factor):
    distancia_escola = sp_distance.euclidean((aluno.x, aluno.y), (escola_x, escola_y))
    
    if distancia_escola <= 5:
        delta_factor = 2.0  # Alunos próximos à escola
    elif 5 < distancia_escola <= 10:
        delta_factor = 1.7  # Alunos em distância intermediária
    else:
        delta_factor = 1.4  # Alunos mais distantes da escola
    
    
    return delta_factor * distancia_escola


def calcular_distancia(aluno1, aluno2):
    
    return sp_distance.euclidean((aluno1.x, aluno1.y), (aluno2.x, aluno2.y))


def calcular_distancia_maxima(rota):
    if not rota:
        return 0
    
    for aluno in rota:
        print(f"Aluno: {aluno.id}, Posição: ({aluno.x}, {aluno.y}), Distância percorrida: {aluno.distancia_percorrida}")

    return max(aluno.distancia_percorrida for aluno in rota)

def calcular_custo_total(monitores, peso_distancia=1, peso_monitores=1, peso_desvio=0.5):
    custo_total = 0
    distancias = [calcular_distancia_maxima(monitor.rota) for monitor in monitores]
    max_distancia = max(distancias) if distancias else 0
    desvio_padrao = np.std(distancias) if distancias else 0

    custo_total += peso_distancia * max_distancia
    custo_total += peso_monitores * len(monitores)
    custo_total += peso_desvio * desvio_padrao
    
    return custo_total

def otimizar_rota(rota):
    def calcula_custo(rota):
        custo = 0
        for i in range(len(rota) - 1):
            custo += calcular_distancia(rota[i], rota[i + 1])
        return custo

    def dois_opt(rota):
        melhor_rota = rota
        melhor_custo = calcula_custo(melhor_rota)
        for _ in range(100):
            for i in range(1, len(melhor_rota) - 1):
                for j in range(i + 1, len(melhor_rota)):
                    nova_rota = melhor_rota[:i] + melhor_rota[i:j][::-1] + melhor_rota[j:]
                    novo_custo = calcula_custo(nova_rota)
                    if novo_custo < melhor_custo:
                        melhor_rota = nova_rota
                        melhor_custo = novo_custo
            if melhor_custo == calcula_custo(melhor_rota):
                break
        return melhor_rota

    return dois_opt(rota)


def perturbar_solucao(lista_monitores):
    print("Perturbando solução atual...")
    monitor = random.choice(lista_monitores)
    aluno_removido = random.choice(monitor.rota)
    monitor.rota.remove(aluno_removido)
    outro_monitor = random.choice([m for m in lista_monitores if m != monitor])
    outro_monitor.rota.append(aluno_removido)
