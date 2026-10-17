"""Run database seed manually: roles, permissions, and configured initial admin."""

from app.db.seed import seed_database

if __name__ == "__main__":
    seed_database()
    print("Seed completed.")
