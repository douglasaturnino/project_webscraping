
# Monitoramento de Preço com Web Scraping e Notificações no Telegram

Este projeto realiza o monitoramento de preços de produtos do mercado livre. Utilizando técnicas de web scraping, o projeto coleta preços e envia notificações no Telegram quando o valor atinge um preço menor que o atual. A aplicação é modular, dividida em partes para facilitar o desenvolvimento e a manutenção.

## Esse projeto faz parte do workshop de Web Scraping

Assista ao vídeo completo aqui pelo [link](https://youtube.com/live/z1EOlFV8g7g)

## Mode de uso
Para usar o bot é necessario alguns pesquisar o bot no telegram por [@dsoscanprices_bot](https://t.me/dsoscanprices_bot)
O bot aceita os comandos listados abaixo:

"<b>/link [URL]</b> - Adicione um link para monitoramento de preços. O bot verificará o preço periodicamente e informará se houver alterações.\n"
"<b>/cancel [URL]</b> - Cancele o monitoramento de um link específico. Isso interromperá a verificação de preços para o link fornecido.\n"
"<b>/check</b> - Liste todos os links que estão sendo monitorados atualmente. Use este comando para verificar quais links estão ativos.\n"
"<b>/help</b> - Obtenha ajuda sobre como usar os comandos e funcionalidades do bot.\n\n"

Quando é enviado alguma mensagem para o bot que não seja algum dos comandos ele funciona como um repedidor de texto.

## Arquitetura

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Bot as Bot Telegram
    participant Script as Script Principal
    participant DB as Banco de Dados (postgres)
    participant ML as Mercado Livre

    User->>Script: Inicia o script
    Script->>ML: fetch_page() - Requisição para obter HTML da página
    ML-->>Script: Responde com HTML da página

    Script->>Script: parse_page() - Extrai informações de preço e produto
    Script->>DB: create_connection() - Conecta ao banco de dados
    Script->>DB: setup_database() - Cria tabela 'prices' se não existir
    Script->>DB: get_min_price() - Consulta o menor preço registrado

    alt Se não houver preço registrado
        Script->>Bot: send_telegram_message() - "Novo preço menor detectado"
        Bot-->>User: Notificação via Telegram
    else Se houver preço registrado
        Script->>Script: Compara o preço atual com o menor preço registrado
        alt Se o preço atual for menor
            Script->>Bot: send_telegram_message() - "Novo menor preço detectado"
            Bot-->>User: Notificação via Telegram
        else Se o preço atual não for menor
            Script->>Bot: send_telegram_message() - "Menor preço registrado é X"
            Bot-->>User: Notificação via Telegram
        end
    end

    Script->>DB: save_to_database() - Salva informações de preço e produto
    Script->>Script: Aguarda 600 segundos antes de repetir o processo
    loop Loop contínuo
        Script->>ML: Requisição para atualizar preço
        ML-->>Script: Responde com novo preço
        Script->>Script: Processo de verificação e notificação se repete
    end
```

## Bibliotecas Utilizadas e Explicação

1. **requests**: Usada para fazer requisições HTTP e obter o HTML das páginas web.
2. **BeautifulSoup (bs4)**: Utilizada para analisar e extrair informações específicas do HTML das páginas, como o preço do produto.
3. **schedule**: Biblioteca para agendar tarefas, permitindo verificar preços em intervalos regulares.
4. **pandas**: Facilita a manipulação de dados, permitindo salvar e carregar históricos de preços em arquivos CSV.
5. **sqlite3**: Um banco de dados SQLite leve, usado para armazenar e organizar dados de preços ao longo do tempo.
6. **python-telegram-bot**: Biblioteca para enviar mensagens ao Telegram, notificando o usuário quando o preço atinge um valor específico.
7. **python-dotenv**: Carrega variáveis de ambiente de um arquivo `.env`, onde são armazenadas informações sensíveis como o token e o chat ID do Telegram.

## Pré-requisitos

1. **Python 3.12+**: Certifique-se de ter o Python 3.12 ou superior instalado.
2. **Dependências**: Instale as bibliotecas listadas no arquivo `requirements.txt`.

Para instalar as dependências, execute o comando:
```bash
pip install -r requirements.txt
```

## Configuração

1. **Configuração do Telegram**: Crie um bot no Telegram usando o BotFather e obtenha o token de autenticação.
2. **Arquivo `.env`**: Crie um arquivo `.env` na raiz do projeto e insira as credenciais do Telegram:
   ```
   TELEGRAM_TOKEN=SEU_TOKEN_DO_TELEGRAM
   ```
   - Substitua `SEU_TOKEN_DO_TELEGRAM` com o token do seu bot.

3. **Configuração do Banco de Dados**: O banco de dados SQLite será criado automaticamente na primeira execução.

## Estrutura dos Aplicativos

### `app`: Envio de Notificação com `Telegram`
Esse módulo utiliza a biblioteca python-telegram-bot para enviar uma mensagem ao Telegram informando que o preço atingiu o valor desejado.

### `config`: Configuração das variaveis de ambiente
Arquivo onde são carregadas as configurações de ambiente do aplicativo

### `database`: 
Esse módulo gerencia o banco de dados postgres, criando tabelas e armazenando informações do histórico de preços.

### `scraper`:
Modulo onde faz o webcraping dos links 

## Como Executar

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/douglasaturnino/project_webscraping
   cd project_webscraping
   ```

2. **Instale as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o `.env`**:
   - Siga as instruções em "Configuração" e adicione o arquivo `.env` com as variáveis de ambiente para o bot do Telegram.

4. **Execute o Script**:
   ```bash
   python app_8_postgres.py
   ```

O projeto agora iniciará o monitoramento do preço de produtos, verificando em intervalos regulares e notificando o usuário via Telegram caso o preço atinja o valor desejado.

Caso queira fazer um teste local

5. **Execute o postgres para um teste local**:
   ```bash
   docker compose up postgres
   ```

## Migrando para Postgres

Para migrar de SQLite para PostgreSQL, você pode usar a biblioteca `psycopg2` para conectar-se ao banco de dados PostgreSQL. Abaixo está o código atualizado para suportar o PostgreSQL. Vou explicar as mudanças e as etapas adicionais necessárias para configurar o ambiente.

1. Primeiro, instale o `psycopg2`:
   ```bash
   pip install psycopg2-binary
   ```

2. Atualize o arquivo `.env` com as credenciais do PostgreSQL:
   ```env
   TELEGRAM_TOKEN=SEU_TOKEN_DO_TELEGRAM
   TELEGRAM_CHAT_ID=SEU_CHAT_ID
   POSTGRES_DB=nome_do_banco
   POSTGRES_USER=seu_usuario
   POSTGRES_PASSWORD=sua_senha
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

### Alterações Realizadas

- **Substituição do SQLite pelo PostgreSQL**: 
   - O módulo `sqlite3` foi substituído por `psycopg2`, que conecta-se ao PostgreSQL.
   - As variáveis de ambiente foram configuradas para receber as credenciais de conexão ao PostgreSQL.
   
- **Criação da Tabela `prices`**:
   - Utilizamos a sintaxe SQL específica do PostgreSQL para a criação da tabela `prices`.
   
- **Salvamento e Consulta de Dados**:
   - A função `get_min_price` consulta o maior preço registrado até o momento na tabela `prices` do PostgreSQL.
   - `save_to_database` salva o registro atual utilizando um `DataFrame` pandas.

### Observação
Caso deseje simplificar, você pode substituir a função `save_to_database` para um `INSERT` direto ao invés de `pandas.to_sql`, caso tenha dificuldades com integração pandas e PostgreSQL.

## Docker

Aqui estão os comandos para construir e executar o contêiner Docker com o `.env`:

1. **Construir a Imagem Docker**:
   Navegue até o diretório onde o `Dockerfile` está localizado e execute:

   ```bash
   docker build -t projetowebscraping .
   ```

   Esse comando cria uma imagem Docker chamada `projetowebscraping` usando o `Dockerfile` atual.

2. **Executar o Contêiner com as Variáveis de Ambiente do `.env`**:
   Para iniciar o contêiner e carregar as variáveis de ambiente do arquivo `.env`, use:

   ```bash
   docker compose up -d 
   ```

   - `-d`: Executa o contêiner em segundo plano (modo "detached").

Esse processo configurará o contêiner para rodar o `projetowebscraping` com as variáveis de ambiente do `.env`.


### Instalar o Docker

#### Instalar Dependências do Docker

Primeiro, instale os pacotes necessários para adicionar o repositório do Docker:
```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
```

#### Adicionar o Repositório Docker

Adicione a chave GPG do Docker e o repositório oficial:
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### Instalar Docker

Atualize novamente os pacotes e instale o Docker:
```bash
sudo apt update -y
sudo apt install docker-ce docker-ce-cli containerd.io -y
```

#### Iniciar e Habilitar o Docker

Inicie o Docker e configure-o para iniciar automaticamente ao ligar o sistema:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Configurar o Arquivo `.env` com as Variáveis de Ambiente

No diretório do projeto, crie o arquivo `.env` para armazenar as variáveis de ambiente necessárias:

```bash
sudo nano .env
```

Dentro do editor `nano`, insira as variáveis de ambiente do projeto:

```dotenv
# Telegram Bot
TELEGRAM_TOKEN=XXX

# PostgreSQL Database
POSTGRES_DB=XXX
POSTGRES_USER=XXX
POSTGRES_PASSWORD=XXX
POSTGRES_HOST=XXX
POSTGRES_PORT=XXX
```

Pressione `Ctrl + X` para sair, `Y` para confirmar as alterações e `Enter` para salvar.

### Construir a Imagem Docker

No diretório do projeto, onde o `Dockerfile` está localizado, construa a imagem Docker usando `sudo`:

```bash
sudo docker build -t projetowebscraping .
```

Esse comando cria uma imagem Docker chamada `projetowebscraping` com base no `Dockerfile`.

### Executar o Contêiner com o Arquivo `.env`

Agora que a imagem foi construída, execute o contêiner e carregue as variáveis de ambiente do `.env`:

```bash
sudo docker run -d --env-file .env --name projetowebscraping_container projetowebscraping
```

Explicação dos parâmetros:
- `-d`: Executa o contêiner em segundo plano.
- `--env-file .env`: Carrega as variáveis de ambiente do arquivo `.env`.
- `--name projetowebscraping_container`: Nome do contêiner.
- `projetowebscraping`: Nome da imagem Docker criada.

### Verificar os Logs do Contêiner

Para garantir que o contêiner está rodando corretamente, você pode verificar os logs com:

```bash
sudo docker logs projetowebscraping_container
```

Esse processo completo deve configurar sua instância Ubuntu com Git e Docker, permitir que você crie o `.env`, e rode o contêiner Docker do seu projeto com todos os comandos usando `sudo`.