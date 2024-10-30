create table tosend_messages (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    text text not null,
    timestamp bigint not null,
    meta jsonb not null,
    created_at timestamptz default now()
);

-- Add indexes for faster queries
create index idx_tosend_messages_user_id on tosend_messages(user_id);
create index idx_tosend_messages_timestamp on tosend_messages(timestamp);

-- Enable row level security
alter table tosend_messages enable row level security;

-- Create policy to allow read access for authenticated users
create policy "allow read access for authenticated users" on tosend_messages
    for select using (auth.uid() = user_id);
