## Fluxo de Tela – Baixa Fidelidade

Fluxo simples do painel web exibindo como o usuário interage com o sistema.

```
[Página Inicial]
    |
    |-- Cabeçalho: "Painel de Cotações"
    |
    |-- Seção de feedback
    |      - mensagens de erro/sucesso
    |
    |-- Grid com duas colunas
            |
            |-- Coluna 1: "Moedas Favoritas"
            |      - Lista de cards de moedas favoritas
            |      - Cada card exibe símbolo, preço, variação e botão ⭐
            |
            |-- Coluna 2: "Todas as Cotações"
                   - Lista de cards com todos os símbolos carregados
                   - Botão ⭐ para favoritar (move para coluna 1)
    |
    |-- Rodapé: lista de símbolos carregados

Interação principal:
1. Página carrega -> frontend chama `/api/symbols` e `/api/quotes`.
2. Usuário clica no botão ⭐ -> frontend chama `POST /api/favorites`.
3. Usuário desfavorita -> frontend chama `DELETE /api/favorites/<symbol>`.
```

> As chamadas de favoritos exigem o cabeçalho `X-Client-Id`, gerado automaticamente no navegador.
