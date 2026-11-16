module thermal_diffusion
  use iso_fortran_env, only: real64
  implicit none
  private
  public :: step
contains
  subroutine step(temperature, alpha, next)
    real(real64), intent(in) :: temperature(:), alpha
    real(real64), intent(out) :: next(:)
    integer :: i, n
    n = size(temperature)
    if (n < 3 .or. size(next) /= n) error stop "invalid grid size"
    if (alpha < 0.0_real64 .or. alpha > 0.5_real64) &
        error stop "unstable diffusion factor"
    next = temperature
    do i = 2, n - 1
       next(i) = temperature(i) + alpha * &
            (temperature(i - 1) - 2.0_real64 * temperature(i) + temperature(i + 1))
    end do
  end subroutine step
end module thermal_diffusion

program test_diffusion
  use iso_fortran_env, only: real64
  use thermal_diffusion
  implicit none
  real(real64) :: initial(5), evolved(5)
  initial = [0.0_real64, 0.0_real64, 100.0_real64, 0.0_real64, 0.0_real64]
  call step(initial, 0.5_real64, evolved)
  if (any(abs(evolved - &
       [0.0_real64, 50.0_real64, 0.0_real64, 50.0_real64, 0.0_real64]) > 1e-10_real64)) &
       error stop "diffusion test failed"
  print *, "Fortran diffusion checks passed"
end program test_diffusion
