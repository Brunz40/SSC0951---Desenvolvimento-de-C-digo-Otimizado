#include "Multiplica.h"
#include <omp.h>//Só para o pragma do tiling, não usamos paralelismo
#include <stdlib.h>

void multiplica_simples_estático(float A[tamanho][tamanho] , float B[tamanho][tamanho], float C[tamanho][tamanho]){
    for (int i=0;i<tamanho;i++){
        for (int j=0;j<tamanho;j++){
            for (int k=0;k<tamanho;k++){
                C[i][k]+=A[i][j]+B[j][k];
            }
        }
    }
}

float **multiplica_simples_dinâmico(float **A, float **B, float **M){
    for (int i = 0; i < tamanho; i++) {
      for (int j = 0; j < tamanho; j++) {
        for (int k = 0; k < tamanho; k++) {
          M[i][k] += A[i][j] + B[j][k];
        }
      }
    }
    return M;
}

void multiplica_unroll_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
#pragma unroll 256 / sizeof(float) // todo: verificar se pode usar pragma
      for (int k = 0; k < tamanho; k++) {
        C[i][k] += A[i][j] + B[j][k];
      }
    }
  }
}

float **multiplica_unroll_dinâmico(float **A, float **B, float **M){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
#pragma unroll 256 / sizeof(float) // todo: verificar se pode usar pragma
      for (int k = 0; k < tamanho; k++) {
        M[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return M;
}

void multiplica_interchange_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
  for (int i = 0; i < tamanho; i++) {
    for (int k = 0; k < tamanho; k++) {
      for (int j = 0; j < tamanho; j++) {
        C[i][k] += A[i][j] + B[j][k];
      }
    }
  }
}

float **multiplica_interchange_dinâmico(float **A, float **B, float **M){
  for (int i = 0; i < tamanho; i++) {
    for (int k = 0; k < tamanho; k++) {
      for (int j = 0; j < tamanho; j++) {
        M[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return M;
}

void multiplica_tiling_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
#pragma omp tile sizes(2, 2)//todo: verificar se pode usar pragma
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
      for (int k = 0; k < tamanho; k++) {
        C[i][k] += A[i][j] + B[j][k];
      }
    }
  }
}

float **multiplica_tiling_dinâmico(float **A, float **B, float **M){
#pragma omp tile sizes(2, 2) // todo: verificar se pode usar pragma
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
      for (int k = 0; k < tamanho; k++) {
        M[i][k] += A[i][j] + B[j][k];
      }
    }
  }
  return M;
}