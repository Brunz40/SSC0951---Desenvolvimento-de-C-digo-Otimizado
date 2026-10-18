MAKE comparativo:
	gcc -pipe -Wall -O0 -fopenmp spectral-norm.c -o spectral-norm0 -lm -ftime-report
	gcc -pipe -Wall -O1 -fopenmp spectral-norm.c -o spectral-norm1 -lm -ftime-report
	gcc -pipe -Wall -O2 -fopenmp spectral-norm.c -o spectral-norm2 -lm -ftime-report
	gcc -pipe -Wall -O3 -fopenmp spectral-norm.c -o spectral-norm3 -lm -ftime-report
	gcc -pipe -Wall -O3 -march=native -fopenmp spectral-norm.c -o spectral-norm3P -lm -ftime-report
	gcc -pipe -Wall -Os -fopenmp spectral-norm.c -o spectral-normS -lm -ftime-report

MAKE run comparativo: