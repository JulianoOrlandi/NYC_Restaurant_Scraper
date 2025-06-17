# **NEW YORK CITY RESTAURANTS DATA FETCHER**

### **Autor: Juliano Orlandi**

<br>

⚠️ Clique [aqui](README.md) para ver a versão em inglês


### **Descrição:**

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

⚠️ **O uso da Places API (New) é pago!** Você será cobrado no seu cartão de crédito com base no número de requisições feitas pela sua aplicação. Para mais detalhes sobre os custos, consulte o [Item 4 abaixo](#4-preparing-the-parameters-for-the-api-request) ou [a documentação oficial da API](https://mapsplatform.google.com/intl/en-US/pricing/).

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

O objetivo deste trecho do código é gerar uma lista de tuplas, onde cada item representa um quadrante geográfico válido dentro dos limites da cidade. Cada tupla contém duas sub-tuplas, com dois valores cada: latitude e longitude. A primeira sub-tupla corresponde ao vértice sudoeste do quadrante e a segunda ao vértice nordeste.
Esses valores serão utilizados para delimitar as áreas em que as requisições à API serão feitas — mais sobre isso no [item 4](#4-preparing-the-parameters-for-the-api-request).

Um exemplo do formato de retorno seria: `[((40.7, -74.0), (40.72, -73.98)), ((40.72, -74.0), (40.74, -73.98)), ...]`.

O nome da cidade é passado como string para uma variável chamada `place_name`. Ele deve seguir o formato `"Cidade, Estado (ou Região), País"`, pois isso facilita o trabalho do serviço de geocodificação interno da biblioteca `OSMnx`: [**Nominatim**](https://nominatim.openstreetmap.org/) (pertencente ao `OpenStreetMap`). Além de `place_name`, também é passado um número inteiro para a variável `num_divisions`, que define em quantas partes (ou quadrantes) cada lado do mapa da cidade será dividido. No código, foi utilizada uma divisão de 30 x 30, totalizando 900 quadrantes.

Nas primeiras linhas da função `create_quadrants()`, o código utiliza a biblioteca `OSMnx` para obter os limites geográficos da cidade como um polígono (`city_polygon`). Em seguida, calcula as dimensões de cada quadrante com base no valor de `num_divisions` e inicia um laço para gerar as coordenadas (latitude e longitude) dos vértices sudoeste e nordeste de cada quadrante em que o mapa será dividido. Antes de adicionar essas coordenadas à lista `quadr_val` — que será retornada ao final da função — o código verifica se o quadrante se intersecta com os limites do polígono da cidade. Caso haja interseção, o quadrante é incluído na lista; caso contrário, é descartado.

<div style="text-align: center;">
  <img src="images/nyc_quadrants.png" alt="NYC Quadrants" width="500"/>
</div>

<br>

A razão pela qual é necessário dividir o mapa da cidade em vários quadrantes está diretamente relacionada ao funcionamento da [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). Cada requisição feita à API retorna, no máximo, **20** itens dentro da área especificada. Caso existam mais resultados, a resposta incluirá também um valor na variável `pageToken`. Esse token permite realizar uma nova requisição para obter os itens seguintes. Se ainda houver resultados, a API retorna um novo `pageToken`, permitindo uma terceira e última chamada. O problema é que existe um limite de três páginas por requisição, o que significa que no máximo **60** itens podem ser retornados por área consultada. Por exemplo: se a requisição for feita utilizando coordenadas que abrangem toda a cidade de Nova Iorque, a resposta conterá apenas **20** resultados iniciais, mais duas páginas adicionais com até **20** itens cada — totalizando apenas **60** locais. Isso é insuficiente para capturar todos os restaurantes da cidade. É por isso que a subdivisão da área em quadrantes é fundamental: ela reduz a área de cada requisição, aumentando a chance de obter todos os itens presentes em cada região. Vale observar ainda que o mapa retangular utilizado para a divisão pode incluir áreas fora da cidade — como regiões vizinhas ou até partes do oceano. Por isso, a função `create_quadrants()` verifica se cada quadrante gerado se intersecta com os limites reais do polígono da cidade. Apenas os quadrantes válidos são incluídos na busca, evitando requisições inúteis.

---
<br>

### **4. Preparing the parameters for the API request**

Após gerar os quadrantes válidos para consulta, o próximo passo consiste em configurar os parâmetros que serão utilizados nas requisições feitas à [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). Essa configuração ocorre por meio de duas variáveis: `url` e `headers`, que representam, respectivamente, o **endpoint da API** e os **cabeçalhos HTTP** necessários para autenticação e formatação da requisição.

O endpoint `https://places.googleapis.com/v1/places:searchText` permite realizar buscas de lugares com base em termos textuais, como por exemplo: "restaurant", "pharmacy", "supermarket", etc. Esse é o mesmo tipo de busca que se faria manualmente na caixa de pesquisa do **Google Maps**. A resposta da API retorna locais compatíveis com o termo pesquisado, levando em consideração a área geográfica delimitada nos parâmetros da requisição. Como o objetivo deste script é obter dados de **todos** os estabelecimentos de uma determinada categoria, é recomendável escolher o termo de busca entre os tipos listados na própria documentação da API. A lista completa se encontra na [Tabela A](https://developers.google.com/maps/documentation/places/web-service/place-types).

A variável `headers` define os **cabeçalhos HTTP** que acompanham cada requisição feita à API, sendo essencial para garantir tanto a autenticação quanto a correta formatação dos dados. O campo `Authorization` utiliza o token de acesso gerado anteriormente pela função `get_access_token()`, no formato `Bearer`, que é o padrão adotado pelo protocolo OAuth 2.0. Já o campo `Content-Type` é definido como "application/json", indicando que o corpo da requisição será enviado no formato JSON, como exigido pela [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). O campo `X-Goog-FieldMask` especifica exatamente quais campos se deseja receber na resposta: o nome, o telefone, o endereço, a avaliação dos usuários, etc. A lista com todos os campos está disponível na [documentação do Text Search](https://developers.google.com/maps/documentation/places/web-service/text-search).

⚠️ É preciso frisar que os possíveis campos de resposta da API estão organizados pelo **Google** em diferentes categorias chamadas de `SKUs` (**Stock Keeping Units**), que funcionam como unidades de tarifação. Cada `SKU` corresponde a um conjunto de funcionalidades ou informações específicas fornecidas pela API. O uso de cada uma tem um custo associado, e os preços variam de acordo com a complexidade e o valor dos dados fornecidos. Isso significa que quanto mais campos forem incluídos no parâmetro `X-Goog-FieldMask`, maior será o custo por requisição.

⚠️ Um exemplo ajuda a esclarecer. Se uma requisição for feita com os campos `places.displayName` e `places.formattedAddress`, que estão associados a `Text Search Pro SKU`, o custo será na data de hoje (18/04/2025) de **$0,032** por requisição — já que, conforme a [tabela oficial](https://mapsplatform.google.com/intl/en-US/pricing/) de preços da API, 1000 chamadas dessa SKU custam **$32**. Por outro lado, se uma requisição for feita com os campos `places.priceRange` e `places.rating`, vinculados à `Text Search Enterprise SKU`, o custo será de **$0,035**, pois 1000 chamadas dessa SKU custam **$35**.

⚠️ Agora — e aqui está o ponto mais importante —, se uma mesma requisição incluir os **quatro campos mencionados acima, ela acionará duas SKUs simultaneamente**. Nesse caso, o custo total da chamada será de **$0,067**: **$0,032** referentes aos campos da `Text Search Pro SKU` somados aos **$0,035** dos campos da `Text Search Enterprise SKU`. É fundamental estar atento a essa dinâmica de tarifação, pois, com um volume elevado de requisições, os custos podem escalar de forma bastante significativa. Portanto, antes de definir os campos desejados na resposta, é altamente recomendável consultar a documentação oficial e estimar os custos com base no volume esperado de chamadas.

A variável `data_template` funciona como um molde para a construção do corpo das requisições enviadas à [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview). Ela contém os parâmetros que controlam a busca. O campo `textQuery` especifica o termo de interesse - por exemplo, "restaurant". Como discutido acima, é recomendável escolhê-lo entre os tipos listados na [documentação da API](https://developers.google.com/maps/documentation/places/web-service/place-types). Já o campo `locationRestriction` define a área geográfica em que a busca deve ocorrer. Ele é estruturado como um retângulo (`rectangle`) delimitado por dois pares de coordenadas geográficas. A chave `low` representa o vértice sudoeste e a chave `high` representa o vértice nordeste, sendo que ambas contêm valores explícitos de `latitude` e `longitude`. Por fim, o campo `pageToken` é utilizado para controlar a paginação das requisições e permite o acesso aos demais resultados da busca que não foram incluídos na resposta.

Há ainda mais duas variáveis criadas nesse trecho do código: `all_places` e `request_count`. A primeira é um lista que servirá para armazenar o conteúdo retornado pelas requisições. E a segunda é um `integer` utilizada para controlar o número de requisições feitas a [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview).



---
<br>

### **5. Loop through the quadrants to perform the search using the process_quadrant function**

O script entra agora na etapa principal de execução: iterar sobre os quadrantes válidos da cidade e realizar as requisições à API. Essa operação é feita com um laço `for`, que percorre cada quadrante gerado anteriormente pela função `create_quadrants()`. Para cada item da lista `quadrants`, o código chama a função `process_quadrant()`, que recebe os seguintes parâmetros:

- `sw` (tupla): (latitude, longitude) do canto sudoeste;
- `ne` (tupla): (latitude, longitude) do canto nordeste;
- `data_template` (dict): o molde de construção do corpo das requisições;
- `url` (str): o endpoint da API;
- `headers`(dict): os cabeçalhos HTTP que acomapanham a requisição;
- `request_count` (int): a variável para controlar o número de requisições feitas.

A função `process_quadrant()` é responsável por realizar a requisição à API e retornar os resultados encontrados dentro de um determinado quadrante. Em primeiro lugar, ela preenche os valores de latitude e longitude das chaves `low` e `high` do parâmetro `locationRestriction` do `data_template`, utilizando as tuplas `sw`e `ne`. Passa então esta variável junto com `headers` e `url` como os parâmetros da função `fetch_places_by_quadrant()`. É essa função que, de fato, realiza a chamada à API e retorna os resultados em uma lista chamada `places`. Além disso, ela gerencia automaticamente a paginação da API por meio da variável `next_page_token`, garantindo o acesso ao maior número possível de itens dentro da área geográfica consultada.

Após obter a lista de resultados, a função `process_quadrant()` verifica se ela contém exatamente 60 itens — o número máximo que pode ser retornado pela API em uma única sequência de requisições. Se isso ocorrer, o código assume que os dados foram truncados, o que indica que há mais estabelecimentos presentes naquela região do que foi possível obter com apenas três páginas. Para contornar essa limitação, a função chama `subdivide_quadrant()`, passando como argumentos as coordenadas dos cantos sudoeste e nordeste do quadrante original, além do número de divisões desejadas. Essa função divide o quadrante inicial em subáreas menores — no caso, nove subquadrantes — que são retornados como uma lista de coordenadas. A função `process_quadrant()` então itera sobre cada um desses subquadrantes, chamando a si mesma de forma recursiva para realizar novas requisições dentro dessas regiões menores. Essa abordagem garante que a limitação da [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview) quanto ao número máximo de itens por área seja contornada de maneira eficiente, permitindo que o script recupere todos os estabelecimentos de uma determinada categoria, mesmo em regiões densamente povoadas.

Por fim, os resultados coletados em cada iteração — incluindo os de subquadrantes, se houver — são agregados à lista `all_places`, que concentra todos os estabelecimentos encontrados ao longo da execução do script.


---
<br>

### **6. Save the results to a JSON file after completing the search**

Finalizada a coleta dos dados, os resultados são salvos usando a função `save_results_to_json()`. Ela recebe a lista `all_places` e grava o conteúdo em um arquivo `.json` dentro da pasta `results`. O nome do arquivo inclui data e hora da execução para evitar sobrescritas e manter o histórico organizado.