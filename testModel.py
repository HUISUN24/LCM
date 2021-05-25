# Import libraries
import pymatgen.core as mg

# Accept material formula, and other parametwers as needed
def run(formula):
    # Dummy example that checks if the formula is valid. Should be True for all curated.
    try:
        compositionValid = mg.Composition(formula).valid
        return compositionValid
    except:
        print("Couldn't parse composition into pymatgen Composition")
        pass