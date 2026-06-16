import pandas as pd
import os

def check_structure(df, expected_columns):
    """1. Lectura: Validar estructura y contenido."""
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Error de estructura: Faltan las columnas {missing_cols}")
    print("Estructura validada correctamente.")

def escape_sql(val):
    """Función auxiliar para escapar comillas simples en DML."""
    return str(val).replace("'", "''")

def normalize_netflix():
    # ==========================================
    # REQUISITO 1: Lectura de datos originales
    # ==========================================
    # Cargar archivo CSV [cite: 154]
    file_path = 'data/raw/dataset1.csv'
    if not os.path.exists(file_path):
        # Alternativa de nombre si se descargó directamente de Kaggle
        file_path = 'data/raw/netflix_titles.csv' 
        
    print(f"Cargando {file_path}...")
    df = pd.read_csv(file_path)

    # Validar estructura
    expected_cols = ['show_id', 'type', 'title', 'director', 'cast', 'country', 'date_added', 'release_year', 'rating', 'duration', 'listed_in']
    check_structure(df, expected_cols)

    # Manejar datos faltantes o inconsistentes 
    df.fillna('Unknown', inplace=True)
    
    # Limpiar show_id para forzar tipo INT (PK)
    df['show_id'] = df['show_id'].astype(str).str.replace(r'[^\d]', '', regex=True).astype(int)

    # ==========================================
    # REQUISITO 2 y 3: Proceso de normalización y Generación de estructura
    # ==========================================
    # Identificar automáticamente columnas multivaluadas [cite: 159]
    multivalued_columns = ['director', 'cast', 'country', 'listed_in']
    
    # Crear múltiples tablas relacionadas y definir claves [cite: 167, 168]
    tables = {}
    relations = {}

    # Tabla principal (entidad central)
    tables['Show'] = df[['show_id', 'type', 'title', 'date_added', 'release_year', 'rating', 'duration']].copy()

    # Dividir datos según reglas de 1FN y aplicar 3FN separando entidades [cite: 161, 163]
    for col in multivalued_columns:
        # Extraer valores únicos dividiendo por comas
        exploded = df[['show_id', col]].copy()
        exploded[col] = exploded[col].str.split(',')
        exploded = exploded.explode(col)
        exploded[col] = exploded[col].str.strip()
        exploded = exploded[exploded[col] != ""]
        
        # Generar identificadores únicos (PKs) automáticamente para la nueva entidad 
        unique_vals = exploded[col].unique()
        entity_df = pd.DataFrame({f'{col}_name': unique_vals})
        entity_df.insert(0, f'{col}_id', range(1, len(entity_df) + 1))
        
        # Guardar tabla de entidad (ej. Director, Actor, etc.)
        table_name = col.capitalize()
        tables[table_name] = entity_df
        
        # Crear tabla relacional (M:N) uniendo con la entidad extraída
        merged = pd.merge(exploded, entity_df, left_on=col, right_on=f'{col}_name', how='inner')
        relations[f'Show_{table_name}'] = merged[['show_id', f'{col}_id']].drop_duplicates()

    # ==========================================
    # REQUISITO 4: Exportación de resultados
    # ==========================================
    os.makedirs('data/normalized/dataset1', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    # Exportar archivos CSV separados para cada tabla [cite: 177]
    print("Exportando CSVs normalizados...")
    for name, tbl in tables.items():
        tbl.to_csv(f'data/normalized/dataset1/{name.lower()}.csv', index=False)
    for name, rel in relations.items():
        rel.to_csv(f'data/normalized/dataset1/{name.lower()}.csv', index=False)

    # Generar scripts DDL para crear las tablas y aplicar restricciones de integridad [cite: 170, 173]
    print("Generando esquema DDL...")
    ddl_lines = []
    
    ddl_lines.append("""CREATE TABLE Show (
    show_id INT PRIMARY KEY,
    type VARCHAR(20),
    title VARCHAR(255),
    date_added VARCHAR(50),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(20)
);""")

    for col in multivalued_columns:
        tbl_name = col.capitalize()
        col_id = f'{col}_id'
        
        # DDL de la Entidad
        ddl_lines.append(f"""CREATE TABLE {tbl_name} (
    {col_id} INT PRIMARY KEY,
    {col}_name VARCHAR(255)
);""")
        
        # DDL de la Relación (Claves primarias compuestas y foráneas)
        ddl_lines.append(f"""CREATE TABLE Show_{tbl_name} (
    show_id INT,
    {col_id} INT,
    PRIMARY KEY (show_id, {col_id}),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY ({col_id}) REFERENCES {tbl_name}({col_id})
);""")

    with open('sql/ddl/dataset1_schema.sql', 'w', encoding='utf-8') as f:
        f.write("\n\n".join(ddl_lines))

    # Generar scripts DML para insertar datos transformados [cite: 175]
    print("Generando scripts DML...")
    with open('sql/dml/dataset1_data.sql', 'w', encoding='utf-8') as f:
        
        # Insertar entidades secundarias
        for col in multivalued_columns:
            tbl_name = col.capitalize()
            f.write(f"\n-- Datos para la tabla {tbl_name}\n")
            for _, row in tables[tbl_name].iterrows():
                val_name = escape_sql(row[f'{col}_name'])
                f.write(f"INSERT INTO {tbl_name} ({col}_id, {col}_name) VALUES ({row[f'{col}_id']}, '{val_name}');\n")
                
        # Insertar Shows
        f.write("\n-- Datos para la tabla Show\n")
        for _, row in tables['Show'].iterrows():
            title = escape_sql(row['title'])
            date_added = escape_sql(row['date_added'])
            rating = escape_sql(row['rating'])
            duration = escape_sql(row['duration'])
            f.write(f"INSERT INTO Show (show_id, type, title, date_added, release_year, rating, duration) "
                    f"VALUES ({row['show_id']}, '{row['type']}', '{title}', '{date_added}', {row['release_year']}, '{rating}', '{duration}');\n")
            
        # Insertar relaciones
        for rel_name, rel_df in relations.items():
            f.write(f"\n-- Datos para la tabla relacional {rel_name}\n")
            col_id = [c for c in rel_df.columns if c != 'show_id'][0]
            for _, row in rel_df.iterrows():
                f.write(f"INSERT INTO {rel_name} (show_id, {col_id}) VALUES ({row['show_id']}, {row[col_id]});\n")

    print("Proceso de normalización automatizado completado con éxito.")

if __name__ == "__main__":
    normalize_netflix()