#include "aux.h"
#include "ordenadores.h"
int main(){
    int* vetor=cria_vetor_rand(10);
    int* vetor2=duplica_vetor(vetor, 10);
    printa_vetor(vetor, 10);
    unsigned int teste=busca_binaria(vetor,10,0);
    vetor[teste]=0;
    printa_vetor(vetor, 10);
    /**
    printa_vetor(vetor, 10);
    printa_vetor(vetor2, 10);
    vetor=bubble_sort(vetor, 10);
    printa_vetor(vetor, 10);
    vetor2=selection_sort(vetor2, 10);
    printa_vetor(vetor2, 10);
*/

    return 0;
}