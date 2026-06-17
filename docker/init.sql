CREATE EXTENSION IF NOT EXISTS vector;

-- Phones Table
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    price_inr INTEGER,
    price_tier VARCHAR(20),
    amazon_url TEXT,
    flipkart_url TEXT,
    display_size NUMERIC(4,2),
    display_type VARCHAR(50),
    refresh_rate INTEGER,
    resolution VARCHAR(50),
    peak_brightness INTEGER,
    chipset VARCHAR(100),
    ram_gb INTEGER[],
    storage_gb INTEGER[],
    os VARCHAR(50),
    main_camera_mp NUMERIC(5,1),
    camera_setup VARCHAR(255),
    front_camera_mp NUMERIC(5,1),
    ultrawide_mp NUMERIC(5,1),
    telephoto_mp NUMERIC(5,1),
    optical_zoom NUMERIC(4,1),
    video_max VARCHAR(50),
    battery_mah INTEGER,
    charging_watts INTEGER,
    wireless_charging_w INTEGER,
    weight_grams INTEGER,
    dimensions VARCHAR(100),
    ip_rating VARCHAR(20),
    build_material VARCHAR(100),
    has_5g BOOLEAN DEFAULT true,
    has_nfc BOOLEAN DEFAULT false,
    has_ir_blaster BOOLEAN DEFAULT false,
    has_headphone_jack BOOLEAN DEFAULT false,
    usb_type VARCHAR(20),
    release_date DATE,
    image_url TEXT,
    gsmarena_url TEXT,
    source VARCHAR(50),
    performance_score NUMERIC(3,1),
    camera_score NUMERIC(3,1),
    battery_score NUMERIC(3,1),
    display_score NUMERIC(3,1),
    value_score NUMERIC(3,1),
    overall_score NUMERIC(3,1),
    description_text TEXT,
    embedding vector(384),
    search_vector tsvector,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Personas Table
CREATE TABLE IF NOT EXISTS personas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    weight_performance NUMERIC(3,2) NOT NULL,
    weight_camera NUMERIC(3,2) NOT NULL,
    weight_battery NUMERIC(3,2) NOT NULL,
    weight_display NUMERIC(3,2) NOT NULL,
    weight_value NUMERIC(3,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Review Sentiments Table
CREATE TABLE IF NOT EXISTS review_sentiments (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER REFERENCES phones(id) ON DELETE CASCADE,
    source VARCHAR(50),
    sentiment_score NUMERIC(3,2),
    summary TEXT,
    pros TEXT[],
    cons TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Prices Table
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER REFERENCES phones(id) ON DELETE CASCADE,
    variant_ram_gb INTEGER,
    variant_storage_gb INTEGER,
    platform VARCHAR(50),
    price_inr INTEGER,
    url TEXT,
    is_available BOOLEAN DEFAULT true,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Triggers and Functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_phones_updated_at
    BEFORE UPDATE ON phones
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personas_updated_at
    BEFORE UPDATE ON personas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.brand, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.model, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.full_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.chipset, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.description_text, '')), 'C');
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_phones_search_vector
    BEFORE INSERT OR UPDATE ON phones
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- Indexes
CREATE INDEX idx_phones_brand ON phones(brand);
CREATE INDEX idx_phones_price ON phones(price_inr);
CREATE INDEX idx_phones_battery ON phones(battery_mah);
CREATE INDEX idx_phones_camera ON phones(main_camera_mp);
CREATE INDEX idx_phones_release_date ON phones(release_date);

CREATE INDEX idx_phones_search_vector ON phones USING GIN(search_vector);
CREATE INDEX idx_phones_embedding ON phones USING hnsw(embedding vector_cosine_ops);

CREATE INDEX idx_prices_phone_id ON prices(phone_id);
CREATE INDEX idx_reviews_phone_id ON review_sentiments(phone_id);

-- Seed Data for Personas
INSERT INTO personas (name, description, weight_performance, weight_camera, weight_battery, weight_display, weight_value) VALUES
('Gamer', 'Focuses heavily on performance, cooling, and display responsiveness.', 0.40, 0.10, 0.20, 0.20, 0.10),
('Photographer', 'Prioritizes camera quality, multiple lenses, and image processing.', 0.15, 0.50, 0.10, 0.15, 0.10),
('Power User', 'Needs all-day battery life, fast charging, and multitasking capabilities.', 0.25, 0.15, 0.35, 0.15, 0.10),
('Media Consumer', 'Loves watching videos; prioritizes large, bright, high-resolution screens and good speakers.', 0.15, 0.10, 0.25, 0.40, 0.10),
('Budget Buyer', 'Looking for the best bang for the buck. Value proposition is key.', 0.15, 0.15, 0.20, 0.10, 0.40),
('All-Rounder', 'Wants a balanced phone that does everything well without major compromises.', 0.20, 0.20, 0.20, 0.20, 0.20),
('Status Seeker', 'Premium build, brand value, and flagship features.', 0.25, 0.25, 0.10, 0.25, 0.15)
ON CONFLICT (name) DO NOTHING;
