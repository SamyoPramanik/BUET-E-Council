-- =============================================================================
-- EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "vector";

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE userrole_enum AS ENUM ('staff', 'viewer', 'admin');

CREATE TYPE memberrole_enum AS ENUM ('Dean', 'Head', 'Regular');

-- =============================================================================
-- AUTH
-- =============================================================================

CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    email VARCHAR NOT NULL UNIQUE,
    role userrole_enum NOT NULL DEFAULT 'viewer',
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_user_id ON "user" (id);

CREATE INDEX ix_user_email ON "user" (email);

CREATE TABLE usersession (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    user_id UUID NOT NULL,
    ip_address VARCHAR,
    user_agent VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (
        CURRENT_TIMESTAMP + INTERVAL '7 days'
    ),
    FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
);

CREATE INDEX ix_usersession_id ON usersession (id);

-- =============================================================================
-- ORGANISATION
-- =============================================================================

CREATE TABLE faculty (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    "order" INTEGER NOT NULL UNIQUE,
    name_bangla VARCHAR NOT NULL UNIQUE,
    name_english VARCHAR UNIQUE
);

CREATE INDEX ix_faculty_order ON faculty ("order");

CREATE TABLE department (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    name_bangla VARCHAR NOT NULL UNIQUE,
    name_english VARCHAR UNIQUE,
    alias_bangla VARCHAR NOT NULL UNIQUE,
    alias_english VARCHAR UNIQUE,
    faculty_id UUID NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES faculty (id) ON DELETE CASCADE
);

CREATE INDEX ix_department_faculty_id ON department (faculty_id);

-- =============================================================================
-- PARTICIPANTS
-- =============================================================================

CREATE TABLE participantcard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    content VARCHAR NOT NULL,
    role memberrole_enum NOT NULL DEFAULT 'Regular',
    email VARCHAR,
    department_id UUID NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE
);

CREATE INDEX ix_participantcard_content ON participantcard (content);

CREATE INDEX ix_participantcard_role ON participantcard (role);

CREATE INDEX ix_participantcard_department_id ON participantcard (department_id);

-- =============================================================================
-- FILES
-- =============================================================================

CREATE TABLE uploadedfile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    original_filename VARCHAR NOT NULL,
    stored_filename VARCHAR NOT NULL UNIQUE,
    path VARCHAR NOT NULL,
    storage_key VARCHAR,
    mime_type VARCHAR NOT NULL,
    size_bytes INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_uploadedfile_id ON uploadedfile (id);

CREATE TABLE signaturecard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_signaturecard_id ON signaturecard (id);

CREATE INDEX ix_signaturecard_content ON signaturecard (content);

-- =============================================================================
-- MEETINGS
-- =============================================================================

CREATE TABLE meeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    serial_num INTEGER NOT NULL,
    is_academic BOOLEAN NOT NULL DEFAULT TRUE,
    title VARCHAR NOT NULL,
    description TEXT,
    conclusion TEXT,
    is_finished BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    meeting_date TIMESTAMP WITH TIME ZONE,
    president_card_id UUID,
    agenda_pdf UUID,
    resolution_pdf UUID,
    FOREIGN KEY (president_card_id) REFERENCES participantcard (id) ON DELETE SET NULL,
    FOREIGN KEY (agenda_pdf) REFERENCES uploadedfile (id) ON DELETE SET NULL,
    FOREIGN KEY (resolution_pdf) REFERENCES uploadedfile (id) ON DELETE SET NULL
);

CREATE INDEX ix_meeting_id ON meeting (id);

CREATE INDEX ix_meeting_serial_num ON meeting (serial_num);

CREATE TABLE meetingparticipantlink (
    meeting_id UUID NOT NULL,
    participant_card_id UUID NOT NULL,
    PRIMARY KEY (
        meeting_id,
        participant_card_id
    ),
    FOREIGN KEY (meeting_id) REFERENCES meeting (id) ON DELETE CASCADE,
    FOREIGN KEY (participant_card_id) REFERENCES participantcard (id) ON DELETE CASCADE
);

CREATE TABLE meetingsignaturelink (
    meeting_id UUID NOT NULL,
    signature_card_id UUID NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (meeting_id, signature_card_id),
    FOREIGN KEY (meeting_id) REFERENCES meeting (id) ON DELETE CASCADE,
    FOREIGN KEY (signature_card_id) REFERENCES signaturecard (id) ON DELETE CASCADE
);

-- =============================================================================
-- AGENDA ITEMS
-- =============================================================================

CREATE TABLE agendum (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    serial INTEGER NOT NULL,
    body TEXT,
    is_supplementary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    meeting_id UUID NOT NULL,
    FOREIGN KEY (meeting_id) REFERENCES meeting (id) ON DELETE CASCADE
);

CREATE INDEX ix_agendum_id ON agendum (id);

CREATE INDEX ix_agendum_serial ON agendum (serial);

CREATE INDEX ix_agendum_meeting_id ON agendum (meeting_id);

-- =============================================================================
-- RESOLUTIONS
-- =============================================================================

CREATE TABLE resolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    body TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    agendum_id UUID NOT NULL UNIQUE,
    FOREIGN KEY (agendum_id) REFERENCES agendum (id) ON DELETE CASCADE
);

CREATE INDEX ix_resolution_id ON resolution (id);

CREATE INDEX ix_resolution_agendum_id ON resolution (agendum_id);

-- =============================================================================
-- FILE ATTACHMENT JUNCTION TABLES
-- =============================================================================

CREATE TABLE agendumannexure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    agendum_id UUID NOT NULL,
    file_id UUID NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uq_agendum_file UNIQUE (agendum_id, file_id),
    FOREIGN KEY (agendum_id) REFERENCES agendum (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES uploadedfile (id) ON DELETE CASCADE
);

CREATE INDEX ix_agendumannexure_agendum_id ON agendumannexure (agendum_id);

CREATE INDEX ix_agendumannexure_file_id ON agendumannexure (file_id);

CREATE TABLE resolutionattachment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    resolution_id UUID NOT NULL,
    file_id UUID NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uq_resolution_file UNIQUE (resolution_id, file_id),
    FOREIGN KEY (resolution_id) REFERENCES resolution (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES uploadedfile (id) ON DELETE CASCADE
);

CREATE INDEX ix_resolutionattachment_resolution_id ON resolutionattachment (resolution_id);

CREATE INDEX ix_resolutionattachment_file_id ON resolutionattachment (file_id);

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
    resolution_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resolution_id) REFERENCES resolution (id) ON DELETE CASCADE
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