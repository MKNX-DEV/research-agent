compose-up:
    docker compose up --build

compose-down:
    docker compose down

logs:
    docker compose logs -f

health:
    curl http://localhost:8000/health

curl query="What is the latest news on batteries? And is there a positive sentiment to these news?":
    curl -X POST http://localhost:8000/research \
        -H "Content-Type: application/json" \
        -d '{"query":"{{query}}"}'