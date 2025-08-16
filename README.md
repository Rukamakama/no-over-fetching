# Smarter REST API – Fixing Over-Fetching with Field Selection

This project is a companion to my article:  
**[Fetch Only What You Need: Smarter REST APIs Without Over-Fetching](https://medium.com/)**  

It shows how to reduce **data over-fetching** in REST APIs without changing your tech stack.  
The example here is implemented with **Python, FastAPI, and SQLAlchemy**, but the principles are **stack independent** and can be applied in any backend.  

---

## ✨ Features
 
- **Field Selection** – request only specific fields and nested attributes via query params
- **Flexible Query Language** – use curly braces `{}` for nested fields and commas for field separation
- **Relationship Loading** – efficiently load related data with eager loading to prevent N+1 queries

---

## 📋 Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy 2.0+
- Uvicorn (for running the server)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd no-over-fetching
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
```bash
python init_db.py
```

### 4. Start the Server
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

---

## 📖 Usage & Examples

### Field Selection Query Language

The `fields` parameter uses a simple query language:
- **Simple fields**: comma-separated → `id,status,user_id`
- **Nested fields**: use curly braces → `user{username,email}`
- **Deep nesting**: multiple levels → `orders{id,user{username},product{name,price}}`

### API Endpoints

#### 1. List Orders (with Field Selection)

**Basic Request:**
```http
GET /orders
```

**Response:**
```json
[
  {
    "id": 1,
    "status": "pending",
    "user_id": 1,
    "product_id": 1,
    "address_id": 1
  },
  {
    "id": 2,
    "status": "pending",
    "user_id": 2,
    "product_id": 2,
    "address_id": 2
  }
]
```

**Field Selection Request:**
```http
GET /orders?fields=id,status
```

**Response:**
```json
[
  {
    "id": 1,
    "status": "pending"
  },
  {
    "id": 2,
    "status": "pending"
  }
]
```

**Nested Field Selection Request:**
```http
GET /orders?fields=orders{id,status,users{username},products{name},addresses{zipcode}}
```

**Response:**
```json
[
  {
    "id": 1,
    "status": "pending",
    "user": {
      "username": "john_doe"
    },
    "product": {
      "name": "Laptop"
    },
    "address": {
      "zipcode": "12345"
    }
  },
  {
    "id": 2,
    "status": "pending",
    "user": {
      "username": "jane_smith"
    },
    "product": {
      "name": "Mouse"
    },
    "address": {
      "zipcode": "54321"
    }
  }
]
```

#### 2. Get Single Order

**Request:**
```http
GET /orders/1
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "user_id": 1,
  "product_id": 1,
  "address_id": 1
}
```

#### 3. Get Product

**Request:**
```http
GET /products/1
```

**Response:**
```json
{
  "id": 1,
  "name": "Laptop",
  "price": "999.99"
}
```

#### 4. Get Address

**Request:**
```http
GET /addresses/1
```

**Response:**
```json
{
  "id": 1,
  "zipcode": "12345",
  "country": "USA"
}
```

---


## 📁 Project Structure

```
no-over-fetching/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy models (User, Order, Product, Address)
├── routes.py            # API route handlers
├── utils.py             # Field parsing and query utilities
├── init_db.py           # Database initialization with sample data
├── requirements.txt     # Python dependencies
├── test_field_queries.py # Test suite
└── README.md           # This file
```

---

## 🔧 How It Works

1. **Field Parsing**: The `parse_params()` function in `utils.py` converts the field selection string into a structured list
2. **Query Building**: The `fields_to_query()` function builds SQLAlchemy queries with eager loading based on requested fields
3. **Response Filtering**: Only requested fields are included in the JSON response, reducing payload size
4. **Relationship Mapping**: Plural relationship names (e.g., `users`) are mapped to singular model relationships (e.g., `user`)

---

## 🎯 Benefits

- **Reduced Bandwidth**: Only fetch the data you need
- **Better Performance**: Fewer database queries with eager loading
- **Flexible Frontend**: Frontend can request exactly what it needs for each view
- **No Over-fetching**: Eliminate unnecessary data transfer
- **GraphQL Alternative**: Get GraphQL-like flexibility with REST APIs

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
