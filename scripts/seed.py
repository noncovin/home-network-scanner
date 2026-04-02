from database.db import Base, engine, SessionLocal
from database import crud


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        scan = crud.create_scan(db, scan_name="Seed Scan", target="192.168.1.0/24")
        crud.add_device_with_ports(
            db,
            scan.id,
            {
                "ip": "192.168.1.1",
                "mac": "00:11:22:33:44:55",
                "hostname": "router.local",
                "status": "up",
                "ports": [
                    {"port": 80, "protocol": "tcp", "state": "open", "service": "http"},
                    {"port": 443, "protocol": "tcp", "state": "open", "service": "https"},
                ],
            },
        )
        crud.complete_scan(db, scan)
        print("Seed data created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
