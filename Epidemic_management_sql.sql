create database epidemic_management;
use epidemic_management;

CREATE TABLE Diseases (
    Disease_ID INT PRIMARY KEY AUTO_INCREMENT,
    Disease_Name VARCHAR(100) NOT NULL,
    Symptoms TEXT NOT NULL,
    Mortality_Rate DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 CREATE TABLE Patients (
    Patient_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Address TEXT NOT NULL,
    Disease_ID INT NOT NULL,
    Status ENUM('Infected', 'Recovered', 'Deceased') NOT NULL,
    FOREIGN KEY (Disease_ID) REFERENCES Diseases(Disease_ID) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 CREATE TABLE Outbreaks (
    Outbreak_ID INT PRIMARY KEY AUTO_INCREMENT,
    Disease_ID INT NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE,
    Number_of_Cases INT NOT NULL DEFAULT 0,
    Fatality_Rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (Disease_ID) REFERENCES Diseases(Disease_ID) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 CREATE TABLE Resources (
    Resource_ID INT PRIMARY KEY AUTO_INCREMENT,
    Type VARCHAR(100) NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    Allocated INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE Resource_Allocation (
    Allocation_ID INT PRIMARY KEY AUTO_INCREMENT,
    Resource_ID INT NOT NULL,
    Outbreak_ID INT NOT NULL,
    Quantity_Allocated INT NOT NULL,
    FOREIGN KEY (Resource_ID) REFERENCES Resources(Resource_ID) ON DELETE CASCADE,
    FOREIGN KEY (Outbreak_ID) REFERENCES Outbreaks(Outbreak_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 CREATE TABLE Users (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    Role ENUM('Admin', 'Healthcare Worker', 'Analyst') NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


SHOW tables;


