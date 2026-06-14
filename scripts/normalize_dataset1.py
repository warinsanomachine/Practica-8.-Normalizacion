import pandas as pd
import os

# 1. Crear estructura de directorios
os.makedirs('data/normalized/dataset1', exist_ok=True)
os.makedirs('sql/ddl', exist_ok=True)
os.makedirs('sql/dml', exist_ok=True)

# 2. Cargar datos originales
df = pd.read_csv('data/raw/netflix_titles.csv')

# Manejo de valores nulos
df['director'] = df['director'].fillna('Unknown')
df['cast'] = df['cast'].fillna('Unknown')
df['country'] = df['country'].fillna('Unknown')
df['date_added'] = df['date_added'].fillna('Unknown')
df['rating'] = df['rating'].fillna('Unknown')
df['duration'] = df['duration'].fillna('Unknown')

# 3. Función para extraer Entidades (3FN)
def extract_entity(df, col_name, entity_col_name):
    # Separar por comas, apilar en una sola columna y limpiar espacios
    s = df[col_name].str.split(',').explode().str.strip()
    s = s[s != ""] # Eliminar vacíos
    unique_vals = s.unique()
    
    # Crear DataFrame de la nueva tabla
    entity_df = pd.DataFrame({entity_col_name: unique_vals})
    entity_df.insert(0, f'{entity_col_name}_id', range(1, len(entity_df) + 1))
    return entity_df

# Generar tablas de entidades
directors_df = extract_entity(df, 'director', 'director_name')
actors_df = extract_entity(df, 'cast', 'actor_name')
countries_df = extract_entity(df, 'country', 'country_name')
categories_df = extract_entity(df, 'listed_in', 'category_name')

# Tabla principal de Títulos (Películas/Series)
titles_df = df[['show_id', 'type', 'title', 'date_added', 'release_year', 'rating', 'duration', 'description']].copy()

# 4. Función para crear Relaciones (Tablas intermedias M:N)
def create_relation(df, col_name, entity_df, entity_col_name, title_id_col='show_id'):
    exploded = df[[title_id_col, col_name]].copy()
    exploded[col_name] = exploded[col_name].str.split(',')
    exploded = exploded.explode(col_name)
    exploded[col_name] = exploded[col_name].str.strip()
    exploded = exploded[exploded[col_name] != ""]
    
    # Unir con la tabla de entidades para obtener el ID correspondiente
    merged = pd.merge(exploded, entity_df, left_on=col_name, right_on=entity_col_name, how='inner')
    relation_df = merged[[title_id_col, f'{entity_col_name}_id']].copy()
    return relation_df

# Generar tablas relacionales
title_directors_df = create_relation(df, 'director', directors_df, 'director_name')
title_actors_df = create_relation(df, 'cast', actors_df, 'actor_name')
title_countries_df = create_relation(df, 'country', countries_df, 'country_name')
title_categories_df = create_relation(df, 'listed_in', categories_df, 'category_name')

# 5. Exportar a CSV
titles_df.to_csv('data/normalized/dataset1/titles.csv', index=False)
directors_df.to_csv('data/normalized/dataset1/directors.csv', index=False)
actors_df.to_csv('data/normalized/dataset1/actors.csv', index=False)
countries_df.to_csv('data/normalized/dataset1/countries.csv', index=False)
categories_df.to_csv('data/normalized/dataset1/categories.csv', index=False)

title_directors_df.to_csv('data/normalized/dataset1/title_directors.csv', index=False)
title_actors_df.to_csv('data/normalized/dataset1/title_actors.csv', index=False)
title_countries_df.to_csv('data/normalized/dataset1/title_countries.csv', index=False)
title_categories_df.to_csv('data/normalized/dataset1/title_categories.csv', index=False)

print("Normalización del Dataset 1 completada y exportada con éxito.")