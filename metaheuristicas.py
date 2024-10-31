from entidades import Aluno, Monitor
from utils import calcular_distancia, calcular_limite_distancia, calcular_custo_total, calcular_distancia_maxima
import random
import numpy as np
from copy import deepcopy
import time


# Ajuste na construção do GRASP com um alpha mais flexível
def grasp_construir_solucao(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor, alpha=0.7):
    monitores = []
    alunos_atendidos = set()  # Estrutura para armazenar IDs de alunos já atendidos

    while len(alunos_atendidos) < len(alunos):
        novo_monitor = Monitor(capacidade_monitor, distancia_maxima_monitor)
        alunos_nao_atendidos = [a for a in alunos if a.id not in alunos_atendidos]

        if not alunos_nao_atendidos:
            break

        # Ordenar e selecionar candidatos de acordo com o alpha
        alunos_ordenados = sorted(alunos_nao_atendidos, key=lambda a: (calcular_distancia(novo_monitor, a), a.necessidade))
        limite = max(1, int(len(alunos_ordenados) * alpha))
        candidato = random.choice(alunos_ordenados[:limite])

        # Verifica se o aluno já está atendido antes de tentar adicionar
        if candidato.id not in alunos_atendidos:
            if novo_monitor.adicionar_parada(candidato, calcular_limite_distancia(candidato, escola_x, escola_y, delta_factor)):
                alunos_atendidos.add(candidato.id)  # Marca o aluno como atendido

        # Adiciona o monitor à lista se ele tiver uma rota válida
        if novo_monitor.rota:
            monitores.append(novo_monitor)

    custo_total = calcular_custo_total(monitores)
    return monitores, custo_total


def perturbar_solucao(monitores, delta_factor, intensidade_perturbacao=1):
    """
    Perturba a solução atual trocando alunos entre monitores.

    
        monitores: Lista de monitores
        delta_factor: Fator de ajuste para calcular a distância limite.
        intensidade_perturbacao: Número de trocas a serem feitas (valor padrão é 1).

    Retorna:
        Lista de monitores com a solução perturbada.
    """
    if len(monitores) < 2:
        print("Não há monitores suficientes para perturbação.")
        return monitores

    for _ in range(intensidade_perturbacao):
        monitor1, monitor2 = random.sample(monitores, 2)

        if not monitor1.rota or not monitor2.rota:
            print("Um dos monitores não possui rota definida para troca.")
            continue

        # Troca de alunos entre monitores
        aluno_monitor1 = random.choice(monitor1.rota)
        aluno_monitor2 = random.choice(monitor2.rota)

        # Remove alunos das rotas atuais
        monitor1.rota.remove(aluno_monitor1)
        monitor2.rota.remove(aluno_monitor2)

        # Adiciona os alunos de volta nos monitores opostos, considerando a distância limite
        limite1 = calcular_limite_distancia(aluno_monitor2, monitor1.x, monitor1.y, delta_factor)
        limite2 = calcular_limite_distancia(aluno_monitor1, monitor2.x, monitor2.y, delta_factor)
        
        if monitor1.adicionar_parada(aluno_monitor2, limite1):
            monitor1.rota.append(aluno_monitor2)
        else:
            # Reverte a mudança caso não seja possível adicionar o aluno
            monitor1.rota.append(aluno_monitor1)

        if monitor2.adicionar_parada(aluno_monitor1, limite2):
            monitor2.rota.append(aluno_monitor1)
        else:
            # Reverte a mudança caso não seja possível adicionar o aluno
            monitor2.rota.append(aluno_monitor2)

    return monitores


def simulated_annealing(monitores_iniciais, alunos, delta_factor, temp_inicial=500, resfriamento=0.98, max_iter_sem_melhoria=100, min_temp=0.5):
    melhor_solucao = deepcopy(monitores_iniciais)
    custo_atual = calcular_custo_total(melhor_solucao)
    melhor_custo = custo_atual
    iteracoes_sem_melhoria = 0
    temp_atual = temp_inicial

    while iteracoes_sem_melhoria < max_iter_sem_melhoria and temp_atual > min_temp:
        nova_solucao = perturbar_solucao(melhor_solucao, delta_factor)
        novo_custo = calcular_custo_total(nova_solucao)

        delta = novo_custo - custo_atual
        if delta < 0 or np.exp(-delta / temp_atual) > random.uniform(0, 1):
            melhor_solucao = deepcopy(nova_solucao)
            custo_atual = novo_custo
            iteracoes_sem_melhoria = 0
        else:
            iteracoes_sem_melhoria += 1

        temp_atual *= resfriamento

        if custo_atual < melhor_custo:
            melhor_custo = custo_atual

    return melhor_solucao, melhor_custo


# Ajuste do alpha e do critério de aceitação
def grasp_com_simulated_annealing(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor, alpha=0.9):
    monitores_iniciais, custo_inicial = grasp_construir_solucao(
        alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor, alpha)

    melhor_solucao, melhor_custo = simulated_annealing(
        monitores_iniciais, alunos, delta_factor, temp_inicial=300, resfriamento=0.99)

    return melhor_solucao, melhor_custo
