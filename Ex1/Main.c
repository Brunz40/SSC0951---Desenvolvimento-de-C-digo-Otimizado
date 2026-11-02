#include "Multiplica.h"
#include "aux.h"
int main(){
    //matrizes a serem multiplicadas:
    float A[tamanho][tamanho];
    float B[tamanho][tamanho];
    randomiza_matriz_estat(A);
    randomiza_matriz_estat(B);
    //matrizes que receberão o resultado
    float C[tamanho][tamanho];
    float C_unroll[tamanho][tamanho];
    float C_interchange[tamanho][tamanho];
    float C_tiling[tamanho][tamanho];
    //inicializando com 0:
    for(int i=0;i<tamanho;i++){
        for(int j=0;j<tamanho;j++){
            C[i][j]=0;
            C_unroll[i][j]=0;
            C_interchange[i][j]=0;
            C_tiling[i][j]=0;
        }
    }
    //multiplicação:
    multiplica_simples_estático(A, B, C);
    multiplica_unroll_estático(A, B, C_unroll);
    multiplica_interchange_estático(A, B, C_interchange);
    multiplica_tiling_estático(A, B, C_tiling);

#ifdef DEBUG
    printa_matriz_estat(C);
    printa_matriz_estat(C_unroll);
    printa_matriz_estat(C_interchange);
    printa_matriz_estat(C_tiling);

    #endif
    return 0;
}