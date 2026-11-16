include("oscillator.jl")
using .Oscillator
using Test

@test simulate(1.0, 0.0, 0.0, 1.0, 0.1, 2) == [1.0, 1.0, 1.0]
@test length(simulate(2, 0, 4, 2, 0.01, 100)) == 101
@test_throws ArgumentError simulate(1, 0, 2, 0, 0.01, 3)
@test_throws ArgumentError simulate(1, 0, 2, 1, -0.01, 3)
println("Julia oscillator checks passed")
