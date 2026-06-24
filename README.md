
# 📊 Práctica 8: Normalización de Bases de Datos

![Python](https://img.shields.io/badge/python-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
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
- [x] Desarrollo de script de automatización utilizando Python
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

## ⚡ Inicio Rápido

Para levantar el proyecto de forma básica:

1. Clona este repositorio en tu entorno local.
2. Navega a la raíz del proyecto.
3. Ejecuta el siguiente comando para levantar los contenedores en segundo plano:
   ```bash
   docker-compose up -d
   ```

## 📂 Estructura del Proyecto
El proyecto sigue la organización requerida para el manejo de datos, scripts y documentación:

    normalizacion-db/
    ├── data/ 
    │   ├── raw/                  # Datasets originales (.csv) 
    │   └── normalized/           # Datos normalizados exportados 
    ├── scripts/                  # Scripts de automatización en Python 
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
    
### 3️⃣ Apagar el Proyecto
Cuando hayas completado las pruebas, validado las consultas o extraído los diagramas Entidad-Relación desde herramientas de administración como pgAdmin, ejecuta este comando para detener los contenedores y liberar los recursos de tu computadora:

    docker-compose down
### 4️⃣ Contenedor en Ejecución
<img width="1577" height="856" loading="lazy" alt="image" src="https://github.com/user-attachments/assets/12381ed8-f868-4015-b86a-636f79acc033" />

---

## 🖥️ Administración y Visualización con pgAdmin 4

Para conectarte a la base de datos PostgreSQL de Docker, ver los datos de las tablas normalizadas y generar su diagrama de relaciones (ERD) en pgAdmin 4, sigue las siguientes instrucciones:

### 🔌 1. Conexión a la Base de Datos
1. Abre **pgAdmin 4** en tu computadora.
2. Haz clic derecho sobre **Servers** en el panel de navegación izquierdo y selecciona **Register** ➡️ **Server...**
3. En la pestaña **General**, ingresa un nombre para identificar la conexión (por ejemplo: `Práctica Normalización`).
4. Ve a la pestaña **Connection** e ingresa la siguiente configuración (tomada de [docker-compose.yml](file:///c:/Users/flin1/OneDrive/Documentos/GitHub/Practica-8.-Normalizacion/docker-compose.yml)):
   - **Host name/address:** `localhost`
   - **Port:** `5432`
   - **Maintenance database:** `normalizacion_db`
   - **Username:** `admin`
   - **Password:** `password` *(puedes activar la casilla "Save password" para guardarla)*.
5. Haz clic en **Save**.

---

### 📊 2. Visualización de las Tablas e Información
Una vez que te hayas conectado con éxito:
1. En el menú de navegación izquierdo, despliega la ruta:
   `Servers` ➡️ `Práctica Normalización` ➡️ `Databases` ➡️ `normalizacion_db` ➡️ `Schemas` ➡️ `public` ➡️ `Tables`.
2. Aquí verás listadas todas las tablas resultantes del proceso de normalización (como `show`, `actor`, `show_actor`, etc.).
3. **Ver filas y datos rápidamente:**
   - Haz clic derecho sobre cualquier tabla.
   - Selecciona **View/Edit Data** ➡️ **All Rows** (o *First 100 Rows*).
   - Se abrirá una cuadrícula interactiva con la información guardada en la tabla.
4. **Consultas personalizadas con Query Tool:**
   - Selecciona la base de datos `normalizacion_db` o el esquema `public`.
   - Haz clic en el botón de **Query Tool** (icono de base de datos con un rayo) en la barra superior.
   - Escribe una consulta SQL en el panel (por ejemplo: `SELECT * FROM show;`).
   - Presiona la tecla **F5** o haz clic en el botón de reproducir (▶️) para ejecutar la consulta y visualizar los resultados en la parte inferior.

---

### 🗺️ 3. Visualización del Diagrama Relacional (ERD)
pgAdmin 4 incluye una funcionalidad integrada para generar y estructurar automáticamente los diagramas Entidad-Relación de tus bases de datos:
1. En el panel izquierdo de navegación, despliega la base de datos hasta llegar al esquema **public** (`normalizacion_db` ➡️ `Schemas` ➡️ `public`).
2. Haz clic derecho sobre **public** y selecciona **Generate ERD** (o **ERD Tool** dependiendo de tu versión de pgAdmin).
3. pgAdmin analizará todas las llaves primarias (PK) y llaves foráneas (FK) que conectan las tablas y generará automáticamente un diagrama entidad-relación interactivo.
4. Podrás mover las tablas en el lienzo para organizarlas como prefieras, y exportar el diagrama como una imagen utilizando el botón de guardado/cámara en la barra de herramientas del ERD.
