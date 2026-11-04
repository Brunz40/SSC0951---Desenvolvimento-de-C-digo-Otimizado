SOURCE_FILES = main.c ordenadores.c aux.c

OBJECT_FILES = $(SOURCE_FILES:.c=.o)

CFLAGS_PROFILE = -g -Og -Wall -pg

build: $(OBJECT_FILES)
	gcc $(CFLAGS_PROFILE) -o $@ $^

%.o: %.c
	gcc $(CFLAGS_PROFILE) -c $< -o $@

clean:
	rm -f $(OBJECT_FILES) build

converter:
	gprof build gmon.out > perfil_relatorio.txt
