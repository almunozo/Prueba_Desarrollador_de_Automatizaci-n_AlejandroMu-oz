# Prueba_Desarrollador_de_Automatizaci-n_AlejandroMu-oz

## Descripción del Proyecto
Este proyecto automatiza la descarga, procesamiento y análisis de un archivo desde la página oficial del DANE. Su propósito principal es extraer información relevante, generar un reporte con los 10 productos más vendidos y enviar un correo electrónico con un resumen de los resultados obtenidos.

---

## Funcionalidades Principales
1. **Automatización de Descarga**: Accede al sitio web del DANE y descarga automáticamente el archivo requerido.
2. **Procesamiento y Análisis de Datos**: 
   - Extrae datos específicos como el nombre del producto, marca y precio.
   - Identifica los 10 productos más vendidos basándose en las cantidades.
3. **Generación de Reporte**:
   - Crea un archivo CSV con los datos de los 10 productos más vendidos.
   - Agrega un total acumulado de los precios en el archivo generado.
4. **Cálculos Adicionales**:
   - Calcula el total de todos los productos vendidos.
   - Determina el total de los 10 productos más vendidos y el porcentaje que representan sobre el total.
5. **Envío de Correo Electrónico**:
   - Envía un correo con un resumen de los resultados y adjunta el archivo generado.

---
## Ejecucion del proyecto 
Simplemente darle correr al script generara todo el proceso, si los archivos ya existen simplemente enviara el correo.

## Instalación de Dependencias
Antes de ejecutar el proyecto, instala las dependencias necesarias utilizando el siguiente comando:
```bash
pip install pandas requests beautifulsoup4 smtplib openpyxl


