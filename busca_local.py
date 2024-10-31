# busca_local.py
from entidades import Monitor
from utils import calcular_distancia, calcular_distancia_maxima, otimizar_rota
from copy import deepcopy
import numpy as np
import random

def busca_local(monitores, alunos, delta_factor, max_iteracoes_sem_melhoria=200, fase_reinicializacao=200):
    def calcular_custo(monitores, peso_monitores=1, peso_distancia=1, balanceamento_distancia=True, peso_desvio=0.5):
        custo_monitores = len(monitores) * peso_monitores
        max_distancia = 0
        distancias = []

        for monitor in monitores:
            distancia_maxima_monitor = calcular_distancia_maxima(monitor.rota)
            distancias.append(distancia_maxima_monitor)
            max_distancia = max(max_distancia, distancia_maxima_monitor)

        if balanceamento_distancia:
            desvio_padrao = np.std(distancias)
            return custo_monitores + (max_distancia * peso_distancia) + (desvio_padrao * peso_desvio)
        else:
            return custo_monitores + (max_distancia * peso_distancia)

    def gerar_vizinho(monitores, historico_movimentacoes):
        monitores_vizinho = deepcopy(monitores)
        encontrou_vizinho = False

        for i, monitor1 in enumerate(monitores_vizinho):
            for aluno1 in monitor1.rota:
                for j, monitor2 in enumerate(monitores_vizinho):
                    if i != j:
                        nova_supervisao_m1 = monitor1.supervisao_necessaria - aluno1.necessidade
                        nova_supervisao_m2 = monitor2.supervisao_necessaria + aluno1.necessidade
                        dist_m2 = calcular_distancia(monitor2, aluno1)

                        if (i, j, aluno1.id) in historico_movimentacoes:
                            continue

                        if (nova_supervisao_m1 <= monitor1.capacidade * 1.1 and
                            nova_supervisao_m2 <= monitor2.capacidade * 1.1 and
                            dist_m2 <= monitor2.distancia_maxima * 1.1):

                            monitor1.rota.remove(aluno1)
                            monitor2.rota.append(aluno1)

                            historico_movimentacoes.add((i, j, aluno1.id))
                            encontrou_vizinho = True
                            break
                if encontrou_vizinho:
                    break
            if encontrou_vizinho:
                break

        return monitores_vizinho, encontrou_vizinho

    def reinicializacao_aleatoria(monitores, alunos):
        for aluno in alunos:
            aluno.atendido = False

        random.shuffle(alunos)
        monitores_reinicializados = deepcopy(monitores)

        for aluno in alunos:
            for monitor in monitores_reinicializados:
                if monitor.adicionar_parada(aluno, calcular_distancia_maxima([aluno])):
                    break

        for monitor in monitores_reinicializados:
            print(f"Rota após reinicialização: {[aluno.id for aluno in monitor.rota]}")

        return monitores_reinicializados

    custo_atual = calcular_custo(monitores)
    melhor_solucao = deepcopy(monitores)
    iteracoes_sem_melhoria = 0
    historico_movimentacoes = set()
    reinicializacoes_consecutivas = 0
    temperatura_inicial = 100
    taxa_resfriamento = 0.99
    temperatura_atual = temperatura_inicial

    while iteracoes_sem_melhoria < max_iteracoes_sem_melhoria:
        nova_solucao, houve_mudanca = gerar_vizinho(melhor_solucao, historico_movimentacoes)
        if houve_mudanca:
            novo_custo = calcular_custo(nova_solucao)
            delta = novo_custo - custo_atual

            if delta < 0 or random.uniform(0, 1) < np.exp(-delta / temperatura_atual):
                melhor_solucao = deepcopy(nova_solucao)
                custo_atual = novo_custo
                iteracoes_sem_melhoria = 0
                reinicializacoes_consecutivas = 0
            else:
                iteracoes_sem_melhoria += 1
        else:
            iteracoes_sem_melhoria += 1

        # Adaptação da temperatura
        temperatura_atual = max(temperatura_atual * taxa_resfriamento, 1)
        print(f"Iterações sem melhoria: {iteracoes_sem_melhoria}, Temperatura: {temperatura_atual}")

        # Limpeza do histórico de movimentações a cada 50 iterações sem melhoria
        if iteracoes_sem_melhoria % 50 == 0:
            print("Limpando histórico de movimentações.")
            historico_movimentacoes.clear()

        # Fase de reinicialização após um número maior de iterações sem melhoria
        if iteracoes_sem_melhoria >= fase_reinicializacao:
            if reinicializacoes_consecutivas >= 3:
                print("Parando reinicializações, não houve progresso.")
                break

            print("Reinicializando solução...")
            melhor_solucao = reinicializacao_aleatoria(monitores, alunos)
            custo_atual = calcular_custo(melhor_solucao)
            iteracoes_sem_melhoria = 0
            reinicializacoes_consecutivas += 1

    return melhor_solucao
