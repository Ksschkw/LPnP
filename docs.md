# LocaLe API - Comprehensive Documentation 
> or just use swagger lol

##  Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Admin Features](#admin-features)
- [Error Handling](#error-handling)
- [Development](#development)

##  Overview

**LocaLe** is a peer-to-peer marketplace where **"Your Community is Your Credential"**. This API powers a trust-based local service platform where users can offer and book services within their community.

### Key Features
- **JWT Authentication** - Secure user authentication
- **User Profiles** - Comprehensive user management
- **Service Marketplace** - Create, browse, and manage services
- **Service Categories** - Organized service classification
- **Trust System** - Community-based verification and ratings
- **Admin Panel** - Full platform management capabilities

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT Bearer Tokens
- **Documentation**: Auto-generated OpenAPI/Swagger

---

## Quick Start

### Base URL
```
http://127.0.0.1:8000
```

### Interactive Documentation
Visit the auto-generated Swagger UI at:
```
http://127.0.0.1:8000/docs
```

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

---

## Authentication

LocaLe uses **JWT Bearer Token** authentication. Most endpoints require a valid token in the Authorization header.

### Getting a Token
1. **Register** a new user account
2. **Login** with phone and password
3. **Use the token** in subsequent requests

### Example Auth Header
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Lifetime
- **30 minutes** default expiration
- Automatic token refresh recommended

---

## API Endpoints

### User Management

#### Register New User
```http
POST /users/
```
**Request Body:**
```json
{
  "name": "Kosi okafor",
  "email": "kosi@example.com",
  "phone": "+1234567890",
  "password": "securepassword123"
}
```

#### 🔹 User Login
```http
POST /users/login
```
**Response:**
```json
{
  "id": "user-uuid",
  "name": "Kosi Okafor",
  "phone": "+1234567890",
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

#### 🔹 Get My Profile
```http
GET /users/me
```
*Requires authentication*

#### 🔹 Update My Profile
```http
PUT /users/me
```
**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

#### 🔹 Get Specific User
```http
GET /users/{user_id}
```

#### 🔹 Update User (Admin)
```http
PUT /users/{user_id}
```

#### 🔹 Delete User
```http
DELETE /users/{user_id}
```

### 🛠️ Service Management

#### 🔹 Browse Active Services
```http
GET /services/?skip=0&limit=100
```

#### 🔹 Get Service Details
```http
GET /services/{service_id}
```

#### 🔹 Create New Service
```http
POST /services/
```
**Request Body:**
```json
{
  "title": "Professional Plumbing",
  "description": "Expert plumbing services for homes and offices",
  "base_price": 75000.00,
  "hourly_rate": 50000.00,
  "service_radius_km": 25,
  "current_location": "Ikate, Lekki",
  "category_name": "Home-Services"
}
```

#### 🔹 Update Service
```http
PUT /services/{service_id}
```

#### 🔹 Delete Service
```http
DELETE /services/{service_id}
```

#### 🔹 Activate Service
```http
POST /services/{service_id}/activate
```

#### 🔹 Get My Services
```http
GET /services/my
```
*Returns all services created by the current user*

#### 🔹 Get Services by Seller
```http
GET /services/seller/{seller_id}
```

### Admin Endpoints

*All admin endpoints require `admin_key` query parameter*

#### 🔹 Create Category
```http
POST /admin/categories/categories?name=CategoryName&description=Description&admin_key=your_admin_key
```

#### 🔹 List Categories
```http
GET /admin/categories/categories?admin_key=your_admin_key
```

#### 🔹 Get All Users (Full Data)
```http
GET /admin/categories/users?skip=0&limit=100&admin_key=your_admin_key
```

---

## Data Models

### 👤 User Models

#### UserBaseResponse
```json
{
  "id": "uuid-string",
  "name": "Kosi King",
  "email": "kosi@example.com",
  "phone": "+1234567890", (I did not handle this lol, maybe FE would)
  "avatar_url": "https://example.com/avatar.jpg",
  "trust_score": 85,
  "verification_level": 2,
  "is_online": true,
  "last_active": "2024-01-15T10:30:00Z"
}
```

#### UserDetailResponse (Admin)
```json
{
  ...UserBaseResponse,
  "nin_verified": true,
  "completion_count": 15,
  "total_earnings": 2500.00,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### UserWithTokenResponse
```json
{
  ...UserBaseResponse,
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### 🛠️ Service Models

#### ServiceBaseResponse
```json
{
  "id": "uuid-string",
  "title": "Service Title",
  "description": "Service description",
  "base_price": "75.00",
  "hourly_rate": "50.00",
  "service_radius_km": 25,
  "current_location": "New York, NY",
  "is_available_now": true,
  "status": "active",
  "trust_points": 42,
  "completion_count": 8,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### ServiceDetailResponse
```json
{
  ...ServiceBaseResponse,
  "seller": { /* UserBaseResponse */ },
  "categories": [
    {
      "id": "category-uuid",
      "name": "Home-Services",
      "description": "Home related services",
      "icon_url": "https://example.com/icon.png"
    }
  ],
  "total_earnings": "600.00",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

OpenAPI schema 
### What eh Get:
1. **Complete API Specification** - All endpoints, methods, parameters
2. **Request/Response Schemas** - Exact data structures
3. **Authentication Flow** - JWT token handling
4. **Error Handling** - Standardized error responses
5. **Interactive Documentation** - Live testing via Swagger UI

### FE ready?:
1. **User Registration/Login Flow**
2. **Service Browsing & Search**
3. **Service Creation & Management**
4. **User Profile Management**
5. **Admin Dashboard**

---

## Admin Features

### Admin Key Setup
Set `ADMIN_KEY` environment variable to enable admin features.

### Admin Capabilities:
- ✅ Create and manage service categories
- ✅ View all user data (including private fields)

### Example Admin Flow:
```bash
# Create categories
curl -X POST "http://127.0.0.1:8000/admin/categories/categories?name=Plumbing&description=Plumbing%20services&admin_key=your_key"

# View all users
curl -X GET "http://127.0.0.1:8000/admin/categories/users?admin_key=your_key"
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": [
    {
      "loc": ["body", "phone"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (admin access denied)
- `404` - Not Found
- `422` - Unprocessable Entity (input validation failed)

---

## Development

### Environment Setup
```bash
# Clone and setup
git clone <repository>
cd LPnP

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your database and admin settings

# Run development server
uvicorn app.main:app --reload
```

### Key Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/locale_db
SECRET_KEY=your-jwt-secret-key
ADMIN_KEY=your-admin-access-key
```

### Database Schema
The API automatically creates necessary tables on startup using SQLAlchemy models.

---

##  Support & Resources

- **API Documentation**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`
- **Health Check**: `http://127.0.0.1:8000/health`

---

---