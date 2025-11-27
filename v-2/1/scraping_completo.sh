#!/bin/bash

# Script completo: Scraping + Procesamiento + Generación JSON
# Combina q2.py (Python) y procesar_texto.sh en un solo script
# Uso: bash scraping_completo.sh

echo "=========================================="
echo "  Pipeline Completo de Scraping Rambam"
echo "=========================================="
echo ""

# PASO 1: SCRAPING CON PYTHON
echo "📥 Paso 1/2: Ejecutando scraping con Playwright..."
python3 q2.py > salida4.txt

if [ $? -ne 0 ]; then
    echo "✗ Error en el scraping de Python"
    exit 1
fi

echo "✓ Scraping completado"
echo ""

# PASO 2: PROCESAMIENTO Y GENERACIÓN DE JSON
echo "🔄 Paso 2/2: Procesando datos y generando JSON..."

OUTPUT_FILE="salida_formateada.json"
HTML_FILE="salida_rtl.html"

# Crear archivo JSON con estructura Sefaria
cat > "$OUTPUT_FILE" << 'JSONEOF'
{
    "Rambam": {
        "he_vtitle": "Miqra according to the Masorah",
        "he_text": [
JSONEOF

# Extraer y procesar los versículos
sed -n '3p' salida4.txt | \
    sed 's/^ \[//; s/\]$//' | \
    sed "s/', '/'\n'/g" | \
    awk '{
        # Remover comillas simples del inicio y fin
        gsub(/^'\''/, "", $0)
        gsub(/'\''$/, "", $0)
        
        # Escapar comillas dobles y backslashes para JSON válido
        gsub(/\\/, "\\\\", $0)
        gsub(/"/, "\\\"", $0)
        
        if (NR > 1) print ","
        printf "            \"%s\"", $0
    }' >> "$OUTPUT_FILE"

# Cerrar la estructura JSON
cat >> "$OUTPUT_FILE" << 'JSONEOF'

        ]
    }
}
JSONEOF

# Crear archivo HTML para visualizar en RTL
cat > "$HTML_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>רמב"ם - Versículos en Hebreo</title>
    <style>
        body {
            font-family: 'David Libre', 'Times New Roman', serif;
            direction: rtl;
            text-align: right;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.8;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            text-align: center;
        }
        .metadata {
            background-color: #e8f4f8;
            padding: 10px;
            margin: 20px 0;
            border-radius: 4px;
            font-size: 14px;
            color: #555;
        }
        .verse {
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-right: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 4px;
        }
        .verse-number {
            color: #3498db;
            font-weight: bold;
            margin-left: 10px;
            font-size: 16px;
        }
        .verse-text {
            font-size: 18px;
            color: #333;
            line-height: 2;
        }
    </style>
</head>
<body>
    <h1>רמב"ם - הלכות</h1>
    <div class="metadata" id="metadata"></div>
    <div id="verses-container"></div>
    
    <script>
        fetch('salida_formateada.json')
            .then(response => response.json())
            .then(data => {
                // Mostrar metadatos
                const metadataDiv = document.getElementById('metadata');
                if (data.Rambam && data.Rambam.he_vtitle) {
                    metadataDiv.innerHTML = `<strong>מקור:</strong> ${data.Rambam.he_vtitle}`;
                }
                
                // Mostrar versículos
                const container = document.getElementById('verses-container');
                if (data.Rambam && data.Rambam.he_text) {
                    data.Rambam.he_text.forEach((verse, index) => {
                        const verseDiv = document.createElement('div');
                        verseDiv.className = 'verse';
                        verseDiv.innerHTML = `
                            <span class="verse-number">${index + 1}</span>
                            <span class="verse-text">${verse}</span>
                        `;
                        container.appendChild(verseDiv);
                    });
                }
            })
            .catch(error => console.error('Error cargando JSON:', error));
    </script>
</body>
</html>
EOF

echo ""
echo "=========================================="
echo "  ✓ Pipeline completado exitosamente"
echo "=========================================="
echo ""
echo "📄 Archivos generados:"
echo "  • salida4.txt - Salida raw del scraping"
echo "  • salida_formateada.json - JSON formato Sefaria API"
echo "  • salida_rtl.html - Visualizador HTML RTL"
echo ""
echo "🌐 Abre salida_rtl.html en tu navegador para ver el resultado"
