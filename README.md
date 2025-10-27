## Painel de Cotações – Backend

Este serviço expõe a API consumida pelo frontend React do projeto **Painel de Cotações**. Ele encapsula o acesso à AwesomeAPI, aplica regras de negócio (filtros, favoritos por cliente) e entrega respostas padronizadas para o aplicativo web.

### Visão geral
- **Stack**: Django 5, Django REST Framework, SQLite (desenvolvimento)
- **Integração externa**: [AwesomeAPI Economia](https://docs.awesomeapi.com.br/api-de-moedas)
- **Identificador de cliente**: cabeçalho `X-Client-Id` com UUID gerado pelo frontend

### Endpoints planejados
| Método | Caminho | Descrição | Entrada | Saída |
| --- | --- | --- | --- | --- |
| `GET` | `/api/symbols` | Catálogo de pares suportados. | – | `{"symbols": ["USD-BRL", ...]}` |
| `GET` | `/api/quotes` | Cotações atuais para os símbolos solicitados (ou todos). | Query `symbols=USD-BRL,EUR-BRL` (opcional) | `{"quotes": [{ "symbol": "USD-BRL", "price": 5.18, ... }]}` |
| `GET` | `/api/favorites` | Lista os símbolos favoritos do cliente. | – | `{"favorites": ["USD-BRL", ...]}` |
| `POST` | `/api/favorites` | Adiciona um símbolo aos favoritos. | JSON `{"symbol": "USD-BRL"}` | `201 Created` com `{ "symbol": "...", "favorited": true }` |
| `DELETE` | `/api/favorites/<symbol>` | Remove o símbolo favorito. | – | `204 No Content` |

> Todas as operações de favoritos exigem o cabeçalho `X-Client-Id`.

### Como executar
```bash
# 1. Ambiente virtual (Windows)
python -m venv .venv
.venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt

# 3. Banco de dados
python manage.py migrate

# 4. Servidor de desenvolvimento
python manage.py runserver
```

### Testes automatizados
Após implementar os testes de integração:
```bash
pytest          # ou python manage.py test
```

### Deploy no Render (guia rápido)
1. Crie um serviço **Web Service** apontando para este repositório.
2. Configure o runtime como *Python* e o comando de inicialização para `gunicorn core.wsgi:application` (ou deixe o Render detectar o `Procfile` automaticamente).
3. Defina variáveis de ambiente:
   - `DJANGO_SECRET_KEY`: uma chave segura gerada por você.
   - `DJANGO_DEBUG=false`
   - `DJANGO_ALLOWED_HOSTS=<domínio-do-render>` (ex.: `painel.onrender.com`)
   - `DJANGO_CORS_ALLOWED_ORIGINS=https://<domínio-do-frontend>`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://<domínio-do-frontend>`
4. Execute `python manage.py migrate` a partir do dashboard do Render (aba Shell) após o primeiro deploy.
5. Opcional: ative auto deploy via GitHub e configure uma pipeline de testes (`python manage.py test`) antes do deploy.
