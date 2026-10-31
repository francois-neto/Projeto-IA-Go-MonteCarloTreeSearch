# Plano de implementação e apresentação — Go com MCTS

## Objetivo e limites

Em três dias, explicar seleção, expansão, simulação e retropropagação do MCTS aplicado ao Go; medir o efeito do tempo de busca; e comparar matematicamente o custo de uma busca Minimax com e sem poda alfa-beta. A apresentação dura 20 minutos. Não implementar Minimax, interface nova ou dependências externas. Usar apenas os tamanhos já suportados: **5×5, 7×7 e 9×9** (`src/go/rules.py`, `KOMI`, e `main.py`).

O código já permite jogar no terminal (`python3 main.py`), oferece orçamentos de 0,5 s, 2 s e 6 s por jogada e possui três testes (`python3 -m unittest discover -s tests -v`). `src/evaluation/arena.py` está vazio: os comandos e os resultados do experimento descritos abaixo **ainda precisam ser implementados/produzidos**.

## Pergunta experimental e protocolo

**Pergunta:** um MCTS com 6 s por jogada vence mais partidas que o mesmo MCTS com 0,5 s, nas condições testadas? Os 2 s entram na análise de custo, não no torneio principal. Ambos usam as mesmas regras, tabuleiro e algoritmo; só muda o tempo de busca.

1. Fazer um piloto de duas partidas em **5×5**, trocando as cores, para medir a duração real e estimar quantos pares de partidas cabem em **30 minutos no total**, incluindo a execução definitiva. Definir o número de pares antes de olhar o resultado final; preservar o mesmo número por cor. Se não couber sequer um par, reduzir o escopo e registrar a limitação, sem fingir uma amostra maior.
2. Em cada par, jogar 0,5 s × 6 s com um bot de preto e depois com o outro de preto; registrar a semente usada, a configuração de cada cor, o vencedor, o número de jogadas, o tempo e as simulações de **cada decisão** de MCTS. Fixar sementes e registrar a máquina/versão do Python. Como a busca termina por relógio, a semente **não garante execução bit a bit idêntica** em outra máquina ou carga de CPU.
3. Encerrar uma partida normalmente apenas após dois passes. Definir e registrar um limite de segurança de jogadas/tempo para a arena; se atingido, marcar **inconclusiva**, não pontuar um tabuleiro intermediário como vitória. Não contar partidas inconclusivas no denominador da taxa de vitórias; informar quantas houve. Não alterar `Estado` nem as regras para facilitar a medição.
4. Agregar vitórias/partidas concluídas **por configuração e por cor**; exibir também número de inconclusivas, mediana de simulações por decisão e tempo real de decisão. O custo do confronto inclui as jogadas dos dois bots: considerar isso no piloto. Uma diferença de vitórias numa amostra pequena é observação, **não demonstração estatística de superioridade**.
5. Separadamente, em **5×5, 7×7 e 9×9**, medir decisões de uma mesma posição inicial com 0,5 s, 2 s e 6 s. Como o orçamento em segundos já determina quase todo o tempo, comparar sobretudo **simulações realizadas** e **simulações por segundo**; repetir e registrar variação, sem comparar taxas de vitória entre tabuleiros diferentes.

Salvar os dados brutos e tabelas/figuras efetivamente usadas na apresentação em `results/` (versionada). Incluir no CSV cabeçalho explícito e, em arquivo acompanhante, comandos de reprodução, semente(s), quantidade de partidas, versão do Python, CPU e data. Não colocar dados finais em `docs/` (ignorada pelo Git). Não inventar resultados se a arena não estiver pronta.

## Demonstração das quatro etapas

Mostrar apenas os lances iniciais de uma partida e então pausar numa jogada concreta do bot. Nessa posição, explicar com um pequeno desenho da árvore: **seleção** pelo UCT (exploração × aproveitamento), **expansão** de uma jogada ainda não tentada, **simulação** de uma continuação, e **retropropagação** do vencedor até a raiz. Mostrar número de visitas, vitórias e simulações da decisão, sem chamar `vitorias/visitas` de probabilidade calibrada de vitória. Se houver instrumentação, mantê-la opcional e curta; a árvore de uma partida inteira não precisa ser impressa.

## Comparação matemática com Minimax

Na posição inicial, o código lista `n²` pontos mais o passe: **26, 50 e 82 jogadas disponíveis** para 5×5, 7×7 e 9×9, respectivamente. Para ilustrar uma árvore hipotética de fator de ramificação constante `b` e profundidade `d`, a busca sem poda examina aproximadamente `b^d` folhas; com ordenação ideal, alfa-beta pode reduzir esse crescimento para a ordem de `b^(d/2)` no melhor caso clássico. Montar uma tabela para algumas profundidades declaradas, distinguindo **folhas estimadas** de posições efetivamente medidas. Explicar que o fator de ramificação muda ao longo da partida (capturas, suicídio, superko e passes), que ordenação ruim reduz a poda e que `b = n² + 1` não é constante durante um jogo real.

Isso demonstra **crescimento exponencial sob as hipóteses do modelo**, não prova que todo Minimax com alfa-beta é inviável em toda posição ou que uma execução levaria um número específico de segundos. Não apresentar a estimativa como teste de um Minimax implementado. Relacionar a limitação de busca profunda ao uso de simulações sob orçamento de tempo no MCTS, sem afirmar que ele encontra sempre a melhor jogada.

## Delegação e entregas verificáveis

| Pessoa | Responsabilidade | Entrega e revisão |
| --- | --- | --- |
| Xandinho | Conferir regras e testes do Go em 5×5, 7×7 e 9×9; verificar passes, captura, superko e pontuação; acrescentar teste mínimo quando necessário. | Testes executáveis e lista das regras/limitações para Caioba e Francisco. |
| Caioba | Explicar uma decisão real de MCTS e as quatro etapas; definir os números mínimos a mostrar na demonstração. | Diagrama/roteiro de um lance e slides da explicação; revisar a terminologia com Xandinho. |
| Francisco | Implementar a arena mínima em `src/evaluation/arena.py`, executar piloto e torneio com cores alternadas; exportar dados brutos e síntese. | Script reproduzível e arquivos finais em `results/`; revisar tabelas com Davi. |
| Jorge | Derivar as fórmulas e tabela de Minimax/alfa-beta para os três tamanhos; documentar hipóteses e limites. | Slides de comparação matemática com contas verificáveis; validar contagens de jogadas com Xandinho. |
| Davi | Integrar alterações, executar testes e experimento final, revisar afirmações e organizar a apresentação. | Slides finais, comandos de reprodução e checklist de entrega; revisão cruzada dos resultados. |

Todos devem saber explicar o que a taxa de vitórias **não** mede. Revisar em dupla cada gráfico/conta antes de apresentar. Evitar implementação de um bot aleatório ou de Minimax: não são necessários para a pergunta experimental escolhida.

## Cronograma de três dias

| Dia | Meta | Critério de saída |
| --- | --- | --- |
| 1 | Xandinho valida regras; Caioba escolhe posição e desenho; Francisco prepara arena e piloto; Jorge prepara hipóteses/fórmulas; Davi integra. | Testes passando, piloto concluído, quantidade de pares e teto de execução decididos. |
| 2 | Rodar experimento dentro dos 30 minutos, revisar CSVs e contas; montar gráficos/tabelas e slides. | Arquivos reais em `results/`, resultados coerentes com dados brutos, roteiro completo. |
| 3 | Ensaiar 20 minutos, conferir comandos em máquina de apresentação e preparar contingência. | Reproduzir ao menos uma jogada e explicar um gráfico e uma conta sem depender da execução longa ao vivo. |

## Roteiro dos 20 minutos

| Tempo | Conteúdo | Responsável |
| --- | --- | --- |
| 0–2 min | Objetivo, regras e tamanhos permitidos | Xandinho |
| 2–6 min | Passos iniciais da partida e quatro etapas numa jogada | Caioba |
| 6–10 min | Arena, cores alternadas, métricas e resultados | Francisco |
| 10–14 min | Minimax, alfa-beta e limites da estimativa | Jorge |
| 14–18 min | Interpretação, limitações e demonstração curta | Davi |
| 18–20 min | Conclusão e margem para transição/perguntas | Grupo |

## Checklist antes da entrega

- [ ] `python3 -m unittest discover -s tests -v` passa.
- [ ] A arena roda partidas até término ou registra inconclusivas, sem alterar regras.
- [ ] Piloto define um número viável de pares antes da execução definitiva.
- [ ] CSVs e tabelas finais estão em `results/` e batem com os slides.
- [ ] Slides distinguem dado medido, estimativa matemática e interpretação.
- [ ] Demonstração curta funciona sem esperar a execução inteira do torneio.
- [ ] Cinco integrantes conhecem suas partes e a apresentação cabe em 20 minutos.
