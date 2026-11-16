# Metodos numericos

- Julia: oscilador por Euler semi-implicito. Teste: julia labs/julia/test_oscillator.jl
- Fortran 2008: um passo de difusao termica unidimensional com fator de estabilidade limitado a 0..0.5. Teste: gfortran -std=f2008 -Wall -Wextra -o /tmp/test_diffusion labs/fortran/diffusion.f90 && /tmp/test_diffusion

Experimentos educacionais isolados do executavel C++ atual; resultados nao devem substituir um solver validado para uso cientifico.
