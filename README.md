# Cálculo IDF - API

Esta API é parte de uma aplicação web para calcular a Intensidade-Duração-Frequência (IDF) a partir de dados de chuva. A API recebe um arquivo CSV com dados de chuva, faz upload do arquivo para o Firebase Storage, chama uma função do Google Cloud para calcular a IDF e retorna os resultados do cálculo.

## Funcionalidades

- Receber um arquivo CSV com dados de chuva.
- Fazer upload do arquivo CSV para o Firebase Storage.
- Chamar uma função do Google Cloud para calcular a IDF.
- Retornar os resultados do cálculo da IDF.

## Tecnologias Utilizadas

- Node.js para a criação da API.
- Express para a criação do servidor e das rotas.
- Multer para o tratamento de arquivos enviados em requisições multipart/form-data.
- Axios para fazer requisições HTTP para a função do Google Cloud.
- Firebase Admin SDK para interagir com o Firebase Storage.

## Como Usar

1. Clone este repositório para a sua máquina local.
2. Instale as dependências do projeto com o comando `npm install`.
3. Inicie a API com o comando `npm start`.
4. A API estará disponível na porta especificada no arquivo `.env` ou na porta 5000 se nenhuma porta for especificada.

## Estrutura do Projeto

- `src/app.cjs`: Este é o arquivo principal da API. Ele define a rota `/upload` para receber o arquivo CSV e iniciar o cálculo da IDF.
- `src/firebase.cjs`: Este arquivo contém funções para interagir com o Firebase Storage.

## Contribuindo

Contribuições são sempre bem-vindas! Sinta-se à vontade para abrir uma issue ou fazer um pull request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
