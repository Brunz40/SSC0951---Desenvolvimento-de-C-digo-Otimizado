# Atividade de profiling — multiplicação de matrizes

A aula `3aAula_Profiling.pdf`, página 14, define a operação como
`R[i][j] += A[i][k] * B[k][j]`. As páginas 15–17 apresentam interchange,
unrolling e tiling. A aula 4 explica gprof, mas o enunciado desta atividade
pede **perf**.

## Implementação

As oito configurações usam a mesma multiplicação e as mesmas entradas:

| Experimento | Técnica | Alocação |
| --- | --- | --- |
| 1 | Simples: laços i-j-k | Estática |
| 2 | Simples: laços i-j-k | Dinâmica |
| 3 | Interchange: laços i-k-j | Estática |
| 4 | Interchange: laços i-k-j | Dinâmica |
| 5 | Unrolling: i-j-k, k desenrolado por fator 2 | Estática |
| 6 | Unrolling: i-j-k, k desenrolado por fator 2 | Dinâmica |
| 7 | Tiling: blocos nas três dimensões, i-j-k dentro do bloco | Estática |
| 8 | Tiling: blocos nas três dimensões, i-j-k dentro do bloco | Dinâmica |

Unrolling e tiling são implementados explicitamente, sem pragmas ou OpenMP.
O unrolling trata tamanhos ímpares e o tiling trata blocos incompletos.
Na versão estática, as matrizes possuem armazenamento `static`; na dinâmica,
cada linha é alocada separadamente com `malloc` e acessada por `float **`.

As funções recebem uma matriz de saída já alocada e a zeram a cada chamada.
Isso substitui a antiga interface que retornava uma matriz interna. Entradas
e saída devem ser matrizes distintas. A alocação dinâmica verifica falhas e
a memória é liberada pelo chamador.

## Compilar e executar

Dentro de `Ex1`:

```sh
make
./build/multiplicacao 1
./build/multiplicacao 8
make executar EXPERIMENTO=3
```

O padrão é dimensão 512 e bloco 32. São valores iniciais para exploração,
ainda sem uma análise que justifique a escolha final para o relatório.
Para alterá-los:

```sh
make TAMANHO=1024 BLOCO=32
./build/multiplicacao 1
```

A dimensão estática é definida na compilação. A versão dinâmica utiliza a
mesma dimensão para permitir a comparação. Cada invocação de `make` que
compila o programa recompila com os parâmetros informados; sem parâmetros,
volta aos valores padrão. Todos os experimentos são compilados com `-O0`,
sem `-pg`, e com avisos tratados como erros. Os objetos antigos da pasta
não são usados. Os novos binários ficam em `build/`.

Cada processo executa **uma** configuração **uma** vez e imprime CSV com
identificação, dimensão, bloco, tempo em segundos e checksum. A geração das
entradas usa semente fixa e algoritmo determinístico, igual nos oito casos.
O checksum consome toda a saída, mas não substitui os testes de correção.

## Testes

```sh
make teste
make verificar
make teste BLOCO=7
```

Os testes comparam as oito versões com uma referência em `double`, usando
matrizes densas com números negativos e frações, multiplicação pela identidade
e pela matriz zero. Repetem chamadas para detectar acúmulo indevido e testam
as dimensões 1, 2, 3, 10, 32, 33 e 65, cobrindo bordas de unrolling e tiling.

`make verificar` executa os mesmos casos com AddressSanitizer e verificações
de comportamento indefinido. Estas últimas encerram o processo por trap,
sem exigir a biblioteca dinâmica libubsan, ausente no ambiente inicial.
Esses binários instrumentados são somente para testes, não para medições.

## Coleta concluída e relatório

A campanha de 07/09/2026 está em `resultados/coleta_2026-09-07/`:

- `analise/Relatorio_Atividade2.pdf`: relatório de nove páginas.
- `medicoes.csv`: 80 observações, dez por experimento, com as cinco métricas.
- `brutos/`: saída original do perf, saída do programa e comandos de cada execução.
- `metadados.json`: configuração, ordem sorteada, versões, cobertura e hashes.
- `fontes/`: cópia das fontes usadas na coleta, inclusive o Makefile daquela versão.
- `analise/resumo.csv`: médias, desvios, intervalos de confiança de 95%, mínimos,
  máximos e coeficientes de variação para as 40 combinações de experimento/métrica.
- `analise/influencias.csv` e `.json`: coeficientes, efeitos, somas de quadrados
  e influências dos fatores, com e sem o resíduo das repetições.
- `analise/graficos/`: gráficos em PNG e PDF vetorial.

O piloto, `resultados/piloto/`, foi excluído da amostra definitiva. Todos os
contadores tiveram cobertura de 100%. Nenhuma observação foi descartada.
A cópia das fontes preserva a configuração original mesmo se o código atual
for alterado. Os objetos antigos não foram modificados.

## Tempo e perf

O campo `tempo_segundos` usa `CLOCK_MONOTONIC` e mede a chamada da função,
incluindo zerar o resultado, excluindo alocação, geração das entradas,
checksum, impressão e liberação. Não há aquecimento prévio no processo; a
primeira escrita na saída ocorre no trecho medido.

O coletor abre dois pipes para comandar o perf e receber suas confirmações.
O perf inicia com `--delay=-1`; o programa envia `enable` imediatamente antes
do trecho cronometrado e `disable` depois dele. Os contadores incluem um
pequeno custo de controle e relógio, mas excluem a preparação e a impressão.
Executar `perf stat` diretamente sem esse protocolo mede o processo inteiro.

Eventos: `L1-dcache-loads:u`, `L1-dcache-load-misses:u`,
`branch-instructions:u`, `branch-misses:u`. O sufixo `:u` limita a contagem
ao modo usuário. Os eventos são agrupados e o coletor rejeita cobertura
inferior a 99,99%, ausência de evento ou checksum divergente.

O programa executou na CPU lógica 2, sem isolamento da CPU irmã, com boost
e governador originais. Cada rodada contém as oito configurações em ordem
sorteada com semente 9512026. A entrada usa a mesma semente fixa em todas
as execuções. O relatório explica os limites de comparabilidade, frequência
e variabilidade temporal observada.

## Instalação local

A instalação pelo sistema pediu senha de administrador. Foi baixado o pacote
oficial Fedora `perf-7.1.13-100.fc43.x86_64.rpm`, cuja assinatura foi verificada,
e extraído em `../../.ferramentas/perf/`. O binário usado é
`../../.ferramentas/perf/usr/bin/perf`. Nenhum pacote do sistema ou permissão
do kernel foi alterado. O Makefile detecta essa cópia local, com fallback para
`perf` no PATH; também aceita `PERF=/caminho/perf`.

A análise utiliza Python, NumPy, SciPy, Matplotlib e ReportLab. Foi criado
`../../.ferramentas/venv/`, aproveitando bibliotecas existentes, com NumPy
2.2.6 para compatibilidade com SciPy 1.14.1. O Makefile detecta esse ambiente,
ou utiliza `python3`. As versões estão em `requirements-analise.txt` e
`analise/analise.json`.

## Reproduzir

Para recalcular estatísticas e gráficos dos dados já coletados:

```sh
make analisar
make relatorio
```

Esses alvos não executam novos experimentos. Para gerar o relatório com a
identificação do grupo:

```sh
../../.ferramentas/venv/bin/python scripts/relatorio.py resultados/coleta_2026-09-07 --integrantes 'Nome — número USP; Nome — número USP'
```

Para uma nova campanha, usar uma pasta ainda inexistente:

```sh
make coletar TAMANHO=512 BLOCO=32 RODADAS=10 CPU=2 SAIDA=resultados/nova_coleta
make analisar COLETA=resultados/nova_coleta
make relatorio COLETA=resultados/nova_coleta
```

Para um piloto com uma rodada de todas as oito configurações:

```sh
make perfil SAIDA=resultados/novo_piloto
```

O coletor recusa sobrescrever uma pasta existente. Não misturar o piloto
com a campanha definitiva. `make clean` remove somente os binários em
`build/`; preserva as medições e os relatórios.

## Método estatístico e pontos a completar pelo grupo

Média e IC95% usam desvio padrão amostral e t de Student com nove graus de
liberdade. Para cache, analisam-se E1,E2,E3,E4 (simples/interchange); para
branch, E1,E2,E5,E6 (simples/unrolling). A decomposição 2² inclui técnica,
alocação, interação e erro entre repetições. A versão que usa apenas as
quatro médias também está registrada, para distinguir os denominadores.

O arquivo `../../r.txt` estava vazio no disco durante o trabalho. Por isso,
não foi possível conferir o script R do material de apoio; a análise foi
implementada em Python com fórmulas descritas no relatório e referências
estatísticas. O enunciado não exige que os cálculos sejam feitos em R.

Os nomes e números USP não foram informados e estão como campo a preencher
no PDF. O grupo deve revisar o texto e acrescentar essa identificação antes
da entrega. A submissão ao e-Disciplinas não foi realizada.
