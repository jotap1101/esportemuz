<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# EsporteMuz - Sistema de Gerenciamento de Campeonatos

Este é um sistema web completo desenvolvido em Django para gerenciamento de campeonatos de futsal e futebol.

## Arquitetura do Projeto

- **Backend**: Django 5.2.4 com Python
- **Frontend**: HTML, CSS, JavaScript e Bootstrap 5 integrados via templates Django
- **Banco de Dados**: SQLite (desenvolvimento)
- **Autenticação**: Sistema padrão do Django

## Estrutura dos Modelos

### Principais entidades:
- `Campeonato`: Gerencia campeonatos (pontos corridos ou grupos+mata-mata)
- `Equipe`: Informações das equipes participantes
- `Participacao`: Relaciona equipes aos campeonatos
- `Rodada`: Organiza partidas em rodadas
- `Partida`: Registro de jogos e resultados
- `Classificacao`: Tabela de classificação calculada automaticamente

## Padrões de Desenvolvimento

### Views:
- Use function-based views com decorators apropriados
- Implemente paginação para listagens
- Use context processors para dados comuns
- Aplique filtros via QueryParams

### Templates:
- Extend sempre de `base.html`
- Use Bootstrap 5 para componentes UI
- Implemente responsividade mobile-first
- Use modais para formulários de criação/edição

### JavaScript:
- Use fetch() para requisições AJAX
- Implemente validações client-side
- Use SweetAlert2 para alertas
- Mantenha funções organizadas no namespace `EsporteMuz`

### CSS:
- Use classes do Bootstrap 5 como base
- Customize apenas quando necessário
- Mantenha variáveis CSS no `:root`
- Implemente animações sutis

## Services e Lógica de Negócio

### CampeonatoService:
- Geração automática de rodadas
- Distribuição de equipes em grupos
- Validações de configuração

### ClassificacaoService:
- Cálculo automático de pontuação
- Ordenação por critérios de desempate
- Atualização em tempo real

### PartidaService:
- Registro de resultados
- Validações de dados
- Triggers para atualização de classificação

## Convenções de Nomenclatura

- Modelos: PascalCase em português (`Campeonato`, `Equipe`)
- Views: snake_case descritivo (`campeonato_detail`, `registrar_resultado`)
- URLs: kebab-case (`campeonatos/`, `gerar-rodadas/`)
- Templates: snake_case com sufixo (`campeonato_form.html`)
- CSS Classes: Bootstrap + custom prefixados (`team-logo`, `match-card`)

## Funcionalidades Específicas

### Sistema de Classificação:
- Pontos: 3 vitória, 1 empate, 0 derrota
- Critérios desempate: pontos > saldo > gols pró > nome
- Atualização automática via signals

### Geração de Rodadas:
- Pontos corridos: todos contra todos
- Grupos: combinações dentro de cada grupo
- Validação mínima de 2 equipes

### Interface do Usuário:
- Dashboard com estatísticas
- Filtros dinâmicos
- Modais para ações rápidas
- Feedback visual com badges e cores

## APIs e Endpoints

### AJAX Endpoints:
- `/api/registrar-resultado/`: POST para salvar resultados
- `/api/adicionar-equipe-campeonato/`: POST para adicionar equipes
- `/api/classificacao/<id>/`: GET para tabela atualizada
- `/api/equipes/`: GET para busca de equipes

### Autenticação:
- Use o sistema Django Admin para login/logout
- Proteja endpoints de modificação com `@login_required`
- Valide permissões conforme necessário

## Considerações de Performance

- Use `select_related()` e `prefetch_related()` em queries
- Implemente cache para classificações quando necessário
- Otimize queries com `only()` e `defer()` quando apropriado
- Use paginação para grandes datasets

## Tratamento de Erros

- Capture exceções específicas nos services
- Retorne mensagens user-friendly
- Log erros importantes para debug
- Use transações para operações críticas

## Testes e Qualidade

- Implemente testes unitários para services
- Teste views com diferentes cenários
- Valide formulários com dados inválidos
- Teste responsividade em diferentes dispositivos
