# ValMed Prototype

This is a prototype for a patient management and drug analysis system using FastAPI, PostgreSQL, and a blockchain PoC (Ganache). The backend includes a minimal HTML frontend for demonstration.

## Services
- **backend**: FastAPI app with REST API and basic HTML UI
- **db**: PostgreSQL database
- **ganache**: Local Ethereum blockchain for PoC

## Running the Project

1. Build and start all services:
   ```sh
   docker-compose up --build
   ```

2. Access the backend:
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Basic UI: [http://localhost:8000/](http://localhost:8000/)

3. Database:
   - Host: `localhost`
   - Port: `5432`
   - User: `valmed`
   - Password: `valmedpass`
   - DB: `valmed`

4. Ganache (blockchain PoC):
   - RPC endpoint: `http://localhost:8545`

## Notes
- The backend will auto-create tables on startup.
- Blockchain PoC is stubbed for demonstration.
- For development, code changes in `./backend` will auto-reload the backend service. 