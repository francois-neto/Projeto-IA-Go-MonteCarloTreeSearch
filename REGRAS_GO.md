# Regras do Go neste projeto

Go (também chamado Weiqi ou Baduk) é um jogo para duas pessoas. O objetivo é
terminar com mais pontos, ocupando o tabuleiro e cercando território.

## Tabuleiro e turnos

- As pretas jogam primeiro. Em cada turno, o jogador coloca uma pedra ou
  **passa** a vez; depois, é a vez do adversário.
- As pedras são colocadas nas **interseções vazias** das linhas, não nos espaços
  entre elas. Uma vez colocadas, não se movem, mas podem ser capturadas.
- O tabuleiro tradicional tem 19 × 19 interseções. Este projeto oferece
  tabuleiros de 5 × 5, 7 × 7 e 9 × 9 porque avaliar partidas em um tabuleiro
  de 19 × 19 exigiria muito mais tempo e poder computacional.

## Liberdades, grupos e captura

Uma **liberdade** é uma interseção vazia imediatamente acima, abaixo, à esquerda
ou à direita de uma pedra. Diagonais não contam. Uma pedra isolada tem até quatro
liberdades no centro, três na borda e duas no canto.

Pedras da mesma cor ligadas por essas direções formam um **grupo** e compartilham
as liberdades ao redor dele. Quando um grupo fica com uma única liberdade, está
em **atari** (ameaçado de captura). Se uma jogada ocupa sua última liberdade, o
grupo inteiro é retirado do tabuleiro.

Não é permitido jogar em uma interseção ocupada nem fazer **suicídio**: colocar
uma pedra que deixaria seu próprio grupo sem liberdades. A exceção é a jogada
que captura pedras adversárias e, após removê-las, deixa liberdades para o
grupo que acabou de jogar.

## Repetição de posição (superko)

Não se pode colocar uma pedra se o tabuleiro resultante repetir **qualquer
posição anterior da partida**, mesmo que não seja a do turno imediatamente
anterior. Essa é a regra de *superko posicional* implementada aqui; ela é mais
abrangente que a regra simples de ko descrita como “não repetir o turno
anterior”. Passar a vez é permitido e não coloca uma nova posição no histórico.

## Fim da partida e pontuação

A partida termina após **dois passes consecutivos**. Uma jogada com pedra entre
os passes reinicia a contagem. Antes de encerrar, é preciso capturar as pedras
adversárias que se deseja remover: este projeto não faz uma etapa separada de
retirada de pedras mortas.

O projeto usa **pontuação por área**:

- Cada pedra que continua no tabuleiro vale **1 ponto** para sua cor.
- Cada interseção vazia de uma região que toca apenas pedras de uma cor vale
  **1 ponto de território** para essa cor. Regiões que tocam as duas cores (ou
  nenhuma) não pontuam.
- As brancas recebem **komi**, pontos para compensar a vantagem de as pretas
  começarem: 0,5 no tabuleiro 5 × 5; 4,5 no 7 × 7; 6,5 no 9 × 9.

**Placar das pretas = pedras pretas no tabuleiro + território preto.**
**Placar das brancas = pedras brancas no tabuleiro + território branco + komi.**
Vence quem tiver mais pontos. Em caso de igualdade, o código declara vitória
das brancas.
