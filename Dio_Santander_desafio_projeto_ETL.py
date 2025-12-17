import pandas as pd
import numpy as np
import json
import csv
from pathlib import Path
from scipy.interpolate import CubicSpline

# Extarct - Extraindo as coordenadas do arquivo .txt para um dataframe

pd.options.display.float_format = '{:.5f}'.format
mmcv_df = pd.DataFrame()
mmcv_df = pd.read_table('MASTER_153_ADM.txt')

with Path.open('parameters.json') as file:
    part_parameters = json.load(file)

# Transform - Formatando os dados
# 1. Excluir as colunas que não serão utilizadas
# 2. Renomear as colunas remanescentes
# 3. Excluir dados duplicados
# 4. Adicionar a última linha de coordenada
# 5. Substituir separador decimal (vírgula por ponto)

mmcv_df = mmcv_df.drop(mmcv_df.columns[[2, 3, 4, 5]], axis=1)
mmcv_df.columns = ['angle', 'displacement']
mmcv_df = mmcv_df.drop_duplicates(subset="displacement")
mmcv_df = mmcv_df.drop_duplicates(subset="angle")
final_coordinate = {'angle': '360,00', 'displacement': mmcv_df.loc[0, 'displacement']}
final_line_df = pd.DataFrame([final_coordinate])
mmcv_df = pd.concat([mmcv_df, final_line_df])
mmcv_df = mmcv_df.replace([np.inf, -np.inf], np.nan).dropna()
mmcv_df = mmcv_df.replace({',': '.'}, regex=True).astype(float)

# 6. Interpolar para encontrar os deslocamentos em função do valor de grau desejado

open_angle = part_parameters['open_angle']
close_angle = part_parameters['close_angle']

# Função de interpolação
def interpol_cubica(x, y, xi):
    f = CubicSpline(x, y, extrapolate=True)
    if xi < float(open_angle) or xi > float(close_angle):
        return 0
    else:
        return f(xi)

# Aplicar a interpolação para todos os "displacements" em função de "integer_degree":
polar_coordinates_df = pd.DataFrame(range(361), columns=['integer_degree']).astype(float)
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df.apply(lambda row: interpol_cubica(mmcv_df['angle'].values, mmcv_df['displacement'].values, row['integer_degree']), axis=1)
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df['interpol_displacement'].apply(lambda x: np.round(x, 5))

#Ajuste fino de Abertura/Fechamento em função de "open_angle" e "close_angle":
x1 = [polar_coordinates_df.loc[i + open_angle, 'integer_degree'] for i in range(-5, 19, 4)]
y1 = [polar_coordinates_df.loc[e, 'interpol_displacement'] for e in x1]
for angulo in range(open_angle, open_angle + 3):
    polar_coordinates_df.loc[angulo, 'interpol_displacement'] = interpol_cubica(x1, y1, polar_coordinates_df.loc[angulo, 'integer_degree'])
x2 = [polar_coordinates_df.loc[i + close_angle, 'integer_degree'] for i in range(-15, 9, 4)]
y2 = [polar_coordinates_df.loc[e, 'interpol_displacement'] for e in x2]
for angulo in range(close_angle - 2, close_angle + 1):
    polar_coordinates_df.loc[angulo, 'interpol_displacement'] = interpol_cubica(x2, y2, polar_coordinates_df.loc[angulo, 'integer_degree'])

# Arredondar casas decimais (após a interpolação pode acontecer alguns valores ficarem com muitas casas decimais):
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df['interpol_displacement'].apply(lambda x: np.round(x, 5))

# Criar a coluna "radius" que conterá o valor do deslocamento + o raio base:
base_radius = part_parameters['base_diameter'] / 2
polar_coordinates_df['radius'] = polar_coordinates_df['interpol_displacement'] + base_radius

# 7. Converter as coordenadas polares para coordenadas cartesianas:

cartesian_coordinates_df = pd.DataFrame().astype(float)

#Coordenadas do eixo X:
cartesian_coordinates_df['mm'] = polar_coordinates_df['radius'] * np.cos(np.deg2rad(polar_coordinates_df['integer_degree'] - 90))
#Coordenadas do eixo Y:
cartesian_coordinates_df[''] = polar_coordinates_df['radius'] * np.sin(np.deg2rad(polar_coordinates_df['integer_degree'] - 90))
#Coordenadas do eixo Z (como se trata de uma coleção de pontos para uso bidimensional, a coluna Z é preenchida com valores 0.00000):
cartesian_coordinates_df[" "] = np.round(polar_coordinates_df['radius'] * 0.0, 5)

# Load - Exportar as coordenadas para os formatos de arquivos 
# 1. Carregar somente as coordenadas necessárias no dataframe coord_load_df
# 2. Criar os cabeçalhos de acordo com a necessidade de cada software CAD:
#   -Autodesk Inventor: Exige um arquivo .xlsx com a primeira célula (A1) especificando a unidade de medida (mm, no caso);
#                       As células A2, B2 e C2 identificam as colunas com os respectivos eixos x, y e z.
#   -AutoCAD: Exige um arquivo .scr (Script AutoLISP) que lista os comandos necessários para a geração da curva spline:
#             _.OSMODE 0 desliga o Modo "Object Snap";
#             _SPLINE ativa o comando "Spline" que lê as coordenadas que estão separadas por vírgula na ordem x, y e z;
#             No AutoCAD a tecla espaço tem a mesma função que ENTER (return) então, cada ' ' representa um comando RETURN
#             para desativar o comando SPLINE;
#             (setvar "OSMODE" 16383) reabilita o Modo "Object Snap";
#             \x1b no final do script representa o comando "ESC" para cancelar qualquer comando ainda ativo.
#   -SolidWorks: Exige apenas um arquivo .txt com as coordenadas x, y e z separadas por tabulação, sem necessidade de cabeçalho.
#   -Creo Parametric: Exige um arquivo específico .pts, mas que possui a mesma formatação do arquivo para SolidWorks e
#                     pode ser aberto com o Bloco de Notas.
# 3. Concatenar os dataframes de cabeçalho e coordenadas;
# 4. Converter os dataframes para os respectivos formatos.

coord_load_df = pd.DataFrame().astype(float)
coord_load_df = cartesian_coordinates_df.loc[int(open_angle) - 6 : int(close_angle) + 6]

software_df = pd.DataFrame()
header1_df = pd.DataFrame({'mm': ['x'], '': ['y'], " ": ['z']})
header2_df = pd.DataFrame({'_.OSMODE 0': ['_SPLINE']})
end_df = pd.DataFrame({'_.OSMODE 0': [' ', ' ', ' ', '(setvar "OSMODE" 16383)', '\x1b']})
part_number = part_parameters['part_number']

for profile in part_parameters['cam_profile']:
    tipo = "_IN" if profile == "Intake" else "_EX" if profile == "Exhaust" else ''

    for software_cad in part_parameters['software_CAD']:
        if software_cad == "Autodesk Inventor":
            software_df = pd.concat([header1_df, coord_load_df]).reset_index(drop=True)
            software_df.to_excel(f'PROFILE_POINTS_{part_number}{tipo}.xlsx', index=False)       
        elif software_cad == "AutoCAD":
            software_df['_.OSMODE 0'] = coord_load_df['mm'].astype(str) + ',' + coord_load_df[''].astype(str) + ',' + coord_load_df[" "].astype(str)
            software_df = pd.concat([header2_df, software_df, end_df]).reset_index(drop=True)
            software_df.to_csv(f'PROFILE_SPLINE_{part_number}{tipo}.scr', sep='\t', index=False, quoting=csv.QUOTE_NONE)
        elif software_cad == "SolidWorks":
            coord_load_df.to_csv(f'PROFILE_POINTS_{part_number}{tipo}.txt', sep='\t', index=False, header=False)
        else:
            coord_load_df.to_csv(f'PROFILE_POINTS_{part_number}{tipo}.pts', sep='\t', index=False, header=False)
        software_df = pd.DataFrame()