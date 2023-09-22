
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
--заявки связать с пользователями
CREATE TABLE Employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status BOOLEAN DEFAULT TRUE, -- "status" field (TRUE - working, FALSE - not working)
    role VARCHAR(255),
    info VARCHAR(255)

);

CREATE TABLE Requests (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL, -- Request status: entered, in progress, completed, canceled, deleted
    created_date DATE NOT NULL,
    formation_date DATE,
    completion_date DATE,
    moderator_id INT REFERENCES Users(id) -- Reference to the moderator user
);

-- Create the "Request_Employees" table to establish a many-to-many relationship between requests and employees
CREATE TABLE Request_Employees (
    id SERIAL PRIMARY KEY,
    request_id INT REFERENCES Requests(id),
    employee_id INT REFERENCES Employees(id)
);
