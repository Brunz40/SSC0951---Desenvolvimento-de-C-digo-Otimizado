#include "Multiplica.h"
#include <stdint.h>
#include <stdlib.h>

float **aloca_matriz(int n) {
    if (n <= 0 || (size_t)n > SIZE_MAX / sizeof(float *) ||
        (size_t)n > SIZE_MAX / sizeof(float))
        return NULL;
    float **matriz = calloc((size_t)n, sizeof *matriz);
    if (!matriz)
        return NULL;
    for (int i = 0; i < n; i++) {
        matriz[i] = malloc((size_t)n * sizeof *matriz[i]);
        if (!matriz[i]) {
            libera_matriz(matriz, n);
            return NULL;
        }
    }
    return matriz;
}

void libera_matriz(float **matriz, int n) {
    if (!matriz)
        return;
    for (int i = 0; i < n; i++)
        free(matriz[i]);
    free(matriz);
}

static void zera_estatica(float resultado[tamanho][tamanho]) {
    for (int i = 0; i < tamanho; i++)
        for (int j = 0; j < tamanho; j++)
            resultado[i][j] = 0.0f;
}

static void zera_dinamica(float **resultado, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            resultado[i][j] = 0.0f;
}

static int fim_bloco(int inicio, int n) {
    return inicio + (n - inicio < BLOCO ? n - inicio : BLOCO);
}

void multiplica_simples_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]) {
    zera_estatica(resultado);
    for (int i = 0; i < tamanho; i++)
        for (int j = 0; j < tamanho; j++)
            for (int k = 0; k < tamanho; k++)
                resultado[i][j] += A[i][k] * B[k][j];
}

void multiplica_simples_dinâmico(float **A, float **B, float **resultado, int n) {
    zera_dinamica(resultado, n);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                resultado[i][j] += A[i][k] * B[k][j];
}

void multiplica_interchange_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]) {
    zera_estatica(resultado);
    for (int i = 0; i < tamanho; i++)
        for (int k = 0; k < tamanho; k++)
            for (int j = 0; j < tamanho; j++)
                resultado[i][j] += A[i][k] * B[k][j];
}

void multiplica_interchange_dinâmico(float **A, float **B, float **resultado, int n) {
    zera_dinamica(resultado, n);
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++)
            for (int j = 0; j < n; j++)
                resultado[i][j] += A[i][k] * B[k][j];
}

void multiplica_unroll_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]) {
    zera_estatica(resultado);
    /* Fator 2, com tratamento do último elemento ímpar. */
    for (int i = 0; i < tamanho; i++) {
        for (int j = 0; j < tamanho; j++) {
            int k = 0;
            for (; k < tamanho - 1; k += 2) {
                resultado[i][j] += A[i][k] * B[k][j];
                resultado[i][j] += A[i][k + 1] * B[k + 1][j];
            }
            if (k < tamanho)
                resultado[i][j] += A[i][k] * B[k][j];
        }
    }
}

void multiplica_unroll_dinâmico(float **A, float **B, float **resultado, int n) {
    zera_dinamica(resultado, n);
    /* Fator 2, com tratamento do último elemento ímpar. */
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int k = 0;
            for (; k < n - 1; k += 2) {
                resultado[i][j] += A[i][k] * B[k][j];
                resultado[i][j] += A[i][k + 1] * B[k + 1][j];
            }
            if (k < n)
                resultado[i][j] += A[i][k] * B[k][j];
        }
    }
}

void multiplica_tiling_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]) {
    zera_estatica(resultado);
    /* Blocos nas três dimensões, mantendo i-j-k dentro de cada bloco.
     * Os limites tratam dimensões que não são múltiplas de BLOCO. */
    for (int x = 0; x < tamanho; x = fim_bloco(x, tamanho)) {
        int fim_i = fim_bloco(x, tamanho);
        for (int y = 0; y < tamanho; y = fim_bloco(y, tamanho)) {
            int fim_j = fim_bloco(y, tamanho);
            for (int z = 0; z < tamanho; z = fim_bloco(z, tamanho)) {
                int fim_k = fim_bloco(z, tamanho);
                for (int i = x; i < fim_i; i++)
                    for (int j = y; j < fim_j; j++)
                        for (int k = z; k < fim_k; k++)
                            resultado[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

void multiplica_tiling_dinâmico(float **A, float **B, float **resultado, int n) {
    zera_dinamica(resultado, n);
    /* Blocos nas três dimensões, mantendo i-j-k dentro de cada bloco.
     * Os limites tratam dimensões que não são múltiplas de BLOCO. */
    for (int x = 0; x < n; x = fim_bloco(x, n)) {
        int fim_i = fim_bloco(x, n);
        for (int y = 0; y < n; y = fim_bloco(y, n)) {
            int fim_j = fim_bloco(y, n);
            for (int z = 0; z < n; z = fim_bloco(z, n)) {
                int fim_k = fim_bloco(z, n);
                for (int i = x; i < fim_i; i++)
                    for (int j = y; j < fim_j; j++)
                        for (int k = z; k < fim_k; k++)
                            resultado[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}
