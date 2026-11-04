#include <stdlib.h>
// código para limpeza de buffer indicado pelo professor:
// sudo dmidecode -t cache
#define KB (1024)
#define MB (1024 * KB)
#define GB (1024 * MB)
#define LARGEST_CACHE_SZ (512 * KB)
static unsigned char dummy_buffer[LARGEST_CACHE_SZ];
void clean_cache() {
  unsigned long long i;
  for (i = 0; i < LARGEST_CACHE_SZ; i++)
    dummy_buffer[i] += 1;
}

float* cria_vetor_rand(unsigned int tamanho){
    float* vetor=malloc(tamanho*sizeof(int));
    
    for (int i=0;i<tamanho;i++){
        vetor[i]=rand();
    }
    return vetor;
}

float* trocador(float* vetor, unsigned int posiçãoA, unsigned int posiçãoB){
    int aux=vetor[posiçãoA];
    vetor[posiçãoA]=vetor[posiçãoB];
    vetor[posiçãoB]=aux;
    return vetor;
}