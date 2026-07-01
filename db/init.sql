-- =============================================================================
-- EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "vector";     -- For semantic search embeddings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For fallback UUID primitives

-- =============================================================================
-- ENUMS
-- =============================================================================
CREATE TYPE user_role AS ENUM ('staff', 'viewer', 'admin');

-- =============================================================================
-- CORE ACCESS TABLES
-- =============================================================================

-- User Table
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_user_email ON "user" (email);

-- User Session Table
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

-- Faculty Table
CREATE TABLE faculty (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_bangla VARCHAR(255) UNIQUE NOT NULL
);

-- Department table
CREATE TABLE department (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_bangla VARCHAR(255) UNIQUE NOT NULL,
    alias VARCHAR(50) UNIQUE NOT NULL,
    faculty_id UUID NULL REFERENCES faculty(id) ON DELETE SET NULL
);
CREATE INDEX idx_department_alias ON department(alias);

-- Member Table
CREATE TABLE member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    email VARCHAR(255) UNIQUE NULL,
    hide BOOLEAN NOT NULL DEFAULT TRUE,
    is_academic BOOLEAN NOT NULL DEFAULT FALSE,
    is_external BOOLEAN NOT NULL DEFAULT FALSE,
    department_id UUID NULL REFERENCES department(id) ON SET NULL
);
CREATE INDEX idx_member_email ON member(email);
CREATE INDEX idx_member_is_current ON member(is_current);

-- =============================================================================
-- MEETING MANAGEMENT TABLES
-- =============================================================================

-- Agendum Table
CREATE TABLE agendum (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_no INT NOT NULL,
    content JSONB NULL,
    resolution JSONB NULL,
    is_supply BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_agendum_serial_no ON agendum(serial_no);

-- Signature Table
CREATE TABLE signature (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    hide BOOLEAN NOT NULL DEFAULT FALSE
);

-- File Table
CREATE TABLE "file" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_name VARCHAR(255) NOT NULL,
    storage_key VARCHAR(512) NOT NULL, -- The unique generated name or path on disk
    mime_type VARCHAR(100) NOT NULL,    -- e.g., 'application/pdf'
    file_size BIGINT NOT NULL,          -- Size in bytes
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Meeting Table
CREATE TABLE meeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    conclusion TEXT NULL,
    president VARCHAR(255) NULL,
    serial_num INT NOT NULL,
    is_finished BOOLEAN NOT NULL DEFAULT FALSE,
    is_academic BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agenda_file_id UUID NULL REFERENCES "file"(id) ON DELETE SET NULL,
    resolution_file_id UUID NULL REFERENCES "file"(id) ON DELETE SET NULL
);

-- =============================================================================
-- JUNCTION TABLES (MANY-TO-MANY RELATIONSHIPS)
-- =============================================================================

-- Meeting-Signature M2M Table
CREATE TABLE meeting_signature (
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    signature_id UUID NOT NULL REFERENCES signature(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, signature_id)
);

-- Meeting-Member M2M Table
CREATE TABLE meeting_member (
    meeting_id UUID NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES member(id) ON DELETE CASCADE, -- FIXED: type set to UUID
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
