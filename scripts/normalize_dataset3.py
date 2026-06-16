import pandas as pd
import os

def check_structure(df, expected_columns):
    """1. Lectura: Validar estructura y contenido."""
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Error de estructura: Faltan las columnas {missing_cols}")
    print("Estructura validada correctamente.")

def escape_sql(val):
    """Función auxiliar para escapar comillas simples en descripciones DML."""
    if pd.isna(val):
        return 'Unknown'
    return str(val).replace("'", "''")

def normalize_hospital():
    # ==========================================
    # REQUISITO 1: Lectura de datos originales
    # ==========================================
    file_path = 'data/raw/dataset3.csv'
    if not os.path.exists(file_path):
        file_path = 'data/raw/patient_records.csv'
        
    print(f"Cargando {file_path}...")
    df = pd.read_csv(file_path)

    # Validar estructura básica esperada
    expected_cols = ['Patient_ID', 'Patient_Name', 'Age', 'Gender', 'Doctor_ID', 'Doctor_Name', 'Specialty', 'Admission_ID', 'Date_of_Admission', 'Diagnosis']
    check_structure(df, expected_cols)

    # Manejar datos faltantes o inconsistentes
    df = df.dropna(subset=['Patient_ID', 'Doctor_ID', 'Admission_ID']).copy()
    
    # Asegurar tipos INT estrictos
    df['Patient_ID'] = df['Patient_ID'].astype(int)
    df['Doctor_ID'] = df['Doctor_ID'].astype(int)
    df['Admission_ID'] = df['Admission_ID'].astype(int)
    df['Age'] = df['Age'].fillna(0).astype(int)
    df['Diagnosis'] = df['Diagnosis'].fillna('Unknown')

    # ==========================================
    # REQUISITO 2 y 3: Proceso de normalización y Generación de estructura
    # ==========================================
    print("Aplicando transformaciones a 3FN...")
    
    # 1. Tabla Paciente (Evita redundancia de datos personales)
    patients_df = df[['Patient_ID', 'Patient_Name', 'Age', 'Gender']].drop_duplicates('Patient_ID').copy()

    # 2. Tabla Medico (Evita redundancia de datos del doctor)
    doctors_df = df[['Doctor_ID', 'Doctor_Name', 'Specialty']].drop_duplicates('Doctor_ID').copy()

    # 3. Tabla Diagnostico (3FN: Extrayendo descripciones de texto repetitivas)
    # Generar identificador único (PK) automático INT
    unique_diagnoses = df['Diagnosis'].unique()
    diagnoses_df = pd.DataFrame({'descripcion': unique_diagnoses})
    diagnoses_df.insert(0, 'id_diagnostico', range(1, len(diagnoses_df) + 1))

    # 4. Tabla Cita / Admision (Tabla de Hechos)
    # Unir con el catálogo de diagnósticos para obtener el ID numérico
    merged_df = pd.merge(df, diagnoses_df, left_on='Diagnosis', right_on='descripcion', how='inner')
    admissions_df = merged_df[['Admission_ID', 'Patient_ID', 'Doctor_ID', 'id_diagnostico', 'Date_of_Admission']].drop_duplicates('Admission_ID').copy()

    # ==========================================
    # REQUISITO 4: Exportación de resultados
    # ==========================================
    os.makedirs('data/normalized/dataset3', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    print("Exportando CSVs normalizados...")
    patients_df.to_csv('data/normalized/dataset3/pacientes.csv', index=False)
    doctors_df.to_csv('data/normalized/dataset3/medicos.csv', index=False)
    diagnoses_df.to_csv('data/normalized/dataset3/diagnosticos.csv', index=False)
    admissions_df.to_csv('data/normalized/dataset3/citas.csv', index=False)

    print("Generando esquema DDL...")
    ddl_script = """CREATE TABLE Paciente (
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
);"""

    with open('sql/ddl/dataset3_schema.sql', 'w', encoding='utf-8') as f:
        f.write(ddl_script)

    print("Generando scripts DML de inserción...")
    with open('sql/dml/dataset3_data.sql', 'w', encoding='utf-8') as f:
        
        f.write("-- Poblado de la tabla Diagnostico\n")
        for _, row in diagnoses_df.iterrows():
            desc = escape_sql(row['descripcion'])
            f.write(f"INSERT INTO Diagnostico (id_diagnostico, descripcion) VALUES ({row['id_diagnostico']}, '{desc}');\n")
            
        f.write("\n-- Poblado de la tabla Medico\n")
        for _, row in doctors_df.iterrows():
            name = escape_sql(row['Doctor_Name'])
            spec = escape_sql(row['Specialty'])
            f.write(f"INSERT INTO Medico (Doctor_ID, Doctor_Name, Specialty) VALUES ({row['Doctor_ID']}, '{name}', '{spec}');\n")
            
        f.write("\n-- Poblado de la tabla Paciente\n")
        for _, row in patients_df.iterrows():
            name = escape_sql(row['Patient_Name'])
            gender = escape_sql(row['Gender'])
            f.write(f"INSERT INTO Paciente (Patient_ID, Patient_Name, Age, Gender) VALUES ({row['Patient_ID']}, '{name}', {row['Age']}, '{gender}');\n")
            
        f.write("\n-- Poblado de la tabla Cita\n")
        for _, row in admissions_df.iterrows():
            f.write(f"INSERT INTO Cita (Admission_ID, Patient_ID, Doctor_ID, id_diagnostico, Date_of_Admission) VALUES ({row['Admission_ID']}, {row['Patient_ID']}, {row['Doctor_ID']}, {row['id_diagnostico']}, '{row['Date_of_Admission']}');\n")

    print("Proceso de normalización automatizado para Dataset 3 completado con éxito.")

if __name__ == "__main__":
    normalize_hospital()