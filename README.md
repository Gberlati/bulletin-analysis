# Análisis del Boletin Oficial de Argentina

## Problema para resolver

Hoy en día, no hay herramientas que permitan extraer y analizar la información publica de las Sociedades Argentinas. Esto causa una falta de transparencia en los negocios que se construyen día a día en el pais.

## Pregunta de datos

- ¿Cómo podemos estrucutrar y normalizar los movimientos de las Sociedades Argentinas?
- ¿Qué tendencias están tomando las Sociedades en el pais?
- ¿Cuántas empresas han tenido que anunciarse en liquidación?
- ¿Cuántas sociedades existen por cada rubro?

## Objetivos

- Normalizar y estructurar todos los movimientos y creaciones de Sociedades en Argentina.
- Automatizar y definir un pipeline de ETL robusto que permita replicar el dataset para cualquier investigador.
- Investigar y analizar las tendencias de las Sociedades Argentinas.

## Alcance

- 

## Métricas de exito

- +10.000 Sociedades Argentinas normaliza.

## Fuente de datos

La fuente de datos es el [Boletin Oficial](https://www.boletinoficial.gob.ar). 

## Metodología

### Fase 1: Extracción de Datos Crudos
El objetivo es extraer todos los boletines con un scraper en Python, y almacenarlos en una tabla temporal dentro de una base de datos.
 1. Iterar por cada aviso del Boletin directamente, ya que no es necesario filtrar por fecha. Se puede acceder a cada aviso mediante la URL `detalleAviso/segunda/A1426199`, siendo el valor `A1426199` un ID autoincremental.
 2. Por cada URL, extraer el cuerpo del aviso y el tipo de movimiento.
 3. Cargar la información extraida en una tabla en una Base de Datos MySQL.

### Fase 2: Finetuning de Gemma 3
Para poder hacer un procesamiento óptimo de los avisos, se va a hacer un Finetuning de Gemma 3 4B.
 1. Construir un pipeline con la librería LangExtract, que tome de input

### Fase 3: Transformación y Enriquecimiento
En esta fase convertiremos el texto no estructurado en una base de datos normalizada.
 1. 

## Cronograma


