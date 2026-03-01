-- 1. Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Define Enum Types
CREATE TYPE user_role AS ENUM ('admin', 'moderator', 'viewer');

CREATE TYPE member_type_enum AS ENUM ('academic', 'syndicate', 'both');

CREATE TYPE meeting_type AS ENUM ('syndicate', 'academic');

CREATE TYPE meeting_status AS ENUM ('locked', 'open', 'end');

CREATE TYPE annexure_type AS ENUM ('agendaItem', 'resolution');

-- CREATE TYPE execution_bool AS ENUM ('yes', 'no'); change3.a: using 'built-in' boolean instead of custom ENUM

CREATE TYPE member_status AS ENUM ('active', 'onleave', 'past');

CREATE TYPE template_visibility AS ENUM ('public', 'private');

CREATE TYPE template_type AS ENUM ('agendaItem', 'resolutionItem');

CREATE TYPE content_type AS ENUM ('agendaItem', 'resolutionItem');

-- CREATE TYPE presentee_status AS ENUM ('yes', 'no'); change5.a: using 'built-in' boolean instead of custom ENUM

CREATE TYPE account_status AS ENUM ('active', 'inactive');

-- 3. Create Tables

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name VARCHAR(255) NOT NULL UNIQUE, -- change0: 'fullname' -> 'username'
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL, -- Store hashed passwords only
    role user_role NOT NULL DEFAULT 'viewer',
    status account_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    user_id UUID REFERENCES users (id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    device_info TEXT,
    ip_address VARCHAR(45),
    signin_location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
-- Members Table (Base table for people attending meetings)
CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name_english VARCHAR(255) NOT NULL, -- change2: added english_ prefix
    name_bangla VARCHAR(255) NOT NULL, --change6: added bangla name
    status member_status NOT NULL DEFAULT 'active',
    member_type member_type_enum NOT NULL DEFAULT 'academic',
    reg_office_id INTEGER,
    user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    designation_2_id UUID REFERENCES designation_2 (id) ON DELETE SET NULL,
    designation_id UUID REFERENCES designations (id) ON DELETE SET NULL,
    faculty_id UUID REFERENCES faculties (id) ON DELETE SET NULL,
    department_id UUID REFERENCES departments (id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    email VARCHAR(255) NOT NULL,
    member_id UUID REFERENCES members (id) ON DELETE CASCADE,
);

CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name_bangla VARCHAR(255) NOT NULL,
    name_english VARCHAR(255) NOT NULL,
    alias_bangla VARCHAR(255) NOT NULL,
    alias_english VARCHAR(255) NOT NULL,
    faculty_id UUID REFERENCES faculties (id) ON DELETE CASCADE
);

CREATE TABLE faculties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name_bangla VARCHAR(255) NOT NULL,
    name_english VARCHAR(255) NOT NULL
);

CREATE TABLE designations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    designation_english VARCHAR(255) NOT NULL,
    designation_bangla VARCHAR(255) NOT NULL,
);

CREATE TABLE designation_2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    designation_english VARCHAR(255) NOT NULL,
    designation_bangla VARCHAR(255) NOT NULL,
    office_bangla VARCHAR(255),
    office_english VARCHAR(255),
)

-- Meetings Table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    serial INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL, -- change1: adding description field
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    type meeting_type NOT NULL,
    meeting_link VARCHAR(255),
    agenda_pdf_link VARCHAR(255),
    transcript VARCHAR(255),
    resolution_pdf_link VARCHAR(255),
    status meeting_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content Table (Stores the core text data and embeddings)
CREATE TABLE agenda (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    current_version INTEGER DEFAULT 1,
    is_suppli_agendum BOOLEAN DEFAULT FALSE, --change4: adding a new field
    serial INTEGER, -- e.g., "Ag-1", "Res-5"
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resolutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    embedding vector (768),
    current_version INTEGER DEFAULT 1,
    is_executed BOOLEAN DEFAULT FALSE, -- change3.b: reflected changes as mentined 3.a
    execution_status TEXT, -- Detailed status description
    agenda_id UUID REFERENCES agenda (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agenda_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    agenda_id UUID REFERENCES agenda (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resolution_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    resolution_id UUID REFERENCES resolutions (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agendaItem_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    entities TEXT,
    embedding vector (768),
    agenda_id UUID REFERENCES agenda (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resolution_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    entities TEXT,
    embedding vector (768),
    resolution_id UUID REFERENCES resolutions (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resolutionItem_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    embedding vector (768),
    resolution_id UUID REFERENCES resolutions (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Templates Table
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    body TEXT NOT NULL,
    visibility template_visibility NOT NULL DEFAULT 'private',
    created_by UUID REFERENCES users (id) ON DELETE SET NULL,
    type template_type NOT NULL,
    used_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Presentees Table (Linking table for attendance)
CREATE TABLE presentees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
    member_id UUID REFERENCES members (id) ON DELETE CASCADE,
    designation_id UUID REFERENCES designations (id) ON DELETE SET NULL,
    designation_2_id UUID REFERENCES designation_2 (id) ON DELETE SET NULL,
    agenda_emailed BOOLEAN DEFAULT FALSE,
    resolution_emailed BOOLEAN DEFAULT FALSE,
    is_present BOOLEAN DEFAULT FALSE, -- -- change5.b: reflected changes as mentined 5.a
    UNIQUE (meeting_id, member_id) -- Prevent duplicate entries for same person in same meeting
);

-- Annexures Table (Attachments/Appendices)
CREATE TABLE agendaAnnexures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    agendaItem_id UUID REFERENCES agenda (id) ON DELETE CASCADE,
    file_id UUID REFERENCES files (id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
);

CREATE TABLE resolutionAnnexures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    resolutionItem_id UUID REFERENCES resolutions (id) ON DELETE CASCADE,
    file_id UUID REFERENCES files (id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
);

CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agenda_tags (
    content_id UUID REFERENCES agenda (id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (content_id, tag_id)
);

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    summary TEXT,
    embedding vector (768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users (id) ON DELETE SET NULL
)

-- 4. Create Indexes for Performance Optimization

-- Users & Sessions
CREATE INDEX idx_users_email ON users (email);

CREATE INDEX idx_sessions_user_id ON sessions (user_id);

CREATE INDEX idx_sessions_token ON sessions (session_token);

-- Members & Hierarchies
CREATE INDEX idx_members_user_id ON members (user_id);

CREATE INDEX idx_members_department_id ON members (department_id);

CREATE INDEX idx_members_faculty_id ON members (faculty_id);

CREATE INDEX idx_departments_faculty_id ON departments (faculty_id);

-- Meetings & Content
CREATE INDEX idx_meetings_date ON meetings (meeting_date);

CREATE INDEX idx_meetings_status ON meetings (status);

CREATE INDEX idx_agenda_meeting_id ON agenda (meeting_id);

CREATE INDEX idx_resolutions_agenda_id ON resolutions (agenda_id);

-- Attendance (Presentees)
CREATE INDEX idx_presentees_meeting_id ON presentees (meeting_id);

CREATE INDEX idx_presentees_member_id ON presentees (member_id);

-- Attachments & Annexures
CREATE INDEX idx_agenda_annexures_agenda_id ON agendaAnnexures (agendaItem_id);

CREATE INDEX idx_resolution_annexures_resolution_id ON resolutionAnnexures (resolutionItem_id);

-- Vector Search Indexes for Embeddings (requires hnsw extension or similar from pgvector)
CREATE INDEX idx_agenda_chunks_embedding ON agendaItem_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_resolution_chunks_embedding ON resolution_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_resolutionItem_chunks_embedding ON resolutionItem_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_resolutions_embedding ON resolutions USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_files_embedding ON files USING hnsw (embedding vector_cosine_ops);

-- GIN Indexes for Text Search on Entities
CREATE INDEX idx_agendaItem_chunks_entities ON agendaItem_chunks USING GIN (
    to_tsvector('simple', entities)
);

CREATE INDEX idx_resolution_chunks_entities ON resolution_chunks USING GIN (
    to_tsvector('simple', entities)
);

-- GIN Indexes for Text Search on Chunk Bodies
CREATE INDEX idx_agendaItem_chunks_body ON agendaItem_chunks USING GIN (to_tsvector('simple', body));

CREATE INDEX idx_resolution_chunks_body ON resolution_chunks USING GIN (to_tsvector('simple', body));

CREATE INDEX idx_resolutionItem_chunks_body ON resolutionItem_chunks USING GIN (to_tsvector('simple', body));