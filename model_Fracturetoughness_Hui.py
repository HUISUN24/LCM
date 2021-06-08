import FT_Thomson, FT_Rice_92, FT_Niu, FT_Rice_68, FT_Mazhnik

def calculate(linear_combination_result):
     for j in linear_combination_result.keys():
          for k in linear_combination_result[j].keys():
               linear_combination_result[j][k]['FT_Thomson_exp']=[FT_Thomson.run(linear_combination_result[j][k]['SurfEne'],linear_combination_result[j][k]['G_wiki'],linear_combination_result[j][k]['Possion_exp'])]
               linear_combination_result[j][k]['FT_Thomson_dft']=[FT_Thomson.run(linear_combination_result[j][k]['SurfEne'],linear_combination_result[j][k]['DFTGh'],linear_combination_result[j][k]['DFTpoisson'])]
               linear_combination_result[j][k]['FT_Rice_92_exp']=[FT_Rice_92.run(linear_combination_result[j][k]['G_wiki'],linear_combination_result[j][k]['USFE'],linear_combination_result[j][k]['Possion_exp'])]
               linear_combination_result[j][k]['FT_Rice_92_dft']=[FT_Rice_92.run(linear_combination_result[j][k]['DFTGh'],linear_combination_result[j][k]['USFE'],linear_combination_result[j][k]['DFTpoisson'])]
               linear_combination_result[j][k]['FT_Niu_exp']=[FT_Niu.run(linear_combination_result[j][k]['DFTv0'],linear_combination_result[j][k]['G_wiki'],linear_combination_result[j][k]['B_wiki'])]
               linear_combination_result[j][k]['FT_Niu_dft']=[FT_Niu.run(linear_combination_result[j][k]['DFTv0'],linear_combination_result[j][k]['DFTGh'],linear_combination_result[j][k]['DFTBh'])]
               linear_combination_result[j][k]['FT_Mazhnik_exp']=[FT_Mazhnik.run(linear_combination_result[j][k]['DFTv0'],linear_combination_result[j][k]['Possion_exp'],linear_combination_result[j][k]['Y_wiki'])]
               linear_combination_result[j][k]['FT_Mazhnik_dft']=[FT_Mazhnik.run(linear_combination_result[j][k]['DFTv0'],linear_combination_result[j][k]['DFTpoisson'],linear_combination_result[j][k]['DFTYoung'])]
               linear_combination_result[j][k]['FT_Rice_68_exp']=[FT_Rice_68.run(linear_combination_result[j][k]['Y_wiki'],linear_combination_result[j][k]['Possion_exp'])]
               linear_combination_result[j][k]['FT_Rice_68_dft']=[FT_Rice_68.run(linear_combination_result[j][k]['DFTYoung'],linear_combination_result[j][k]['DFTpoisson'])]
     	
     return linear_combination_result