CC = gcc
SRC = Main.c multiplica.c
OBJ = $(SRC:.c=.o)

CFLAGS_TESTE = -g -O0 -DDEBUG -Wall
CFLAGS_PERFILAGEM = -g -O0 -DDEBUG -Wall -pg
#printa os resultados pra ver se ta tudo certo
teste: executavel_teste
executavel_teste: $(OBJ)
	gcc $(CFLAGS_TESTE) -o $@ $(SRC)
	gcc $(CFLAGS_TESTE) -c $< -o $@


#roda com GProf
perfil:
	gcc $(CFLAGS_PERFILAGEM) -o $@ $(SRC)
	gcc $(CFLAGS_PERFILAGEM) -c $< -o $@

#roda limpo
