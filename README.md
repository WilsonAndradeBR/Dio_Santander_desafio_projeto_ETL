# Desafio de projeto ETL-DIO-Santander 2025

Sou iniciante em programação Python e este é meu primeiro projeto na plataforma DIO.
Antes de encarar o “Bootcamp Santander 2025 – Ciência de Dados com Python”, na DIO, eu já havia desenvolvidos alguns códigos para automatizar algumas tarefas. Ter obtido um resultado satisfatório me deixou empolgado para me aprofundar mais na linguagem e me tornar um desenvolvedor.
Quanto a este desafio de projeto DIO, assistindo às aulas de ETL, do professor Diego Bruno, percebi que, intuitivamente, alguns de meus projetos já seguiam a estrutura ETL – extrair, transformar, carregar – e que eu poderia apresentar um deles neste primeiro desafio.
Como sou iniciante, considero que meus códigos são “rústicos”. Nem tudo segue boas práticas. Então, tenho certeza que meus projetos serão lapidados com o passar do tempo, conforme aprimoro meu conhecimento e a colaboração dos colegas.

## O código
Uma das minhas atribuições como desenhista projetista mecânico é desenvolver os desenhos técnicos dos produtos, especificando todas as suas características dimensionais e geométricas. Algumas peças possuem geometrias complexas difíceis de mensurar e representar graficamente. Ainda mais quando para gerar certa geometria no software CAD seja necessário coletar uma coleção de coordenadas, sejam elas polares ou cartesianas.
Instrumentos e equipamentos de medição modernos ajudam coletar estas coordenadas com exatidão e rapidez, mas, às vezes, exportar estes pontos para um software CAD manualmente consome tempo e pode levar a erros. Além do mais, se o equipamento de medição gerar algum tipo de arquivo com os dados coletados, nem sempre este estará organizado ou no formato aceito pelo software CAD.
Então, esta foi a motivação para o desenvolvimento do código: tratar os dados do arquivo de texto gerado pelo equipamento de medição e salvá-los no formato de arquivo que o software CAD aceite importar.
O código original que criei possui uma GUI desenvolvida com tkinter, onde posso informar tanto o caminho onde está salvo o arquivo com os dados quanto o local de destino do novo arquivo, além de possuir os campos onde posso inserir os parâmetros da peça necessários para a geração dos novos dados. Aqui apresentarei uma versão simplificada, sem interface gráfica, que pode ser executada de forma simples, desde que tanto o arquivo de texto original quanto o arquivo JSON com os parâmetros da peça estejam no mesmo diretório do código.

## A peça a ser medida
Irei apresentar como exemplo um eixo comando de válvulas, que nos motores de combustão interna, são responsáveis por abrir e fechar as válvulas de admissão e escape no devido tempo. Os elementos do eixo comando de válvulas responsáveis por esta função são os cames radiais.

## O equipamento de medição
O equipamento, chamado MMCV (Módulo de medição de comando de válvulas), utiliza um encoder rotativo e um encoder linear para fazer uma varredura no perfil do came, registrando o deslocamento linerar gerado a cada divisão de grau na rotação da peça. Ao final da varredura, é gerado um arquivo de texto com as coordenadas polares (grau, deslocamento).