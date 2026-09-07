#include "Multiplica.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char *argv[]) {
  // todo: não contar essa parte do código no profiling
  float A[tamanho][tamanho];
  float B[tamanho][tamanho];
  float **C = malloc(tamanho * sizeof(float));
  float **D = malloc(tamanho * sizeof(float));
  for (int i = 0; i < tamanho; i++) {
    C[i] = malloc(tamanho * sizeof(float));
    D[i] = malloc(tamanho * sizeof(float));

    for (int j = 0; j < tamanho; j++) {
      A[i][j] = (float)rand() / (float)(RAND_MAX);
      B[i][j] = (float)rand() / (float)(RAND_MAX);
      C[i][j] = (float)rand() / (float)(RAND_MAX);
      D[i][j] = (float)rand() / (float)(RAND_MAX);
    }
  }
  // todo: contar desempenho a partir daqui
  float matriz[tamanho][tamanho];
  memcpy(matriz, multiplica_simples_estático(A, B), sizeof(matriz));
#ifdef DEBUG
        // printar resultados de cada algoritmo
        printf("\n--- Matriz %dx% ---\n", tamanho);

    for (int i = 0; i < tamanho; i++) {
      // Para cada linha, vamos iterar pelas colunas
      for (int j = 0; j < tamanho; j++) {
        printf("%4d ", matriz[i][j]); // "%4d" alinha os números em colunas
      }
      printf("\n"); // Pula para a próxima linha após imprimir toda a fila
    }
#endif
return 0;
}