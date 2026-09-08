#include "Multiplica.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    static float A[tamanho][tamanho], B[tamanho][tamanho], R[tamanho][tamanho];
    static double esperado[tamanho][tamanho];
    MultiplicaEstatica estaticas[] = {
        multiplica_simples_estático, multiplica_interchange_estático,
        multiplica_unroll_estático, multiplica_tiling_estático
    };
    MultiplicaDinamica dinamicas[] = {
        multiplica_simples_dinâmico, multiplica_interchange_dinâmico,
        multiplica_unroll_dinâmico, multiplica_tiling_dinâmico
    };
    float **Ad = aloca_matriz(tamanho), **Bd = aloca_matriz(tamanho);
    float **Rd = aloca_matriz(tamanho);
    int status = EXIT_FAILURE;
    if (!Ad || !Bd || !Rd) {
        fprintf(stderr, "Falha na alocação do teste.\n");
        goto fim;
    }
    /* Casos: matrizes densas distintas com sinais e frações, identidade e zero. */
    for (int caso = 0; caso < 3; caso++) {
        for (int i = 0; i < tamanho; i++) {
            for (int j = 0; j < tamanho; j++) {
                A[i][j] = Ad[i][j] = (float)((i * 3 + j * 7) % 17 - 8) / 7.0f;
                float b = (float)((i * 5 + j * 2) % 13 - 6) / 3.0f;
                B[i][j] = Bd[i][j] = caso == 0 ? b : (caso == 1 ? (float)(i == j) : 0.0f);
            }
        }
        /* Referência em double com acumulador local, independente das funções. */
        for (int i = 0; i < tamanho; i++) {
            for (int j = 0; j < tamanho; j++) {
                double soma = 0.0;
                for (int k = 0; k < tamanho; k++)
                    soma += (double)A[i][k] * B[k][j];
                esperado[i][j] = soma;
            }
        }
        for (int tecnica = 0; tecnica < 4; tecnica++) {
            for (int i = 0; i < tamanho; i++)
                for (int j = 0; j < tamanho; j++)
                    R[i][j] = Rd[i][j] = 123.0f;
            /* A segunda chamada detecta acúmulo indevido entre execuções. */
            for (int repeticao = 0; repeticao < 2; repeticao++) {
                estaticas[tecnica](A, B, R);
                dinamicas[tecnica](Ad, Bd, Rd, tamanho);
                for (int i = 0; i < tamanho; i++) {
                    for (int j = 0; j < tamanho; j++) {
                        double ref = esperado[i][j];
                        double tolerancia = 1e-4 + 1e-4 * fabs(ref);
                        if (!isfinite(R[i][j]) || !isfinite(Rd[i][j]) ||
                            fabs(R[i][j] - ref) > tolerancia ||
                            fabs(Rd[i][j] - ref) > tolerancia) {
                            fprintf(stderr, "Falha: n=%d caso=%d tecnica=%d repeticao=%d [%d][%d]: esperado=%.9g estatica=%.9g dinamica=%.9g\n",
                                    tamanho, caso, tecnica, repeticao, i, j, ref, R[i][j], Rd[i][j]);
                            goto fim;
                        }
                        if (A[i][j] != Ad[i][j] || B[i][j] != Bd[i][j]) {
                            fprintf(stderr, "Entradas divergiram após multiplicação.\n");
                            goto fim;
                        }
                    }
                }
            }
        }
    }
    printf("OK: n=%d, bloco=%d; oito versões, três casos e chamadas repetidas.\n", tamanho, BLOCO);
    status = EXIT_SUCCESS;
fim:
    libera_matriz(Ad, tamanho);
    libera_matriz(Bd, tamanho);
    libera_matriz(Rd, tamanho);
    return status;
}
