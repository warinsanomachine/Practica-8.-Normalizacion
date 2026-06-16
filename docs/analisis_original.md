# 🔍 Análisis Inicial de los Datasets Originales

Este documento contiene la documentación de la estructura inicial, tipos de datos y la identificación de problemas de normalización de los tres datasets seleccionados de Kaggle antes de ser procesados por los scripts de automatización.

---

## 🎬 Dataset 1: Netflix Movies and TV Shows

### 1. Estructura Original
* **Origen de Datos:** Kaggle (shivamb/netflix-shows)
* **Tamaño aproximado:** ~8,800 registros
* **Formato:** CSV
* **Columnas Identificadas:** `show_id`, `type`, `title`, `director`, `cast`, `country`, `date_added`, `release_year`, `rating`, `duration`, `listed_in`.

### 2. Identificación de Problemas de Normalización
* **Violación de la 1FN (Columnas Multivaluadas):** Las columnas `director`, `cast`, `country`, y `listed_in` contienen listas de valores delimitadas por comas. Esto rompe la regla de atomicidad de los datos.
* **Redundancia de Datos:** Los nombres de los directores, actores, países y géneros se repiten de forma literal como cadenas de texto en múltiples filas, incrementando drásticamente el peso del archivo original.
* **Anomalías de Actualización:** Si se requiere corregir el nombre de un actor o director, se debe modificar cada uno de los registros de los shows en los que aparece, corriendo el riesgo de generar inconsistencias.

### 3. Dependencias Funcionales Detectadas
* `show_id` $\rightarrow$ {`type`, `title`, `date_added`, `release_year`, `rating`, `duration`}
* `show_id` $\rightarrow\rightarrow$ `director` *(Dependencia multivaluada)*
* `show_id` $\rightarrow\rightarrow$ `cast` *(Dependencia multivaluada)*
* `show_id` $\rightarrow\rightarrow$ `country` *(Dependencia multivaluada)*
* `show_id` $\rightarrow\rightarrow$ `listed_in` *(Dependencia multivaluada)*

---

## 🛍️ Dataset 2: E-commerce Sales Data

### 1. Estructura Original
* **Origen de Datos:** Kaggle (carrie1/ecommerce-data)
* **Tamaño aproximado:** ~500,000 registros
* **Formato:** CSV
* **Columnas Identificadas:** `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.

### 2. Identificación de Problemas de Normalización
* **Violación de la 2FN (Dependencias Parciales):** La clave primaria natural de una línea de transacción es compuesta: (`InvoiceNo`, `StockCode`). Sin embargo, los atributos `Description` y `UnitPrice` dependen únicamente de una parte de la clave (`StockCode`), lo cual causa una severa duplicación de descripciones de producto por cada factura emitida.
* **Violación de la 3FN (Dependencia Transitiva):** Existe una relación jerárquica en la que el país (`Country`) está determinado directamente por el cliente (`CustomerID`), y no por la factura en sí misma. Estructuralmente: `InvoiceNo` $\rightarrow$ `CustomerID` $\rightarrow$ `Country`.
* **Anomalías de Eliminación:** Si se elimina la única factura de un cliente específico, se pierden por completo los datos históricos de su procedencia geográfica (`Country`).

### 3. Dependencias Funcionales Detectadas
* {`InvoiceNo`, `StockCode`} $\rightarrow$ `Quantity`
* `StockCode` $\rightarrow$ {`Description`, `UnitPrice`} *(Dependencia Parcial - Violación 2FN)*
* `InvoiceNo` $\rightarrow$ {`InvoiceDate`, `CustomerID`}
* `CustomerID` $\rightarrow$ `Country` *(Dependencia Transitiva - Violación 3FN)*

---

## 🏥 Dataset 3: Hospital Patient Records

### 1. Estructura Original
* **Origen de Datos:** Kaggle (mitishaagarwal/patient)
* **Tamaño aproximado:** Variable
* **Formato:** CSV
* **Columnas Identificadas:** `Patient_ID`, `Patient_Name`, `Age`, `Gender`, `Doctor_ID`, `Doctor_Name`, `Specialty`, `Admission_ID`, `Date_of_Admission`, `Diagnosis`.

### 2. Identificación de Problemas de Normalización
* **Violación de la 2FN:** Mezcla múltiples entidades en una única tabla desnormalizada. Atributos como `Patient_Name`, `Age` y `Gender` dependen directamente del paciente (`Patient_ID`), mientras que `Doctor_Name` y `Specialty` pertenecen en su totalidad a la entidad del médico (`Doctor_ID`). Ninguno requiere de la clave compuesta de admisión o cita para definirse.
* **Violación de la 3FN:** La columna `Diagnosis` almacena cadenas de texto clínico altamente repetitivas asociadas de manera directa a la admisión, obligando a duplicar texto descriptivo masivo en lugar de utilizar catálogos parametrizados numéricamente.
* **Anomalías de Inserción:** No se puede dar de alta a un médico nuevo con su especialidad en el sistema hasta que este tenga asignado al menos el ingreso de un paciente real.

### 3. Dependencias Funcionales Detectadas
* `Admission_ID` $\rightarrow$ {`Patient_ID`, `Doctor_ID`, `Date_of_Admission`, `Diagnosis`}
* `Patient_ID` $\rightarrow$ {`Patient_Name`, `Age`, `Gender`} *(Violación de dependencias en tabla única)*
* `Doctor_ID` $\rightarrow$ {`Doctor_Name`, `Specialty`} *(Violación de dependencias en tabla única)*
