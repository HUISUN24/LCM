import math
def run(Volume,Poisson_Ratio ,Young_Modulus ):
    if Volume[0]==0 or Poisson_Ratio [0]==0 or Young_Modulus [0]==0:
        return 0
    else:
        return Volume[0]**(1/6)*((1-13.7*Poisson_Ratio [0]+48.6*Poisson_Ratio [0]**2)/(1-15.2*Poisson_Ratio [0]+70.2*Poisson_Ratio [0]**2-81.5*Poisson_Ratio [0]**3)*Young_Modulus [0])**(3/2)
