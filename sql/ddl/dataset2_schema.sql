DROP TABLE IF EXISTS Detalle_Factura CASCADE;
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
);