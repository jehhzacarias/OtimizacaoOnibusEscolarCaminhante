# guloso.py
from entidades import Aluno, Monitor
from utils import calcular_distancia, calcular_limite_distancia, otimizar_rota, calcular_custo_total, calcular_distancia_maxima

def melhorar_alocacao(monitores, escola_x, escola_y, delta_factor):
    for monitor in monitores:
        monitor.rota = otimizar_rota(monitor.rota)
    return monitores

def minimizar_numero_de_monitores_guloso_balanceado(alunos, capacidade_monitor, distancia_maxima_monitor, escola_x, escola_y, delta_factor):
    monitores = []
    alunos_atendidos_ids = set()

    while len(alunos_atendidos_ids) < len(alunos):
        novo_monitor = Monitor(capacidade_monitor, distancia_maxima_monitor)
        alunos_nao_atendidos = [a for a in alunos if a.id not in alunos_atendidos_ids]

        alunos_ordenados = sorted(
            alunos_nao_atendidos, 
            key=lambda a: (calcular_distancia(novo_monitor, a), a.necessidade)
        )

        for aluno in alunos_ordenados:
            # Verificação adicional para garantir que só sejam processados alunos não atendidos
            if aluno.atendido or aluno.id in alunos_atendidos_ids:
                continue

            distancia_maxima_aluno = calcular_limite_distancia(aluno, escola_x, escola_y, delta_factor)

            # Adiciona o aluno ao monitor apenas se respeitar as restrições de supervisão e distância
            if novo_monitor.adicionar_parada(aluno, distancia_maxima_aluno):
                alunos_atendidos_ids.add(aluno.id)
                print(f"Aluno {aluno.id} marcado como atendido após ser adicionado à rota.")

        # Se o monitor conseguiu atender algum aluno, adiciona-o à lista de monitores
        if novo_monitor.rota:
            monitores.append(novo_monitor)
        else:
            break

    # Otimiza as rotas para minimizar as distâncias
    monitores = melhorar_alocacao(monitores, escola_x, escola_y, delta_factor)
    custo_total = calcular_custo_total(monitores)
    return monitores, custo_total
