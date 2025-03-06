#!/usr/bin/env python3
# gestor_clientes_sky.py - Adaptado para GitHub Actions

import os
import datetime
import sys
import json
import argparse

# Configuración de rutas
CLIENTES_DIR = 'clientes'

def inicializar():
    """Asegura que exista la estructura de carpetas necesaria."""
    if not os.path.exists(CLIENTES_DIR):
        os.makedirs(CLIENTES_DIR)
    return True

def listar_clientes():
    """Devuelve la lista de clientes existentes."""
    inicializar()
    clientes = os.listdir(CLIENTES_DIR)
    # Filtrar solo archivos .txt y quitar la extensión para la lista
    clientes = [c.replace('.txt', '') for c in clientes if c.endswith('.txt')]
    return clientes

def obtener_cliente(nombre):
    """Obtiene la información de un cliente específico."""
    ruta = f"{CLIENTES_DIR}/{nombre}.txt"
    
    if not os.path.exists(ruta):
        return None
    
    with open(ruta, 'r') as archivo:
        contenido = archivo.read()
    
    # Parsear el contenido en un formato más estructurado
    lineas = contenido.split('\n')
    datos = {}
    servicios = []
    
    modo_servicios = False
    for linea in lineas:
        if linea.strip() == "SERVICIOS:":
            modo_servicios = True
            continue
        
        if not linea.strip():
            continue
            
        if modo_servicios:
            if linea.startswith('- '):
                servicios.append(linea[2:])
        else:
            if ':' in linea:
                clave, valor = linea.split(':', 1)
                datos[clave.strip()] = valor.strip()
    
    datos['servicios'] = servicios
    return datos

def crear_cliente(nombre, direccion, telefono, servicio):
    """Crea un nuevo cliente con los datos proporcionados."""
    inicializar()
    ruta = f"{CLIENTES_DIR}/{nombre}.txt"
    
    if os.path.exists(ruta):
        return {"status": "error", "message": "Este cliente ya existe"}
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    
    with open(ruta, 'w') as archivo:
        archivo.write(f"Nombre: {nombre}\n")
        archivo.write(f"Dirección: {direccion}\n")
        archivo.write(f"Teléfono: {telefono}\n")
        archivo.write(f"Fecha registro: {fecha}\n\n")
        archivo.write(f"SERVICIOS:\n")
        archivo.write(f"- {servicio} ({fecha})\n")
    
    return {"status": "success", "message": "Cliente creado correctamente"}

def agregar_servicio(nombre, servicio):
    """Agrega un nuevo servicio al cliente especificado."""
    ruta = f"{CLIENTES_DIR}/{nombre}.txt"
    
    if not os.path.exists(ruta):
        return {"status": "error", "message": "Cliente no existe"}
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    
    with open(ruta, 'a') as archivo:
        archivo.write(f"- {servicio} ({fecha})\n")
    
    return {"status": "success", "message": "Servicio agregado correctamente"}

def procesar_accion():
    """Procesa la acción solicitada basándose en argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Gestor de Clientes Sky para GitHub Actions')
    parser.add_argument('accion', choices=['listar', 'ver', 'crear', 'agregar_servicio'], 
                        help='Acción a realizar')
    parser.add_argument('--nombre', help='Nombre del cliente')
    parser.add_argument('--direccion', help='Dirección del cliente')
    parser.add_argument('--telefono', help='Teléfono del cliente')
    parser.add_argument('--servicio', help='Servicio para el cliente')
    parser.add_argument('--formato', choices=['texto', 'json'], default='json',
                        help='Formato de salida (por defecto: json)')
    
    args = parser.parse_args()
    
    # Ejecutar la acción seleccionada
    if args.accion == 'listar':
        resultado = listar_clientes()
        
        if args.formato == 'json':
            return json.dumps({"clientes": resultado})
        else:
            return "\n".join(resultado) if resultado else "No hay clientes"
    
    elif args.accion == 'ver':
        if not args.nombre:
            return json.dumps({"status": "error", "message": "Se requiere el nombre del cliente"})
        
        cliente = obtener_cliente(args.nombre)
        
        if cliente is None:
            if args.formato == 'json':
                return json.dumps({"status": "error", "message": "Cliente no existe"})
            else:
                return "Cliente no existe"
        
        if args.formato == 'json':
            return json.dumps(cliente)
        else:
            # Formatear los datos del cliente como texto
            texto = []
            for clave, valor in cliente.items():
                if clave != 'servicios':
                    texto.append(f"{clave}: {valor}")
            
            texto.append("\nSERVICIOS:")
            for servicio in cliente['servicios']:
                texto.append(f"- {servicio}")
            
            return "\n".join(texto)
    
    elif args.accion == 'crear':
        if not all([args.nombre, args.direccion, args.telefono, args.servicio]):
            return json.dumps({"status": "error", "message": "Faltan datos obligatorios"})
        
        resultado = crear_cliente(args.nombre, args.direccion, args.telefono, args.servicio)
        
        if args.formato == 'json':
            return json.dumps(resultado)
        else:
            return resultado["message"]
    
    elif args.accion == 'agregar_servicio':
        if not all([args.nombre, args.servicio]):
            return json.dumps({"status": "error", "message": "Se requiere nombre y servicio"})
        
        resultado = agregar_servicio(args.nombre, args.servicio)
        
        if args.formato == 'json':
            return json.dumps(resultado)
        else:
            return resultado["message"]

if __name__ == "__main__":
    try:
        resultado = procesar_accion()
        print(resultado)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
