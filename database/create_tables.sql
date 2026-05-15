

-- GOVERNMENT ENTITIES

CREATE TABLE government_entities (
    entity_id SERIAL PRIMARY KEY,
    entity_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    city VARCHAR(100),
    established_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NDI COMPONENTS

CREATE TABLE ndi_components (
    component_id SERIAL PRIMARY KEY,
    component_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- DATA MANAGEMENT DOMAINS

CREATE TABLE data_domains (
    domain_id SERIAL PRIMARY KEY,
    domain_code VARCHAR(20),
    domain_name VARCHAR(255) NOT NULL,
    description TEXT,
    component_id INT,

    CONSTRAINT fk_domain_component
        FOREIGN KEY (component_id)
        REFERENCES ndi_components(component_id)
);

-- NATIONAL PLATFORMS

CREATE TABLE national_platforms (
    platform_id SERIAL PRIMARY KEY,
    platform_name VARCHAR(100),
    abbreviation VARCHAR(20),
    description TEXT,
    domain_id INT,

    CONSTRAINT fk_platform_domain
        FOREIGN KEY (domain_id)
        REFERENCES data_domains(domain_id)
);

-- MATURITY LEVELS

CREATE TABLE maturity_levels (
    level_id SERIAL PRIMARY KEY,
    level_number INT,
    level_name VARCHAR(100),
    score_value NUMERIC(4,2)
);

-- COMPLIANCE STATUS

CREATE TABLE compliance_status (
    compliance_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50)
);

-- POLICY DOCUMENTS

CREATE TABLE policy_documents (
    policy_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    source_authority VARCHAR(255),
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COMPLIANCE RULES

CREATE TABLE compliance_rules (
    rule_id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL,
    rule_code VARCHAR(50),
    description TEXT,
    severity VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rule_policy
        FOREIGN KEY (policy_id)
        REFERENCES policy_documents(policy_id)
);

-- DOCUMENTS (INPUT FILES)

CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20),
    file_path TEXT,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DATA CLASSIFICATIONS (Public, Restricted, Confidential, Secret)

CREATE TABLE data_classifications (
    classification_id SERIAL PRIMARY KEY,
    classification_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- DOCUMENT CLASSIFICATION RESULTS

CREATE TABLE document_classifications (
    doc_classification_id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    classification_id INT NOT NULL,
    confidence_score NUMERIC(5,2),
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_doc_class_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id),

    CONSTRAINT fk_doc_classification
        FOREIGN KEY (classification_id)
        REFERENCES data_classifications(classification_id)
);

-- SENSITIVE DATA FINDINGS

CREATE TABLE sensitive_data_findings (
    finding_id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    data_type VARCHAR(100),
    detected_value TEXT,
    risk_level VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_finding_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
);

-- COMPLIANCE SCANS

CREATE TABLE compliance_scans (
    scan_id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    compliance_id INT NOT NULL,
    overall_score NUMERIC(5,2),
    json_output_path TEXT,
    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_scan_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id),

    CONSTRAINT fk_scan_status
        FOREIGN KEY (compliance_id)
        REFERENCES compliance_status(compliance_id)
);

-- COMPLIANCE VIOLATIONS

CREATE TABLE compliance_violations (
    violation_id SERIAL PRIMARY KEY,
    scan_id INT NOT NULL,
    rule_id INT,
    violation_text TEXT,
    severity VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_violation_scan
        FOREIGN KEY (scan_id)
        REFERENCES compliance_scans(scan_id),

    CONSTRAINT fk_violation_rule
        FOREIGN KEY (rule_id)
        REFERENCES compliance_rules(rule_id)
);

-- ENTITY ASSESSMENTS

CREATE TABLE entity_assessments (
    assessment_id SERIAL PRIMARY KEY,
    entity_id INT NOT NULL,
    domain_id INT NOT NULL,
    level_id INT NOT NULL,
    compliance_id INT NOT NULL,
    assessment_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assessment_entity
        FOREIGN KEY (entity_id)
        REFERENCES government_entities(entity_id),

    CONSTRAINT fk_assessment_domain
        FOREIGN KEY (domain_id)
        REFERENCES data_domains(domain_id),

    CONSTRAINT fk_assessment_level
        FOREIGN KEY (level_id)
        REFERENCES maturity_levels(level_id),

    CONSTRAINT fk_assessment_compliance
        FOREIGN KEY (compliance_id)
        REFERENCES compliance_status(compliance_id)
);

-- INDEXES:

-- Government Entities
CREATE INDEX idx_entities_sector
ON government_entities(sector);

CREATE INDEX idx_entities_city
ON government_entities(city);

-- Data Domains
CREATE INDEX idx_domains_code
ON data_domains(domain_code);

CREATE INDEX idx_domains_component
ON data_domains(component_id);

-- National Platforms
CREATE INDEX idx_platforms_abbreviation
ON national_platforms(abbreviation);

CREATE INDEX idx_platforms_domain
ON national_platforms(domain_id);

-- Maturity Levels
CREATE INDEX idx_maturity_level_number
ON maturity_levels(level_number);

-- Documents
CREATE INDEX idx_documents_type
ON documents(file_type);

CREATE INDEX idx_documents_uploaded_at
ON documents(uploaded_at);

-- Document Classifications
CREATE INDEX idx_doc_class_document
ON document_classifications(document_id);

CREATE INDEX idx_doc_class_level
ON document_classifications(classification_id);

-- Sensitive Data Findings
CREATE INDEX idx_sensitive_document
ON sensitive_data_findings(document_id);

CREATE INDEX idx_sensitive_type
ON sensitive_data_findings(data_type);

-- Compliance Rules
CREATE INDEX idx_rules_policy
ON compliance_rules(policy_id);

-- Compliance Scans
CREATE INDEX idx_scan_document
ON compliance_scans(document_id);

CREATE INDEX idx_scan_status
ON compliance_scans(compliance_id);

CREATE INDEX idx_scan_date
ON compliance_scans(scan_date);

-- Compliance Violations
CREATE INDEX idx_violation_scan
ON compliance_violations(scan_id);

CREATE INDEX idx_violation_rule
ON compliance_violations(rule_id);

-- Entity Assessments
CREATE INDEX idx_assessment_entity
ON entity_assessments(entity_id);

CREATE INDEX idx_assessment_domain
ON entity_assessments(domain_id);

CREATE INDEX idx_assessment_level
ON entity_assessments(level_id);

CREATE INDEX idx_assessment_compliance
ON entity_assessments(compliance_id);

CREATE INDEX idx_assessment_date
ON entity_assessments(assessment_date);
