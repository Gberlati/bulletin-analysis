# Análisis del Boletin Oficial de Argentina

## Problema para resolver

Hoy en día, no hay herramientas que permitan extraer y analizar la información publica de las Sociedades Argentinas. Esto causa una falta de transparencia en los negocios que se construyen día a día en el pais.

## Pregunta de datos

- ¿Cómo podemos estructurar y normalizar los movimientos de las Sociedades Argentinas?
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

- +10.000 Sociedades Argentinas normalizadas.
- +1.000 registros de alta fidelidad para utilizar en Finetuning.

## Fuente de datos

La fuente de datos es el [Boletin Oficial](https://www.boletinoficial.gob.ar). 

## Metodología

### Fase 1: Extracción de Datos Crudos
El objetivo es extraer todos los boletines con un scraper en Python, y almacenarlos en una tabla temporal dentro de una base de datos.
 1. Iterar por cada aviso del Boletin directamente, ya que no es necesario filtrar por fecha. Se puede acceder a cada aviso mediante la URL `detalleAviso/segunda/A1426199`, siendo el valor `A1426199` un ID autoincremental.
 2. Por cada URL, extraer el cuerpo del aviso y el tipo de movimiento.
 3. Cargar la información extraida en una tabla en una Base de Datos MySQL.

### Fase 2: Finetuning de Gemma 3
Para poder hacer un procesamiento óptimo de los avisos, se va a hacer un Finetune del modelo Gemma 3 4B, utilizando qLoRA.
 1. Construir un dataset de entrenamiento con la librería LangExtract, utilizando de input los avisos, y construyendo un JSON de respuesta con los campos clave. Utilizar Gemini 2.5 Flash para la extracción.
 2. Obtener 1.000 registros de alta calidad, dividir el conjunto en 80/10/10 (test/train/validation).
 3. Hacer un primer experimento de finetune con Gemma 1B, 4bit quantization, medir la accuracy.
 4. Si la accuracy es menor al 50%, construir más registros e investigar los casos con error.
 5. Si la accuracy es mayor al +70%, pasar al finetuning de Gemma 4B. 
 6. Guardar el checkpoint final del modelo para utilizar en inferencia local.

### Fase 3: Transformación y Enriquecimiento
En esta fase convertiremos el texto no estructurado en una base de datos normalizada.
 1. Construir un script para enviar cada aviso al motor de inferencia de Gemma 3 finetuneado.
 2. Guardar en una nueva tabla las entidades normalizadas de las Sociedades, socios, inversiones y avisos relacionados.

### Fase 4: Análisis de las Sociedades Argentinas
 1. Hacer una investigación exhaustiva del conjunto de datos.
 2. Identificar los rubros con más sociedades creadas, tendencias de sociedades constituidas por mes/año.

## Cronograma


