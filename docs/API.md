# 📡 API Documentation

Complete reference for all Eclari API endpoints and database functions.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Public Routes](#public-routes)
3. [Protected Routes](#protected-routes)
4. [API Endpoints](#api-endpoints)
5. [Database Functions](#database-functions)
6. [Response Formats](#response-formats)
7. [Error Handling](#error-handling)

---

## Authentication

All protected routes and API endpoints require a valid Supabase JWT token.

### How Authentication Works

1. **Login:** User authenticates via `/login` with email/password
2. **Token Generation:** Supabase creates a JWT token on successful login
3. **Cookie Storage:** Frontend stores token in `supabase-token` cookie
4. **Token Verification:** Flask middleware (`@verify_supabase_token`) validates token on each request
5. **Session Management:** User info stored in Flask session for quick access

### Token Validation

```python
@app.route("/protected")
@verify_supabase_token  # This decorator validates the token
def protected_route():
    user = session.get('user')  # Access authenticated user
    return f"Hello, {user['email']}"
```

### Authentication Headers

All authenticated requests should include:
```
Cookie: supabase-token=<JWT_TOKEN>
```

---

## Public Routes

### `GET /`
**Description:** Landing page  
**Authentication:** Not required  
**Response:** HTML page with system overview

### `GET /login`
**Description:** Login page  
**Authentication:** Not required  
**Response:** HTML login form

---

## Protected Routes

All these routes require authentication via `@verify_supabase_token`.

### `GET /dashboard/<role>`
**Description:** Role-specific dashboard  
**Authentication:** Required  
**Parameters:**
- `role` (path): One of `student`, `teacher`, `finance`, `hall`, `coach`, `lab`

**Response:** HTML dashboard with role-specific data

**Example:**
```
GET /dashboard/student
```

### `GET /subject/<subject_id>`
**Description:** Subject detail page showing books/materials for that subject  
**Authentication:** Required  
**Parameters:**
- `subject_id` (path): Subject identifier (e.g., "MATH-Y2", "PHYS-Y1")

**Response:** HTML page with:
- Subject name and teacher
- Books for this subject
- Materials for this subject
- Clearance percentage
- Return status and actions

**Example:**
```
GET /subject/MATH-Y2
```

---

## API Endpoints

### Upload Proof of Return

#### `POST /api/upload-proof`
**Description:** Upload photo proof that Y1 student returned a book  
**Authentication:** Required (student only)  

**Request Body (multipart/form-data):**
- `book_id`: String - ID of the book being returned
- `photo`: File - Image file (JPEG, PNG, or HEIC)

**Response:**
```json
{
  "success": true,
  "message": "Proof uploaded successfully",
  "book": {
    "book_id": "BK001",
    "proof_image_url": "https://...",
    "proof_uploaded_at": "2025-01-15T10:30:00"
  }
}
```

**Error Responses:**
```json
{
  "success": false,
  "error": "No file uploaded"
}

{
  "success": false,
  "error": "Invalid file type"
}

{
  "success": false,
  "error": "File too large (max 5MB)"
}
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('book_id', 'BK001');
formData.append('photo', fileInput.files[0]);

const response = await fetch('/api/upload-proof', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

---

### Generate Clearance PDF

#### `GET /api/generate-clearance-pdf`
**Description:** Generate and download a PDF certificate when student is 100% cleared  
**Authentication:** Required (student only)  

**Response:** PDF file download

**Example:**
```javascript
window.location.href = '/api/generate-clearance-pdf';
```

**Note:** This endpoint checks if the student has 100% clearance before generating PDF. If not cleared, it returns an error page.

---

### Approve Photo Proof

#### `POST /api/approve-proof`
**Description:** Teacher approves a Y1 student's photo proof  
**Authentication:** Required (teacher only)  

**Request Body (JSON):**
```json
{
  "book_id": "BK001",
  "approved": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Proof approved",
  "book": {
    "book_id": "BK001",
    "returned": true,
    "return_date": "2025-01-15"
  }
}
```

**Example:**
```javascript
await fetch('/api/approve-proof', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ book_id: 'BK001', approved: true })
});
```

---

### Mark Book Returned (Y2 Physical Return)

#### `POST /api/mark-returned`
**Description:** Teacher marks a Y2 book as physically returned  
**Authentication:** Required (teacher only)  

**Request Body (JSON):**
```json
{
  "book_id": "BK002"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Book marked as returned",
  "book": {
    "book_id": "BK002",
    "returned": true,
    "return_date": "2025-01-15"
  }
}
```

---

### Update Finance Status

#### `POST /api/update-finance`
**Description:** Finance staff updates student's balance  
**Authentication:** Required (finance staff only)  

**Request Body (JSON):**
```json
{
  "student_id": "ST001",
  "amount_due": 0,
  "replacement_costs": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Finance status updated"
}
```

---

### Update Hall Status

#### `POST /api/update-hall`
**Description:** Hall head marks room as cleared  
**Authentication:** Required (hall staff only)  

**Request Body (JSON):**
```json
{
  "student_id": "ST001",
  "cleared": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hall status updated"
}
```

---

## Database Functions

These are Python functions in `supabase_client.py` that the API endpoints use.

### Student Functions

#### `get_student_by_id(student_id: str) -> dict`
Get student profile with all clearance information.

**Returns:**
```python
{
  'student_id': 'ST001',
  'first_name': 'Ama',
  'last_name': 'Nkrumah',
  'email': 'ama@example.com',
  'year_group': 'Y1',
  'clearance_percentage': 75.5
}
```

---

#### `get_student_books(student_id: str) -> list[dict]`
Get all books assigned to a student.

**Returns:**
```python
[
  {
    'book_id': 'BK001',
    'book_code': 'MATH-101',
    'book_name': 'Mathematics Y2 Textbook',
    'subject_id': {'subject_id': 'MATH-Y2', 'subject_name': 'Mathematics'},
    'returned': False,
    'proof_image_url': None,
    'proof_uploaded_at': None
  }
]
```

---

#### `get_student_materials(student_id: str) -> list[dict]`
Get all materials (lab equipment, sports gear, etc.) assigned to a student.

**Returns:**
```python
[
  {
    'material_id': 'MAT001',
    'material_code': 'LAB-GOGGLES',
    'material_name': 'Safety Goggles',
    'material_type': 'lab',
    'returned': True,
    'return_date': '2025-01-10'
  }
]
```

---

#### `calculate_overall_clearance_percentage(student_id: str) -> float`
Calculate student's overall clearance percentage across all categories.

**Formula:**
```
(Books Returned + Materials Returned + Finance Clear + Hall Clear) / Total Items * 100
```

**Returns:** `75.5` (percentage)

---

#### `calculate_overall_clearance_status(student_id: str) -> str`
Get clearance status as a string.

**Returns:** One of:
- `"Cleared"` - 100% complete
- `"Not Cleared"` - < 100%

---

### Teacher Functions

#### `get_teacher_by_id(teacher_id: str) -> dict`
Get teacher profile information.

**Returns:**
```python
{
  'teacher_id': 'T001',
  'first_name': 'John',
  'last_name': 'Smith',
  'email': 'john@example.com',
  'subject_specialization': 'Mathematics'
}
```

---

#### `get_teacher_classes(teacher_id: str) -> list[dict]`
Get all classes taught by a teacher.

**Returns:**
```python
[
  {
    'class_id': 'CLS001',
    'class_name': 'Math Y2-A',
    'subject': {'subject_id': 'MATH-Y2', 'subject_name': 'Mathematics'}
  }
]
```

---

#### `get_pending_approvals_for_teacher(teacher_id: str) -> list[dict]`
Get all Y1 books awaiting photo approval from this teacher's subjects.

**Returns:**
```python
[
  {
    'book_id': 'BK001',
    'book_name': 'Math Textbook',
    'student': {'student_id': 'ST001', 'first_name': 'Ama'},
    'proof_image_url': 'https://...',
    'proof_uploaded_at': '2025-01-15T10:30:00'
  }
]
```

---

### File Upload Functions

#### `upload_proof_image(book_id: str, file_content: bytes, content_type: str) -> str`
Upload photo proof to Supabase Storage.

**Parameters:**
- `book_id`: ID of the book
- `file_content`: Binary file content
- `content_type`: MIME type (e.g., 'image/jpeg')

**Returns:** Public URL of uploaded file
```python
"https://xyz.supabase.co/storage/v1/object/public/clearance-proofs/BK001_proof.jpg"
```

---

### Update Functions

#### `mark_book_returned(book_id: str) -> bool`
Mark a book as physically returned (for Y2 students).

**Returns:** `True` if successful

---

#### `approve_proof(book_id: str) -> bool`
Approve Y1 student's photo proof and mark book as returned.

**Returns:** `True` if successful

---

#### `update_finance_status(student_id: str, amount_due: float, replacement_costs: float) -> bool`
Update student's financial clearance status.

**Returns:** `True` if successful

---

#### `update_hall_status(student_id: str, cleared: bool) -> bool`
Update student's hall clearance status.

**Returns:** `True` if successful

---

## Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* optional result data */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

### Validation Error
```json
{
  "success": false,
  "error": "Invalid input",
  "details": {
    "field": "email",
    "message": "Must be a valid email address"
  }
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input or missing parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User doesn't have permission for this operation
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server-side error occurred

### Common Error Scenarios

**Invalid Token:**
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

**Permission Denied:**
```json
{
  "success": false,
  "error": "You don't have permission to perform this action"
}
```

**Not Found:**
```json
{
  "success": false,
  "error": "Student not found"
}
```

**Database Error:**
```json
{
  "success": false,
  "error": "Database operation failed"
}
```

---

## Rate Limiting

Currently, there's no rate limiting implemented. For production, consider:

- **Per user:** 100 requests per minute
- **Per IP:** 1000 requests per hour
- **File uploads:** 10 uploads per minute

---

## Webhook Support

Not currently implemented, but planned for future:

- `clearance.completed` - Triggered when student reaches 100%
- `proof.uploaded` - Triggered when Y1 student uploads photo
- `approval.needed` - Triggered when teacher approval needed

---

## Testing Endpoints

Use these tools for testing:

### cURL Examples

**Login:**
```bash
curl -X POST https://your-project.supabase.co/auth/v1/token \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password"}'
```

**Upload Proof:**
```bash
curl -X POST http://localhost:5000/api/upload-proof \
  -H "Cookie: supabase-token=YOUR_TOKEN" \
  -F "book_id=BK001" \
  -F "photo=@/path/to/image.jpg"
```

**Get Dashboard:**
```bash
curl http://localhost:5000/dashboard/student \
  -H "Cookie: supabase-token=YOUR_TOKEN"
```

---

## Best Practices

1. **Always validate input** - Never trust client-side data
2. **Use transactions** - For operations that update multiple tables
3. **Handle errors gracefully** - Return user-friendly messages
4. **Log everything** - Use `print()` for debugging (replace with proper logging in production)
5. **Validate file types** - Only accept allowed image formats
6. **Limit file sizes** - Enforce 5MB maximum for uploads
7. **Use RLS policies** - Let Supabase handle row-level security
8. **Cache when possible** - Store frequently accessed data in session

---

<div align="center">
Questions? Check the <a href="./DEVELOPMENT.md">Development Guide</a> or <a href="../README.md">README</a>
</div>
