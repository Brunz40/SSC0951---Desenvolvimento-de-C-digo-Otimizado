#include "Multiplica.h"
#include <stdlib.h>
#include <stdio.h>

float **cria_matriz_din(){
  float **C = malloc(tamanho * sizeof(float));
  for (int i = 0; i < tamanho; i++) {
    C[i] = malloc(tamanho * sizeof(float));
    for(int j=0;j<tamanho;j++){
        C[i][j]=0;
    }
  }
  return C;
}

float **randomiza_matriz_din(float **C){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
      C[i][j] = (float)rand() / (float)(RAND_MAX);
    }
  }
  return C;
}

void libera_matriz(float **C){
  for (int i = 0; i < tamanho; i++) {
    free(C[i]);
  }
  free(C);
}

void printa_matriz_din(float **C){
  for(int i=0;i<tamanho;i++){
    printf("\n");
    for (int j=0;j<tamanho;j++){
      printf(" %f", C[i][j]);
    }
  }
 }

void randomiza_matriz_estat(float C[tamanho][tamanho]){
  for (int i = 0; i < tamanho; i++) {
    for (int j = 0; j < tamanho; j++) {
      C[i][j] = (float)rand() / (float)(RAND_MAX);
    }
  }
 }

 void printa_matriz_estat(float C[tamanho][tamanho]){
  printf("\n printando matriz \n");
   for (int i = 0; i < tamanho; i++) {
     printf("\n");
     for (int j = 0; j < tamanho; j++) {
       printf(" %.5f", C[i][j]);
     }
   }
 }