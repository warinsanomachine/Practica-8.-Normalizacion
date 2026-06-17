DROP TABLE IF EXISTS Laboratorios CASCADE;
DROP TABLE IF EXISTS Signos_Vitales CASCADE;
DROP TABLE IF EXISTS Comorbilidades CASCADE;
DROP TABLE IF EXISTS Apache_Scores CASCADE;
DROP TABLE IF EXISTS Encuentro CASCADE;
DROP TABLE IF EXISTS Unidad_UCI CASCADE;
DROP TABLE IF EXISTS Paciente CASCADE;
DROP TABLE IF EXISTS Hospital CASCADE;

CREATE TABLE Hospital (
    hospital_id INT PRIMARY KEY
);

CREATE TABLE Paciente (
    patient_id INT PRIMARY KEY,
    age INT,
    gender VARCHAR(255),
    ethnicity VARCHAR(255),
    bmi DECIMAL(10,4),
    height DECIMAL(10,4),
    weight DECIMAL(10,4)
);

CREATE TABLE Unidad_UCI (
    icu_id INT PRIMARY KEY,
    icu_type VARCHAR(255),
    icu_stay_type VARCHAR(255),
    icu_admit_source VARCHAR(255)
);

CREATE TABLE Encuentro (
    encounter_id INT PRIMARY KEY,
    patient_id INT,
    hospital_id INT,
    icu_id INT,
    hospital_death INT,
    FOREIGN KEY (patient_id) REFERENCES Paciente(patient_id),
    FOREIGN KEY (hospital_id) REFERENCES Hospital(hospital_id),
    FOREIGN KEY (icu_id) REFERENCES Unidad_UCI(icu_id)
);

CREATE TABLE Apache_Scores (
    encounter_id INT PRIMARY KEY,
    apache_2_diagnosis INT,
    apache_3j_diagnosis DECIMAL(10,4),
    apache_post_operative INT,
    arf_apache INT,
    gcs_eyes_apache INT,
    gcs_motor_apache INT,
    gcs_unable_apache INT,
    gcs_verbal_apache INT,
    heart_rate_apache INT,
    intubated_apache INT,
    map_apache INT,
    resprate_apache DECIMAL(10,4),
    temp_apache DECIMAL(10,4),
    ventilated_apache INT,
    apache_4a_hospital_death_prob DECIMAL(10,4),
    apache_4a_icu_death_prob DECIMAL(10,4),
    apache_3j_bodysystem VARCHAR(255),
    apache_2_bodysystem VARCHAR(255),
    FOREIGN KEY (encounter_id) REFERENCES Encuentro(encounter_id)
);

CREATE TABLE Comorbilidades (
    encounter_id INT PRIMARY KEY,
    aids INT,
    cirrhosis INT,
    diabetes_mellitus INT,
    hepatic_failure INT,
    immunosuppression INT,
    leukemia INT,
    lymphoma INT,
    solid_tumor_with_metastasis INT,
    FOREIGN KEY (encounter_id) REFERENCES Encuentro(encounter_id)
);

CREATE TABLE Signos_Vitales (
    encounter_id INT PRIMARY KEY,
    d1_diasbp_max INT,
    d1_diasbp_min INT,
    d1_diasbp_noninvasive_max INT,
    d1_diasbp_noninvasive_min INT,
    d1_heartrate_max INT,
    d1_heartrate_min INT,
    d1_mbp_max INT,
    d1_mbp_min INT,
    d1_mbp_noninvasive_max INT,
    d1_mbp_noninvasive_min INT,
    d1_resprate_max INT,
    d1_resprate_min INT,
    d1_spo2_max INT,
    d1_spo2_min INT,
    d1_sysbp_max INT,
    d1_sysbp_min INT,
    d1_sysbp_noninvasive_max INT,
    d1_sysbp_noninvasive_min DECIMAL(10,4),
    d1_temp_max DECIMAL(10,4),
    d1_temp_min DECIMAL(10,4),
    h1_diasbp_max INT,
    h1_diasbp_min INT,
    h1_diasbp_noninvasive_max INT,
    h1_diasbp_noninvasive_min INT,
    h1_heartrate_max INT,
    h1_heartrate_min INT,
    h1_mbp_max INT,
    h1_mbp_min INT,
    h1_mbp_noninvasive_max INT,
    h1_mbp_noninvasive_min INT,
    h1_resprate_max INT,
    h1_resprate_min INT,
    h1_spo2_max INT,
    h1_spo2_min INT,
    h1_sysbp_max INT,
    h1_sysbp_min INT,
    h1_sysbp_noninvasive_max INT,
    h1_sysbp_noninvasive_min INT,
    FOREIGN KEY (encounter_id) REFERENCES Encuentro(encounter_id)
);

CREATE TABLE Laboratorios (
    encounter_id INT PRIMARY KEY,
    elective_surgery INT,
    d1_glucose_max INT,
    d1_glucose_min INT,
    d1_potassium_max DECIMAL(10,4),
    d1_potassium_min DECIMAL(10,4),
    Unnamed__83 INT,
    FOREIGN KEY (encounter_id) REFERENCES Encuentro(encounter_id)
);

