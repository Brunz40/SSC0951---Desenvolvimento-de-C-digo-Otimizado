CC = gcc
SRC = Main.c multiplica.c
OBJ = $(SRC:.c=.o)

CFLAGS_TESTE = -g -O0 -DDEBUG -Wall -fopenmp
CFLAGS_PERFILAGEM = -g -O0 -Wall -pg -fopenmp
#printa os resultados pra ver se ta tudo certo
teste: executavel_teste
executavel_teste: $(SRC)
	$(CC) $(CFLAGS_TESTE) $(SRC) -o $@


#roda com GProf
perfil: $(SRC)
	$(CC) $(CFLAGS_PERFILAGEM) $(SRC) -o executavel_perfil

#roda limpo
