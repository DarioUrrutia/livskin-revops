"""Seed inicial de usuarios (ADR-0026).

Crea 2 cuentas:
- Dario (admin)
- Doctora (operadora)

Uso:
    python /app/scripts/seed_users.py [--reset]

Sin --reset: idempotente, no toca usuarios existentes.
Con --reset: re-genera passwords y resetea last_login_at = NULL (forzando primer-login flow).

Las passwords iniciales se imprimen UNA SOLA VEZ por stdout. Copialas inmediatamente.
"""
import secrets
import string
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select  # noqa: E402

from db import session_scope  # noqa: E402
from models.user import User  # noqa: E402
from services import auth_service  # noqa: E402


SEED_USERS = [
    {
        "cod_usuario": "USR0001",
        "username": "dario",
        "nombre_completo": "Dario Urrutia",
        "email": "daizurma@gmail.com",
        "rol": "admin",
    },
    {
        "cod_usuario": "USR0002",
        "username": "claudia",
        "nombre_completo": "Claudia Delgado",
        "email": None,
        "rol": "operadora",
    },
]


def generate_strong_password(length: int = 18) -> str:
    """Password aleatoria: letras + dígitos + 1 mayúscula + 1 dígito garantizados."""
    alphabet = string.ascii_letters + string.digits
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.isupper() for c in pwd)
            and any(c.islower() for c in pwd)
            and any(c.isdigit() for c in pwd)
        ):
            return pwd


def main(reset: bool = False) -> None:
    created: list[tuple[str, str]] = []

    with session_scope() as db:
        for spec in SEED_USERS:
            existing = db.execute(
                select(User).where(User.username == spec["username"])
            ).scalar_one_or_none()

            if existing is not None and not reset:
                print(f"SKIP {spec['username']}: ya existe (usar --reset para regenerar)")
                continue

            pwd = generate_strong_password()
            password_hash = auth_service.hash_password(pwd)

            if existing is None:
                user = User(
                    cod_usuario=spec["cod_usuario"],
                    username=spec["username"],
                    nombre_completo=spec["nombre_completo"],
                    email=spec["email"],
                    password_hash=password_hash,
                    rol=spec["rol"],
                    activo=True,
                    failed_login_count=0,
                )
                db.add(user)
                action = "CREADO"
            else:
                existing.password_hash = password_hash
                existing.last_login_at = None
                existing.failed_login_count = 0
                existing.locked_until = None
                action = "RESET"

            created.append((spec["username"], pwd))
            print(f"{action} {spec['username']} (rol={spec['rol']})")

    if not created:
        print("\nNada que hacer. Todos los usuarios ya existen.")
        return

    print()
    print("=" * 60)
    print("PASSWORDS INICIALES — COPIA AHORA, NO SE VOLVERÁN A MOSTRAR")
    print("=" * 60)
    for username, pwd in created:
        print(f"  {username:12s} {pwd}")
    print("=" * 60)
    print()
    print("En el primer login se forzará a cambiarlas.")


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    main(reset=reset_flag)
