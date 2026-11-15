# MAISON — REST API contract v1

`BASE_URL=http://127.0.0.1:8000/api/v1` (local development). JSON responses; user/admin Bearer access token required where noted. Interactive definitions and schemas: `GET /docs` or `/openapi.json`.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/restaurant` | Public | Restaurant about/contact/hours |
| PATCH | `/restaurant` | Admin | Edit restaurant information |
| POST | `/auth/register` | Public | Registration |
| POST | `/auth/login` | Public | Login, JWT token |
| GET/PATCH | `/users/me` | User | Profile |
| GET | `/menu/categories` | Public | Active categories |
| POST/PATCH | `/menu/categories`, `/menu/categories/{id}` | Admin | Manage categories |
| GET | `/menu/items?category_id=1&q=pasta&limit=20&offset=0` | Public | Menu search |
| GET | `/menu/items/{id}` | Public | Menu item |
| POST/PATCH/DELETE | `/menu/items`, `/menu/items/{id}` | Admin | Manage/archive dishes |
| GET | `/tables` | Public | Table metadata |
| POST | `/tables` | Admin | Add table |
| GET | `/reservations/availability?starts_at=...&guests=2` | Public | Available tables for requested time |
| POST | `/reservations` | User | Book a table |
| GET | `/reservations` | User | Own reservations |
| GET | `/reservations/{id}` | Owner/Admin | One reservation |
| POST | `/reservations/{id}/cancel` | Owner/Admin | Cancel booking |
| GET | `/admin/reservations` | Admin | Recent bookings |
| POST | `/orders` | User | Place pickup/dine-in order |
| GET | `/orders`, `/orders/{id}` | Owner/Admin* | Own orders / detail |
| POST | `/orders/{id}/cancel` | Owner | Cancel new order |
| GET | `/admin/orders` | Admin | Recent orders |
| PATCH | `/admin/orders/{id}/status` | Admin | Update kitchen/fulfillment status |

*The order list `/orders` is always own orders; admin accesses all through `/admin/orders`.

## Auth examples

**Register**
```http
POST /api/v1/auth/register
Content-Type: application/json

{"email":"customer@example.com","password":"safe-password-123","full_name":"Customer"}
```

**Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{"email":"customer@example.com","password":"safe-password-123"}
```

**Success**
```json
{"access_token":"<JWT>","token_type":"bearer","expires_in":3600}
```

Protected endpoints require `Authorization: Bearer <JWT>`.

## Reservation sample

Note: ISO 8601 timestamps must include timezone offset; `+06:00` is valid.

```http
POST /api/v1/reservations
Authorization: Bearer <JWT>
Content-Type: application/json

{"starts_at":"2026-12-20T19:00:00+06:00","guests":2,"table_id":1,"notes":"Near window, if available"}
```

Booking success returns status 201 with `id`, `table_id`, `user_id`, `guests`, `starts_at`, `ends_at`, `status`, `notes`, `created_at`.

When the requested table is not available: `409 {"detail":"No available table for this period and party size"}`. Omitting `table_id` automatically allocates the smallest suitable free table.

## Order sample

```http
POST /api/v1/orders
Authorization: Bearer <JWT>
Content-Type: application/json

{"order_type":"pickup","items":[{"menu_item_id":1,"quantity":2},{"menu_item_id":2,"quantity":1}],"notes":"No onions"}
```

**Response fields**: `id`, `user_id`, `reservation_id`, `order_type`, `status`, `total_som`, `notes`, `created_at`, `items[]` with `unit_price_som`, `line_total_som`, `name_snapshot`. Server uses current menu prices, ignoring any client-supplied price fields.

For `order_type="dine_in"`, a confirmed reservation belonging to the current user is required via `reservation_id`.

## Flutter example (package: dio)

```dart
import 'package:dio/dio.dart';

final dio = Dio(BaseOptions(baseUrl: 'http://10.0.2.2:8000/api/v1'));

Future<void> example() async {
  final login = await dio.post('/auth/login', data: {
    'email': 'customer@example.com',
    'password': 'safe-password-123',
  });
  final token = login.data['access_token'] as String;
  dio.options.headers['Authorization'] = 'Bearer $token';

  final menu = await dio.get('/menu/items');
  print(menu.data);

  final reservation = await dio.post('/reservations', data: {
    'starts_at': DateTime.now().add(const Duration(days: 3)).toUtc().toIso8601String(),
    'guests': 2,
  });
  print(reservation.data['id']);
}
```

For real apps, store the access token in secure device storage, inject it via a Dio interceptor, and handle `401` by asking the user to log in again.

## Browser frontend example (JavaScript)

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

async function login(email, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw await response.json();
  return (await response.json()).access_token;
}

async function loadOrders(token) {
  const response = await fetch(`${BASE_URL}/orders`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw await response.json();
  return response.json();
}
```

Prefer short-lived in-memory access tokens for the browser rather than localStorage; use HTTPS and design a refresh/cookie flow separately before production.

## HTTP status handling

- `200`: successful GET/PATCH/cancel
- `201`: created
- `204`: dish archived
- `401`: missing/invalid/expired JWT
- `403`: customer attempted admin operation
- `404`: resource not found, or not owned
- `409`: booking collision, invalid status transition, duplicate email or name
- `422`: request validation or business-rule failure

No payment processing, inventory availability, opening-hours enforcement or time-slot generation is included. The endpoint `GET /reservations/availability` accepts a particular datetime; the UI chooses the list of candidate datetimes to check.
