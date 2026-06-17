import pandas as pd
import numpy as np
import os
import psycopg2

def inyectar_en_bd(ruta_ddl, ruta_dml):
    try:
        conexion = psycopg2.connect(
            host="db_normalizacion",
            database="normalizacion_db",
            user="admin",
            password="password",
            port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()

        with open(ruta_ddl, 'r', encoding='utf-8') as archivo_ddl:
            cursor.execute(archivo_ddl.read())

        with open(ruta_dml, 'r', encoding='utf-8') as archivo_dml:
            cursor.execute(archivo_dml.read())

        cursor.close()
        conexion.close()
        print("Datos inyectados exitosamente")
    except Exception as error:
        print(f"Error: {error}")

def mapear_tipo_sql(tipo):
    if pd.api.types.is_integer_dtype(tipo):
        return "INT"
    elif pd.api.types.is_float_dtype(tipo):
        return "DECIMAL(10,4)"
    else:
        return "VARCHAR(255)"

def escapar_sql(valor):
    if pd.isna(valor):
        return 'Unknown'
    return str(valor).replace("'", "''")

def normalizar_hospital_tematico():
    ruta_archivo = 'data/raw/dataset3.csv'
    if not os.path.exists(ruta_archivo):
        ruta_archivo = 'data/raw/patient_records.csv'

    datos = pd.read_csv(ruta_archivo)

    datos.columns = datos.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)

    datos.replace([np.inf, -np.inf], -1, inplace=True)

    columnas_id = ['encounter_id', 'patient_id', 'hospital_id', 'icu_id']
    for columna in columnas_id:
        if columna in datos.columns:
            datos[columna] = datos[columna].fillna(0).astype(int)

    for columna in datos.columns:
        if columna not in columnas_id:
            if pd.api.types.is_numeric_dtype(datos[columna]):
                datos[columna] = datos[columna].fillna(0)
                if (datos[columna] % 1 == 0).all():
                    datos[columna] = datos[columna].astype(int)
            else:
                datos[columna] = datos[columna].fillna('Unknown')
                datos[columna] = datos[columna].apply(escapar_sql)

    hospitales_df = datos[['hospital_id']].drop_duplicates('hospital_id').copy()

    columnas_paciente = [c for c in ['patient_id', 'age', 'gender', 'ethnicity', 'bmi', 'height', 'weight'] if c in datos.columns]
    pacientes_df = datos[columnas_paciente].drop_duplicates('patient_id').copy()

    columnas_uci = [c for c in ['icu_id', 'icu_type', 'icu_stay_type', 'icu_admit_source'] if c in datos.columns]
    uci_df = datos[columnas_uci].drop_duplicates('icu_id').copy()

    usadas = set(columnas_paciente + columnas_uci + ['hospital_id', 'encounter_id', 'hospital_death', 'pre_icu_los_days'])

    columnas_apache = [c for c in datos.columns if 'apache' in c.lower() and c not in usadas]
    apache_df = datos[['encounter_id'] + columnas_apache].copy()
    usadas.update(columnas_apache)

    lista_comorbilidades = ['aids', 'cirrhosis', 'diabetes_mellitus', 'hepatic_failure', 'immunosuppression', 'leukemia', 'lymphoma', 'solid_tumor_with_metastasis']
    columnas_comorb = [c for c in lista_comorbilidades if c in datos.columns and c not in usadas]
    comorb_df = datos[['encounter_id'] + columnas_comorb].copy()
    usadas.update(columnas_comorb)

    patrones_vitales = ['bp', 'heartrate', 'temp', 'resprate', 'spo2']
    columnas_vitales = [c for c in datos.columns if any(v in c.lower() for v in patrones_vitales) and c not in usadas]
    vitales_df = datos[['encounter_id'] + columnas_vitales].copy()
    usadas.update(columnas_vitales)

    columnas_labs = [c for c in datos.columns if c not in usadas]
    labs_df = datos[['encounter_id'] + columnas_labs].copy()

    encuentros_df = datos[['encounter_id', 'patient_id', 'hospital_id', 'icu_id', 'hospital_death']].drop_duplicates('encounter_id').copy()

    os.makedirs('data/normalized/dataset3', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    hospitales_df.to_csv('data/normalized/dataset3/hospitales.csv', index=False)
    pacientes_df.to_csv('data/normalized/dataset3/pacientes.csv', index=False)
    uci_df.to_csv('data/normalized/dataset3/unidades_uci.csv', index=False)
    encuentros_df.to_csv('data/normalized/dataset3/encuentros.csv', index=False)
    apache_df.to_csv('data/normalized/dataset3/apache_scores.csv', index=False)
    comorb_df.to_csv('data/normalized/dataset3/comorbilidades.csv', index=False)
    vitales_df.to_csv('data/normalized/dataset3/signos_vitales.csv', index=False)
    if not labs_df.empty and len(labs_df.columns) > 1:
        labs_df.to_csv('data/normalized/dataset3/laboratorios.csv', index=False)

    def generar_tabla(nombre_tabla, tabla_df, pk, fks=None):
        if tabla_df.empty or len(tabla_df.columns) <= 1 and nombre_tabla != 'Hospital': return ""
        lineas = [f"CREATE TABLE {nombre_tabla} ("]
        for col in tabla_df.columns:
            tipo_sql = mapear_tipo_sql(tabla_df[col].dtype)
            linea = f"    {col} {tipo_sql}"
            if col == pk:
                linea += " PRIMARY KEY"
            lineas.append(linea + ",")
        if fks:
            for fk_col, ref_tabla, ref_pk in fks:
                lineas.append(f"    FOREIGN KEY ({fk_col}) REFERENCES {ref_tabla}({ref_pk}),")
        lineas[-1] = lineas[-1].rstrip(',')
        lineas.append(");\n")
        return "\n".join(lineas)

    script_ddl = "DROP TABLE IF EXISTS Laboratorios CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Signos_Vitales CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Comorbilidades CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Apache_Scores CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Encuentro CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Unidad_UCI CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Paciente CASCADE;\n"
    script_ddl += "DROP TABLE IF EXISTS Hospital CASCADE;\n\n"

    script_ddl += generar_tabla('Hospital', hospitales_df, 'hospital_id') + "\n"
    script_ddl += generar_tabla('Paciente', pacientes_df, 'patient_id') + "\n"
    script_ddl += generar_tabla('Unidad_UCI', uci_df, 'icu_id') + "\n"

    fks_encuentro = [('patient_id', 'Paciente', 'patient_id'), ('hospital_id', 'Hospital', 'hospital_id'), ('icu_id', 'Unidad_UCI', 'icu_id')]
    script_ddl += generar_tabla('Encuentro', encuentros_df, 'encounter_id', fks_encuentro) + "\n"

    fks_satelite = [('encounter_id', 'Encuentro', 'encounter_id')]
    script_ddl += generar_tabla('Apache_Scores', apache_df, 'encounter_id', fks_satelite) + "\n"
    script_ddl += generar_tabla('Comorbilidades', comorb_df, 'encounter_id', fks_satelite) + "\n"
    script_ddl += generar_tabla('Signos_Vitales', vitales_df, 'encounter_id', fks_satelite) + "\n"
    if not labs_df.empty and len(labs_df.columns) > 1:
        script_ddl += generar_tabla('Laboratorios', labs_df, 'encounter_id', fks_satelite) + "\n"

    with open('sql/ddl/dataset3_schema.sql', 'w', encoding='utf-8') as archivo_ddl:
        archivo_ddl.write(script_ddl)

    def generar_inserciones(nombre_tabla, tabla_df, archivo):
        if tabla_df.empty or len(tabla_df.columns) <= 1 and nombre_tabla != 'Hospital': return
        cols = ", ".join(tabla_df.columns)
        for fila in tabla_df.itertuples(index=False, name=None):
            valores = [f"'{v}'" if isinstance(v, str) else str(v) for v in fila]
            archivo.write(f"INSERT INTO {nombre_tabla} ({cols}) VALUES ({', '.join(valores)});\n")

    with open('sql/dml/dataset3_data.sql', 'w', encoding='utf-8') as archivo_dml:
        generar_inserciones('Hospital', hospitales_df, archivo_dml)
        generar_inserciones('Paciente', pacientes_df, archivo_dml)
        generar_inserciones('Unidad_UCI', uci_df, archivo_dml)
        generar_inserciones('Encuentro', encuentros_df, archivo_dml)
        generar_inserciones('Apache_Scores', apache_df, archivo_dml)
        generar_inserciones('Comorbilidades', comorb_df, archivo_dml)
        generar_inserciones('Signos_Vitales', vitales_df, archivo_dml)
        generar_inserciones('Laboratorios', labs_df, archivo_dml)

    inyectar_en_bd('sql/ddl/dataset3_schema.sql', 'sql/dml/dataset3_data.sql')

if __name__ == "__main__":
    normalizar_hospital_tematico()