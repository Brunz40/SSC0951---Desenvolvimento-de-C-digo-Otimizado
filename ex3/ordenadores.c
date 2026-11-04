#include "aux.h"
#include <stdlib.h>
int* bubble_sort(int* vetor, unsigned int tamanho){
    short desordenado=1;
    unsigned int i;
    while (desordenado) {
        desordenado=0;
        for (i=1;i<tamanho;i++){
            if(vetor[i]<vetor[i-1]){
                vetor=trocador(vetor,i,i-1);
                desordenado=1;
            }
        }
    }
    return vetor;
}

int* insertion_sort(int* vetor, unsigned int tamanho){


    return vetor;
}

int* selection_sort(int* vetor, unsigned int tamanho){
    int menor;
    unsigned int menor_pos;
    unsigned int j;
    for(unsigned int i=0;i<tamanho;i++){
        menor=RAND_MAX;
        menor_pos=i;
        for(j=i;j<tamanho;j++){
            if(vetor[j]<menor){
                menor=vetor[j];
                menor_pos=j;
            }
        }
        vetor=trocador(vetor, i, menor_pos);
    }
    return (vetor);
}