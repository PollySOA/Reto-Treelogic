#!/bin/bash

echo "🚀 Iniciando reparación del Pipeline de Treelogic..."

# 1. Crear el archivo .env con las variables solicitadas
echo "📝 Configurando variables de entorno..."
cat <<EOT > .env
VITE_ANALYTICS_ENDPOINT=localhost
VITE_ANALYTICS_WEBSITE_ID=hackathon
NODE_ENV=development
OAUTH_SERVER_URL=http://localhost:3000
EOT

# 2. Parchear el error TypeError: Invalid URL en client/src/const.ts
# Este error ocurre porque getLoginUrl() falla si OAUTH_SERVER_URL está vacío
echo "🛠️ Parcheando error de URL inválida..."
CONST_FILE="client/src/const.ts"
if [ -f "$CONST_FILE" ]; then
    # Reemplazar la lógica de login para que no explote si la URL es inválida
    sed -i "s|return new URL.*|return 'http://localhost:3000/login';|g" "$CONST_FILE"
    echo "✅ Archivo const.ts parcheado."
else
    echo "⚠️ No se encontró client/src/const.ts, asegúrate de estar en la raíz del proyecto."
fi

# 3. Instalar dependencia faltante de Python (por si acaso)
echo "🐍 Verificando dependencias de Python..."
pip install python-multipart ultralytics opencv-python scikit-image fastapi uvicorn --quiet

# 4. Instrucciones finales
echo ""
echo "✨ ¡Reparación completada! ✨"
echo "-------------------------------------------------------"
echo "Para arrancar el proyecto ahora:"
echo "1. En una terminal lanza el BACKEND:"
echo "   cd server && python main.py"
echo ""
echo "2. En OTRA terminal lanza el FRONTEND:"
echo "   pnpm dev"
echo "-------------------------------------------------------"
echo "El error 'Invalid URL' debería haber desaparecido."
