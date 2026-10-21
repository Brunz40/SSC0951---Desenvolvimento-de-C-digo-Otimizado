# colocar &> results.txt para salvar o stdout e stderr mu, arquivo
SHELL := /bin/bash #shell do make não roda comando time
MAKE comparativo:
	gcc -pipe -Wall -O0 -fopenmp mandelbrot.c -o mandelbrot0 -lm -ftime-report 
	gcc -pipe -Wall -O1 -fopenmp mandelbrot.c -o mandelbrot1 -lm -ftime-report 
	gcc -pipe -Wall -O2 -fopenmp mandelbrot.c -o mandelbrot2 -lm -ftime-report
	gcc -pipe -Wall -O3 -fopenmp mandelbrot.c -o mandelbrot3 -lm -ftime-report
	gcc -pipe -Wall -O3 -march=native -fopenmp mandelbrot.c -o mandelbrot3P -lm -ftime-report
	gcc -pipe -Wall -Os -fopenmp mandelbrot.c -o mandelbrotS -lm -ftime-report

MAKE run:
	@echo "O0"
	@for i in $$(seq 1 5); do \
		time ./mandelbrot0 10000 output.pbm;\
	done
	@echo "O1"
	@for i in $$(seq 1 5); do \
		time ./mandelbrot1 10000 output.pbm;\
	done
	@echo "O2"
	@for i in $$(seq 1 5); do \
		time ./mandelbrot2 10000 output.pbm;\
	done
	@echo "O3"
	@for i in $$(seq 1 5); do \
		time ./mandelbrot3 10000 output.pbm;\
	done
	@echo "O3 com instruções especificas de cpu"
	@for i in $$(seq 1 5); do \
		time ./mandelbrot3P 10000 output.pbm;\
	done
	@echo "OS"
	@for i in $$(seq 1 5); do \
		time ./mandelbrotS 10000 output.pbm;\
	done