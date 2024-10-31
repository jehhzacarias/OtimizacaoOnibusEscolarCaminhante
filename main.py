#main.py
from guloso import minimizar_numero_de_monitores_guloso_balanceado
from parcial import minimizar_numero_de_monitores_parcialmente_guloso
from metaheuristicas import grasp_com_simulated_annealing
from entidades import Aluno, Monitor
from utils import calcular_distancia_maxima, calcular_custo_total
from busca_local import busca_local
import time

def configurar_dados():
    H = [1, 2, 3, 4]
    I = [6, 7, 9]
    qki = [[3, 2, 1, 3], [2, 3, 0, 1], [1, 3, 0, 2]]
    pk = [2.0, 1.5, 1.0]
    cij = [
        [0, 20, 34, 35, 18],
        [20, 0, 30, 40, 33],
        [34, 30, 0, 18, 27],
        [35, 40, 18, 0, 19],
        [18, 33, 27, 19, 0],
    ]
    p = 5
    alunos = []
    coordenadas = {1: (2, 3), 2: (4, 7), 3: (5, 1), 4: (7, 8)}

    for idx, casa in enumerate(H):
        for k, idade in enumerate(I):
            quantidade = qki[k][idx]
            necessidade = pk[k]
            if quantidade > 0:
                x, y = coordenadas[casa]
                aluno = Aluno(id=casa, x=x, y=y, idade=idade, quantidade=quantidade, necessidade=necessidade)
                alunos.append(aluno)

    capacidade_monitor = p
    distancia_maxima_monitor = max(max(cij))
    return alunos, capacidade_monitor, distancia_maxima_monitor

def imprimir_resultados(monitores, theta, custo_total):
    # Armazena os alunos já impressos para evitar repetição
    alunos_impressos = set()

    # Imprime o número de alunos por monitor
    vetor_monitores = [len(monitor.rota) for monitor in monitores]
    print(f"Alunos por monitor: {vetor_monitores}")
    print(f"Número total de monitores: {len(monitores)}")

    # Itera por cada monitor e aluno, imprimindo somente uma vez por aluno
    for monitor in monitores:
        for aluno in monitor.rota:
            if aluno.id not in alunos_impressos:
                print(f"Aluno: {aluno.id}, Posição: ({aluno.x}, {aluno.y}), Distância percorrida: {aluno.distancia_percorrida}")
                alunos_impressos.add(aluno.id)  # Marca o aluno como impresso

    # Calcula a distância máxima percorrida por cada monitor
    vetor_distancias = [calcular_distancia_maxima(monitor.rota) for monitor in monitores]
    print(f"Distâncias por monitor: {vetor_distancias}")
    print(f"Custo total: {custo_total}")
    print(f"Distância máxima percorrida: {theta}")


def main():
    escola_x = 0
    escola_y = 0
    delta_factor = 2.0

    alunos, capacidade_monitor, distancia_maxima_monitor = configurar_dados()

    opcao = input("Digite '1' para heurística gulosa, '2' para heurística parcialmente gulosa, '3' para busca local, ou '4' para GRASP com Simulated Annealing: ").strip()

    start_time = time.time()

    if opcao == '1':
        monitores_guloso, custo_total_guloso = minimizar_numero_de_monitores_guloso_balanceado(
            alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor)
        theta_guloso = max(calcular_distancia_maxima(monitor.rota) for monitor in monitores_guloso if monitor.rota)
        imprimir_resultados(monitores_guloso, theta_guloso, custo_total_guloso)

    elif opcao == '2':
        monitores_parcial = minimizar_numero_de_monitores_parcialmente_guloso(
            alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor)
        if monitores_parcial:
            custo_total_parcial = calcular_custo_total(monitores_parcial)
            theta_parcial = max(calcular_distancia_maxima(monitor.rota) for monitor in monitores_parcial if monitor.rota)
            imprimir_resultados(monitores_parcial, theta_parcial, custo_total_parcial)
        else:
            print("Nenhuma solução foi encontrada para a heurística parcialmente gulosa.")

    elif opcao == '3':
        monitores_iniciais, custo_total_inicial = minimizar_numero_de_monitores_guloso_balanceado(
            alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor)
        monitores_otimizados = busca_local(monitores_iniciais, alunos, delta_factor)
        custo_total_otimizado = calcular_custo_total(monitores_otimizados)
        theta_otimizado = max(calcular_distancia_maxima(monitor.rota) for monitor in monitores_otimizados if monitor.rota)
        imprimir_resultados(monitores_otimizados, theta_otimizado, custo_total_otimizado)

    elif opcao == '4':
        melhor_solucao, melhor_custo = grasp_com_simulated_annealing(
            alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor)
        theta_otimizado = max(calcular_distancia_maxima(monitor.rota) for monitor in melhor_solucao if monitor.rota)
        imprimir_resultados(melhor_solucao, theta_otimizado, melhor_custo)

    else:
        print("Opção inválida. Execute o programa novamente e escolha uma opção válida.")

    end_time = time.time()
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()
