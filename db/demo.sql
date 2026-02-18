-- 1. Setup Enums for strict data integrity
CREATE TYPE user_role AS ENUM ('ADMIN_APPROVER', 'EDITOR', 'READER');

CREATE TYPE user_category AS ENUM ('STAFF', 'ACADEMIC', 'SYNDICATE');

-- 2. Base User Table (The "Parent")
-- This table stores everything needed for Auth and Identity
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    username VARCHAR(100) UNIQUE NOT NULL, -- Legacy compatibility
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'READER',
    user_type user_category NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Staff Profile (The "Staff" Extension)
-- Attributes specifically for administrative staff
-- CREATE TABLE staff (
--     user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
-- );

-- 4. Academic Profile (The "Academic" Extension)
-- Derived from ACQ.MEMBERS and your images
CREATE TABLE academic (
    user_id UUID PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    faculty VARCHAR(100), -- e.g., Engineering, Business
    department VARCHAR(100), -- e.g., CSE, EEE (From ACQ.MEMBERS)
    designation VARCHAR(100), -- e.g., Professor, Lecturer
    seniority_order INT, -- Used for sorting members in meeting lists
    is_internal BOOLEAN DEFAULT TRUE
);

-- 5. Syndicate Profile (The "Syndicate" Extension)
-- Based on the 1st image description and typical university structure
CREATE TABLE syndicate (
    user_id UUID PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    institution VARCHAR(255), -- "From where" (e.g., UGC, Govt Ministry)
    department VARCHAR(100),
    designation VARCHAR(100),
    appointment_date DATE,
    term_expiry DATE
);

-- 1. Setup Enums for Templates
CREATE TYPE template_visibility AS ENUM ('PRIVATE', 'PUBLIC');

CREATE TYPE template_type AS ENUM ('AGENDA', 'RESOLUTION');

-- 2. Agenda Table
-- Links to your existing 'meeting' table (use UUID or Serial as per your preference)
CREATE TABLE agenda (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    meeting_id UUID NOT NULL REFERENCES meetings (id) ON DELETE CASCADE,
    content TEXT NOT NULL, -- The agenda item description
    embedding vector (1536),
    decision TEXT, -- The "Minutes/Resolution" result
    order_index INT, -- To maintain the sequence of items in a meeting
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_executed execution_bool DEFAULT 'no',
    execution_status TEXT, -- Detailed status description
);

-- 3. Annexure Table (Supporting PDFs)
-- One Agenda can have many Annexures
CREATE TABLE agenda_annexures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    content_id UUID NOT NULL REFERENCES agendas (id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    annexure_type annexure_type,
    file_path TEXT NOT NULL, -- Path to the PDF in your storage (S3/Local),
    summary TEXT,
    embedding vector (1536), -- Vector embedding for the annexure summary/content
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Template Table
-- Modular system for reusable snippets
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    content TEXT NOT NULL,
    type template_type NOT NULL, -- Is this for an Agenda or a Resolution?
    visibility template_visibility NOT NULL DEFAULT 'PRIVATE',
    created_by UUID NOT NULL REFERENCES users (id),
    title VARCHAR(200), -- Brief name for the template (e.g., "Standard PhD Approval")
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1. Setup Enums for Meeting Logic
CREATE TYPE meeting_type AS ENUM ('SYNDICATE', 'ACADEMIC');

CREATE TYPE meeting_status AS ENUM ('DRAFT', 'ONGOING', 'COMPLETED', 'CANCELLED');

-- 2. Meeting Table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    type meeting_type NOT NULL,
    status meeting_status DEFAULT 'DRAFT',
    meeting_link TEXT, -- e.g., Zoom/Teams link
    location VARCHAR(255), -- Physical room if applicable
    agenda_pdf_path TEXT, -- Full Agenda backup
    resolution_pdf_path TEXT, -- Final signed Minutes/Resolution
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
);

-- 3. Meeting Participants (The "Member List")
-- This table replaces the legacy 'MEETINGMEMBERS' from your SQL
CREATE TABLE meeting_participants (
    meeting_id UUID REFERENCES meetings (id) ON DELETE CASCADE,
    user_id UUID REFERENCES users (id) ON DELETE CASCADE,
    attendance_status BOOLEAN DEFAULT FALSE, -- Did they show up?
    remarks TEXT, -- e.g., "Left early" or "On leave"
    PRIMARY KEY (meeting_id, user_id)
);