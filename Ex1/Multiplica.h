#define tamanho 10
void multiplica_simples_estático(float A[tamanho][tamanho],
                                 float B[tamanho][tamanho],
                                 float C[tamanho][tamanho]);

float **multiplica_simples_dinâmico(float **A, float **B, float **M);

void multiplica_unroll_estático(float A[tamanho][tamanho],
                                float B[tamanho][tamanho],
                                float C[tamanho][tamanho]);

float **multiplica_unroll_dinâmico(float **A, float **B, float **M);

void multiplica_interchange_estático(float A[tamanho][tamanho],
                                     float B[tamanho][tamanho],
                                     float C[tamanho][tamanho]);

float **multiplica_interchange_dinâmico(float **A, float **B, float **M);

void multiplica_tiling_estático(float A[tamanho][tamanho],
                                float B[tamanho][tamanho],
                                float C[tamanho][tamanho]);

float **multiplica_tiling_dinâmico(float **A, float **B, float **M);