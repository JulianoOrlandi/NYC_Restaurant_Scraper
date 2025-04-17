# **NEW YORK CITY RESTAURANT SCRAPER**

### **Autor: Juliano Orlandi**

<br>

### **Description:**

Este script implementa a busca automatizada de dados sobre resturantes na cidade de Nova Iorque, utilizando a [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview) do Google. O objetivo final é construir uma base de dados contendo informações como endereço, telefone, horário de funcionamento, avaliações de clientes, entre outras.

O código principal se encontra no arquivo [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py). No entanto, ele faz uso de um conjunto de funções auxiliares disponíveis no arquivo [helpers.py](helpers.py). Para fins didáticos, a explicação a seguir acompanha a estrutura do código principal. À medida que as funções auxiliares forem aparecendo, suas respectivas implementações no arquivo de suporte serão explicadas.

---
<br>

### **1. Imports**

No arquivo [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py), são importadas principalmente as funções definidas no arquivo [helpers.py](helpers.py). As dependências utilizadas são as seguintes:

| Requisito                | Versão |
|---------------------------|--------|
| **Python**                | 3.11.9 |
| **google_auth_oauthlib**  | 1.2.1  |
| **osmnx**                 | 2.0.2  |
| **pandas**                | 2.2.3  |
| **protobuf**              | 6.30.2 |
| **Requests**              | 2.32.3 |
| **Shapely**               | 2.1.0  |


---
<br>

### **2. Get Google's API access_token**

Antes de utilizar a função `get_access_token()`, que está presente na única linha de código deste trecho, é necessário criar um projeto no [Google Cloud Console](https://console.cloud.google.com/), habilitar o uso da [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview), configurar a tela de consentimento do OAuth, gerar as credenciais apropriadas e fazer o download do arquivo `credentials.json`. Abaixo está o passo a passo deste processo. Antes de prosseguir, no entanto, é importante deixar claro:

**O USO DA PLACES API (NEW) É PAGO!**

Você será cobrado no seu cartão de crédito com base no número de requisições feitas pela sua aplicação. Para mais detalhes sobre os custos da Places API (New), consulte:  
[https://mapsplatform.google.com/intl/en-US/pricing/](https://mapsplatform.google.com/intl/en-US/pricing/)

#### **2.1. Criar um projeto no Google Cloud Console:**
- Acesse o [Google Cloud Console](https://console.cloud.google.com/);
- Clique em "Select a project" no topo da tela;
- Clique em "New Project";
- Preencha o `Project Name`;
- Clique em `Create`.

#### **2.2. Habilitar o uso da Places API (New):**
- No menu de navegação (canto superior esquerdo), clique em `APIs & Services > Library`;
- Na barra de busca, pesquise `Places API (New)`;
- Clique na opção correspondente;
- Ative a API, clicando em `Enable`;
- Clique em `Go to Google Cloud Plataform`;
- Clique em `Maybe later`;

#### **2.3. Configurar a tela de consentimento do OAuth:**
- No menu de navegação (canto superior esquerdo), clique em `APIs & Services > OAuth consent screen`;
- Clique em `Get started`;
- Preencha o `App Name`;
- Escolha seu endereço de e-mail em `User support email`;
- Escolha `external` em `Audience`;
- Coloque seu endereço de e-mail em `Contact information`;
- Marque que concorda com a [Google API Services: User Data Policy](https://developers.google.com/terms/api-services-user-data-policy) em `Finish`;
- Clique em `Create`.

#### **2.3. Gerar as credenciais:**
- No menu de navegação (canto superior esquerdo), clique em `APIs & Services > Credentials`;
- Clique em `Create credentials > OAuth client ID`;
- Em `Application Type`, escolha `Desktop App`;
- Preencha o `Name`;
- Clique em `Create`;
- Na tela `OAuth client created`, clique em `Download JSON`;
- Salve o arquivo baixado com o nome `credentials.json` na raiz do seu projeto.

<br>

A função `get_access_token()` recebe três parâmetros:
- `credentials_file` (str): Caminho para o arquivo JSON com as credenciais OAuth 2.0;
- `token_file` (str): Caminho onde o token gerado será armazenado para uso futuro;
- `scopes` (list): Lista de permissões (escopos) que a aplicação precisará para acessar a API do Google.

Se o parâmetro `scopes` não for fornecido, o valor padrão será o escopo mais amplo (`'https://www.googleapis.com/auth/cloud-platform'`), permitindo o acesso à plataforma do Google Cloud. A função verifica então se já existe um arquivo de token válido. Caso exista, o token é carregado e retornado. Se não houver um token válido ou se o token estiver expirado, o processo de autenticação é iniciado utilizando as credenciais do arquivo `credentials.json`. A função salva o token obtido em `token.json`para uso futuro e o retorna para a variável `access_token` em [nyc_restaurant_scraper.py](nyc_restaurant_scraper.py).

---
<br>

### **3. Subdividing the city into quadrants to narrow down the search area**

A.

---
<br>

### **4. Preparing the parameters for the API request**

A.

---
<br>

### **5. Loop through the quadrants to perform the search using the process_quadrant function**

A.

---
<br>

### **6. Save the results to a JSON file after completing the search**