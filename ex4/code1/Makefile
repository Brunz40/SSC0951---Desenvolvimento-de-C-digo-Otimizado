# colocar &> results.txt para salvar o stdout e stderr mu, arquivo
MAKE comparativo:
	gcc -pipe -Wall -O0 -fopenmp mandelbrot.c -o mandelbrot0 -lm -ftime-report 
	gcc -pipe -Wall -O1 -fopenmp mandelbrot.c -o mandelbrot1 -lm -ftime-report 
	gcc -pipe -Wall -O2 -fopenmp mandelbrot.c -o mandelbrot2 -lm -ftime-report
	gcc -pipe -Wall -O3 -fopenmp mandelbrot.c -o mandelbrot3 -lm -ftime-report
	gcc -pipe -Wall -O3 -march=native -fopenmp mandelbrot.c -o mandelbrot3P -lm -ftime-report
	gcc -pipe -Wall -Os -fopenmp mandelbrot.c -o mandelbrotS -lm -ftime-report

MAKE run comparativo: