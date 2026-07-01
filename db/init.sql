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
    name_english VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE department (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_bangla VARCHAR(255) UNIQUE NOT NULL,
    name_english VARCHAR(255) UNIQUE NOT NULL, -- FIXED: Added comma
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
CREATE TABLE agendum (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_no INT NOT NULL,
    content JSONB NULL,
    resolution JSONB NULL,
    is_supply BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_agendum_serial_no ON agendum(serial_no);

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
