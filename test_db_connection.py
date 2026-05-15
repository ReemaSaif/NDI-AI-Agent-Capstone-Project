import psycopg2

try:
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ndi_agent_management",
        user="postgres",
        password="Project33"
    )

    print("Connected successfully to PostgreSQL!")

    connection.close()

except Exception as e:
    print("Connection failed:")
    print(e)

