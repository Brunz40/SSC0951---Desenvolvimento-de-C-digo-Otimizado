#include <stdlib.h>
#include <stdio.h>
#include <string.h>
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

int* cria_vetor_rand(unsigned int tamanho){
    int* vetor=malloc(tamanho*sizeof(int));
    
    for (int i=0;i<tamanho;i++){
        vetor[i]=rand();
    }
    return vetor;
}

int* trocador(int* vetor, unsigned int posiçãoA, unsigned int posiçãoB){
    int aux=vetor[posiçãoA];
    vetor[posiçãoA]=vetor[posiçãoB];
    vetor[posiçãoB]=aux;
    return vetor;
}

void printa_vetor(int* vetor, unsigned int tamanho){
    for (unsigned int i=0;i<tamanho;i++){
        printf(" %d",vetor[i]);
    }
    printf("\n");
}

int* duplica_vetor(int* vetor, unsigned int tamanho){
    int* novoVetor= malloc(tamanho*sizeof(int));
    memcpy(novoVetor, vetor, tamanho*sizeof(int));
    return novoVetor;
}