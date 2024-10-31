# parcial.py
from entidades import Aluno, Monitor
from utils import calcular_distancia, calcular_limite_distancia, otimizar_rota, calcular_custo_total, calcular_distancia_maxima

def melhorar_alocacao(monitores, escola_x, escola_y, delta_factor):
    melhor_custo_total = calcular_custo_total(monitores)
    for monitor in monitores:
        monitor.rota = otimizar_rota(monitor.rota)

    # Balanceamento da supervisão entre monitores
    for monitor in monitores:
        for outro_monitor in monitores:
            if monitor != outro_monitor and outro_monitor.supervisao_necessaria < outro_monitor.capacidade:
                for aluno in list(monitor.rota):
                    if aluno.atendido:
                        continue

                    distancia_maxima_aluno = calcular_limite_distancia(aluno, escola_x, escola_y, delta_factor)
                    
                    if outro_monitor.adicionar_parada(aluno, distancia_maxima_aluno):
                        monitor.rota.remove(aluno)
                        aluno.atendido = True
                        break
    
    novo_custo_total = calcular_custo_total(monitores)
    return monitores if novo_custo_total < melhor_custo_total else monitores

def minimizar_numero_de_monitores_parcialmente_guloso(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor):
    monitores = []
    
    while any(not aluno.atendido for aluno in alunos):
        novo_monitor = Monitor(capacidade_monitor, distancia_maxima_monitor)
        alunos_nao_atendidos = [a for a in alunos if not a.atendido]

        alunos_ordenados = sorted(
            alunos_nao_atendidos,
            key=lambda a: (
                calcular_distancia(novo_monitor, a),
                a.necessidade
            )
        )
        
        supervisao_extra = 0.3  # Ajustar para 0.3 em vez de 0.2
        distancia_extra = 1.4  # Ajustar para 1.4 em vez de 1.3

        for aluno in alunos_ordenados:
            if not aluno.atendido:
                distancia_maxima_aluno = calcular_limite_distancia(aluno, escola_x, escola_y, delta_factor) * distancia_extra
                if novo_monitor.adicionar_parada(aluno, distancia_maxima_aluno):
                    aluno.atendido = True

        if novo_monitor.rota:
            monitores.append(novo_monitor)

    monitores = melhorar_alocacao(monitores, escola_x, escola_y, delta_factor)
    
    return monitores


def refinar_heuristica_parcial(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y):
    melhores_monitores = []
    melhor_custo_total = float('inf')
    melhor_supervisao_extra = 0
    melhor_distancia_extra = 0

    for supervisao_extra in [0.1, 0.2, 0.3]:
        for distancia_extra in [1.1, 1.2, 1.3]:
            print(f"Testando supervisao_extra={supervisao_extra} e distancia_extra={distancia_extra}")

            monitores = minimizar_numero_de_monitores_parcialmente_guloso(
                alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, 2.0, supervisao_extra, distancia_extra
            )

            if monitores:
                custo_total = calcular_custo_total(monitores)
                print(f"Custo total para supervisao_extra={supervisao_extra}, distancia_extra={distancia_extra}: {custo_total}")

                if custo_total < melhor_custo_total:
                    melhores_monitores = monitores
                    melhor_custo_total = custo_total
                    melhor_supervisao_extra = supervisao_extra
                    melhor_distancia_extra = distancia_extra

    print(f"Melhor combinação encontrada: supervisao_extra={melhor_supervisao_extra}, distancia_extra={melhor_distancia_extra}")
    return melhores_monitores, melhor_custo_total


def gerar_solucoes_pareto(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor, epsilon_max):
    solucoes_pareto = []
    
    for epsilon in range(epsilon_max + 2):  # Aumentar ligeiramente o intervalo de variação do epsilon
        # Reinicializa o status dos alunos para cada iteração
        for aluno in alunos:
            aluno.atendido = False
            aluno.distancia_percorrida = 0
        
        monitores = minimizar_numero_de_monitores_parcialmente_guloso(
            alunos, capacidade_monitor + epsilon, distancia_maxima_monitor, escola_x, escola_y, delta_factor)
        
        theta = max(calcular_distancia_maxima(monitor.rota) for monitor in monitores if monitor.rota)
        
        solucoes_pareto.append((len(monitores), theta))
    
    return solucoes_pareto
