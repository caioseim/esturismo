# ES Turismo - Sistema de Cadastro de Motoristas

Sistema completo para gerenciar motoristas da ES Turismo com interface em português.

## Como Usar

### 1. Instalar Python
- Baixe o Python 3.8 ou superior em: https://www.python.org/downloads/
- Durante a instalação, marque "Add Python to PATH"

### 2. Instalar Dependências
Abra o Prompt de Comando (cmd) e digite:
```
pip install flask flask-sqlalchemy gunicorn werkzeug
```

### 3. Executar o Sistema
1. Clique duas vezes no arquivo `iniciar.bat`
2. Ou abra o cmd na pasta do programa e digite: `python main.py`
3. Abra o navegador e acesse: http://localhost:5000

## Funcionalidades

✅ Cadastro completo de motoristas
✅ Upload de fotos e documentos
✅ Controle de vencimento de documentos
✅ Sistema de holerites por mês/ano
✅ Backup automático dos dados
✅ Busca e filtros avançados
✅ Validação de CPF brasileiro
✅ Tipo de vínculo (Registrado/Freelancer)
✅ Ativação/desativação de motoristas
✅ Download de documentos e holerites

## Estrutura de Pastas

- `data/` - Dados dos motoristas (JSON)
- `uploads/` - Fotos e documentos
- `templates/` - Páginas HTML
- `static/` - CSS e JavaScript

## Backup

Use o botão "Criar Backup" na página inicial para salvar todos os dados em um arquivo ZIP.

## Suporte

Sistema criado para uso interno da ES Turismo.
Todos os dados ficam salvos localmente no seu computador.