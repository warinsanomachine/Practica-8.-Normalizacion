# 📈 Reporte del Proceso de Normalización Manual y Automatizado

Este reporte documenta las transformaciones aplicadas por los scripts de Python para migrar las estructuras desnormalizadas de los tres datasets a la **Tercera Forma Normal (3FN)**, garantizando la integridad referencial dentro de PostgreSQL.

---

## 🎬 Transformación del Dataset 1 (Netflix)

### 🧩 De Estructura Plana a 3FN
1. **Tratamiento de Nulos y Limpieza:** Se mapearon los valores nulos al string `'Unknown'` y se procesó el campo `show_id` eliminando caracteres no numéricos para consolidarlo como llave primaria de tipo `INT`.
2. [cite_start]**Aplicación de 1FN:** Las columnas multivaluadas (`director`, `cast`, `country`, `listed_in`) se separaron utilizando la función `.split(',')` combinada con `.explode()` en Pandas, eliminando espacios en blanco marginales[cite: 71].
3. [cite_start]**Modelado en 3FN (Catálogos Independientes):** Para evitar la redundancia de texto, se extrajeron los valores únicos de cada una de estas columnas y se les asignó un ID autoincremental único (`director_id`, `cast_id`, etc.)[cite: 122, 164].
4. [cite_start]**Resolución de Relaciones Muchos a Muchos (M:N):** Se crearon tablas puente/relacionales (`Show_Director`, `Show_Cast`, `Show_Country`, `Show_Listed_in`) gobernadas por llaves primarias compuestas por los IDs de ambas entidades[cite: 167, 168].

### 📐 Esquema Relacional Resultante (DDL)

    CREATE TABLE Show (
        show_id INT PRIMARY KEY,
        type VARCHAR(20),
        title VARCHAR(255),
        date_added VARCHAR(50),
        release_year INT,
        rating VARCHAR(20),
        duration VARCHAR(20)
    );
    
    CREATE TABLE Director (
        director_id INT PRIMARY KEY,
        director_name VARCHAR(255)
    );
    
    CREATE TABLE Show_Director (
        show_id INT,
        director_id INT,
        PRIMARY KEY (show_id, director_id),
        FOREIGN KEY (show_id) REFERENCES Show(show_id),
        FOREIGN KEY (director_id) REFERENCES Director(director_id)
    );
    -- Estructura idéntica replicada para: Cast, Country y Listed_in
## 🛍️ Transformación del Dataset 2 (E-commerce)
### 🧩 De Estructura Plana a 3FN
Se descartaron todos los registros sin un CustomerID asignado para resguardar la consistencia transaccional. El formato del identificador de facturas InvoiceNo fue limpiado mediante expresiones regulares para eliminar prefijos de texto (como la 'C' de cancelaciones) e insertarse como INT.Aplicación de 2FN (Aislamiento de Productos): Se removieron las columnas Description y UnitPrice de la tabla de transacciones de facturas, trasladándolas a la entidad Producto. Dado que el código original StockCode presenta caracteres alfanuméricos inconsistentes, se generó un campo surrogate llamado product_id de tipo entero como su clave primaria.Aplicación de 3FN (Aislamiento de Clientes): La columna de país (Country) fue removida de la tabla de transacciones generales y se encapsuló directamente dentro de la tabla de la entidad Cliente, solucionando la dependencia transitiva existente.Consolidación del Detalle de Factura: Para mapear la relación entre las facturas y los artículos comprados, se construyó la tabla Detalle_Factura que agrupa cantidades de producto adquiridas bajo una misma clave primaria compuesta (InvoiceNo, product_id).
## 📐 Esquema Relacional Resultante
    (DDL)SQLCREATE TABLE Cliente (
        CustomerID INT PRIMARY KEY,
        Country VARCHAR(100)
    );
    
    CREATE TABLE Producto (
        product_id INT PRIMARY KEY,
        Description VARCHAR(255),
        UnitPrice DECIMAL(10,2)
    );
    
    CREATE TABLE Factura (
        InvoiceNo INT PRIMARY KEY,
        CustomerID INT,
        InvoiceDate TIMESTAMP,
        FOREIGN KEY (CustomerID) REFERENCES Cliente(CustomerID)
    );
    
    CREATE TABLE Detalle_Factura (
        InvoiceNo INT,
        product_id INT,
        Quantity INT,
        PRIMARY KEY (InvoiceNo, product_id),
        FOREIGN KEY (InvoiceNo) REFERENCES Factura(InvoiceNo),
        FOREIGN KEY (product_id) REFERENCES Producto(product_id)
    );
  ## 🏥 Transformación del Dataset 3(Hospital)
  ### 🧩 De Estructura Plana a 3FN
  Aislamiento de Entidades Fuertes (2FN): La estructura original combinaba pacientes, médicos y registros de admisión en una sola vista. El script dividió este conjunto de datos en dos colecciones independientes aplicando el método .drop_duplicates(): la entidad Paciente (con llaves funcionales basadas en Patient_ID) y la entidad Medico (con base en Doctor_ID).Normalización de Texto Clínico (3FN): Las descripciones del campo de diagnóstico (Diagnosis) contenían cadenas con alta tasa de redundancia. Se creó un catálogo limpio llamado Diagnostico asignándoles claves numéricas (id_diagnostico) para evitar almacenar texto duplicado en cada fila transaccional.  Creación de la Tabla de Hechos: La tabla Cita (o admisión) quedó exclusivamente como la entidad central que interconecta a todas las demás a través de restricciones de integridad referencial, conservando únicamente las llaves foráneas (Patient_ID, Doctor_ID, id_diagnostico) y la propiedad nativa del evento: Date_of_Admission.  📐 Esquema Relacional Resultante (DDL)SQLCREATE TABLE Paciente (
        Patient_ID INT PRIMARY KEY,
        Patient_Name VARCHAR(150),
        Age INT,
        Gender VARCHAR(20)
    );
    
    CREATE TABLE Medico (
        Doctor_ID INT PRIMARY KEY,
        Doctor_Name VARCHAR(150),
        Specialty VARCHAR(100)
    );
    
    CREATE TABLE Diagnostico (
        id_diagnostico INT PRIMARY KEY,
        descripcion VARCHAR(255)
    );
    
    CREATE TABLE Cita (
        Admission_ID INT PRIMARY KEY,
        Patient_ID INT,
        Doctor_ID INT,
        id_diagnostico INT,
        Date_of_Admission DATE,
        FOREIGN KEY (Patient_ID) REFERENCES Paciente(Patient_ID),
        FOREIGN KEY (Doctor_ID) REFERENCES Medico(Doctor_ID),
        FOREIGN KEY (id_diagnostico) REFERENCES Diagnostico(id_diagnostico)
    );
