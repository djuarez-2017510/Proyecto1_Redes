import json
import sys
import os

INVENTARIO_FILE = 'inventario.json'

def cargar_inventario():
    if not os.path.exists(INVENTARIO_FILE):
        return []
    with open(INVENTARIO_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Los logs informativos deben ir a stderr porque MCP usa stdout para comunicarse
    sys.stderr.write("Iniciando Servidor MCP Inmobiliario Local...\n")
    sys.stderr.flush()
    
    inventario = cargar_inventario()
    sys.stderr.write(f"Inventario cargado exitosamente. {len(inventario)} propiedades listas.\n")
    sys.stderr.flush()

if __name__ == "__main__":
    main()