import math
def run(Surface_Energy,Shear_Modulus,Poisson_Ratio):
	print(Surface_Energy)
	if Surface_Energy[0]==0 or Shear_Modulus[0]==0 or Poisson_Ratio[0]==0:
		return 0
	else:
		return math.sqrt(4*Surface_Energy[0]*Shear_Modulus[0]/(1-Poisson_Ratio[0]))
