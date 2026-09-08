#ifndef MULTIPLICA_H
#define MULTIPLICA_H

#ifndef TAMANHO
#define TAMANHO 512
#endif
#ifndef BLOCO
#define BLOCO 32
#endif
#if TAMANHO <= 0 || BLOCO <= 0
#error "TAMANHO e BLOCO devem ser positivos"
#endif
#define tamanho TAMANHO

/* O chamador fornece o resultado, sem sobrepor A ou B. Cada chamada o zera.
 * As funções dinâmicas exigem n > 0 e matrizes n x n válidas. */
typedef void (*MultiplicaEstatica)(const float A[tamanho][tamanho],
                                  const float B[tamanho][tamanho],
                                  float resultado[tamanho][tamanho]);
typedef void (*MultiplicaDinamica)(float **A, float **B, float **resultado, int n);

void multiplica_simples_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]);
void multiplica_unroll_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]);
void multiplica_interchange_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]);
void multiplica_tiling_estático(const float A[tamanho][tamanho], const float B[tamanho][tamanho], float resultado[tamanho][tamanho]);

void multiplica_simples_dinâmico(float **A, float **B, float **resultado, int n);
void multiplica_unroll_dinâmico(float **A, float **B, float **resultado, int n);
void multiplica_interchange_dinâmico(float **A, float **B, float **resultado, int n);
void multiplica_tiling_dinâmico(float **A, float **B, float **resultado, int n);

/* Alocação por linha, com liberação parcial em caso de falha. */
float **aloca_matriz(int n);
void libera_matriz(float **matriz, int n);

#endif
