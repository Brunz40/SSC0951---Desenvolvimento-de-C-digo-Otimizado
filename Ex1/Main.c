#include "Multiplica.h"
#include "aux.h"
int main(){
    //parte estática
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
    //parte dinâmica
    //matrizes a serem multiplicadas:
    float **Adin=cria_matriz_din();
    float **Bdin = cria_matriz_din();
    Adin=randomiza_matriz_din(Adin);
    Bdin=randomiza_matriz_din(Bdin);
    //matrizes que receberão o resultado:
    float **M=cria_matriz_din();
    float **M_unroll = cria_matriz_din();
    float **M_interchange = cria_matriz_din();
    float **M_tiling = cria_matriz_din();
    //multiplicação
    M=multiplica_simples_dinâmico(Adin, Bdin, M);
    M_unroll=multiplica_unroll_dinâmico(Adin, Bdin, M_unroll);
    multiplica_interchange_dinâmico(Adin, Bdin, M_interchange);
    multiplica_tiling_dinâmico(Adin, Bdin, M_tiling);

#ifdef DEBUG
    printa_matriz_estat(C);
    printa_matriz_estat(C_unroll);
    printa_matriz_estat(C_interchange);
    printa_matriz_estat(C_tiling);
    printa_matriz_din(M);
    printa_matriz_din(M_unroll);
    printa_matriz_din(M_interchange);
    printa_matriz_din(M_tiling);

    #endif
    libera_matriz(Adin);
    libera_matriz(Bdin);
    libera_matriz(M);
    libera_matriz(M_interchange);
    libera_matriz(M_unroll);
    libera_matriz(M_tiling);
    return 0;
}