import pandas as pd
import os
import re

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

def normalize_ecommerce():
    # ==========================================
    # REQUISITO 1: Lectura de datos originales
    # ==========================================
    file_path = 'data/raw/dataset2.csv'
    if not os.path.exists(file_path):
        file_path = 'data/raw/ecommerce_data.csv'
        
    print(f"Cargando {file_path} (esto puede tomar unos segundos debido al volumen)...")
    # Este dataset en particular suele requerir ISO-8859-1
    df = pd.read_csv(file_path, encoding='ISO-8859-1')

    # Validar estructura
    expected_cols = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    check_structure(df, expected_cols)

    # Manejar datos faltantes o inconsistentes
    # Eliminar registros sin CustomerID (no se pueden asociar a un cliente válido)
    df = df.dropna(subset=['CustomerID']).copy()
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    # Limpiar Description para evitar nulos
    df['Description'] = df['Description'].fillna('Unknown')

    # ==========================================
    # REQUISITO 2 y 3: Proceso de normalización y Generación de estructura
    # ==========================================
    print("Aplicando transformaciones a 3FN...")
    
    # 1. Tabla Cliente (3FN: El país depende del cliente)
    customers_df = df[['CustomerID', 'Country']].drop_duplicates('CustomerID').copy()

    # 2. Tabla Producto (2FN: La descripción y precio unitario dependen del código)
    products_df = df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates('StockCode').copy()
    # Generar identificador único (PK) automático INT para el producto, ya que StockCode tiene letras
    products_df.insert(0, 'product_id', range(1, len(products_df) + 1))

    # 3. Tabla Factura (Invoice)
    # Limpiar InvoiceNo (quitar 'C' de cancelaciones u otras letras) para forzar tipo INT
    df['InvoiceNo_Clean'] = df['InvoiceNo'].astype(str).str.replace(r'[^\d]', '', regex=True)
    # Filtrar vacíos por si quedó alguno y convertir a int
    df = df[df['InvoiceNo_Clean'] != '']
    df['InvoiceNo_Clean'] = df['InvoiceNo_Clean'].astype(int)
    
    invoices_df = df[['InvoiceNo_Clean', 'CustomerID', 'InvoiceDate']].drop_duplicates('InvoiceNo_Clean').copy()
    invoices_df.rename(columns={'InvoiceNo_Clean': 'InvoiceNo'}, inplace=True)

    # 4. Tabla Detalle Factura (Resolviendo N:M entre Facturas y Productos)
    # Unimos con products_df para recuperar el product_id numérico que acabamos de crear
    merged = pd.merge(df, products_df[['StockCode', 'product_id']], on='StockCode', how='inner')
    invoice_details_df = merged[['InvoiceNo_Clean', 'product_id', 'Quantity']].copy()
    invoice_details_df.rename(columns={'InvoiceNo_Clean': 'InvoiceNo'}, inplace=True)
    
    # Agrupar para sumar cantidades en caso de que un mismo producto aparezca dos veces en la misma factura
    # Esto asegura que la llave primaria compuesta (InvoiceNo, product_id) sea verdaderamente única
    invoice_details_df = invoice_details_df.groupby(['InvoiceNo', 'product_id'], as_index=False)['Quantity'].sum()

    # ==========================================
    # REQUISITO 4: Exportación de resultados
    # ==========================================
    os.makedirs('data/normalized/dataset2', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    print("Exportando CSVs normalizados...")
    customers_df.to_csv('data/normalized/dataset2/clientes.csv', index=False)
    products_df[['product_id', 'Description', 'UnitPrice']].to_csv('data/normalized/dataset2/productos.csv', index=False)
    invoices_df.to_csv('data/normalized/dataset2/facturas.csv', index=False)
    invoice_details_df.to_csv('data/normalized/dataset2/detalles_factura.csv', index=False)

    print("Generando esquema DDL...")
    ddl_script = """CREATE TABLE Cliente (
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
);"""

    with open('sql/ddl/dataset2_schema.sql', 'w', encoding='utf-8') as f:
        f.write(ddl_script)

    print("Generando scripts DML de inserción...")
    with open('sql/dml/dataset2_data.sql', 'w', encoding='utf-8') as f:
        
        f.write("-- Poblado de la tabla Cliente\n")
        for _, row in customers_df.iterrows():
            country = escape_sql(row['Country'])
            f.write(f"INSERT INTO Cliente (CustomerID, Country) VALUES ({row['CustomerID']}, '{country}');\n")
            
        f.write("\n-- Poblado de la tabla Producto\n")
        for _, row in products_df.iterrows():
            desc = escape_sql(row['Description'])
            f.write(f"INSERT INTO Producto (product_id, Description, UnitPrice) VALUES ({row['product_id']}, '{desc}', {row['UnitPrice']});\n")
            
        f.write("\n-- Poblado de la tabla Factura\n")
        for _, row in invoices_df.iterrows():
            f.write(f"INSERT INTO Factura (InvoiceNo, CustomerID, InvoiceDate) VALUES ({row['InvoiceNo']}, {row['CustomerID']}, '{row['InvoiceDate']}');\n")
            
        f.write("\n-- Poblado de la tabla Detalle_Factura\n")
        for _, row in invoice_details_df.iterrows():
            f.write(f"INSERT INTO Detalle_Factura (InvoiceNo, product_id, Quantity) VALUES ({row['InvoiceNo']}, {row['product_id']}, {row['Quantity']});\n")

    print("Proceso de normalización automatizado para Dataset 2 completado con éxito.")

if __name__ == "__main__":
    normalize_ecommerce()