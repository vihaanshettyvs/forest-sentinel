create extension if not exists pgcrypto;

create table sensors (
  sensor_id text primary key,
  sector text not null,
  status text default 'online',
  last_seen timestamptz default now()
);

create table events (
  event_id text primary key,
  incident_id text not null,
  sensor_id text references sensors(sensor_id),
  detected_at timestamptz not null default now(),
  event_type text not null,
  confidence numeric not null,
  sector text not null,
  source text default 'simulator'
);

create table agent_decisions (
  id uuid primary key default gen_random_uuid(),
  incident_id text not null,
  event_id text references events(event_id),
  agent_name text not null,
  result jsonb not null,
  reasoning text,
  score numeric,
  created_at timestamptz default now()
);

create table threats (
  incident_id text primary key,
  anchor_event_id text references events(event_id),
  threat_level text not null,
  risk_score numeric,
  action text not null,
  notify_ranger boolean default false,
  reason text,
  status text default 'pending_approval',
  created_at timestamptz default now()
);

create table authorizations (
  id uuid primary key default gen_random_uuid(),
  sector text not null,
  activity_type text not null,
  status text default 'active'
);

create table ranger_feedback (
  id uuid primary key default gen_random_uuid(),
  incident_id text references threats(incident_id),
  outcome text check (outcome in ('confirmed', 'false_alarm')),
  ranger_name text,
  notes text,
  created_at timestamptz default now()
);

insert into sensors (sensor_id, sector) values
  ('S01', 'B6'),
  ('S02', 'B7'),
  ('S03', 'B7'),
  ('S04', 'C7');

insert into authorizations (sector, activity_type, status)
values ('B6', 'authorized_logging', 'active');
