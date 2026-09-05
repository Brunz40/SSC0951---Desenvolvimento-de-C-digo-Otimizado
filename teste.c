#include <stdio.h>

// Sintaxe do retorno: float (*nome_funcao(parametros))[colunas]
float (*obter_matriz(void))[10] {
  static float A[10][10];

  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < 10; j++) {
      A[i][j] = i * 0.5f;
    }
  }

  return A;
}

int main(void) {
  float (*matriz)[10] = obter_matriz();
  printf("Valor em [4][0]: %.2f\n", matriz[4][0]);
  return 0;
}