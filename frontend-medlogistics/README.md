# Medication Logistics Frontend (MVP)

This is the React PWA frontend for the Medication Logistics MVP. It is designed for speed, clarity, and role-based workflows (Doctor, Nurse, Pharmacist).

## Features

- **Role-based Dashboards:** Doctor, Nurse, and Pharmacist views.
- **Drug Inventory:** View, add, update, and see low-stock drugs (Pharmacist).
- **Medication Orders:** Create and view prescriptions (Doctor).
- **Medication Administration:** Record administration events (Nurse).
- **API Key Authentication:** All requests require an API key in the `X-API-Key` header.

## Tech Stack

- React (Vite)
- Tailwind CSS
- Nginx (for production build)
- Docker (for containerization)

## Getting Started

### Development

```sh
npm install
npm run dev
```

### Production Build

```sh
npm run build
```

### Docker

Build and run with Docker Compose (see project root):

```sh
docker-compose up --build
```

## API Endpoints

- `GET /drugs` — View all drugs
- `POST /drugs` — Add drug (Pharmacist)
- `PUT /drugs/{id}` — Update drug (Pharmacist)
- `GET /drugs/low-stock` — Low stock drugs (Pharmacist)
- `GET /orders` — View active orders
- `POST /orders` — Create order (Doctor)
- `POST /administrations` — Record administration (Nurse)

## Environment Variables

- `VITE_API_URL` — The base URL for the backend API (default: `/api`)

## Testing

See below for test instructions.