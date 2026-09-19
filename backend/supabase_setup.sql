-- Enable the uuid-ossp extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create datasets table
CREATE TABLE public.datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    storage_path TEXT,
    file_size BIGINT,
    row_count INTEGER,
    column_count INTEGER,
    timestamp_column TEXT,
    consumption_column TEXT,
    quality_score NUMERIC,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create water_consumption table
CREATE TABLE public.water_consumption (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE,
    consumption NUMERIC,
    temperature NUMERIC,
    rain NUMERIC,
    sun NUMERIC,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Add indexes for better query performance
CREATE INDEX idx_water_consumption_dataset_id ON public.water_consumption(dataset_id);
CREATE INDEX idx_water_consumption_timestamp ON public.water_consumption(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.water_consumption ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage their own datasets" ON public.datasets FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users manage their own consumption records" ON public.water_consumption FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Create storage bucket for AquaSense data
INSERT INTO storage.buckets (id, name, public) 
VALUES ('aquasense-data', 'aquasense-data', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Users manage their own dataset files" ON storage.objects FOR ALL
USING (bucket_id = 'aquasense-data' AND (storage.foldername(name))[1] = auth.uid()::text)
WITH CHECK (bucket_id = 'aquasense-data' AND (storage.foldername(name))[1] = auth.uid()::text);
