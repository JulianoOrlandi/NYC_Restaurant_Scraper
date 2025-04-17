# **NEW YORK CITY RESTAURANT SCRAPER**

### **Autor: Juliano Orlandi**

<br>

### **Description:**

Este script implementa a busca autmatizada de dados sobre resturantes na cidade de Nova Iorque, utilizando a [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview) do Google. O objetivo principal é construir uma base de dados com informações tais como endereço, telefone, horário de funcionamento, avaliação dos clientes, etc.

O projeto é composto de diversos arquivos.






Este projeto foi desenvolvido com o intuito de aprendizado e desenvolvimento de técnicas área de *machine learning*. Trata-se, na verdade, de um desafio educacional proposto pela plataforma *Kaggle*. A página inicial da competição pode ser acessada [aqui](https://www.kaggle.com/competitions/spaceship-titanic). A ideia central era praticar os conhecimentos de *machine Learning* de tal modo que fosse possível comparar o meu trabalho com o trabalho de outras pessoas.

O contexto do desafio é o seguinte: no ano de 2912, uma espaçonave chamada *Titanic* transportava emigrantes no nosso sistema solar para três novos planetas habitáveis. Nas proximidades de *Alpha Centauri*, ela colidiu com uma anomalia espaço-temporal e praticamente a metade dos passageiros foi transportada para uma dimensão alternativa. O desafio é desenvolver um modelo de aprendizado de máquina que, utilizando os registros recuperados da *Titanic*, seja capaz de prever quais passageiros foram transportados e quais não.

---
<br>

### **/data**

Nesta pasata estão os três arquivos fornecidos pelo *Kaggle* para a competição. [*"train.csv"*](data\train.csv) contém a base de dados para o treinamento do modelo. [*"test.csv"*](data\test.csv) contém o arquivo sem a coluna *target*, *"Transported"*, para utilizar o modelo e fazer as previsões. E [*"sample_submisson.csv"*](data\sample_submission.csv) contém um exemplo de formatação dos arquivos de submissão.

---
<br>

### **/notebooks**

Nesta pasta estão todos os *jupyter notebooks* que foram utilizados ao longo do trabalho. Eles estão divididos pelas datas que cobrem o período entre 06 e 29 de janeiro de 2025. Resolvi montar os arquivos deste modo para, em primeiro lugar, tornar o processo mais organizado e, em segundo, para evitar jogar código fora que posteriormente eu desejasse utilizar. Por isso, muitas vezes o código de um dia se repete no início do outro. É bem provável, no entanto, que o material seja muito confuso para que alguém possa tirar algum proveito dele. De qualquer forma, resolvi mantê-lo disponível no repositório.

---
<br>

### **spaceship_titanic_ml_project.ipynb**

Neste arquivo está o projeto completo e organizado. Está dividido em quatro grandes seções: **1. Imports**, **2. Data Preparation**, **3. Modelling** e **4. Submission**. A primeira contém apenas a importação de bibliotecas e módulos que são utilizados no restante do *notebook*. A segunda contém a **análise exploratória dos dados**, o **pré-processamento**, a **engenharia de atributos** e a **seleção dos atributos** para o modelo. A seção 3 está dividida, por sua vez, em **treinamento do modelo**, **avaliação** e **otimização dos hiperparâmetros**. A quarta seção corresponderia à **implantação** do modelo num projeto regular de *machine learning*. Como nesse caso se trata de um desafio do *Kaggle*, substituí pelo código que cria o arquivo de submissão.

---
<br>

### **gbc_model_trained.pkl**

Este arquivo corresponde ao modelo treinado com o algoritmo *Gradient Boosting*.

---
<br>

### **relatorio_final.md**

Este arquivo contém um relato organizado e detalhado de todos os passos do processo. Em certo sentido, ele é a explicação do código que se encontra em [spaceship_titanic_ml_project.ipynb](spacechip_titanic_ml_project.ipynb). Ele obedece, por conseguinte, mais ou menos a mesma divisão em seções que o *notebook*: **1. Introdução**, **2. Preparação dos Dados**, **3. Modelagem**, **4. Submissão** e **5. Conclusão**. Nesta última, apresento algumas reflexões sobre o desenvolvimento do projeto bem como sobre o meu desenvolvimento profissional ao longo do processo. Espero que outras pessoas possam tirar proveito da minha experiência.

---
<br>