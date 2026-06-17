import asyncio
from app.db.database import get_db_pool, close_db_pool

async def seed_db():
    pool = await get_db_pool()
    
    # Create extension
    await pool.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create table
    await pool.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            model_name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            price FLOAT NOT NULL,
            release_date DATE,
            has_5g BOOLEAN DEFAULT FALSE,
            price_tier VARCHAR(100),
            image_url TEXT,
            
            camera_score FLOAT DEFAULT 0.0,
            performance_score FLOAT DEFAULT 0.0,
            battery_score FLOAT DEFAULT 0.0,
            display_score FLOAT DEFAULT 0.0,
            storage_score FLOAT DEFAULT 0.0,
            build_score FLOAT DEFAULT 0.0,
            value_score FLOAT DEFAULT 0.0,
            
            camera_sentiment FLOAT DEFAULT 0.0,
            performance_sentiment FLOAT DEFAULT 0.0,
            battery_sentiment FLOAT DEFAULT 0.0,
            display_sentiment FLOAT DEFAULT 0.0,
            storage_sentiment FLOAT DEFAULT 0.0,
            build_sentiment FLOAT DEFAULT 0.0,
            value_sentiment FLOAT DEFAULT 0.0,
            
            specs JSONB DEFAULT '{}',
            embedding vector(384)
        )
    ''')
    
    print("Database seeded with tables.")
    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(seed_db())
