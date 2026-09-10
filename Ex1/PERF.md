# Medir e conferir com perf

Os comandos abaixo mostram primeiro uma medição simples e depois a medição
usada no trabalho. Feche os outros aplicativos antes de medir e deixe o
computador sem interação durante as execuções. Se possível, mantenha o
notebook conectado à energia durante toda a coleta.

## 1. Preparar o programa

No terminal do VS Code:

```sh
cd "/home/fersuaiden/Área de trabalho/Faculdade/DCO/ATIVIDADE2/SSC0951---Desenvolvimento-de-C-digo-Otimizado"
make TAMANHO=512 BLOCO=32
make teste
```

`make` compila com `-O0`, sem otimização automática. `make teste` compara as
oito funções com resultados de referência; isso verifica o cálculo, não o
desempenho. A compilação e os testes de correção precedem as medições.

## 2. Encontrar o perf

```sh
perf_atividade="../.ferramentas/perf/usr/bin/perf"
"$perf_atividade" --version
"$perf_atividade" list cache
"$perf_atividade" list hardware
```

Nesta máquina usamos uma cópia local do perf. `--version` mostra a versão;
`list` mostra os eventos conhecidos. Um evento listado ainda pode ser
indisponível para uma medição específica; a tentativa de contagem é a
verificação efetiva.

## 3. Fazer uma medição simples

```sh
"$perf_atividade" stat \
  -e '{L1-dcache-loads:u,L1-dcache-load-misses:u,branch-instructions:u,branch-misses:u}' \
  -- taskset -c 2 ./Ex1/build/multiplicacao 1
```

- `stat` conta eventos enquanto o comando é executado.
- `-e` escolhe os eventos. As chaves pedem que eles sejam medidos juntos.
- `:u` restringe a contagem ao modo usuário, excluindo a execução no kernel.
- `--` separa as opções do perf do comando medido.
- `taskset -c 2` mantém o programa na CPU lógica 2. Não impede que outros
  processos usem esse núcleo ou a CPU irmã.
- `multiplicacao 1` executa a versão simples com alocação estática.

**Este comando mede o processo inteiro.** Os contadores incluem preparação
das matrizes, cálculo e impressão. Ele serve para aprender a ler o perf;
as medições do trabalho usam a delimitação descrita no passo 5.

## 4. Entender a saída

O programa imprime uma linha CSV com o tempo do cálculo e o checksum.
O perf imprime as contagens separadamente:

| Evento | O que está sendo contado |
| --- | --- |
| `L1-dcache-loads` | Leituras na cache L1 de dados |
| `L1-dcache-load-misses` | Leituras que não encontraram o dado na L1 |
| `branch-instructions` | Instruções de desvio executadas |
| `branch-misses` | Erros de predição desses desvios |

As contagens abrangem o código executado no intervalo, inclusive acessos a
variáveis e ponteiros; não são apenas operações matemáticas das matrizes.

`seconds time elapsed`, impresso pelo perf, é o tempo total do comando.
`tempo_segundos`, impresso pelo programa, mede zeramento da saída e
multiplicação. São intervalos diferentes. A análise utiliza o segundo.

Conferir:

1. Os quatro eventos têm números, sem `<not supported>` ou `<not counted>`.
2. Não há erro de permissão.
3. A cobertura deve ser 100%: os eventos ficaram ativos durante todo o
   intervalo em que estavam habilitados. Isso não significa CPU ociosa nem
   ausência de interferência de outros processos.
4. O checksum deve coincidir entre as oito versões com a mesma dimensão.

Os nomes e a disponibilidade dos eventos dependem do processador. A opção
`:u` permitiu a coleta nesta máquina com a configuração atual do kernel;
não foi necessário mudar permissões.

## Comparar versões diretamente no terminal

Mantenha o mesmo comando do passo 3 e troque apenas o último número:

| Versão | Estática | Dinâmica |
| --- | --- | --- |
| Simples | 1 | 2 |
| Interchange | 3 | 4 |
| Unrolling | 5 | 6 |
| Tiling | 7 | 8 |

Compare 1 com 3 para observar as faltas de cache e 1 com 5 para observar
as instruções de desvio. Faça o equivalente com 2/4 e 2/6 para alocação dinâmica.

Para repetir um comando dez vezes:

```sh
"$perf_atividade" stat -r 10 \
  -e '{L1-dcache-loads:u,L1-dcache-load-misses:u,branch-instructions:u,branch-misses:u}' \
  -- taskset -c 2 ./Ex1/build/multiplicacao 1
```

O perf apresenta médias e uma medida de dispersão. O percentual entre
parênteses da repetição não é o intervalo t de Student de 95% do relatório.

A taxa de faltas de L1 é `100 * L1-dcache-load-misses / L1-dcache-loads`.
A taxa de erro de predição é `100 * branch-misses / branch-instructions`.
Por exemplo, 50 faltas em 1.000 leituras correspondem a 5% de faltas.

## Ver quais funções concentram as amostras

`stat` conta eventos. `record` registra amostras da execução, que podem ser
examinadas por função com `report`:

```sh
pasta_amostras="$(mktemp -d Ex1/build/perf_amostras_XXXXXX)"
"$perf_atividade" record -e cycles:u -o "$pasta_amostras/perf.data" \
  -- taskset -c 2 ./Ex1/build/multiplicacao 1
"$perf_atividade" report --stdio -i "$pasta_amostras/perf.data"
```

Procure a coluna `Symbol`: ela contém os nomes das funções. O percentual de
`Overhead` indica a participação de cada função nas amostras ponderadas do
evento escolhido. Aqui o evento é ciclos de CPU; o percentual não é uma
taxa de erro de cache ou de predição.

Para abrir a interface navegável no terminal:

```sh
"$perf_atividade" report --tui -i "$pasta_amostras/perf.data"
```

Use as setas para navegar, Enter para abrir as opções de uma função e `q`
para sair. Isso é um exercício de exploração; a atividade usa as contagens
do `perf stat`.

## 5. Medir somente o cálculo

```sh
pasta_teste="Ex1/build/perf_e1_$(date +%Y%m%d_%H%M%S)"
python3 Ex1/scripts/coletar.py \
  --piloto --rodadas 1 --experimento 1 --mostrar-comando \
  --saida "$pasta_teste"
```

O script mostra o comando real antes de executá-lo. Além das opções do
passo 3, aparecem:

- `--delay=-1`: inicia com os contadores desativados.
- `--control fd:...`: recebe comandos por um canal de comunicação.
- `-x ';'`: separa as colunas do arquivo por ponto e vírgula.
- `-o`: salva a saída do perf.

O caminho percorrido em `Main.c` é:

```text
Alocar e preencher as matrizes
Enviar enable e esperar a confirmação do perf
Ler o relógio inicial
Zerar a saída e multiplicar
Ler o relógio final
Enviar disable e esperar a confirmação
Calcular checksum, imprimir e liberar memória
```

São dois pipes: um leva `enable`/`disable` ao perf, o outro devolve a
confirmação `ack`. O script passa os descritores ao programa pelas variáveis
`DCO_PERF_CTL_FD` e `DCO_PERF_ACK_FD`. Os números mudam a cada execução; não
copie esses números manualmente de uma execução anterior.

Os contadores ainda incluem um pequeno custo dos comandos de controle e
das leituras do relógio. Eles não incluem a geração das entradas, malloc,
checksum ou impressão.

## 6. Abrir os arquivos da medição

```sh
cat "$pasta_teste/brutos/001_r01_e1.stdout.csv"
cat "$pasta_teste/brutos/001_r01_e1.perf.csv"
cat "$pasta_teste/brutos/001_r01_e1.stderr.txt"
```

A linha de um evento tem este formato:

```text
contagem;;nome-do-evento;tempo-ativo-em-ns;percentual-ativo;;
```

A segunda coluna é a unidade e costuma ficar vazia para contagens. A quinta
coluna deve ser `100.00`. O coletor rejeita valores inferiores a 99,99%,
eventos ausentes, contagens inválidas ou checksums divergentes.

O nome `001_r01_e1` significa execução 1, rodada 1, experimento 1. O arquivo
`.comando.json` guarda os argumentos usados. `medicoes.csv` reúne o tempo e
os quatro contadores em uma linha; `metadados.json` registra a configuração.

## 7. Coletar os oito experimentos

Depois de conferir a execução individual:

```sh
pasta_coleta="dados/pratica_perf_$(date +%Y%m%d_%H%M%S)"
make coletar TAMANHO=512 BLOCO=32 RODADAS=10 CPU=2 SAIDA="$pasta_coleta"
```

Isso executa dez rodadas. Cada rodada contém os oito experimentos em uma
ordem sorteada, totalizando 80 medições. Um processo novo é iniciado a cada
medição. O script não substitui uma pasta que já existe.

Usamos arquivos separados por execução para poder conferir os dados. A
opção `perf stat -r 10` é útil para repetir um comando e obter estatísticas,
mas não faz o sorteio entre as oito versões nem substitui nossa análise de
intervalo de confiança.

## 8. Calcular as estatísticas

```sh
make validar-r COLETA="$pasta_coleta"
cat "$pasta_coleta/analise/resumo.csv"
```

`analise/resumo.csv` contém 40 linhas: oito experimentos vezes cinco
métricas. Cada linha informa `n`, média, desvio padrão e limites do IC95%.
O arquivo `validacao_R.txt` confirma a comparação com R. Esse comando
atualiza apenas a análise da pasta de prática. O relatório de entrega continua
usando `dados/coleta_entrega/`.

Para conferir uma linha à mão: calcule a média das dez observações, o desvio
padrão amostral e a margem `2,262157 × desvio / √10`. O intervalo é a média
menos/mais essa margem. Não misture observações de coletas diferentes.
As interpretações do relatório também precisam ser revisadas quando os
resultados mudarem.

Documentação: [perf stat](https://man7.org/linux/man-pages/man1/perf-stat.1.html), [perf record](https://man7.org/linux/man-pages/man1/perf-record.1.html) e [perf report](https://man7.org/linux/man-pages/man1/perf-report.1.html).
