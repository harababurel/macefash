"""
Computes the inverse of the standard normal function.
Source: http://www.johndcook.com/blog/python_phi_inverse/
"""
import math


def rationalApproximation(t):
    # Abramowitz and Stegun formula 26.2.23.
    # The absolute value of the error should be less than 4.5 e-4.
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    numerator = (c[2]*t + c[1])*t + c[0]
    denominator = ((d[2]*t + d[1])*t + d[0])*t + 1.0
    return t - numerator / denominator


def normalCDFinverse(p):
    assert p > 0.0 and p < 1.0

    # See article above for explanation of this section.
    if p < 0.5:
        # F^-1(p) = - G^-1(p)
        return -rationalApproximation(math.sqrt(-2.0 * math.log(p)))
    else:
        # F^-1(p) = G^-1(1-p)
        return rationalApproximation(math.sqrt(-2.0 * math.log(1.0-p)))


def sgn(x):
    return ['', '+'][x >= 0.0]


def demo():
    print "\nShow that the NormalCDFInverse function is accurate at"
    print "0.05, 0.15, 0.25, ..., 0.95 and at a few extreme values.\n\n"

    p = [
        0.0000001,
        0.0000100,
        0.0010000,
        0.0500000,
        0.1500000,
        0.2500000,
        0.3500000,
        0.4500000,
        0.5500000,
        0.6500000,
        0.7500000,
        0.8500000,
        0.9500000,
        0.9990000,
        0.9999900,
        0.9999999
    ]

    # Exact values computed by Mathematica.
    exact = [
            -5.199337582187471,
            -4.264890793922602,
            -3.090232306167813,
            -1.6448536269514729,
            -1.0364333894937896,
            -0.6744897501960817,
            -0.38532046640756773,
            -0.12566134685507402,
            0.12566134685507402,
            0.38532046640756773,
            0.6744897501960817,
            1.0364333894937896,
            1.6448536269514729,
            3.090232306167813,
            4.264890793922602,
            5.199337582187471
            ]

    maxError = 0.0
    numValues = len(p)
    print "         p         |    exact inverse   |  computed inverse  |        diff       "
    print "-------------------|--------------------|--------------------|-------------------"

    for i in range(numValues):
        computed = normalCDFinverse(p[i])
        error = exact[i] - computed
        print "%s%.15f | %s%.15f | %s%.15f | %s%.15f" % (sgn(p[i]), p[i], sgn(exact[i]), exact[i], sgn(computed), computed, sgn(error), error)
        maxError = max(maxError, abs(error))

    print "\nMaximum error: +-%.15f" % maxError

if __name__ == "__main__":
    demo()
