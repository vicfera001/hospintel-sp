# MVP de linguagem natural — HospIntel SP

O aplicativo `app.py` é independente do Power BI. Os dois produtos consultam a
mesma base Oracle, mas nenhum depende do outro para funcionar.

## Modos disponíveis

1. **Demonstração local:** utiliza o CSV processado e responde a exemplos
   previamente definidos. Não exige wallet nem acesso à internet.
2. **Oracle Select AI:** transforma perguntas livres em SQL, valida o SQL
   localmente e somente depois executa a consulta no Oracle.

## Arquitetura do Select AI

O perfil `HOSPINTEL_AI` pertence ao esquema `ADMIN` e utiliza o provedor Cohere.
O usuário restrito `HOSPINTELAPP` não acessa diretamente a credencial de IA.

O fluxo implementado é:

```text
Pergunta no Streamlit
    → HOSPINTELAPP
    → ADMIN.HOSPINTEL_GENERATE_SQL
    → perfil HOSPINTEL_AI
    → geração de SQL pelo Select AI
    → validação local de somente leitura
    → execução nas views autorizadas
    → resultado exibido com o SQL utilizado

```

## Publicação no Streamlit Community Cloud

O aplicativo pode ser publicado a partir do repositório GitHub. No ambiente
hospedado, a wallet Oracle não deve ser adicionada ao repositório. O arquivo ZIP
da wallet deve ser convertido para Base64 e armazenado exclusivamente nos
secrets do Streamlit Community Cloud.

Variáveis necessárias no ambiente hospedado:

```text
APP_MODE=oracle
ORACLE_USER=HOSPINTELAPP
ORACLE_PASSWORD=<SENHA_DO_USUARIO_DO_BANCO>
ORACLE_DSN=fiap_low
ORACLE_WALLET_PASSWORD=<SENHA_DA_WALLET>
SELECT_AI_PROFILE=HOSPINTEL_AI
ORACLE_WALLET_ZIP_B64=<CONTEUDO_BASE64_DO_ZIP_DA_WALLET>
```

No ambiente hospedado, `ORACLE_CONFIG_DIR` deve permanecer ausente. O aplicativo
decodifica a wallet em um diretório temporário protegido durante a execução.

Depois da publicação, a URL HTTPS do aplicativo pode ser utilizada em um botão
do Power BI com a ação **Web URL**, permitindo que o usuário abra a interface de
consultas em linguagem natural.
