# EsporteMuz - Sistema de Gerenciamento de Campeonatos

Sistema web completo para gerenciamento de campeonatos de futsal e futebol, desenvolvido com Django e frontend integrado usando HTML, CSS, JavaScript e Bootstrap 5.

## 🎯 Objetivo

Resolver a falta de organização dos campeonatos locais, estruturando e automatizando a gestão dos campeonatos e partidas que hoje é feita de forma manual.

## ⚡ Funcionalidades Principais

### 🏆 Gerenciamento de Campeonatos
- Criação de campeonatos (pontos corridos ou grupos + mata-mata)
- Configuração de grupos, times por grupo e classificados
- Geração automática de rodadas e partidas
- Acompanhamento de status (planejado, em andamento, finalizado)

### 👥 Gerenciamento de Equipes
- Cadastro completo de equipes com escudo
- Organização por cidade e representante
- Vinculação a múltiplos campeonatos

### 📅 Sistema de Partidas
- Geração automática baseada no formato do campeonato
- Registro de resultados via interface amigável
- Controle de local, data e horário
- Status de partidas (pendente/finalizada)

### 📊 Classificação Automática
- Cálculo automático de pontos, vitórias, empates, derrotas
- Saldo de gols e critérios de desempate
- Atualização em tempo real após resultados
- Visualização por grupos (quando aplicável)

### 🎨 Interface Moderna
- Dashboard com estatísticas gerais
- Design responsivo para mobile, tablet e desktop
- Filtros dinâmicos e paginação
- Modais para ações rápidas
- Feedback visual com alertas e animações

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.4 + Python
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Database**: SQLite (desenvolvimento)
- **Autenticação**: Sistema Django Admin
- **UI Components**: Bootstrap Icons, SweetAlert2
- **Media Handling**: Pillow para upload de imagens

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passo a passo

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd esportemuz
```

2. **Crie e ative um ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute as migrações**
```bash
python manage.py migrate
```

5. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

6. **Inicie o servidor de desenvolvimento**
```bash
python manage.py runserver
```

7. **Acesse o sistema**
- Sistema: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 🚀 Como Usar

### 1. Primeiro Acesso
1. Acesse o sistema e faça login via Admin
2. Cadastre algumas equipes pelo menu "Equipes"
3. Crie um novo campeonato definindo o formato
4. Adicione equipes ao campeonato
5. Gere as rodadas automaticamente
6. Registre os resultados das partidas

### 2. Tipos de Campeonato

**Pontos Corridos**
- Todos os times jogam entre si
- Classificação única por pontos
- Ideal para campeonatos menores

**Grupos + Mata-mata**
- Times divididos em grupos
- Classificados de cada grupo avançam
- Ideal para campeonatos maiores

### 3. Funcionalidades por Página

**Dashboard**
- Visão geral dos campeonatos
- Últimos resultados e próximas partidas
- Estatísticas gerais do sistema

**Campeonatos**
- Lista com filtros por ano e status
- Visualização detalhada com abas:
  - Informações gerais
  - Equipes participantes
  - Tabela de classificação
  - Partidas e rodadas

**Equipes**
- Cadastro com upload de escudo
- Busca por nome ou cidade
- Histórico de participações

**Partidas**
- Listagem com filtros por campeonato
- Registro rápido de resultados
- Status visual das partidas

## 📁 Estrutura do Projeto

```
esportemuz/
├── campeonatos/           # App principal
│   ├── models.py         # Modelos do banco de dados
│   ├── views.py          # Views do Django
│   ├── forms.py          # Formulários
│   ├── services.py       # Lógica de negócio
│   ├── admin.py          # Configuração do admin
│   └── urls.py           # URLs do app
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   └── campeonatos/      # Templates do app
├── static/               # Arquivos estáticos
│   ├── css/             # Estilos customizados
│   └── js/              # JavaScript
├── media/               # Uploads (escudos)
└── esportemuz/          # Configurações do projeto
```

## 🎮 Exemplos de Uso

### Campeonato Municipal de Futsal
1. Criar campeonato "Municipal 2024" tipo "Pontos Corridos"
2. Cadastrar 12 equipes da cidade
3. Gerar 11 rodadas automaticamente
4. Registrar resultados conforme jogos acontecem
5. Acompanhar classificação em tempo real

### Copa Regional com Grupos
1. Criar campeonato "Copa Regional 2024" tipo "Grupos + Mata-mata"
2. Configurar 4 grupos com 4 times cada
3. Definir 2 classificados por grupo
4. Sistema gera automaticamente:
   - 6 partidas por grupo (fase de grupos)
   - Mata-mata com os 8 classificados

## 🔧 Customizações

### Adicionando Novos Campos
- Edite `models.py` para novos campos
- Atualize `forms.py` para formulários
- Modifique templates conforme necessário
- Execute `makemigrations` e `migrate`

### Modificando Regras de Pontuação
- Edite `ClassificacaoService` em `services.py`
- Ajuste método `calcular_estatisticas()`
- Teste com dados de exemplo

### Personalizando Interface
- Edite `static/css/style.css` para estilos
- Modifique templates em `templates/`
- Use classes Bootstrap como base

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou sugestões:
- Abra uma issue no GitHub
- Entre em contato via email

## 🎉 Agradecimentos

Desenvolvido para resolver problemas reais de organização esportiva local, contribuindo para a gestão profissional de campeonatos amadores.
