SHELL := /bin/bash #shell do make não roda comando time
MAKE comparativo:
	gcc -pipe -Wall -O0 -fopenmp spectral-norm.c -o spectral-norm0 -lm -ftime-report
	gcc -pipe -Wall -O1 -fopenmp spectral-norm.c -o spectral-norm1 -lm -ftime-report
	gcc -pipe -Wall -O2 -fopenmp spectral-norm.c -o spectral-norm2 -lm -ftime-report
	gcc -pipe -Wall -O3 -fopenmp spectral-norm.c -o spectral-norm3 -lm -ftime-report
	gcc -pipe -Wall -O3 -march=native -fopenmp spectral-norm.c -o spectral-norm3P -lm -ftime-report
	gcc -pipe -Wall -Os -fopenmp spectral-norm.c -o spectral-normS -lm -ftime-report

MAKE run:
	@echo "O0"
	@for i in $$(seq 1 5); do \
		time ./spectral-norm0; \
	done
	@echo "O1"
	@for i in $$(seq 1 5); do \
		time ./spectral-norm1;\
	done
	@echo "O2"
	@for i in $$(seq 1 5); do \
		time ./spectral-norm2;\
	done
	@echo "O3"
	@for i in $$(seq 1 5); do \
		time ./spectral-norm3;\
	done
	@echo "O3 com instruções especificas de cpu"
	@for i in $$(seq 1 5); do \
		time ./spectral-norm3P;\
	done
	@echo "OS"
	@for i in $$(seq 1 5); do \
		time ./spectral-normS;\
	done