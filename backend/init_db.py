import asyncio
from app.database import engine, Base
from app.models import *  # Make sure all models are imported

async def init_tables():
    async with engine.begin() as conn:
        print("Création des tables dans la base de données...")
        await conn.run_sync(Base.metadata.create_all)
        print("Opération terminée.")

if __name__ == "__main__":
    asyncio.run(init_tables())
