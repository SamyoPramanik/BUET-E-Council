# API Documentation

## 1. Overview

**Base URL**: `http://localhost:8000/api`

This API provides endpoints for managing the BUET E-Council system. It handles users, members (academic/syndicate), meetings, agenda items with versioning, attachments (annexures), and templates.

### 1.1 Authentication & Authorization
All endpoints (except `/auth/signin`) require a valid Bearer Token in the `Authorization` header.
- **Header Format**: `Authorization: Bearer <token>`

### 1.2 Common API Parameters
- **Pagination**: Use `page` (default: 1) and `limit` (default: 10).
  - Example: `GET /users?page=2&limit=20`
- **Sorting**: Use `sort_by` (field name) and `order` (`asc` or `desc`).
  - Example: `GET /meetings?sort_by=meeting_date&order=desc`
- **Searching**: Use `q` for keyword search or specific fields.
  - Example: `GET /members?q=professor`

### 1.3 Standard Response Format
**Success Response**:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "RESOURCE_NOT_FOUND", 
  "details": {} 
}
```

### 1.4 Data Types (Enums)
Refer to these values when creating/updating resources:
- **User Role**: `admin`, `moderator`, `member`
- **Member Type**: `academic`, `syndicate`, `none`
- **Meeting Type**: `syndicate`, `academic`
- **Meeting Status**: `locked`, `open`, `end`
- **Member Status**: `active`, `onleave`, `past`
- **Template Visibility**: `public`, `private`
- **Content Type**: `agendaItem`, `resolutionItem`

---

## 2. Authentication

### POST `/auth/signin`
Authenticate a user and retrieve an access token.

**Request Body**:
```json
{
  "username": "admin_user",
  "password": "secret_password"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid-string",
      "username": "admin_user",
      "role": "admin"
    }
  }
}
```

**Response (401 Unauthorized)**:
```json
{
  "success": false,
  "message": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS"
}
```

### POST `/auth/signout`
Invalidate the current session.

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 3. Users Management

### GET `/users`
List all users with pagination and filtering.
**Query Parameters**:
- `role`: Filter by role (e.g., `admin`, `member`)
- `status`: Filter by status (`active`, `inactive`)
- `page`, `limit`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "uuid-1",
        "username": "john_doe",
        "email": "john@example.com",
        "role": "member",
        "status": "active"
      }
    ],
    "pagination": {
      "total": 50,
      "page": 1,
      "limit": 10,
      "total_pages": 5
    }
  }
}
```

**Response (403 Forbidden)**:
```json
{
  "success": false,
  "message": "Access denied. Admin role required."
}
```

### POST `/users`
Create a new user account.

**Request Body**:
```json
{
  "username": "new_user",
  "email": "user@buet.ac.bd",
  "password": "secure_password",
  "role": "member",
  "member_type": "none"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "uuid-new",
    "username": "new_user",
    "email": "user@buet.ac.bd",
    "role": "member",
    "status": "active",
    "created_at": "2023-11-01T10:00:00Z"
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "success": false,
  "message": "Validation error",
  "details": {
    "email": "Invalid email format"
  }
}
```

**Response (409 Conflict)**:
```json
{
  "success": false,
  "message": "Username or email already exists"
}
```

### GET `/users/{id}`
Get details of a specific user.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "member",
    "status": "active",
    "created_at": "2023-11-01T10:00:00Z"
  }
}
```

**Response (404 Not Found)**:
```json
{
  "success": false,
  "message": "User not found"
}
```

### PATCH `/users/{id}`
Update user details.

**Request Body**:
```json
{
  "email": "new_email@example.com",
  "role": "moderator"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "id": "uuid-1",
    "email": "new_email@example.com",
    "role": "moderator"
  }
}
```

### DELETE `/users/{id}`
Deactivate a user.

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

---

## 4. Members Management

### GET `/members`
List all potential meeting attendees.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "members": [
      {
        "id": "uuid-m1",
        "name": "Dr. Smith",
        "status": "active",
        "type": "academic", // Inferred from joined table
        "designation": "Professor"
      }
    ]
  }
}
```

### POST `/members`
Create a new member profile.

**Request Body (Syndicate)**:
```json
{
  "name": "Dr. X",
  "status": "active",
  "user_id": "optional-uuid",
  "type": "syndicate",
  "designation": "Dean",
  "address": "Dhaka"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "Member created successfully",
  "data": {
    "id": "uuid-m2",
    "name": "Dr. X",
    "type": "syndicate"
  }
}
```

---

## 5. Meetings Management

### GET `/meetings`
List scheduled meetings.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "meetings": [
      {
        "id": "uuid-mt1",
        "title": "50th Syndicate Meeting",
        "meeting_date": "2023-11-15T10:00:00Z",
        "status": "open",
        "type": "syndicate"
      }
    ]
  }
}
```

### POST `/meetings`
Schedule a new meeting.

**Request Body**:
```json
{
  "title": "50th Syndicate Meeting",
  "meeting_date": "2023-11-15T10:00:00Z",
  "type": "syndicate",
  "meeting_link": "https://zoom.us/j/123456"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "Meeting scheduled successfully",
  "data": {
    "id": "uuid-mt2",
    "title": "50th Syndicate Meeting",
    "meeting_date": "2023-11-15T10:00:00Z",
    "status": "open"
  }
}
```

### POST `/meetings/{id}/lock`
Lock a meeting.

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Meeting locked successfully. No further agenda changes allowed."
}
```

**Response (400 Bad Request)**:
```json
{
  "success": false,
  "message": "Meeting is already ended"
}
```

---

## 6. Agenda & Content

### GET `/meetings/{id}/agenda`
List agenda items.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "agenda_items": [
      {
        "id": "uuid-ag1",
        "agenda_serial": 1,
        "text_content": "Approval of minutes...",
        "decision": "Approved",
        "annexures": []
      }
    ]
  }
}
```

### POST `/meetings/{id}/agenda`
Add a new agenda item.

**Request Body**:
```json
{
  "agenda_serial": 1,
  "text_content": "Approval of previous meeting minutes...",
  "decision": "Approved unanimously", 
  "tags": ["administrative", "minutes"]
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "Agenda item added",
  "data": {
    "id": "uuid-ag2",
    "text_content": "Approval of previous meeting minutes..."
  }
}
```

**Response (403 Forbidden)**:
```json
{
  "success": false,
  "message": "Cannot modify agenda for a locked meeting"
}
```

### GET `/agenda/search`
Semantic search.

**Query Parameters**: `q=enrollment`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid-ag5",
        "text_content": "Discussing student enrollment increase...",
        "similarity_score": 0.89,
        "meeting_date": "2023-09-10"
      }
    ]
  }
}
```

---

## 7. Actions & Attendance

### POST `/meetings/{id}/attendance`
Record attendance.

**Request Body**:
```json
{
  "attendees": [
    { "member_id": "uuid-m1", "is_present": "yes" },
    { "member_id": "uuid-m2", "is_present": "no" }
  ]
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Attendance updated"
}
```

### PATCH `/agenda/{id}/execution`
Update execution status of a resolution.

**Request Body**:
```json
{
  "is_executed": "yes",
  "execution_status": "Implemented by Engineering Dept on 2023-12-01"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Execution status updated"
}
```

---

## 8. Annexures (Files)

### POST `/agenda/{id}/annexures`
Upload a file.

**Request Body**: Multipart/Form-Data
- `file`: (Binary data)
- `type`: `agendaItem`
- `summary`: "Scanned copy of minutes"

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "File uploaded",
  "data": {
    "id": "uuid-an1",
    "file_name": "minutes.pdf",
    "url": "/uploads/minutes.pdf"
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "success": false,
  "message": "Invalid file type. Only PDF permitted."
}
```

---

## 9. Templates

### GET `/templates`
List available templates for agenda or resolutions.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "uuid-t1",
        "text_content": "## Standard Agenda...",
        "type": "agendaItem",
        "visibility": "public"
      }
    ]
  }
}
```

### POST `/templates`
Create a new reusable template.

**Request Body**:
```json
{
  "text_content": "## Standard Agenda Structure\n\n1. Introduction...",
  "visibility": "public",
  "type": "agendaItem"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "Template created",
  "data": {
    "id": "uuid-t2",
    "type": "agendaItem"
  }
}
```
