CREATE TABLE IF NOT EXISTS student (
    pid CHAR(7) PRIMARY KEY,
    email VARCHAR(32766) NOT NULL,
    birth_date DATE NOT NULL,
    county VARCHAR(32766) NOT NULL,
    primary_college VARCHAR(32766) NOT NULL,
    race VARCHAR(32766) NOT NULL,
    tianjin_based BOOL NOT NULL
);

show tables;

SHOW CREATE TABLE student;


CREATE TABLE IF NOT EXISTS daily_health_indicators (
    temperature VARCHAR(32766),
    oxygen_saturation VARCHAR(32766),
    headache VARCHAR(32766),
    cough VARCHAR(32766),
    trouble_breathing VARCHAR(32766),
    smell_taste_loss VARCHAR(32766),
    abnormally_tired BOOL,
    occured DATE,
    pid CHAR(7),
    FOREIGN KEY (pid) REFERENCES student(pid),
    PRIMARY KEY (pid, occured)
);

show tables;

SHOW CREATE TABLE daily_health_indicators;


CREATE TABLE IF NOT EXISTS comorbidity (
    student_smoke BOOL,
    student_overweight BOOL,
    immunocompromised BOOL,
    respiratory_disease BOOL,
    renal_impairment BOOL,
    congestive_heart_failure BOOL,
    hypertension BOOL,
    diabetes BOOL,
    pid CHAR(7) PRIMARY KEY,
    FOREIGN KEY (pid) REFERENCES student(pid)
);

show tables;

SHOW CREATE TABLE comorbidity;


CREATE TABLE IF NOT EXISTS precaution (
    typical_mask_used VARCHAR(32766),
    protective_eyewear_use BOOL,
    hand_wash_frequency VARCHAR(32766),
    exposure_careless_individuals BOOL,
    pid CHAR(7) PRIMARY KEY,
    FOREIGN KEY (pid) REFERENCES student(pid)
);

show tables;

SHOW CREATE TABLE precaution;




show tables;
select * from student;
select * from daily_health_indicators;
select * from comorbidity;
select * from precaution;