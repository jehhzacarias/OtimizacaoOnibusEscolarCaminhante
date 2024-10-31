#entidades.py
from scipy.spatial import distance as sp_distance

class Aluno:
    def __init__(self, id, x, y, idade, quantidade=1, necessidade=1):
        self.id = id
        self.x = x
        self.y = y
        self.idade = idade
        self.quantidade = quantidade
        self.necessidade = necessidade
        self.atendido = False
        self.distancia_percorrida = 0


class Monitor:
    def __init__(self, capacidade, distancia_maxima, x=0, y=0):
        self.capacidade = capacidade
        self.distancia_maxima = distancia_maxima
        self.rota = []
        self.alunos_atendidos = 0
        self.distancia_percorrida = 0
        self.x = x
        self.y = y
        self.supervisao_necessaria = 0
        self.distancias_cache = {}

    def calcular_supervisao(self, aluno):
        if aluno.idade == 6:
            return 2.0
        elif aluno.idade == 7 or aluno.idade == 8:
            return 1.5
        elif aluno.idade == 9 or aluno.idade == 10:
            return 1.0
        return 1.0

    def validar_supervisao(self, aluno):
        supervisao_requerida = self.calcular_supervisao(aluno) * aluno.quantidade
        margem_supervisao = self.capacidade * 0.3

        if self.supervisao_necessaria + supervisao_requerida <= self.capacidade + margem_supervisao:
            return True
        
        return False

    def calcular_distancia(self, ponto1, ponto2):
        chave = (ponto1, ponto2)
        if chave not in self.distancias_cache:
            self.distancias_cache[chave] = sp_distance.euclidean(ponto1, ponto2)
        return self.distancias_cache[chave]

    def validar_distancia(self, aluno, distancia, distancia_maxima_aluno):
        margem_distancia = distancia_maxima_aluno * 0.2
        
        if self.distancia_percorrida + distancia <= self.distancia_maxima + margem_distancia:
            return True
        
        return False

    def adicionar_parada(self, aluno, distancia_maxima_aluno):
        if aluno.atendido:
            print(f"Aluno {aluno.id} já foi atendido. Ignorando duplicata...")
            return False

        # Calcular a distância entre a última posição do monitor e o novo aluno
        if not self.rota:
            distancia = self.calcular_distancia((self.x, self.y), (aluno.x, aluno.y))
        else:
            ultimo_aluno = self.rota[-1]
            distancia = self.calcular_distancia((ultimo_aluno.x, ultimo_aluno.y), (aluno.x, aluno.y))

        # Verifica as condições de supervisão e de distância
        if self.validar_supervisao(aluno) and self.validar_distancia(aluno, distancia, distancia_maxima_aluno):
            self.rota.append(aluno)
            self.alunos_atendidos += aluno.quantidade
            self.distancia_percorrida += distancia
            self.supervisao_necessaria += self.calcular_supervisao(aluno) * aluno.quantidade

            # Atualiza a posição do monitor para a do aluno recém-atendido
            self.x, self.y = aluno.x, aluno.y
            aluno.atendido = True
            aluno.distancia_percorrida = distancia

            print(f"Monitor movido para: ({self.x}, {self.y}), Aluno adicionado: {aluno.id}, Distância: {distancia}")
            return True
        else:
            print(f"Aluno {aluno.id} não pôde ser adicionado devido a restrições.")
            return False


