#include "aux.h"
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