-- =============================================================================
-- EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "vector";     
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  

-- =============================================================================
-- ENUMS
-- =============================================================================
CREATE TYPE user_role AS ENUM ('staff', 'viewer', 'admin');
CREATE TYPE meeting_status AS ENUM ('draft', 'open', 'closed');

-- =============================================================================
-- CORE ACCESS TABLES
-- =============================================================================
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_user_email ON "user" (email);

CREATE TABLE user_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days')
);
CREATE INDEX idx_user_session_user_id ON user_session(user_id);

-- =============================================================================
-- INSTITUTIONAL TABLES
-- =============================================================================
CREATE TABLE faculty (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_bangla VARCHAR(255) UNIQUE NOT NULL,
    name_english VARCHAR(255) UNIQUE NULL
);

CREATE TABLE department (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_bangla VARCHAR(255) UNIQUE NOT NULL,
    name_english VARCHAR(255) UNIQUE NULL, -- FIXED: Added comma
    alias VARCHAR(50) UNIQUE NOT NULL,
    faculty_id UUID NULL REFERENCES faculty(id) ON DELETE SET NULL
);
CREATE INDEX idx_department_alias ON department(alias);

CREATE TABLE member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    email VARCHAR(255) UNIQUE NULL,
    hide BOOLEAN NOT NULL DEFAULT TRUE,
    is_academic BOOLEAN NOT NULL DEFAULT FALSE,
    is_external BOOLEAN NOT NULL DEFAULT FALSE,
    department_id UUID NULL REFERENCES department(id) ON DELETE SET NULL -- FIXED: Missing DELETE
);
CREATE INDEX idx_member_email ON member(email);

-- =============================================================================
-- MEETING MANAGEMENT TABLES
-- =============================================================================
CREATE TABLE signature (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    hide BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE "file" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_name VARCHAR(255) NOT NULL,
    storage_key VARCHAR(512) NOT NULL, 
    mime_type VARCHAR(100) NOT NULL,    
    file_size BIGINT NOT NULL,          
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    conclusion TEXT NULL,
    president VARCHAR(255) NULL,
    serial_num INT NOT NULL,
    status meeting_status NOT NULL DEFAULT 'draft', -- FIXED: Aligned default to 'draft'
    is_academic BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agenda_file_id UUID NULL REFERENCES "file"(id) ON DELETE SET NULL,
    resolution_file_id UUID NULL REFERENCES "file"(id) ON DELETE SET NULL,
    meeting_date TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_meeting_agenda_file ON meeting(agenda_file_id);
CREATE INDEX idx_meeting_resolution_file ON meeting(resolution_file_id);

CREATE TABLE agendum (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_no INT NOT NULL,
    content JSONB NULL,
    resolution JSONB NULL,
    is_supply BOOLEAN NOT NULL DEFAULT FALSE,
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE
);
CREATE INDEX idx_agendum_serial_no ON agendum(serial_no);
CREATE INDEX idx_agendum_meeting_id ON agendum(meeting_id);

-- =============================================================================
-- JUNCTION TABLES
-- =============================================================================
CREATE TABLE meeting_signature (
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    signature_id UUID NOT NULL REFERENCES signature(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, signature_id)
);

CREATE TABLE meeting_member (
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES member(id) ON DELETE CASCADE, 
    PRIMARY KEY (meeting_id, member_id)
);


-- =============================================================================
-- SEED DATA: BUET FACULTIES AND DEPARTMENTS
-- Sourced from the eCouncil production directory (kept byte-for-byte so fresh
-- installs match the live dataset, including its two utility placeholder rows:
-- "Default" and "অন্যান্য"/Other, used when a member has no assigned faculty/dept).
-- =============================================================================
INSERT INTO faculty (id, name_bangla, name_english) VALUES
    ('4a59e1c2-2af6-4f90-963b-7558fe5f8605', 'Default', 'Default'),
    ('ded521d9-b53f-4d0f-b55f-f88074650c17', 'প্রকৌশল অনুষদ', 'Faculty of Engineering'),
    ('a2476b19-47c4-41da-8ef8-6e7c196b3b92', 'পুরকৌশল অনুষদ', 'Faculty of Civil Engineering'),
    ('6fea112a-2b2e-4555-bda7-7ff12dc1bac6', 'তড়িৎ ও ইলেকট্রনিক কৌশল অনুষদ', 'Faculty of Electrical and Electronic Engineering'),
    ('9d8547b2-1d6e-445c-80c4-c26e40dd80f3', 'যন্ত্রকৌশল অনুষদ', 'Faculty of Mechanical Engineering'),
    ('f5ca902d-afa4-4af3-be65-77ba7e79af6c', 'স্থাপত্য ও পরিকল্পনা অনুষদ', 'Faculty of Architecture and Planning'),
    ('c83e5af0-823c-43f8-926d-5b3a522e850f', 'বিজ্ঞান অনুষদ', 'Faculty of Science'),
    ('51ac1586-bc6e-4564-8c75-51acecf8c09e', 'কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ', 'Faculty of Chemical & Materials Engineering'),
    ('227974ae-bbd5-475e-9440-3f29b2cbe266', 'No Faculty', 'No Faculty');

INSERT INTO department (id, name_bangla, name_english, faculty_id, alias) VALUES
    ('df226286-5eb7-4615-9f2e-b2bb2b111f42', 'Default', NULL, '4a59e1c2-2af6-4f90-963b-7558fe5f8605', 'Default'),
    ('1279083c-c744-4511-b3ac-8fb8276d28e4', 'মানবিক বিভাগ', 'Dept of Humanities', '227974ae-bbd5-475e-9440-3f29b2cbe266', 'HUM'),
    ('77c25cff-02f8-4122-8a96-6c60022bbcb6', 'নগর ও অঞ্চল পরিকল্পনা বিভাগ', 'Dept of Urban & Regional Planning', '227974ae-bbd5-475e-9440-3f29b2cbe266', 'URP'),
    ('775dad79-27fd-4120-83b6-8d687a5b20c4', 'ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট', 'IWFM', '227974ae-bbd5-475e-9440-3f29b2cbe266', 'IWFM'),
    ('ba85086a-df75-4243-86ef-669e606fb368', 'ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি', 'IICT', '227974ae-bbd5-475e-9440-3f29b2cbe266', 'IICT'),
    ('5b97e45d-7618-4591-9e26-9bc9e942bb2b', 'অন্যান্য', NULL, '227974ae-bbd5-475e-9440-3f29b2cbe266', 'অন্যান্য'),
    ('d27d40f5-7747-4e6c-8ddf-e37ce45e7034', 'তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ', 'Dept of Electrical and Electronic Engineering', '6fea112a-2b2e-4555-bda7-7ff12dc1bac6', 'EEE'),
    ('68bade93-be48-4f01-8703-2e09d898a998', 'কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ', 'Dept of Computer Science and Engineering', '6fea112a-2b2e-4555-bda7-7ff12dc1bac6', 'CSE'),
    ('b42f5b72-76bf-410a-a81f-b39e499a89ae', 'বায়োমেডিক্যাল ইঞ্জিনিয়ারিং বিভাগ', 'Dept of Biomedical Engineering', '6fea112a-2b2e-4555-bda7-7ff12dc1bac6', 'BME'),
    ('6a3c82a0-0358-4909-bb2e-5f33f0cacbc3', 'কেমিকৌশল বিভাগ', 'Dept of Chemical Engineering', '51ac1586-bc6e-4564-8c75-51acecf8c09e', 'ChE'),
    ('f22942d0-5175-4e3b-8cae-22dba0097726', 'বস্তু ও ধাতব কৌশল বিভাগ', 'Dept of Materials & Metallurgical Engineering', '51ac1586-bc6e-4564-8c75-51acecf8c09e', 'MME'),
    ('c4b07d76-2fd3-4779-8188-4fc28ed839ca', 'গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ', 'Dept of Glass and Ceramic Engineering', '51ac1586-bc6e-4564-8c75-51acecf8c09e', 'GCE'),
    ('c1c88616-3da9-4cc3-abac-fee7c56fcd82', 'ন্যানোমেটেরিয়ালস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ', 'Dept of NCE', '51ac1586-bc6e-4564-8c75-51acecf8c09e', 'NCE'),
    ('9ff24608-e196-4515-9601-0d5427b0bad0', 'পেট্রোলিয়াম এন্ড মিনারেল রিসোর্সেস ইঞ্জিনিয়ারিং বিভাগ', 'Dept of PMRE', 'ded521d9-b53f-4d0f-b55f-f88074650c17', 'PMRE'),
    ('4ecdb080-556f-4da2-9bf5-1a1940455435', 'পুরকৌশল বিভাগ', 'Dept of Civil Engineering', 'a2476b19-47c4-41da-8ef8-6e7c196b3b92', 'CE'),
    ('8158b73f-093d-4a53-9e3f-6430dcf69f6e', 'পানি সম্পদ কৌশল বিভাগ', 'Dept of Water Resources Engineering', 'a2476b19-47c4-41da-8ef8-6e7c196b3b92', 'WRE'),
    ('a0a1bec7-44b6-4979-af86-aae8416c87c2', 'যন্ত্রকৌশল বিভাগ', 'Dept of Mechanical Engineering', '9d8547b2-1d6e-445c-80c4-c26e40dd80f3', 'ME'),
    ('9f3c6b73-9208-49cc-99f5-36a9487e4313', 'ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ', 'Dept of Industrial and Production Engineering', '9d8547b2-1d6e-445c-80c4-c26e40dd80f3', 'IPE'),
    ('573361d8-1475-41a8-a8cc-3e19ee9066a3', 'নৌযান ও নৌযন্ত্র কৌশল বিভাগ', 'Dept of Naval Architecture and Marine Engineering', '9d8547b2-1d6e-445c-80c4-c26e40dd80f3', 'NAME'),
    ('d69ba612-4709-4de9-9e82-03a7bce0f3c8', 'রসায়ন বিভাগ', 'Dept of Chemistry', 'c83e5af0-823c-43f8-926d-5b3a522e850f', 'CHEM'),
    ('a91ab99e-4d7d-43cf-b7ab-2969e681c98a', 'গণিত বিভাগ', 'Dept of Mathematics', 'c83e5af0-823c-43f8-926d-5b3a522e850f', 'MATH'),
    ('b5a5e2bc-47da-47a1-9a25-b93f9184570b', 'পদার্থ বিজ্ঞান বিভাগ', 'Dept of Physics', 'c83e5af0-823c-43f8-926d-5b3a522e850f', 'PHY'),
    ('f661656e-00e0-406b-814b-e18061c015fa', 'স্থাপত্য বিভাগ', 'Dept of Architecture', 'f5ca902d-afa4-4af3-be65-77ba7e79af6c', 'ARCH');

-- =============================================================================
-- SEMANTIC SEARCH (CHUNKS)
-- =============================================================================

CREATE TABLE agendum_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    body TEXT NOT NULL,
    entities TEXT,
    embedding vector (768),
    agendum_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agendum_id) REFERENCES agendum (id) ON DELETE CASCADE
);

CREATE TABLE resolution_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    body TEXT NOT NULL,
    entities TEXT,
    embedding vector (768),
    agendum_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agendum_id) REFERENCES agendum (id) ON DELETE CASCADE
);

-- Vector Search Indexes for Embeddings
CREATE INDEX ix_agendum_chunks_embedding ON agendum_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ix_resolution_chunks_embedding ON resolution_chunks USING hnsw (embedding vector_cosine_ops);

-- GIN Indexes for Text Search on Entities
CREATE INDEX ix_agendum_chunks_entities ON agendum_chunks USING GIN (
    to_tsvector('simple', entities)
);

CREATE INDEX ix_resolution_chunks_entities ON resolution_chunks USING GIN (
    to_tsvector('simple', entities)
);

-- GIN Indexes for Text Search on Chunk Bodies
CREATE INDEX ix_agendum_chunks_body ON agendum_chunks USING GIN (to_tsvector('simple', body));

CREATE INDEX ix_resolution_chunks_body ON resolution_chunks USING GIN (to_tsvector('simple', body));
