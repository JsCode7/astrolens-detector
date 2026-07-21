CREATE TABLE processing_jobs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lens_candidates (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES processing_jobs(id),
    candidate_name VARCHAR(255) NOT NULL,
    confidence_score FLOAT NOT NULL,
    image_url TEXT,
    einstein_radius FLOAT,
    mass_estimate FLOAT,
    attention_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
