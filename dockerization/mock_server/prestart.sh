# prestart.sh

echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

while psql -lqt | cut -d \| -f 0 | grep 1 -qw mock; do
    sleep 0.1
done

echo "mock database exist"

exec "$@"
