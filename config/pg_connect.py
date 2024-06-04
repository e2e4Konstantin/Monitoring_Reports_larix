from typing import NamedTuple


class DatabaseAccess(NamedTuple):
    """Учетные данные доступа для подключению к базе данных."""
    host: str
    port: int
    database: str
    username: str
    password: str
    database_type: str = "PostgreSQL"

    def __repr__(self) -> str:
        return f"{self.database_type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def as_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,}


# Connect to the PostgreSQL database
ais_access = DatabaseAccess(
    host="172.16.51.8", port=5432, database="normativ", username="read_larix", password="read_larix"
)

if __name__ == "__main__":
    print(*ais_access)
    print(ais_access)
    print(ais_access.__repr__())

