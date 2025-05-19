## Escolha da API

A API escolhida foi a Jikan, uma API não oficial do My Anime List. A escolha por essa API é que eu queria fazer o site sobre algo que eu gostasse e eu gosto de animes. Das APIs listadas no repositório das APIs públicas no github, essa tinha uma boa quantidade de dados e não precisa fazer autenticação para fazer requisições na API, o que poupa tempo e simplifica a utilização.

## Como Funciona o cache dos dados

No meu projeto, tem um campo de texto onde o usuário irá informar o título do anime que ele quer pesquisar, caso seja a primeira vez que aquele título esteja sendo pesquisado, a função que processa a requisição irá fazer uma requisição para a API do Jikan, que por sua vez retornará uma lista de objetos que tenham um título correspondente ao título informado pelo usuário, essa lista será tratada no backend, para facilitar a manipulação dos valores e então será criado um registro no banco de dados local para cada objeto da lista, fazendo assim um cache desses dados para diminuir o tempo de busca nas próximas requisições para esse título, os dados tratados são transformados em um JSON e enviados como resposta a requisição. No front-end, esses dados são capturados e renderizados, alterando o DOM da página para incluir uma seção de animes com os dados retornados da pesquisa do usuário.

## Como funciona o sistema de favoritos

Para fazer o sistema de favoritos, criei uma classe para representar uma tabela no banco de dados que seria responsável por representar o relacionamento entre o usuário e os animes, a tabela tem um campo para armazenar o id do anime e um campo para armazenar o id do usuário e um parâmetro backref para possibilitar o acesso de todos os animes favoritos a partir do modelo User e vice-versa.
Caso o usuário esteja logado, quando ele pesquisar animes, para cada anime que aparecer, irá ter um botão de adicionar aquele anime aos favoritos. Quando ele clica, o botão envia uma requisição ao back-end passando o id único do My Anime List, esse id é acessado no back-end para fazer uma consulta na tabela de Animes filtrando pelo mal_id e pegando o primeiro resultado correspondente (caso o anime não exista, é enviada um json que informa o erro 404) e usando o método current_user do flask_login para obter o id do usuário. Caso o anime já tenha sido favoritado, é exibida uma mensagem de que aquele anime já está nos favoritos do usuário, caso contrário, o anime é favoritado.

Quando o usuário está logado, aparecerá na navbar o "Profile", que é o perfil do usuário onde é listado todos seus animes favoritos. Cada usuário verá apenas os animes que ele favoritou, caso não tenha favoritado nenhum, aparece uma mensagem de que ele ainda não tem nenhum anime favoritado.

## Como executar a aplicação

Para executar a aplicação, é necessário instalar as dependências do projeto:

```bash
pip install --requirement requirements.txt
```

E então subir o projeto:

```bash
py app.py
```

Eu utilizei o windows para configurar o ambiente virtual e desenvolver a aplicação, então talvez no Linux seja necessário criar um novo ambiente virtual e baixar as dependências do projeto dentro dele.