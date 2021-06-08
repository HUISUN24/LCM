import math
def run(Shear_Modulus,Unstable_Stacking_Fault_Energy,Poisson_Ratio ):
    if Unstable_Stacking_Fault_Energy[0]==0 or Shear_Modulus[0]==0 or Poisson_Ratio [0]==0:
        return 0
    else:
        return math.sqrt(2*Shear_Modulus[0]*Unstable_Stacking_Fault_Energy[0]/(1-Poisson_Ratio [0]))
