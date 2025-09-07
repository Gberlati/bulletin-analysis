# Análisis del Boletin Oficial de Argentina

## Problema para resolver

No existen herramientas que permitan extraer y analizar la información publica de las Sociedades Argentinas. Esto causa una falta de transparencia en los negocios que se construyen día a día en el pais.

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

- Fuente de Datos Única: El análisis se limitará exclusivamente a la información publicada en las secciones de Sociedades del Boletín Oficial de la República Argentina.
- Tipos de Avisos: El foco principal estará en los siguientes tipos de movimientos societarios:
  - Constitución de sociedades (S.A., S.R.L., S.A.S., etc.).
  - Cesión de cuotas o acciones.
  - Designación y cese de autoridades.
  - Aumentos de capital.
  - Disolución y liquidación de sociedades.

### Entregables Clave:
- Una base de datos MySQL con tablas normalizadas que contengan la información estructurada de las sociedades.
- El código fuente del scraper, los scripts de ETL y el pipeline de inferencia.
- El checkpoint final del modelo Gemma fine-tuneado para la extracción de entidades.
- Un informe final o dashboard con los hallazgos y visualizaciones que respondan a las preguntas de datos planteadas.

### Fuera del Alcance
- Otras Fuentes de Datos: No se cruzará información con otras fuentes externas como la AFIP, IGJ, o registros provinciales.
- Análisis en Tiempo Real: El proyecto busca crear un dataset histórico y un pipeline replicable, no un sistema de monitoreo en tiempo real.
- Interpretación Legal: El análisis se centrará en datos cuantitativos y tendencias, sin realizar interpretaciones legales o validaciones jurídicas sobre los avisos.
- Avisos No Societarios: Se excluirán del análisis otros tipos de publicaciones del Boletín Oficial (edictos judiciales, licitaciones, marcas, etc.) que no correspondan a la vida de las sociedades comerciales.

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

### Septiembre
#### Semana 2 (8-14 sep): Inicio y Desarrollo del scraper.
- Configuración del entorno de desarrollo y repositorio.
- Desarrollo y prueba del script de scraping para un lote de 1,000 avisos.
- Diseño final del esquema de la base de datos para los datos crudos.

#### Semana 3 (15-21 sep): Ejecución de la Extracción Masiva.
- Lanzamiento del scraper para la totalidad de los avisos del periodo definido.
- Monitoreo continuo del proceso, gestionando errores y posibles bloqueos.
- Población completa de la tabla de datos crudos en MySQL.

#### Semana 4 (22-28 sep): Inicio de Creación del Dataset de Entrenamiento.
- Limpieza inicial de los textos extraídos.
- Generación de los primeros 250 registros de alta calidad para el finetuning usando LangExtract y Gemini 2.5 Flash.

### Octubre
#### Semana 1 (29 sep - 5 oct): Finalización del Dataset de Entrenamiento.
- Generación y validación manual de los 750 registros restantes hasta alcanzar los 1,000.
- Revisión de la consistencia y calidad de las etiquetas JSON.

#### Semana 2 (6-12 oct): Primer Experimento de Finetuning.
- División del dataset en conjuntos de entrenamiento, validación y prueba (80/10/10).
- Configuración del entorno de finetuning (QLoRA, bitsandbytes, etc.).
- Ejecución del finetuning con el modelo Gemma 1B y evaluación inicial de la métrica de accuracy.

#### Semana 3 (13-19 oct): Iteración y Finetuning del Modelo Principal.
- Si accuracy < 70%: Analizar errores, corregir etiquetas en el dataset y re-entrenar.
- Si accuracy > 70%: Iniciar el proceso de finetuning con el modelo Gemma 4B, que es el objetivo final.

#### Semana 4 (20-26 oct): Finalización y Validación del Modelo.
- Conclusión del entrenamiento del modelo Gemma 4B.
- Evaluación exhaustiva con el conjunto de test.
- Guardado del checkpoint final del modelo y preparación del script para inferencia masiva.

### Noviembre
#### Semana 1 (27 oct - 2 nov): Transformación y Carga (Proceso ETL).
- Ejecución del script de inferencia sobre todos los avisos crudos.
- Población de las tablas normalizadas y estructuradas con la información extraída por el modelo.

#### Semana 2 (3-9 nov): Análisis de Datos y Cierre.
- Realización del análisis exploratorio sobre la base de datos final.
- Generación de métricas y visualizaciones para responder las preguntas de datos.
- Redacción del informe final y documentación del proyecto.

#### Deadline (10-14 nov): Entrega Final.
- Margen para ajustes finales y revisión.
- Entrega del proyecto.

