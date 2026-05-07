import argparse
from getpass import getpass

from app.db.session import SessionLocal
from app.models.tenant import User, UserRole
from app.repositories.tenants import get_tenant_by_code
from app.repositories.users import create_user, get_user_by_username
from app.services.auth import hash_password


def create_admin_user(username: str, password: str, role: UserRole, merchant_code: str | None) -> User:
    with SessionLocal() as db:
        if get_user_by_username(db, username) is not None:
            raise ValueError(f"user already exists: {username}")

        tenant_id = None
        if role == UserRole.merchant_admin:
            if not merchant_code:
                raise ValueError("merchant_admin requires --merchant-code")
            tenant = get_tenant_by_code(db, merchant_code)
            if tenant is None:
                raise ValueError(f"invalid merchant code: {merchant_code}")
            tenant_id = tenant.id

        user = create_user(
            db,
            User(
                username=username,
                password_hash=hash_password(password),
                role=role,
                tenant_id=tenant_id,
            ),
        )
        db.commit()
        db.refresh(user)
        return user


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an API login user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password")
    parser.add_argument("--role", choices=[role.value for role in UserRole], default=UserRole.merchant_admin.value)
    parser.add_argument("--merchant-code", default="QCT001")
    args = parser.parse_args()

    password = args.password or getpass("Password: ")
    user = create_admin_user(args.username, password, UserRole(args.role), args.merchant_code)
    print(f"created user id={user.id} username={user.username} role={user.role.value} tenant_id={user.tenant_id}")


if __name__ == "__main__":
    main()
