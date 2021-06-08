import math
def run(Young_Modulus ,Poisson_Ratio ):
    if Young_Modulus [0]==0 or Poisson_Ratio [0]==0:
        return 0
    else:
        return math.sqrt(Young_Modulus [0]/(1-Poisson_Ratio [0]**2))
