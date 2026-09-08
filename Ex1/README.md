# Código e reprodução

A entrada do repositório é o [README principal](../README.md).

## Arquivos usados

- `Main.c`: seleciona o experimento, prepara as matrizes e mede o tempo.
- `multiplica.c` e `Multiplica.h`: oito versões da multiplicação.
- `TestaMultiplica.c`: testes de correção, bordas e chamadas repetidas.
- `integrantes.json`: nomes e números USP utilizados nos PDFs.
- `scripts/`: coleta, análise Python, conferência em R e geração dos relatórios.
- `material_apoio/r_original.txt`: cópia exata do script fornecido pela disciplina.
- `build/`: binários gerados; ignorados pelo Git.

## Experimentos

| Número | Técnica | Alocação |
| --- | --- | --- |
| 1 / 2 | Simples, i-j-k | Estática / dinâmica |
| 3 / 4 | Interchange, i-k-j | Estática / dinâmica |
| 5 / 6 | Unrolling por fator 2 | Estática / dinâmica |
| 7 / 8 | Tiling, blocos nas três dimensões | Estática / dinâmica |

O padrão é TAMANHO=512 e BLOCO=32. Todas as versões usam `-O0`; não há OpenMP.
As estáticas são contíguas e as dinâmicas usam uma alocação por linha. A saída
é fornecida pelo chamador e zerada a cada chamada. As matrizes de entrada e
saída devem ser distintas. O custo de zerar a saída integra a medição.

## Comandos

```sh
make
make executar EXPERIMENTO=1
make teste
make verificar                         # verificações de memória e comportamento indefinido
make analisar                          # estatísticas e gráficos, usando dados existentes
make validar-r                         # análise e conferência com lm/anova em R
make relatorio                         # gera entrega/Relatorio_Atividade2.pdf e Anexo_tecnico.pdf
make clean                             # remove somente Ex1/build
```

O Makefile recompila o programa com as dimensões informadas; sem parâmetros,
volta ao padrão. Para uma nova campanha (a pasta de saída deve ser nova):

```sh
make coletar TAMANHO=512 BLOCO=32 RODADAS=10 CPU=2 SAIDA=dados/nova_coleta
make relatorio COLETA=dados/nova_coleta
```

As descrições dos resultados nos PDFs foram redigidas para a coleta original;
para uma campanha diferente, revisar também a interpretação, além das tabelas.
`make perfil SAIDA=dados/novo_piloto` executa uma rodada exploratória das oito
configurações. O piloto não deve ser misturado à amostra definitiva.

## Ferramentas e protocolo

O ambiente local em `../../.ferramentas/` (fora do repositório) contém perf,
Python e R, extraídos/instalados sem alterar os pacotes do sistema. O Makefile
os detecta, com alternativa para instalações disponíveis no PATH. Em outra
máquina, instalar GCC, perf, Python e R; as bibliotecas Python estão listadas
em `requirements-analise.txt`. R base é suficiente: FrF2 não é necessário.

O coletor usa pipes de controle e confirmação do perf para ativar os eventos
somente ao redor do cálculo. Contabiliza eventos de usuário, com pequeno
custo de controle, e rejeita dados incompletos, checksum divergente ou
cobertura inferior a 99,99%. Usa dez rodadas sorteadas, afinidade na CPU 2 e
as mesmas entradas. Não altera permissões do kernel.

A análise calcula média e IC95% t de Student. Para as influências, usa E1–E4
em cache e E1,E2,E5,E6 em branch. A normalização do script da disciplina e a
versão adicional com erro entre repetições são identificadas separadamente.
Os avisos de R sobre testes F em ajustes quase perfeitos não são usados
para conclusões; comparamos coeficientes, somas de quadrados e intervalos.

## Arquivos históricos

Apenas esta pasta `scripts/` deve ser usada normalmente. Cópias do coletor
antigo permanecem dentro de `../dados/coleta_2026-09-07/fontes.zip` e do
`../historico/piloto.zip`. Os nomes originais dentro dos ZIPs são preservados.

O `teste.c` da raiz era um exemplo antigo de retorno de matriz por ponteiro,
criado por Bruno no commit `27778ea` (05/09). Está preservado com os binários
antigos em `../historico/arquivos_anteriores.zip`. Não é usado nos testes atuais.
