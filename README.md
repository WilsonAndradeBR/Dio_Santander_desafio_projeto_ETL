# Desafio de projeto ETL-DIO-Santander 2025

Sou iniciante em programação Python e este é meu primeiro projeto na plataforma **DIO**.
Antes de encarar o **Bootcamp Santander 2025 – Ciência de Dados com Python**, na DIO, eu já havia desenvolvidos alguns códigos para automatizar algumas tarefas. Ter obtido um resultado satisfatório me deixou empolgado para me aprofundar mais na linguagem e me tornar um desenvolvedor.
Quanto a este desafio de projeto **DIO**, assistindo às aulas de ETL, do professor Diego Bruno, percebi que, intuitivamente, alguns de meus projetos já seguiam a estrutura **ETL** – **extrair, transformar, carregar** – e que eu poderia apresentar um deles neste primeiro desafio.
Como sou iniciante, considero que meus códigos são “rústicos”. Nem tudo segue boas práticas. Então, tenho certeza que meus projetos serão lapidados com o passar do tempo, conforme aprimoro meu conhecimento e a colaboração dos colegas.

## O código
Uma das minhas atribuições como desenhista projetista mecânico é desenvolver os desenhos técnicos dos produtos, especificando todas as suas características dimensionais e geométricas. Algumas peças possuem geometrias complexas difíceis de mensurar e representar graficamente. Ainda mais quando para gerar certa geometria no software CAD seja necessário coletar uma coleção de coordenadas, sejam elas polares ou cartesianas.
Instrumentos e equipamentos de medição modernos ajudam coletar estas coordenadas com exatidão e rapidez, mas, às vezes, exportar estes pontos para um software CAD manualmente consome tempo e pode levar a erros. Além do mais, se o equipamento de medição gerar algum tipo de arquivo com os dados coletados, nem sempre este estará organizado ou no formato aceito pelo software CAD.
Então, esta foi a motivação para o desenvolvimento do código: tratar os dados do arquivo de texto gerado pelo equipamento de medição e salvá-los no formato de arquivo que o software CAD aceite importar.
O código original que criei possui uma GUI desenvolvida com tkinter, onde posso informar tanto o caminho onde está salvo o arquivo com os dados quanto o local de destino do novo arquivo, além de possuir os campos onde posso inserir os parâmetros da peça necessários para a geração dos novos dados. Aqui apresentarei uma versão simplificada, sem interface gráfica, que pode ser executada de forma simples, desde que tanto o arquivo de texto original quanto o arquivo JSON com os parâmetros da peça estejam no mesmo diretório do código.

## A peça a ser medida
Irei apresentar como exemplo um eixo comando de válvulas, que nos motores de combustão interna, são responsáveis por abrir e fechar as válvulas de admissão e escape no devido tempo. Os elementos do eixo comando de válvulas responsáveis por esta função são os cames radiais.

<img width="300" height="300" src="https://github.com/user-attachments/assets/3d1fc1b3-9789-4afe-99fa-4bb0e29c66e6"> <img width="300" height="300" src="https://github.com/user-attachments/assets/fc194937-a954-444e-ac65-3b4b0f8e67ab">


## O equipamento de medição
O equipamento, chamado MMCV (Módulo de medição de comando de válvulas), utiliza um encoder rotativo e um encoder linear para fazer uma varredura no perfil do came, registrando o deslocamento linerar gerado a cada divisão de grau na rotação da peça. Ao final da varredura, é gerado um arquivo de texto com as coordenadas polares (grau, deslocamento).


Varredura para captar as coordenadas polares do perfil do came

<img width="300" height="300" src="https://github.com/user-attachments/assets/a29f931c-4aa8-45ef-85de-1ac365e130cf">

Interface do equipamento de medição (MMCV) coma representação gráfica do perfil
![MMCV2](https://github.com/user-attachments/assets/592db50b-2c1f-4806-9b52-61fa7c5727ca)

Após a varredura, o MMCV gera um arquito .txt com as coordenadas polares. Como a captura é feita a cada 45 milésimos de grau, e há vários valores duplicados, este arquivo possui, em média, 25 mil linhas. Daí a nessecidade de tratamento, para seu uso tanto no processo de fabricação da peça (programa CNC) quanto na criação do desenho de produto.

<img width="300" height="300" src="https://github.com/user-attachments/assets/daaa9a9f-f060-4d2c-9d6a-c7397012e364">

## Extract
Extraindo o arquivo .txt gerado para um Dataframe e abrindo o arquivo JSON com os parâmetros da peça:
```
pd.options.display.float_format = '{:.5f}'.format
mmcv_df = pd.DataFrame()
mmcv_df = pd.read_table('MASTER_153_ADM.txt') # Caminho do arquivo .txt gerado pelo MMCV

with Path.open('parameters.json') as file: # Caminho do arquivo .json com os parametros
    part_parameters = json.load(file)
```

## Transform
- Excluir as colunas que não serão utilizadas
- Renomear as colunas remanescentes
- Excluir dados duplicados
- Adicionar a última linha de coordenada
- Substituir separador decimal (vírgula por ponto)
```
mmcv_df = mmcv_df.drop(mmcv_df.columns[[2, 3, 4, 5]], axis=1) # Excluir colunas não necessárias
mmcv_df.columns = ['angle', 'displacement'] # Renomear colunas
mmcv_df = mmcv_df.drop_duplicates(subset="displacement") # Eliminar duplicidades na coluna "displacement"
mmcv_df = mmcv_df.drop_duplicates(subset="angle") # Eliminar duplicidades na coluna "angle"
final_coordinate = {'angle': '360,00', 'displacement': mmcv_df.loc[0, 'displacement']} # Criar linha final
final_line_df = pd.DataFrame([final_coordinate])
mmcv_df = pd.concat([mmcv_df, final_line_df]) #Concatenar Dataframe com a linha final
mmcv_df = mmcv_df.replace([np.inf, -np.inf], np.nan).dropna() # Excluir valores infinitamente pequenos ou infinitamente grandes
mmcv_df = mmcv_df.replace({',': '.'}, regex=True).astype(float) # Substituir vírgula por ponto (separador decimal)
```
<img width="300" height="300" src="https://github.com/user-attachments/assets/67150d30-20a6-4364-aaad-190758285942">


- Interpolar para encontrar os deslocamentos em função do valor de grau desejado (desejamos que os valores de grau sejam inteiros)
- Os valores para "displacement" correspondentes aos valores de "angle" < "open_angle" e "angle" > "close_angle" assumem valor ZERO
- Os valores para "open_angle" e "close_angle" estão armazenados no arquivo parameters.json
```
open_angle = part_parameters['open_angle']
close_angle = part_parameters['close_angle']

# Função de interpolação
def interpol_cubica(x, y, xi):
    f = CubicSpline(x, y, extrapolate=True)
    if xi < float(open_angle) or xi > float(close_angle):
        return 0
    else:
        return f(xi)
```

```
# Aplicar a interpolação para todos os "displacements" em função de "integer_degree":
polar_coordinates_df = pd.DataFrame(range(361), columns=['integer_degree']).astype(float)
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df.apply(lambda row: interpol_cubica(mmcv_df['angle'].values, mmcv_df['displacement'].values, row['integer_degree']), axis=1)
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df['interpol_displacement'].apply(lambda x: np.round(x, 5))

# Ajuste fino de Abertura/Fechamento em função de "open_angle" e "close_angle":
x1 = [polar_coordinates_df.loc[i + open_angle, 'integer_degree'] for i in range(-5, 19, 4)]
y1 = [polar_coordinates_df.loc[e, 'interpol_displacement'] for e in x1]
for angulo in range(open_angle, open_angle + 3):
    polar_coordinates_df.loc[angulo, 'interpol_displacement'] = interpol_cubica(x1, y1, polar_coordinates_df.loc[angulo, 'integer_degree'])
x2 = [polar_coordinates_df.loc[i + close_angle, 'integer_degree'] for i in range(-15, 9, 4)]
y2 = [polar_coordinates_df.loc[e, 'interpol_displacement'] for e in x2]
for angulo in range(close_angle - 2, close_angle + 1):
    polar_coordinates_df.loc[angulo, 'interpol_displacement'] = interpol_cubica(x2, y2, polar_coordinates_df.loc[angulo, 'integer_degree'])
```

```
# Arredondar casas decimais (após a interpolação pode acontecer de alguns valores ficarem com muitas casas decimais):
polar_coordinates_df['interpol_displacement'] = polar_coordinates_df['interpol_displacement'].apply(lambda x: np.round(x, 5))
````
<img width="300" height="300" src="https://github.com/user-attachments/assets/9b392670-9311-4ca3-91f8-05bb787a060b">

```
# Criar a coluna "radius" que conterá o valor do deslocamento + o raio base:
base_radius = part_parameters['base_diameter'] / 2
polar_coordinates_df['radius + interpol_displacement'] = polar_coordinates_df['interpol_displacement'] + base_radius
```
<img height="300" src="https://github.com/user-attachments/assets/950b8fc5-9b93-43bd-9d35-d5586209ce36">

- Converter as coordenadas polares para coordenadas cartesianas
- Será criada uma coluna que conterá as coordenadas no eixo Z. Como se trata de um objeto bidimensional, Z=0
```
cartesian_coordinates_df = pd.DataFrame().astype(float)

#Coordenadas do eixo X:
cartesian_coordinates_df['mm'] = polar_coordinates_df['radius + interpol_displacement'] * np.cos(np.deg2rad(polar_coordinates_df['integer_degree'] - 90))
#Coordenadas do eixo Y:
cartesian_coordinates_df[''] = polar_coordinates_df['radius + interpol_displacement'] * np.sin(np.deg2rad(polar_coordinates_df['integer_degree'] - 90))
#Coordenadas do eixo Z (como se trata de uma coleção de pontos para uso bidimensional, a coluna Z é preenchida com valores 0.00000):
cartesian_coordinates_df[" "] = np.round(polar_coordinates_df['radius + interpol_displacement'] * 0.0, 5)
```

<img width="300" height="300" src="https://github.com/user-attachments/assets/31af2689-548d-4bc6-96bf-824ee23fdbbc">

## Load
Na fase de carregamento iremos exportar os dados para o formato de arquivo que cada saoftware CAD consegue ler e importar os pontos da curva.
### Autodesk Inventor
O Autodesk Inventor importa pontos de um arquivo .xlsx. É preciso especificar a unidade de medida, no caso milímetros, e identificar cada coluna de coordenadas com o respectivo nome de eixo (x, y, z).

<img width="300" height="300" src="https://github.com/user-attachments/assets/abeb8152-a68b-4a85-91d6-08fd83148aa7">
<img width="300" height="300" src="https://github.com/user-attachments/assets/2d5da800-089f-4d28-844b-a9570f5a9b7f">

### AutoCad
O AutoCad exige um arquivo .scr (Script AutoLISP) que lista os comandos necessários para a geração da curva spline:
- "_.OSMODE 0" desliga o Modo "Object Snap"
- "_SPLINE" ativa o comando "Spline" que lê as coordenadas que estão separadas por vírgula na ordem x, y e z
- No AutoCad, a tecla espaço tem a mesma função que ENTER (return) então, cada ' ' representa um comando RETURN para desativar o comando SPLINE
- "(setvar "OSMODE" 16383)" reabilita o Modo "Object Snap"
- "\x1b" no final do script representa o comando "ESC" para cancelar qualquer comando ainda ativo

Este arquivo .scr pode ser aberto em um editor de texto.

<img height="300" src="https://github.com/user-attachments/assets/ff4b7a47-df88-4a4d-8d3f-e174363cef5c">
<img width="300" height="300" src="https://github.com/user-attachments/assets/dd2103fd-890e-42ff-983e-2f069937c293">


### SolidWorks
O SolidWorks exige apenas um arquivo .txt com as coordenadas x, y e z separadas por tabulação, sem necessidade de cabeçalho.

<img height="300" src="https://github.com/user-attachments/assets/4e479576-1f7b-4f16-a5da-0a9c7e60a730">

### Creo Parametric
Para o software Creo Parametric a formatação dos dados é idêntica à do SolidWorks, porém o deve ser salva em um arquivo específico (.pts). Este arquivo pode ser aberto no Bloco de Notas normalmente.

<img height="300" src="https://github.com/user-attachments/assets/4e479576-1f7b-4f16-a5da-0a9c7e60a730">
<img width="300" height="300" src="https://github.com/user-attachments/assets/ba379f67-86bb-4004-86dd-340b074b8aef">

Carregamento:
```
coord_load_df = pd.DataFrame().astype(float)
coord_load_df = cartesian_coordinates_df.loc[int(open_angle) - 6 : int(close_angle) + 6]

software_df = pd.DataFrame()
header1_df = pd.DataFrame({'mm': ['x'], '': ['y'], " ": ['z']}) # Cabeçalho para Autodesk Inventor
header2_df = pd.DataFrame({'_.OSMODE 0': ['_SPLINE']}) # Cabeçalho para AutoCad
end_df = pd.DataFrame({'_.OSMODE 0': [' ', ' ', ' ', '(setvar "OSMODE" 16383)', '\x1b']}) # Linhas finais para AutoCad

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
```

#### Peça real e peça desenvolvida no Autodesk Inventor
<img width="300" height="300" src="https://github.com/user-attachments/assets/cc8928ec-5b77-40b1-89cf-4b0ee702ef7b">
<img width="300" height="300" src="https://github.com/user-attachments/assets/d8847439-c212-447c-bbde-0427cf040110">


#### Na pasta Loads estão todos os arquivos gerados ao se executar o código.
