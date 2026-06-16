
# 📊 Práctica 8: Normalización de Bases de Datos

![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

> **Instituto Politécnico Nacional**  | **ESCOM**
> **Ingeniería en Inteligencia Artificial**
> **Unidad de aprendizaje:** Bases de Datos

---

## 🎯 Objetivo
El objetivo principal de esta práctica es aplicar los conceptos y técnicas de normalización de bases de datos sobre conjuntos de datos reales, llevando estructuras desnormalizadas desde su estado original hasta la Tercera Forma Normal (3FN). 

A través de este proyecto se busca:
* Desarrollar habilidades para identificar dependencias funcionales y eliminar redundancias.
* Automatizar el proceso de transformación mediante scripts.
* Comprender las anomalías que surgen en bases de datos desnormalizadas (inserción, actualización y eliminación) y cómo la normalización resuelve estos problemas.

---
## 🚀 Fases del Proyecto y Tareas Realizadas

### Ejercicio 1: Selección y Análisis de Datasets 
- [x] Descarga de datasets desde Kaggle:
  - Netflix Movies and TV Shows.
  - E-commerce Sales Data.
  - Hospital Patient Records.
- [x] Documentación de la estructura original, incluyendo número de columnas, registros y tipos de datos.
- [x] Identificación de problemas de normalización (violaciones a 1FN, 2FN y 3FN) y diagramación de dependencias funcionales.

### Ejercicio 2: Proceso de Normalización Manual
- [x] **1FN:** Eliminación de grupos repetitivos y división de columnas con múltiples valores
- [x] **2FN:** Eliminación de dependencias parciales y separación de atributos en nuevas tablas con sus respectivas claves primarias
- [x] **3FN:** Eliminación de dependencias transitivas y eliminación de información calculable o redundante
- [x] Generación del documento comparativo que incluye el total de columnas, redundancia estimada y anomalías identificadas en cada etapa

### Ejercicio 3: Automatización del Proceso de Normalización
- [x] Desarrollo de script de automatización utilizando Java (con JDBC)
- [x] Lectura, validación de estructura y manejo de datos faltantes en los archivos originales
- [x] Ejecución del proceso de transformación a 1FN, 2FN y 3FN, con generación automática de identificadores únicos (PKs)
- [x] Exportación de los resultados mediante la generación de scripts DDL y DML para su creación e inserción en PostgreSQL

### Ejercicio 4: Implementación con Docker
- [x] Contenerización de la base de datos PostgreSQL asegurando volúmenes para la persistencia de datos
- [x] Configuración del contenedor de la aplicación incluyendo el script de normalización y sus dependencias
- [x] Orquestación de múltiples contenedores mediante Docker Compose, estableciendo red privada y configuración de puertos

### Ejercicio 5: Documentación y Diagramas Finales
- [x] Creación del Diagrama Entidad-Relación Extendido (EER) integrando todas las entidades, relaciones con cardinalidades y atributos
- [x] Definición del modelo relacional final detallando esquemas, tipos de datos, y marcando claramente PKs, FKs y restricciones como UNIQUE o NOT NULL

---

## ⚙️ Instrucciones de Ejecución

Para desplegar y ejecutar el proyecto localmente utilizando Docker, sigue estos pasos:

1. Clona este repositorio en tu entorno local.
2. Navega a la raíz del directorio `normalizacion-db/`.
3. Ejecuta el siguiente comando en tu terminal para levantar los contenedores en segundo plano:
   ```bash
   docker-compose up -d

## 📂 Estructura del Proyecto
El proyecto sigue la organización requerida para el manejo de datos, scripts y documentación:

    normalizacion-db/
    ├── data/ 
    │   ├── raw/                  # Datasets originales (.csv) 
    │   └── normalized/           # Datos normalizados exportados 
    ├── scripts/                  # Scripts de automatización en Java 
    ├── sql/ 
    │   ├── ddl/                  # Scripts de creación de tablas 
    │   └── dml/                  # Scripts de inserción de datos 
    ├── docs/                     # Análisis y proceso de normalización 
    │   └── diagramas_er/         # Diagramas Entidad-Relación 
    ├── docker-compose.yml        # Orquestación de contenedores 
    ├── Dockerfile                # Configuración del contenedor de la aplicación 
    └── README.md                 # Documentación del proyecto

## ⚙️ Instrucciones de Ejecución

Sigue detalladamente estos pasos en tu terminal para levantar el entorno de contenedores, ejecutar el procesamiento automático de los datos e inyectar los resultados limpios en PostgreSQL.

### 1️⃣ Inicialización y Limpieza
Si necesitas iniciar el entorno desde cero o limpiar cualquier residuo o error de ejecuciones previas en la base de datos, destruye el volumen antiguo y levanta los servicios de forma limpia:
  
    docker-compose down -v
    docker-compose up -d --build

### 2️⃣ Ejecución de los Scripts de Automatización
Estos comandos corren los scripts de Python dentro del contenedor de la aplicación. Se encargarán de procesar los archivos CSV originales, aplicar las reglas de normalización (1FN, 2FN y 3FN) y generar tanto los esquemas estructurados (DDL) como los datos limpios (DML):

    docker-compose run --rm app python scripts/normalize_dataset1.py
    docker-compose run --rm app python scripts/normalize_dataset2.py
    docker-compose run --rm app python scripts/normalize_dataset3.py
### 3️⃣ Inserción de Datos (Poblado de la Base de Datos)
Una vez que los scripts del paso anterior hayan generado los archivos estructurados .sql, utiliza los siguientes comandos para inyectar los esquemas y poblar las tablas directamente en el contenedor de PostgreSQL:

    docker exec -i db_normalizacion psql -U admin -d normalizacion_db < sql/dml/dataset1_data.sql
    docker exec -i db_normalizacion psql -U admin -d normalizacion_db < sql/dml/dataset2_data.sql
    docker exec -i db_normalizacion psql -U admin -d normalizacion_db < sql/dml/dataset3_data.sql

### 4️⃣ Apagar el Proyecto
Cuando hayas completado las pruebas, validado las consultas o extraído los diagramas Entidad-Relación desde herramientas de administración como pgAdmin, ejecuta este comando para detener los contenedores y liberar los recursos de tu computadora:

    docker-compose down
