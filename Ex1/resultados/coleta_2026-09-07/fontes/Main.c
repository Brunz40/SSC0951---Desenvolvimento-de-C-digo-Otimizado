#define _POSIX_C_SOURCE 200809L
#include "Multiplica.h"
#include <errno.h>
#include <limits.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* Descritores opcionais herdados do coletor. Sem eles, executa normalmente.
 * O ack garante que o perf ativou/desativou os contadores antes de prosseguir. */
static int controla_perf(const char *comando) {
    const char *controle = getenv("DCO_PERF_CTL_FD");
    const char *resposta = getenv("DCO_PERF_ACK_FD");
    if (!controle && !resposta)
        return 0;
    if (!controle || !resposta) {
        fprintf(stderr, "Controle perf incompleto.\n");
        return -1;
    }
    char *fim;
    errno = 0;
    long ctl = strtol(controle, &fim, 10);
    if (errno || fim == controle || *fim || ctl < 0 || ctl > INT_MAX)
        return -1;
    errno = 0;
    long ack = strtol(resposta, &fim, 10);
    if (errno || fim == resposta || *fim || ack < 0 || ack > INT_MAX)
        return -1;
    size_t total = strlen(comando), enviado = 0;
    while (enviado < total) {
        ssize_t n = write((int)ctl, comando + enviado, total - enviado);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0) {
            perror("Comando perf");
            return -1;
        }
        enviado += (size_t)n;
    }
    char mensagem[4];
    size_t recebido = 0;
    while (recebido < sizeof mensagem) {
        struct pollfd pfd = {.fd = (int)ack, .events = POLLIN};
        int pronto = poll(&pfd, 1, 10000);
        if (pronto < 0 && errno == EINTR)
            continue;
        if (pronto <= 0 || !(pfd.revents & POLLIN)) {
            fprintf(stderr, "Sem confirmação do perf em até 10 segundos.\n");
            return -1;
        }
        char byte;
        ssize_t n = read((int)ack, &byte, 1);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0)
            return -1;
        /* Algumas versões do perf enviam um NUL depois de "ack\n". */
        if (recebido == 0 && byte == '\0')
            continue;
        mensagem[recebido++] = byte;
    }
    if (memcmp(mensagem, "ack\n", sizeof mensagem) != 0) {
        fprintf(stderr, "Confirmação inválida do perf.\n");
        return -1;
    }
    return 0;
}

static float proximo_valor(uint32_t *estado) {
    *estado = *estado * UINT32_C(1664525) + UINT32_C(1013904223);
    return (float)(*estado >> 8) / 16777216.0f;
}

int main(int argc, char **argv) {
    if (argc != 2 || argv[1][0] < '1' || argv[1][0] > '8' || argv[1][1] != '\0') {
        fprintf(stderr, "Uso: %s EXPERIMENTO\n"
                "1: simples/estatica      2: simples/dinamica\n"
                "3: interchange/estatica  4: interchange/dinamica\n"
                "5: unroll/estatica       6: unroll/dinamica\n"
                "7: tiling/estatica       8: tiling/dinamica\n", argv[0]);
        return EXIT_FAILURE;
    }
    int experimento = argv[1][0] - '0';
    int dinamica = experimento % 2 == 0;
    int tecnica = (experimento - 1) / 2;
    const char *nomes[] = {"simples", "interchange", "unroll", "tiling"};
    MultiplicaEstatica estaticas[] = {
        multiplica_simples_estático, multiplica_interchange_estático,
        multiplica_unroll_estático, multiplica_tiling_estático
    };
    MultiplicaDinamica dinamicas[] = {
        multiplica_simples_dinâmico, multiplica_interchange_dinâmico,
        multiplica_unroll_dinâmico, multiplica_tiling_dinâmico
    };
    /* Armazenamento estático: não ocupa a pilha e só é usado nos casos ímpares. */
    static float A[tamanho][tamanho], B[tamanho][tamanho], R[tamanho][tamanho];
    float **Ad = NULL, **Bd = NULL, **Rd = NULL;
    int status = EXIT_FAILURE;
    if (dinamica) {
        Ad = aloca_matriz(tamanho);
        Bd = aloca_matriz(tamanho);
        Rd = aloca_matriz(tamanho);
        if (!Ad || !Bd || !Rd) {
            fprintf(stderr, "Falha ao alocar matrizes.\n");
            goto fim;
        }
    }
    /* Mesma sequência e mesma semente para os oito experimentos. */
    uint32_t estado = 1;
    for (int i = 0; i < tamanho; i++) {
        for (int j = 0; j < tamanho; j++) {
            float a = proximo_valor(&estado), b = proximo_valor(&estado);
            if (dinamica) {
                Ad[i][j] = a;
                Bd[i][j] = b;
            } else {
                A[i][j] = a;
                B[i][j] = b;
            }
        }
    }
    struct timespec inicio, final;
    if (controla_perf("enable\n") != 0)
        goto fim;
    if (clock_gettime(CLOCK_MONOTONIC, &inicio) != 0) {
        perror("clock_gettime");
        goto fim;
    }
    if (dinamica)
        dinamicas[tecnica](Ad, Bd, Rd, tamanho);
    else
        estaticas[tecnica](A, B, R);
    if (clock_gettime(CLOCK_MONOTONIC, &final) != 0) {
        perror("clock_gettime");
        goto fim;
    }
    if (controla_perf("disable\n") != 0)
        goto fim;
    double segundos = (double)(final.tv_sec - inicio.tv_sec) +
                      (double)(final.tv_nsec - inicio.tv_nsec) / 1e9;
    double checksum = 0.0;
    for (int i = 0; i < tamanho; i++)
        for (int j = 0; j < tamanho; j++)
            checksum += dinamica ? Rd[i][j] : R[i][j];
    printf("experimento,tecnica,alocacao,tamanho,bloco,tempo_segundos,checksum\n");
    printf("%d,%s,%s,%d,%d,%.9f,%.17g\n", experimento, nomes[tecnica],
           dinamica ? "dinamica" : "estatica", tamanho, BLOCO, segundos, checksum);
    status = EXIT_SUCCESS;
fim:
    libera_matriz(Ad, tamanho);
    libera_matriz(Bd, tamanho);
    libera_matriz(Rd, tamanho);
    return status;
}
