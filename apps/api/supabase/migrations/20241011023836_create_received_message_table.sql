create table received_messages (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    text text not null,
    timestamp bigint not null,
    processed boolean not null default false,
    meta jsonb not null,
    created_at timestamptz default now()
);

-- Add indexes for faster queries
create index idx_received_messages_user_id on received_messages(user_id);
create index idx_received_messages_timestamp on received_messages(timestamp);

-- Enable row level security
-- alter table received_messages enable row level security;

-- Create policy to allow read access for authenticated users
-- create policy "allow read access for authenticated users" on received_messages
--     for select using (auth.uid() = user_id);

-- -- Create policy to allow insert access for authenticated users
-- create policy "allow insert access for authenticated users" on received_messages
--     for insert with check (auth.uid() = user_id);

-- -- Create policy to allow update access for authenticated users
-- create policy "allow update access for authenticated users" on received_messages
--     for update using (auth.uid() = user_id);

-- -- Create policy to allow delete access for authenticated users
-- create policy "allow delete access for authenticated users" on received_messages
--     for delete using (auth.uid() = user_id);
