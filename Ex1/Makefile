
CC = gcc

SOURCE_FILES = Main.c multiplica.c aux.c


OBJECT_FILES = $(SOURCE_FILES:.c=.o)


CFLAGS_TEST = -g -O0 -DDEBUG -Wall


CFLAGS_PROFILE = -g -Og -Wall


executavel_teste: $(OBJECT_FILES)
	$(CC) $(CFLAGS_TEST) -o $@ $^

perfil: $(OBJECT_FILES)
	$(CC) $(CFLAGS_PROFILE) -o $@ $^

# Regra para compilar arquivos .c em .o
%.o: %.c
	$(CC) $(CFLAGS_TEST) -c $< -o $@

clean:
	rm -f $(OBJECT_FILES) executavel_teste perfil *.out *.o

converter:
	gprof perfil gmon.out > perfil_relatorio.txt

make run:
	@for i in $$(seq 1 10); do \
		perf record ./perfil;\
		done

