#!/bin/bash

# Script de Setup Automático - Sistema de Biblioteca Online
# Este script prepara todo o ambiente e inicia o sistema

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Banner
clear
print_color "$BLUE" "╔════════════════════════════════════════════════════╗"
print_color "$BLUE" "║   📚 Sistema de Biblioteca Online - Setup          ║"
print_color "$BLUE" "║   Configuração e Inicialização Automática          ║"
print_color "$BLUE" "╚════════════════════════════════════════════════════╝"
echo ""

# 1. Verificar Docker
print_color "$YELLOW" "🔍 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_color "$RED" "❌ Docker não encontrado!"
    echo "   Por favor, instale o Docker:"
    echo "   - Windows: https://docs.docker.com/desktop/install/windows-install/"
    echo "   - Mac: https://docs.docker.com/desktop/install/mac-install/"
    echo "   - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi
print_color "$GREEN" "✅ Docker instalado"

# 2. Verificar Docker Compose
print_color "$YELLOW" "🔍 Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_color "$RED" "❌ Docker Compose não encontrado!"
    echo "   Instalando..."
    # Tenta instalar (Linux)
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
print_color "$GREEN" "✅ Docker Compose instalado"

# 3. Verificar portas
print_color "$YELLOW" "🔍 Verificando portas disponíveis..."

check_port() {
    port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_color "$RED" "❌ Porta $port está em uso!"
        echo "   Por favor, libere a porta ou mude a configuração"
        return 1
    else
        print_color "$GREEN" "✅ Porta $port disponível"
        return 0
    fi
}

if ! check_port 5000; then
    echo "   Para matar o processo: lsof -ti:5000 | xargs kill -9"
    exit 1
fi

if ! check_port 80; then
    print_color "$YELLOW" "⚠️  Porta 80 em uso, usando 8080"
    export FRONTEND_PORT=8080
else
    export FRONTEND_PORT=80
fi

# 4. Limpar containers antigos
print_color "$YELLOW" "🧹 Limpando containers antigos..."
docker-compose down 2>/dev/null || true
docker rm -f books-api books-frontend 2>/dev/null || true
print_color "$GREEN" "✅ Limpeza concluída"

# 5. Build das imagens
print_color "$YELLOW" "🏗️  Construindo imagens Docker..."
print_color "$BLUE" "   Isso pode levar alguns minutos na primeira vez..."

if docker-compose build; then
    print_color "$GREEN" "✅ Imagens construídas com sucesso"
else
    print_color "$RED" "❌ Erro ao construir imagens"
    exit 1
fi

# 6. Iniciar serviços
print_color "$YELLOW" "🚀 Iniciando serviços..."
if docker-compose up -d; then
    print_color "$GREEN" "✅ Serviços iniciados"
else
    print_color "$RED" "❌ Erro ao iniciar serviços"
    exit 1
fi

# 7. Aguardar API ficar pronta
print_color "$YELLOW" "⏳ Aguardando API ficar pronta..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        print_color "$GREEN" "✅ API está respondendo"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    print_color "$RED" "❌ API não respondeu a tempo"
    echo "   Verificando logs:"
    docker-compose logs api
    exit 1
fi

# 8. Popular banco com dados de exemplo
print_color "$YELLOW" "📚 Populando banco de dados com exemplos..."
sleep 2

# Criar alguns livros de exemplo via API
curl -s -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "isbn": "978-0451524935",
    "description": "Romance distópico sobre vigilância totalitária",
    "cover_url": "https://covers.openlibrary.org/b/isbn/978-0451524935-M.jpg"
  }' > /dev/null

curl -s -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dom Casmurro",
    "author": "Machado de Assis",
    "isbn": "978-8535911664",
    "description": "Clássico da literatura brasileira"
  }' > /dev/null

print_color "$GREEN" "✅ Dados de exemplo adicionados"

# 9. Verificar frontend
print_color "$YELLOW" "⏳ Aguardando frontend ficar pronto..."
sleep 3

if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    print_color "$GREEN" "✅ Frontend está respondendo"
else
    print_color "$YELLOW" "⚠️  Frontend pode demorar mais um pouco"
fi

# 10. Resumo final
echo ""
print_color "$GREEN" "╔════════════════════════════════════════════════════╗"
print_color "$GREEN" "║          ✅ SISTEMA PRONTO PARA USO!               ║"
print_color "$GREEN" "╚════════════════════════════════════════════════════╝"
echo ""
print_color "$BLUE" "📍 Serviços disponíveis:"
echo ""
print_color "$GREEN" "   🌐 Frontend:  http://localhost:$FRONTEND_PORT"
print_color "$GREEN" "   ⚙️  API:       http://localhost:5000"
print_color "$GREEN" "   📊 Health:    http://localhost:5000/api/health"
echo ""
print_color "$YELLOW" "📚 Comandos úteis:"
echo "   docker-compose logs -f       # Ver logs em tempo real"
echo "   docker-compose ps            # Ver status dos serviços"
echo "   docker-compose down          # Parar tudo"
echo "   docker-compose restart       # Reiniciar"
echo ""
print_color "$BLUE" "🎥 Para gravar o vídeo:"
echo "   1. Abra http://localhost:$FRONTEND_PORT no navegador"
echo "   2. Teste todas as funcionalidades"
echo "   3. Mostre a API respondendo"
echo "   4. Demonstre a integração com Open Library"
echo ""

# Perguntar se quer abrir no navegador
read -p "$(print_color $YELLOW 'Deseja abrir a aplicação no navegador? (s/n): ')" -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_color "$GREEN" "🌐 Abrindo navegador..."
    
    # Detectar sistema operacional e abrir navegador
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:$FRONTEND_PORT 2>/dev/null || sensible-browser http://localhost:$FRONTEND_PORT 2>/dev/null
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:$FRONTEND_PORT
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        start http://localhost:$FRONTEND_PORT
    fi
fi

print_color "$GREEN" "✨ Aproveite sua Biblioteca Online!"
echo ""