"""Run database seed manually: roles, permissions, super admin user."""

from app.db.seed import seed_database

if __name__ == "__main__":
    seed_database()
    print("Seed completed. Login: superadmin@school.com / SuperAdmin@123")
