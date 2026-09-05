#define tamanho 10
float (*multiplica_simples_estático(float A[tamanho][tamanho] , float B[tamanho][tamanho]))[tamanho];


float** multiplica_simples_dinâmico(float** A, float** B, int n);

float multiplica_unroll_estático(float A[tamanho][tamanho],
                                 float B[tamanho][tamanho]);

float** multiplica_unroll_dinâmico(float** A, float** B, int n);

float multiplica_interchange_estático(float A[tamanho][tamanho],
                                      float B[tamanho][tamanho]);

float **multiplica_interchange_dinâmico(float **A, float **B, int n);

float multiplica_tiling_estático(float A[tamanho][tamanho],
                                 float B[tamanho][tamanho]);

float **multiplica_tiling_dinâmico(float **A, float **B, int n);