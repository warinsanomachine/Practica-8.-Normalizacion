CREATE TABLE Paciente (
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