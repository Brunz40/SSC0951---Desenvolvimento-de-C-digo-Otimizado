#include "Multiplica.h"
#include <stdio.h>
#include <stdlib.h>

void Main(){
    float A[tamanho][tamanho];
    float B[tamanho][tamanho];
    float** C = malloc(tamanho*sizeof(float));
    float** D = malloc(tamanho*sizeof(float));
    for (int i=0;i<tamanho;i++){
      C[i] =malloc(tamanho * sizeof(float));
      D[i] = malloc(tamanho * sizeof(float));

      for (int j = 0; j < tamanho; j++) {
        A[i][j] = (float)rand() / (float)(RAND_MAX);
        B[i][j] = (float)rand() / (float)(RAND_MAX);
        C[i][j] = (float)rand() / (float)(RAND_MAX);
        D[i][j] = (float)rand() / (float)(RAND_MAX);
      }
    }

}