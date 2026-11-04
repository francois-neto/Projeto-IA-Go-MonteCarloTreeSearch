import time

from main import desenhar, ler_jogada, nome_ponto
from src.go.rules import KOMI
from src.go.state import Estado
from src.mcts.agent import expandir, retropropagar, selecionar
from src.mcts.node import No

estado = Estado(5, KOMI[5])
desenhar(estado)

ponto = ler_jogada("C3", 5)
print(estado.jogar(ponto))

ponto = ler_jogada("D1", 5)
print(estado.jogar(ponto))

ponto = ler_jogada("A2", 5)
print(estado.jogar(ponto))

desenhar(estado)

raiz = No(estado.copia())
prazo = time.monotonic() + 0.5
simulacoes = 0
while simulacoes < 1 or time.monotonic() < prazo:
    no = selecionar(raiz, 1.4)
    if no.nao_tentadas:
        no = expandir(no)
    copia = no.estado.copia()
    vencedor = copia.simular()
    retropropagar(no, vencedor)
    simulacoes += 1

print(f"Total de simulacoes: {simulacoes}")
soma = 0
for filho in sorted(raiz.filhos, key=No.numero_de_visitas, reverse=True):
    if filho.jogada is None:
        nome = "PASSO"
    else:
        nome = nome_ponto(filho.jogada, 5)
    print(nome, filho.visitas, filho.vitorias, f"{filho.vitorias/filho.visitas:.0%}")
    soma += filho.visitas

print(f"Soma das visitas dos filhos: {soma}")