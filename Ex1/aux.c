#include "Multiplica.h"
#include <stdlib.h>

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

float **randomiza_matriz(float **C){
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