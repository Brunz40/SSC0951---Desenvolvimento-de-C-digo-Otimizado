#include "Multiplica.h"
float (*multiplica_simples_estático(float A[tamanho][tamanho] , float B[tamanho][tamanho]))[tamanho]{
    static float resultado[tamanho][tamanho];//todo: testar essa maracutaia antes de ajustar as outras funções estáticas.
    for (int i=0;i<tamanho;i++){
        for (int j=0;j<tamanho;j++){
            for (int k=0;k<tamanho;k++){
                resultado[i][k]+=A[i][j]+B[j][k];
            }
        }
    }
    return resultado;
}

float **multiplica_simples_dinâmico(float **A, float **B, int n);

float multiplica_unroll_estático(float A[tamanho][tamanho], float B[tamanho][tamanho]){
  float resultado[tamanho][tamanho];
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
#pragma unroll 256 / sizeof(float) // todo: verificar se pode usar pragma
      for (int k = 0; k < tamanho; k++) {
        resultado[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return resultado;
}

float **multiplica_unroll_dinâmico(float **A, float **B, int n);

float multiplica_interchange_estático(float A[tamanho][tamanho], float B[tamanho][tamanho]) {
  float resultado[tamanho][tamanho];
  for (int i = 0; i < tamanho; i++) {
    for (int k = 0; k < tamanho; k++) {
      for (int j = 0; j < tamanho; j++) {
        resultado[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return resultado;
}

float **multiplica_interchange_dinâmico(float **A, float **B, int n);

float multiplica_tiling_estático(float A[tamanho][tamanho], float B[tamanho][tamanho]){
  float resultado[tamanho][tamanho];
#pragma omp tile sizes(2, 2)//todo: verificar se pode usar pragma
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
      for (int k = 0; k < tamanho; k++) {
        resultado[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return resultado;
}

float **multiplica_tiling_dinâmico(float **A, float **B, int n);