# Database Schema

## 1. DB tanlovi

PostgreSQL asosiy source of truth. Redis queue/cache/lock uchun ishlatiladi.

## 2. Asosiy jadvallar

### users

```sql
id UUID PRIMARY KEY
telegram_id BIGINT UNIQUE NOT NULL
username TEXT
role TEXT NOT NULL
is_active BOOLEAN DEFAULT true
created_at TIMESTAMPTZ DEFAULT now()
```

### assets

```sql
id UUID PRIMARY KEY
owner_id UUID REFERENCES users(id)
asset_type TEXT NOT NULL
value TEXT NOT NULL
normalized_value TEXT NOT NULL
label TEXT
status TEXT DEFAULT 'active'
created_at TIMESTAMPTZ DEFAULT now()
UNIQUE(owner_id, value)
UNIQUE(asset_type, normalized_value)
```

### asset_scopes

```sql
id UUID PRIMARY KEY
asset_id UUID REFERENCES assets(id)
scope_type TEXT
domain_pattern TEXT
cidr TEXT
proof_ref TEXT
created_at TIMESTAMPTZ DEFAULT now()
```

### jobs

```sql
id UUID PRIMARY KEY
job_type TEXT NOT NULL
asset_id UUID REFERENCES assets(id)
status TEXT NOT NULL
priority TEXT DEFAULT 'normal'
requested_by UUID REFERENCES users(id)
created_at TIMESTAMPTZ DEFAULT now()
updated_at TIMESTAMPTZ DEFAULT now()
```

### findings

```sql
id UUID PRIMARY KEY
job_id UUID REFERENCES jobs(id)
severity TEXT NOT NULL
category TEXT NOT NULL
title TEXT NOT NULL
detail_jsonb JSONB
fingerprint TEXT
created_at TIMESTAMPTZ DEFAULT now()
```

### incidents

```sql
id UUID PRIMARY KEY
asset_id UUID REFERENCES assets(id)
severity TEXT NOT NULL
state TEXT NOT NULL
summary TEXT
source_ip INET
timeline_jsonb JSONB
opened_at TIMESTAMPTZ DEFAULT now()
closed_at TIMESTAMPTZ
```

### honeypot_events

```sql
id UUID PRIMARY KEY
endpoint TEXT
source_ip INET
method TEXT
headers_jsonb JSONB
payload_preview TEXT
user_agent TEXT
asn TEXT
country TEXT
risk_score INT
created_at TIMESTAMPTZ DEFAULT now()
```

### canary_tokens

```sql
id UUID PRIMARY KEY
token_hash TEXT UNIQUE NOT NULL
token_type TEXT NOT NULL
target_asset_id UUID REFERENCES assets(id)
state TEXT DEFAULT 'active'
expires_at TIMESTAMPTZ
created_at TIMESTAMPTZ DEFAULT now()
```

### evidence

```sql
id UUID PRIMARY KEY
incident_id UUID REFERENCES incidents(id)
kind TEXT NOT NULL
sha256 TEXT
storage_uri TEXT
meta_jsonb JSONB
captured_at TIMESTAMPTZ DEFAULT now()
```

### blocked_ips

```sql
id UUID PRIMARY KEY
ip INET NOT NULL
reason TEXT
source TEXT
expires_at TIMESTAMPTZ
created_at TIMESTAMPTZ DEFAULT now()
```

### audit_log

```sql
id UUID PRIMARY KEY
actor_type TEXT
actor_id TEXT
action TEXT NOT NULL
object_type TEXT
object_id TEXT
result TEXT
meta_jsonb JSONB
prev_hash TEXT
entry_hash TEXT
created_at TIMESTAMPTZ DEFAULT now()
```

### monitoring_states

```sql
id UUID PRIMARY KEY
asset_id UUID REFERENCES assets(id) UNIQUE NOT NULL
enabled BOOLEAN DEFAULT false
last_check_at TIMESTAMPTZ
last_status TEXT
last_detail JSONB
created_at TIMESTAMPTZ DEFAULT now()
```

### architecture_advice

```sql
id UUID PRIMARY KEY
module_name TEXT
window_start TIMESTAMPTZ
window_end TIMESTAMPTZ
metrics_jsonb JSONB
recommendation TEXT
created_at TIMESTAMPTZ DEFAULT now()
```

## 3. Indekslar

```sql
CREATE INDEX idx_findings_detail ON findings USING GIN(detail_jsonb);
CREATE INDEX idx_honeypot_headers ON honeypot_events USING GIN(headers_jsonb);
CREATE INDEX idx_incidents_timeline ON incidents USING GIN(timeline_jsonb);
CREATE INDEX idx_jobs_status_created ON jobs(status, created_at);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
CREATE UNIQUE INDEX ix_assets_type_normalized_value ON assets(asset_type, normalized_value);
CREATE UNIQUE INDEX ix_monitoring_states_asset_id ON monitoring_states(asset_id);
```

## 4. Retention

| Jadval | Retention |
|---|---|
| audit_log | 180 kun hot, keyin archive |
| honeypot_events | 90 kun hot |
| incidents | 1 yil+ |
| findings | 1 yil+ |
| quota_counters | 30 kun |
