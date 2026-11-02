#include "Multiplica.h"

void multiplica_simples_estático(float A[tamanho][tamanho] , float B[tamanho][tamanho], float C[tamanho][tamanho]){
    for (int i=0;i<tamanho;i++){
        for (int j=0;j<tamanho;j++){
            for (int k=0;k<tamanho;k++){
                C[i][j]+=A[i][k]*B[k][j];
            }
        }
    }
}

float **multiplica_simples_dinâmico(float **A, float **B, float **M){
    for (int i = 0; i < tamanho; i++) {
      for (int j = 0; j < tamanho; j++) {
        for (int k = 0; k < tamanho; k++) {
          M[i][j] += A[i][k] * B[k][j];
        }
      }
    }
    return M;
}

void multiplica_unroll_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
#pragma GCC unroll 4
      for (int k = 0; k < tamanho; k++) {
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
}

float **multiplica_unroll_dinâmico(float **A, float **B, float **M){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
#pragma GCC unroll 4
      for (int k = 0; k < tamanho; k++) {
        M[i][j] += A[i][k] * B[k][j];
      }
    }
  }
  return M;
}

void multiplica_interchange_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
  for (int i = 0; i < tamanho; i++) {
    for (int k = 0; k < tamanho; k++) {
      for (int j = 0; j < tamanho; j++) {
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
}

float **multiplica_interchange_dinâmico(float **A, float **B, float **M){
  for (int i = 0; i < tamanho; i++) {
    for (int k = 0; k < tamanho; k++) {
      for (int j = 0; j < tamanho; j++) {
        M[i][j] += A[i][k] * B[k][j];
      }
    }
  }
  return M;
}

void multiplica_tiling_estático(float A[tamanho][tamanho], float B[tamanho][tamanho], float C[tamanho][tamanho]){
//todo:atualizar tiling
for (int i = 0; i < tamanho; i += blocksize) {
  for (int j = 0; j < tamanho; j += blocksize) {
    for (int k = 0; k < tamanho; k += blocksize) {
      for (int x = i; x < i + blocksize; x++) {
        for (int y = j; y < j + blocksize; y++) {
          for (int z = k; z < k + blocksize; z++) {
            C[x][y] += A[x][z] * B[z][y];
          }
        }
      }
    }
  }
}
}

float **multiplica_tiling_dinâmico(float **A, float **B, float **M){
//todo: atualiza tiling
for (int i = 0; i < tamanho; i += blocksize) {
  for (int j = 0; j < tamanho; j += blocksize) {
    for (int k = 0; k < tamanho; k += blocksize) {
      for (int x = i; x < i+blocksize; x++) {
        for (int y = j; y < j+blocksize; y++) {
          for (int z = k; z < k+blocksize; z++) {
            M[x][y] += A[x][z] * B[z][y];
          }
        }
      }
    }
  }
}
  return M;
}