-- 1. Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Define Enum Types
CREATE TYPE user_role AS ENUM ('admin', 'moderator', 'member');

CREATE TYPE member_type_enum AS ENUM ('academic', 'syndicate', 'none');

CREATE TYPE meeting_type AS ENUM ('syndicate', 'academic');

CREATE TYPE meeting_status AS ENUM ('locked', 'open', 'end');

CREATE TYPE content_type AS ENUM ('agendaItem', 'minor', 'resolution');

CREATE TYPE execution_bool AS ENUM ('yes', 'no');

CREATE TYPE member_status AS ENUM ('active', 'onleave', 'past');

CREATE TYPE template_visibility AS ENUM ('public', 'private');

CREATE TYPE template_type AS ENUM ('agendaItem', 'resolutionItem', 'minor');

CREATE TYPE presentee_status AS ENUM ('yes', 'no');

CREATE TYPE account_status AS ENUM ('active', 'inactive');

-- 3. Create Tables

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Store hashed passwords only
    role user_role NOT NULL DEFAULT 'member',
    member_type member_type_enum NOT NULL DEFAULT 'none',
    status account_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Members Table (Base table for people attending meetings)
CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    name VARCHAR(255) NOT NULL,
    status member_status NOT NULL DEFAULT 'active',
    user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Syndicate Members (Extension of members)
CREATE TABLE syndicate_members (
    member_id UUID PRIMARY KEY REFERENCES members (id) ON DELETE CASCADE,
    designation VARCHAR(255),
    address TEXT
);

-- Academic Members (Extension of members)
CREATE TABLE academic_members (
    member_id UUID PRIMARY KEY REFERENCES members (id) ON DELETE CASCADE,
    designation VARCHAR(255),
    department VARCHAR(255)
);

-- Meetings Table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    title VARCHAR(255) NOT NULL,
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    type meeting_type NOT NULL,
    meeting_link TEXT,
    agenda_pdf_link TEXT,
    resolution_pdf_link TEXT,
    minors_pdf_link TEXT,
    status meeting_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content Table (Stores the core text data and embeddings)
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    type content_type NOT NULL,
    -- 'vector(1536)' is standard for OpenAI embeddings. 
    -- Change 1536 to your specific model's dimension if different.
    embedding vector (1536),
    content_serial VARCHAR(50), -- e.g., "Ag-1", "Res-5"
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Resolutions Table (Links specifically to content that are resolutions)
CREATE TABLE resolutions (
    content_id UUID PRIMARY KEY REFERENCES content (id) ON DELETE CASCADE,
    is_executed execution_bool DEFAULT 'no',
    execution_status TEXT, -- Detailed status description
    decision TEXT
);

-- Templates Table
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    text_content TEXT NOT NULL,
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
    is_present presentee_status NOT NULL DEFAULT 'no',
    UNIQUE (meeting_id, member_id) -- Prevent duplicate entries for same person in same meeting
);

-- Revisions Table (Version control for content)
CREATE TABLE revisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    text_content TEXT NOT NULL,
    content_id UUID REFERENCES content (id) ON DELETE CASCADE,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_by UUID REFERENCES users (id) ON DELETE SET NULL
);

-- Annexures Table (Attachments/Appendices)
CREATE TABLE annexures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
    content_id UUID REFERENCES content (id) ON DELETE CASCADE,
    pdf_link TEXT,
    summary TEXT,
    embedding vector (1536), -- Vector embedding for the annexure summary/content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);