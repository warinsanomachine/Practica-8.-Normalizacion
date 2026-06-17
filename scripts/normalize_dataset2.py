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
    if pd.isna(valor):
        return 'Unknown'
    return str(valor).replace("'", "''")

def normalizar_ecommerce():
    ruta_archivo = 'data/raw/dataset2.csv'
    if not os.path.exists(ruta_archivo):
        ruta_archivo = 'data/raw/ecommerce_data.csv'
        
    datos = pd.read_csv(ruta_archivo, encoding='ISO-8859-1')

    columnas_esperadas = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    validar_estructura(datos, columnas_esperadas)

    datos = datos.dropna(subset=['CustomerID']).copy()
    datos['CustomerID'] = datos['CustomerID'].astype(int)
    datos['Description'] = datos['Description'].fillna('Unknown')

    clientes_df = datos[['CustomerID', 'Country']].drop_duplicates('CustomerID').copy()

    productos_df = datos[['StockCode', 'Description', 'UnitPrice']].drop_duplicates('StockCode').copy()
    productos_df.insert(0, 'product_id', range(1, len(productos_df) + 1))

    datos['InvoiceNo_Clean'] = datos['InvoiceNo'].astype(str).str.replace(r'[^\d]', '', regex=True)
    datos = datos[datos['InvoiceNo_Clean'] != '']
    datos['InvoiceNo_Clean'] = datos['InvoiceNo_Clean'].astype(int)
    
    facturas_df = datos[['InvoiceNo_Clean', 'CustomerID', 'InvoiceDate']].drop_duplicates('InvoiceNo_Clean').copy()
    facturas_df.rename(columns={'InvoiceNo_Clean': 'InvoiceNo'}, inplace=True)

    fusionado = pd.merge(datos, productos_df[['StockCode', 'product_id']], on='StockCode', how='inner')
    detalles_factura_df = fusionado[['InvoiceNo_Clean', 'product_id', 'Quantity']].copy()
    detalles_factura_df.rename(columns={'InvoiceNo_Clean': 'InvoiceNo'}, inplace=True)
    detalles_factura_df = detalles_factura_df.groupby(['InvoiceNo', 'product_id'], as_index=False)['Quantity'].sum()

    os.makedirs('data/normalized/dataset2', exist_ok=True)
    os.makedirs('sql/ddl', exist_ok=True)
    os.makedirs('sql/dml', exist_ok=True)

    clientes_df.to_csv('data/normalized/dataset2/clientes.csv', index=False)
    productos_df[['product_id', 'Description', 'UnitPrice']].to_csv('data/normalized/dataset2/productos.csv', index=False)
    facturas_df.to_csv('data/normalized/dataset2/facturas.csv', index=False)
    detalles_factura_df.to_csv('data/normalized/dataset2/detalles_factura.csv', index=False)

    script_ddl = """DROP TABLE IF EXISTS Detalle_Factura CASCADE;
DROP TABLE IF EXISTS Factura CASCADE;
DROP TABLE IF EXISTS Producto CASCADE;
DROP TABLE IF EXISTS Cliente CASCADE;

CREATE TABLE Cliente (
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

    with open('sql/ddl/dataset2_schema.sql', 'w', encoding='utf-8') as archivo_ddl:
        archivo_ddl.write(script_ddl)

    with open('sql/dml/dataset2_data.sql', 'w', encoding='utf-8') as archivo_dml:
        for _, fila in clientes_df.iterrows():
            pais = escapar_sql(fila['Country'])
            archivo_dml.write(f"INSERT INTO Cliente (CustomerID, Country) VALUES ({fila['CustomerID']}, '{pais}');\n")
            
        for _, fila in productos_df.iterrows():
            descripcion = escapar_sql(fila['Description'])
            archivo_dml.write(f"INSERT INTO Producto (product_id, Description, UnitPrice) VALUES ({fila['product_id']}, '{descripcion}', {fila['UnitPrice']});\n")
            
        for _, fila in facturas_df.iterrows():
            archivo_dml.write(f"INSERT INTO Factura (InvoiceNo, CustomerID, InvoiceDate) VALUES ({fila['InvoiceNo']}, {fila['CustomerID']}, '{fila['InvoiceDate']}');\n")
            
        for _, fila in detalles_factura_df.iterrows():
            archivo_dml.write(f"INSERT INTO Detalle_Factura (InvoiceNo, product_id, Quantity) VALUES ({fila['InvoiceNo']}, {fila['product_id']}, {fila['Quantity']});\n")

    inyectar_en_bd('sql/ddl/dataset2_schema.sql', 'sql/dml/dataset2_data.sql')

if __name__ == "__main__":
    normalizar_ecommerce()