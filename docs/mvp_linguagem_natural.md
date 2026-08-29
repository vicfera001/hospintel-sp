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
