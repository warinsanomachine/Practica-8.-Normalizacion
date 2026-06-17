import pandas as pd
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

def validar_estructura(datos, columnas_esperadas):
    columnas_faltantes = [col for col in columnas_esperadas if col not in datos.columns]
    if columnas_faltantes:
        raise ValueError(f"Faltan las columnas {columnas_faltantes}")

def escapar_sql(valor):
    return str(valor).replace("'", "''")

def normalizar_netflix():
    ruta_archivo = 'data/raw/dataset1.csv'
    if not os.path.exists(ruta_archivo):
        ruta_archivo = 'data/raw/netflix_titles.csv' 
        
    datos = pd.read_csv(ruta_archivo)
    
    datos.rename(columns={'cast': 'actor'}, inplace=True)

    columnas_esperadas = ['show_id', 'type', 'title', 'director', 'actor', 'country', 'date_added', 'release_year', 'rating', 'duration', 'listed_in']
    validar_estructura(datos, columnas_esperadas)

    datos.fillna('Unknown', inplace=True)
    
    datos['show_id'] = datos['show_id'].astype(str).str.replace(r'[^\d]', '', regex=True).astype(int)

    columnas_multivaluadas = ['director', 'actor', 'country', 'listed_in']
    
    tablas = {}
    relaciones = {}

    tablas['Show'] = datos[['show_id', 'type', 'title', 'date_added', 'release_year', 'rating', 'duration']].copy()

    for columna in columnas_multivaluadas:
        desglosado = datos[['show_id', columna]].copy()
        desglosado[columna] = desglosado[columna].str.split(',')
        desglosado = desglosado.explode(columna)
        desglosado[columna] = desglosado[columna].str.strip()
        desglosado = desglosado[desglosado[columna] != ""]
        
        valores_unicos = desglosado[columna].unique()
        entidad_df = pd.DataFrame({f'{columna}_name': valores_unicos})
        entidad_df.insert(0, f'{columna}_id', range(1, len(entidad_df) + 1))
        
        nombre_tabla = columna.capitalize()
        tablas[nombre_tabla] = entidad_df
        
        fusionado = pd.merge(desglosado, entidad_df, left_on=columna, right_on=f'{columna}_name', how='inner')
        relaciones[f'Show_{nombre_tabla}'] = fusionado[['show_id', f'{columna}_id']].drop_duplicates()

    os.makedirs('data/normalized/dataset1', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    for nombre, tabla in tablas.items():
        tabla.to_csv(f'data/normalized/dataset1/{nombre.lower()}.csv', index=False)
    for nombre, relacion in relaciones.items():
        relacion.to_csv(f'data/normalized/dataset1/{nombre.lower()}.csv', index=False)

    lineas_ddl = []
    
    lineas_ddl.append("DROP TABLE IF EXISTS Show CASCADE;")
    
    for columna in columnas_multivaluadas:
        nombre_tabla = columna.capitalize()
        lineas_ddl.append(f"DROP TABLE IF EXISTS {nombre_tabla} CASCADE;")
        lineas_ddl.append(f"DROP TABLE IF EXISTS Show_{nombre_tabla} CASCADE;")

    lineas_ddl.append("""CREATE TABLE Show (
    show_id INT PRIMARY KEY,
    type VARCHAR(20),
    title VARCHAR(255),
    date_added VARCHAR(50),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(20)
);""")

    for columna in columnas_multivaluadas:
        nombre_tabla = columna.capitalize()
        id_columna = f'{columna}_id'
        
        lineas_ddl.append(f"""CREATE TABLE {nombre_tabla} (
    {id_columna} INT PRIMARY KEY,
    {columna}_name VARCHAR(255)
);""")
        
        lineas_ddl.append(f"""CREATE TABLE Show_{nombre_tabla} (
    show_id INT,
    {id_columna} INT,
    PRIMARY KEY (show_id, {id_columna}),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY ({id_columna}) REFERENCES {nombre_tabla}({id_columna})
);""")

    with open('sql/ddl/dataset1_schema.sql', 'w', encoding='utf-8') as archivo_salida_ddl:
        archivo_salida_ddl.write("\n\n".join(lineas_ddl))

    with open('sql/dml/dataset1_data.sql', 'w', encoding='utf-8') as archivo_salida_dml:
        for columna in columnas_multivaluadas:
            nombre_tabla = columna.capitalize()
            for _, fila in tablas[nombre_tabla].iterrows():
                nombre_valor = escapar_sql(fila[f'{columna}_name'])
                archivo_salida_dml.write(f"INSERT INTO {nombre_tabla} ({columna}_id, {columna}_name) VALUES ({fila[f'{columna}_id']}, '{nombre_valor}');\n")
                
        for _, fila in tablas['Show'].iterrows():
            titulo = escapar_sql(fila['title'])
            fecha = escapar_sql(fila['date_added'])
            clasificacion = escapar_sql(fila['rating'])
            duracion = escapar_sql(fila['duration'])
            archivo_salida_dml.write(f"INSERT INTO Show (show_id, type, title, date_added, release_year, rating, duration) "
                    f"VALUES ({fila['show_id']}, '{fila['type']}', '{titulo}', '{fecha}', {fila['release_year']}, '{clasificacion}', '{duracion}');\n")
            
        for nombre_relacion, relacion_df in relaciones.items():
            id_columna = [c for c in relacion_df.columns if c != 'show_id'][0]
            for _, fila in relacion_df.iterrows():
                archivo_salida_dml.write(f"INSERT INTO {nombre_relacion} (show_id, {id_columna}) VALUES ({fila['show_id']}, {fila[id_columna]});\n")

    inyectar_en_bd('sql/ddl/dataset1_schema.sql', 'sql/dml/dataset1_data.sql')

if __name__ == "__main__":
    normalizar_netflix()