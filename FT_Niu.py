import math
def run(Volume,Shear_Modulus,Bulk_Modulus):
    if Volume[0]==0 or Shear_Modulus[0]==0 or Bulk_Modulus[0]==0:
        return 0
    else:
        return Volume[0]**(1/6)*Shear_Modulus[0]*(Bulk_Modulus[0]/Shear_Modulus[0])**(1/2)