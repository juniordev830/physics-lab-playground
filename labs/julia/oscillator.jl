module Oscillator
export simulate

"""
    simulate(x0, v0, stiffness, mass, dt, steps)

Semi-implicit Euler integration of a frictionless spring, returning positions.
All parameters are checked to prevent silent invalid simulations.
"""
function simulate(x0::Real, v0::Real, stiffness::Real, mass::Real,
                  dt::Real, steps::Integer)
    values = (x0, v0, stiffness, mass, dt)
    all(isfinite, values) || throw(ArgumentError("parameters must be finite"))
    (stiffness >= 0 && mass > 0 && dt > 0 && steps >= 0) ||
        throw(ArgumentError("invalid physical parameters"))
    x, v = Float64(x0), Float64(v0)
    positions = Vector{Float64}(undef, steps + 1)
    positions[1] = x
    for i in 1:steps
        v -= (stiffness / mass) * x * dt
        x += v * dt
        positions[i + 1] = x
    end
    return positions
end
end
