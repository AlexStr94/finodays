# prestart.sh

echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

while ! psql -lqt | cut -d \| -f 1 | grep -qw mock; do
    sleep 0.1
done

echo "mock database exists"

exec "$@"
