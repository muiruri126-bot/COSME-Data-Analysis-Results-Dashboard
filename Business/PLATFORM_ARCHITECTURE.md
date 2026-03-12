# Multi-Category Service Marketplace — System Architecture Document

**Platform Name:** (TBD — referred to as "the Platform" throughout)
**Version:** 1.0
**Date:** March 2026
**Target Region:** Kenya / East Africa (Urban & Peri-urban)

---

## Assumptions

- The platform launches in Kenya, starting with Nairobi and expanding to other urban centres.
- The primary interface is an Android mobile app; a responsive web app serves as the secondary channel.
- Many service providers (house helps, fundis, gardeners) have low-end Android devices with limited data plans and basic digital literacy.
- Phone-number-based authentication (OTP via SMS or WhatsApp) is the primary login method; email is optional.
- The MVP does not include in-app payments; payment integration is deferred to Phase 2.
- Listings, jobs, and rental postings all map to a single generalized "Listing" entity with category-driven metadata.
- The development team is small (3–6 engineers) and based in East Africa.

---

## 1. High-Level Architecture

### 1.1 Component Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            CLIENTS                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│  │ Android App  │   │  Web App     │   │ Admin Panel  │                │
│  │ (Flutter)    │   │ (React/Next) │   │ (React)      │                │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                │
│         │                  │                   │                        │
└─────────┼──────────────────┼───────────────────┼────────────────────────┘
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY / LOAD BALANCER                      │
│                     (Nginx / Cloud Load Balancer)                        │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   Auth       │   │   Core API       │   │  Real-time       │
│   Service    │   │   (NestJS)       │   │  Service         │
│   (OTP/JWT)  │   │                  │   │  (WebSocket)     │
└──────┬───────┘   └──────┬───────────┘   └──────┬───────────┘
       │                  │                      │
       │     ┌────────────┼──────────────────────┘
       │     │            │
       ▼     ▼            ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA & SERVICES LAYER                           │
│                                                                          │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │ PostgreSQL   │  │  Redis   │  │  Object  │  │  Elasticsearch    │   │
│  │ (Primary DB) │  │  (Cache/ │  │  Storage │  │  (Search – Ph2)   │   │
│  │              │  │  Queue)  │  │  (S3)    │  │                   │   │
│  └──────────────┘  └──────────┘  └──────────┘  └───────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Notification │   │   Payment        │   │   Analytics      │
│ Service      │   │   Gateway        │   │   Pipeline       │
│ (SMS/Push/   │   │   (Phase 2)      │   │   (Phase 2)      │
│  WhatsApp)   │   │                  │   │                  │
└──────────────┘   └──────────────────┘   └──────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| **Android App (Flutter)** | Primary user-facing app. Registration, profile management, listing creation, search, messaging, reviews. Optimized for low-end devices and low bandwidth. |
| **Web App (Next.js / React)** | Responsive web version for desktop/laptop users — landlords, businesses, admin operations. SEO-friendly listing pages. |
| **Admin Panel (React)** | Internal dashboard for moderation, user verification, category management, metrics. |
| **API Gateway** | Single entry point. Rate limiting, request routing, SSL termination, CORS. |
| **Auth Service** | Phone OTP (Africa's Talking / Twilio), email verification, JWT issuance, role-based access control. |
| **Core API (NestJS)** | Business logic: user management, profiles, listings, search, matching, reviews, messaging orchestration. RESTful with potential GraphQL overlay for complex queries. |
| **Real-time Service** | WebSocket server for in-app chat and live notifications. |
| **PostgreSQL** | Primary relational database. All transactional data. |
| **Redis** | Session cache, rate limiting, OTP storage (with TTL), real-time pub/sub for chat. |
| **Object Storage (S3-compatible)** | Profile photos, listing images, uploaded documents (IDs, certificates). |
| **Elasticsearch** | Full-text search, geo-spatial queries, faceted filtering (Phase 2; PostgreSQL full-text + PostGIS for MVP). |
| **Notification Service** | Dispatches SMS (Africa's Talking), push notifications (Firebase Cloud Messaging), email (SendGrid/Mailgun), WhatsApp (WhatsApp Business API). |
| **Payment Gateway** | M-Pesa integration (Daraja API), card payments (Flutterwave/Paystack). Phase 2. |
| **Analytics Pipeline** | Event ingestion, dashboards, usage tracking. Phase 2. |

### 1.3 Data Flow — Key Use Cases

#### A. New User Registration & Login

```
1. User opens app → enters phone number
2. App → POST /auth/otp/request { phone }
3. Auth Service → generates 6-digit OTP → stores in Redis (TTL 5min)
   → sends OTP via Africa's Talking SMS (or WhatsApp)
4. User enters OTP → App → POST /auth/otp/verify { phone, otp }
5. Auth Service → validates OTP against Redis
   → If new user: creates User record in PostgreSQL, status = "pending_profile"
   → Issues JWT (access token + refresh token)
6. App stores JWT → redirects to profile setup
```

#### B. Creating / Updating a Profile

```
1. User fills profile form (name, bio, location, category roles, skills, photos)
2. App → POST /profiles { name, bio, roles: ["house_help", "nanny"], location, skills, ... }
3. Core API → validates input
   → Saves Profile + UserRole + UserSkill records
   → Uploads photos to Object Storage → stores URLs
   → If provider: sets profile.status = "pending_verification"
4. Response → profile created, user sees confirmation
```

#### C. Posting a Listing (Job / Rental / Service Request)

```
1. User selects category (e.g., "House Help Needed" or "2BR To Let")
2. App presents category-specific form (dynamic fields driven by category config)
3. App → POST /listings { category_id, title, description, location, attributes: {...}, budget, ... }
4. Core API → validates, saves Listing record with category-specific attributes (JSONB)
   → Geocodes address if needed (Google Maps / OpenStreetMap Nominatim)
   → Sets listing.status = "active" (or "pending_review" if moderation is enabled)
5. Notification Service → notifies matching providers in the area (optional push/SMS)
```

#### D. Searching & Matching

```
1. User enters search criteria (category, location, budget, keywords, filters)
2. App → GET /listings/search?category=house_help&lat=-1.28&lng=36.82&radius=10km&budget_max=15000&...
3. Core API → builds query:
   a. Filter by category
   b. Filter by location (PostGIS ST_DWithin for radius search)
   c. Filter by attributes (JSONB containment queries)
   d. Filter by budget range
   e. Filter by availability
   f. Sort by relevance score (weighted: distance, rating, recency, completeness)
4. Returns paginated results with summary cards
5. User taps a result → GET /listings/:id → full detail view
6. User can "Apply" / "Express Interest" / "Contact" → creates Application record + opens chat
```

#### E. Messaging Between Users

```
1. User A opens conversation with User B (from a listing context)
2. App → POST /conversations { listing_id, participant_ids: [A, B] }
   → Core API creates Conversation + first Message record
3. Real-time: both users subscribe to WebSocket channel for this conversation
4. User A sends message → WebSocket → Real-time Service → saves to DB → broadcasts to User B
5. If User B is offline → Notification Service sends push notification
6. Messages are stored in PostgreSQL; loaded via REST on app open, streamed via WebSocket live
```

#### F. Leaving a Rating / Review

```
1. After engagement, either party can leave a review
2. App → POST /reviews { listing_id, reviewee_id, rating (1-5), comment }
3. Core API → validates that reviewer was involved in the listing
   → Saves Review record
   → Updates reviewee's Profile.average_rating (running average)
4. Review appears on reviewee's public profile
```

---

## 2. Data Model & Key Entities

### 2.1 Entity Relationship Diagram (Text-Based)

```
┌──────────┐       ┌──────────────┐       ┌─────────────────┐
│   User   │──1:N──│   UserRole   │──N:1──│ ServiceCategory │
└──────┬───┘       └──────────────┘       └────────┬────────┘
       │                                           │
       │1:1                                        │
       ▼                                           │
┌──────────┐                                       │
│ Profile  │                                       │
└──────┬───┘                                       │
       │                                           │
       │1:N                                        │
       ▼                                           │
┌──────────────┐       ┌──────────────┐            │
│  UserSkill   │──N:1──│    Skill     │────N:1─────┘
└──────────────┘       └──────────────┘
       
┌──────────┐                          ┌─────────────────┐
│   User   │──1:N──┌──────────┐──N:1──│ ServiceCategory │
│          │       │ Listing  │       └─────────────────┘
│          │       └────┬─────┘
│          │            │1:N
│          │            ▼
│          │──N:N──┌─────────────┐
│(applicant)│      │ Application │
│          │       └──────┬──────┘
└──────┬───┘              │
       │                  │
       │        ┌─────────┘
       │        ▼
       │  ┌──────────┐
       ├──│  Review   │
       │  └──────────┘
       │
       │  ┌──────────────┐     ┌──────────┐
       └──│ Conversation │──1:N│ Message  │
          │ Participant  │     └──────────┘
          └──────────────┘

┌──────────┐
│ Location │ (referenced by User, Profile, Listing)
└──────────┘

┌────────────────┐
│ Verification   │ (1:N from User)
└────────────────┘

┌────────────────────┐
│ PaymentTransaction │ (Phase 2, linked to Listing + Users)
└────────────────────┘
```

### 2.2 Entity Definitions

#### User
```
User
├── id              UUID (PK)
├── phone           VARCHAR(20) UNIQUE NOT NULL
├── email           VARCHAR(255) UNIQUE NULLABLE
├── password_hash   VARCHAR(255) NULLABLE (phone OTP may be primary auth)
├── status          ENUM('active', 'suspended', 'deactivated', 'pending_profile')
├── is_verified     BOOLEAN DEFAULT FALSE
├── created_at      TIMESTAMP
├── updated_at      TIMESTAMP
└── last_login_at   TIMESTAMP
```

#### Profile
```
Profile
├── id              UUID (PK)
├── user_id         UUID (FK → User, UNIQUE)
├── first_name      VARCHAR(100)
├── last_name       VARCHAR(100)
├── display_name    VARCHAR(100)
├── bio             TEXT
├── avatar_url      VARCHAR(500)
├── date_of_birth   DATE NULLABLE
├── gender          ENUM('male', 'female', 'other', 'prefer_not_to_say') NULLABLE
├── primary_location_id  UUID (FK → Location)
├── average_rating  DECIMAL(2,1) DEFAULT 0.0
├── total_reviews   INTEGER DEFAULT 0
├── total_completed_jobs  INTEGER DEFAULT 0
├── is_available    BOOLEAN DEFAULT TRUE
├── availability_note  VARCHAR(500)  -- e.g., "Available Mon-Fri 8am-5pm"
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

#### ServiceCategory
```
ServiceCategory
├── id              UUID (PK)
├── parent_id       UUID (FK → ServiceCategory, NULLABLE)  -- hierarchical categories
├── name            VARCHAR(100)  -- e.g., "House Help", "Nanny", "Plumber", "Rental - Apartment"
├── slug            VARCHAR(100) UNIQUE  -- URL-safe identifier
├── description     TEXT
├── icon_url        VARCHAR(500)
├── listing_type    ENUM('job', 'rental', 'service', 'space')  -- drives form/display
├── attribute_schema  JSONB  -- defines dynamic fields for this category
│   -- Example for "Rental - Apartment":
│   -- { "bedrooms": {"type": "number"}, "amenities": {"type": "multi-select", 
│   --   "options": ["WiFi","Parking","Water","Security"]}, "furnished": {"type":"boolean"} }
│   -- Example for "Nanny":
│   -- { "age_group": {"type":"multi-select","options":["infant","toddler","school-age"]},
│   --   "live_in": {"type":"boolean"}, "certifications": {"type":"text"} }
├── is_active       BOOLEAN DEFAULT TRUE
├── sort_order      INTEGER DEFAULT 0
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

**Key design:** `attribute_schema` is a JSONB column that defines the dynamic form fields for each category. This lets you add new categories with unique attributes without schema migrations. The corresponding listing stores values in a `attributes` JSONB column.

#### UserRole (Many-to-Many: User ↔ ServiceCategory)
```
UserRole
├── id              UUID (PK)
├── user_id         UUID (FK → User)
├── category_id     UUID (FK → ServiceCategory)
├── role_type       ENUM('client', 'provider')
│   -- A user can be a 'provider' in "House Help" and a 'client' in "Rental"
├── created_at      TIMESTAMP
└── UNIQUE(user_id, category_id, role_type)
```

**This enables multi-role users:** A house help (provider in domestic services) can also be a tenant (client in housing).

#### Skill
```
Skill
├── id              UUID (PK)
├── category_id     UUID (FK → ServiceCategory)
├── name            VARCHAR(100)  -- e.g., "Cooking", "Infant care", "Electrical wiring"
├── slug            VARCHAR(100)
└── is_active       BOOLEAN DEFAULT TRUE
```

#### UserSkill
```
UserSkill
├── id              UUID (PK)
├── user_id         UUID (FK → User)
├── skill_id        UUID (FK → Skill)
├── years_experience  INTEGER NULLABLE
├── proficiency     ENUM('beginner', 'intermediate', 'expert') NULLABLE
└── UNIQUE(user_id, skill_id)
```

#### Location
```
Location
├── id              UUID (PK)
├── country         VARCHAR(100) DEFAULT 'Kenya'
├── county          VARCHAR(100)  -- e.g., "Nairobi", "Mombasa", "Kiambu"
├── sub_county      VARCHAR(100)  -- e.g., "Westlands", "Langata"
├── town            VARCHAR(100)
├── estate_area     VARCHAR(200)  -- e.g., "Kilimani", "Kileleshwa"
├── full_address    TEXT NULLABLE
├── latitude        DECIMAL(10,8)
├── longitude       DECIMAL(11,8)
├── geo_point       GEOGRAPHY(Point, 4326)  -- PostGIS for radius queries
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

#### Listing (Generalized: covers jobs, rentals, service requests, space listings)
```
Listing
├── id              UUID (PK)
├── user_id         UUID (FK → User)  -- the poster
├── category_id     UUID (FK → ServiceCategory)
├── title           VARCHAR(200)
├── description     TEXT
├── listing_type    ENUM('job', 'rental', 'service_request', 'space', 'offer')
│   -- 'job' = "I need a house help"
│   -- 'offer' = "I am a plumber available for hire"
│   -- 'rental' = "2BR apartment to let"
│   -- 'service_request' = "Need a tutor for math"
│   -- 'space' = "Conference room for hire"
├── status          ENUM('draft', 'pending_review', 'active', 'paused', 'filled', 'expired', 'removed')
├── location_id     UUID (FK → Location)
├── attributes      JSONB  -- category-specific data, validated against category.attribute_schema
│   -- Example for rental: {"bedrooms": 2, "amenities": ["WiFi","Parking"], "furnished": true}
│   -- Example for house help job: {"live_in": true, "duties": ["cooking","cleaning","laundry"]}
├── budget_min      DECIMAL(12,2) NULLABLE
├── budget_max      DECIMAL(12,2) NULLABLE
├── budget_period   ENUM('hourly', 'daily', 'weekly', 'monthly', 'fixed', 'negotiable') NULLABLE
├── currency        VARCHAR(3) DEFAULT 'KES'
├── availability_start  DATE NULLABLE
├── availability_end    DATE NULLABLE
├── engagement_type ENUM('full_time', 'part_time', 'one_time', 'short_term', 'long_term') NULLABLE
├── images          JSONB  -- array of image URLs: ["https://storage.../img1.jpg", ...]
├── is_featured     BOOLEAN DEFAULT FALSE  -- for future monetization
├── view_count      INTEGER DEFAULT 0
├── application_count  INTEGER DEFAULT 0
├── expires_at      TIMESTAMP NULLABLE
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP

INDEX: GIN index on attributes for JSONB queries
INDEX: GIST index on location for geo-spatial queries (via Location join)
INDEX: category_id, status, created_at for filtered listing queries
INDEX: Full-text search index on title + description (tsvector)
```

#### Application / Expression of Interest
```
Application
├── id              UUID (PK)
├── listing_id      UUID (FK → Listing)
├── applicant_id    UUID (FK → User)
├── status          ENUM('pending', 'shortlisted', 'accepted', 'rejected', 'withdrawn')
├── cover_message   TEXT NULLABLE
├── proposed_rate   DECIMAL(12,2) NULLABLE
├── rate_period     ENUM('hourly', 'daily', 'weekly', 'monthly', 'fixed') NULLABLE
├── created_at      TIMESTAMP
├── updated_at      TIMESTAMP
└── UNIQUE(listing_id, applicant_id)
```

#### Review
```
Review
├── id              UUID (PK)
├── listing_id      UUID (FK → Listing)
├── reviewer_id     UUID (FK → User)
├── reviewee_id     UUID (FK → User)
├── rating          SMALLINT CHECK (1 <= rating <= 5)
├── comment         TEXT
├── is_visible      BOOLEAN DEFAULT TRUE  -- moderation flag
├── created_at      TIMESTAMP
└── UNIQUE(listing_id, reviewer_id, reviewee_id)
```

#### Conversation & Message
```
Conversation
├── id              UUID (PK)
├── listing_id      UUID (FK → Listing, NULLABLE)  -- context of the conversation
├── created_at      TIMESTAMP
├── updated_at      TIMESTAMP  -- last message timestamp
└── status          ENUM('active', 'archived', 'blocked')

ConversationParticipant
├── id              UUID (PK)
├── conversation_id UUID (FK → Conversation)
├── user_id         UUID (FK → User)
├── joined_at       TIMESTAMP
├── last_read_at    TIMESTAMP NULLABLE
├── is_muted        BOOLEAN DEFAULT FALSE
└── UNIQUE(conversation_id, user_id)

Message
├── id              UUID (PK)
├── conversation_id UUID (FK → Conversation)
├── sender_id       UUID (FK → User)
├── content         TEXT
├── message_type    ENUM('text', 'image', 'system')
├── attachment_url  VARCHAR(500) NULLABLE
├── is_read         BOOLEAN DEFAULT FALSE
├── created_at      TIMESTAMP
└── INDEX: conversation_id, created_at DESC
```

#### Verification
```
Verification
├── id              UUID (PK)
├── user_id         UUID (FK → User)
├── type            ENUM('phone', 'email', 'national_id', 'certificate', 'reference', 'background_check')
├── status          ENUM('pending', 'verified', 'rejected', 'expired')
├── document_url    VARCHAR(500) NULLABLE  -- encrypted storage reference
├── verified_by     UUID (FK → User, NULLABLE)  -- admin who verified
├── notes           TEXT NULLABLE
├── verified_at     TIMESTAMP NULLABLE
├── expires_at      TIMESTAMP NULLABLE
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

#### PaymentTransaction (Phase 2)
```
PaymentTransaction
├── id              UUID (PK)
├── listing_id      UUID (FK → Listing)
├── payer_id        UUID (FK → User)
├── payee_id        UUID (FK → User)
├── amount          DECIMAL(12,2)
├── currency        VARCHAR(3) DEFAULT 'KES'
├── payment_method  ENUM('mpesa', 'card', 'bank_transfer', 'wallet')
├── status          ENUM('pending', 'completed', 'failed', 'refunded', 'escrow')
├── external_ref    VARCHAR(200)  -- M-Pesa transaction ID, etc.
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

#### Notification Log
```
Notification
├── id              UUID (PK)
├── user_id         UUID (FK → User)
├── type            ENUM('sms', 'push', 'email', 'whatsapp', 'in_app')
├── title           VARCHAR(200)
├── body            TEXT
├── data            JSONB  -- deep link info, listing_id, etc.
├── is_read         BOOLEAN DEFAULT FALSE
├── sent_at         TIMESTAMP
└── created_at      TIMESTAMP
```

#### Report / Flag
```
Report
├── id              UUID (PK)
├── reporter_id     UUID (FK → User)
├── reported_user_id UUID (FK → User, NULLABLE)
├── reported_listing_id UUID (FK → Listing, NULLABLE)
├── reason          ENUM('harassment', 'fraud', 'spam', 'inappropriate_content', 'fake_profile', 'other')
├── description     TEXT
├── status          ENUM('pending', 'investigating', 'resolved', 'dismissed')
├── resolved_by     UUID (FK → User, NULLABLE)  -- admin
├── resolution_notes TEXT NULLABLE
├── created_at      TIMESTAMP
└── updated_at      TIMESTAMP
```

### 2.3 Key Design Decisions

**Multi-role support:** The `UserRole` junction table allows one user to hold multiple roles across categories. A single `User` record can be:
- A "provider" in House Help category
- A "provider" in Nanny category  
- A "client" in Rental category (as a tenant)

**Unified Listing model with JSONB attributes:** Instead of separate tables for jobs, rentals, and services, a single `Listing` table uses:
- `category_id` to determine the type
- `attributes` (JSONB) for category-specific fields
- `attribute_schema` on `ServiceCategory` to validate and render dynamic forms

This means adding a new category (e.g., "Pet Care") requires only:
1. Insert a new `ServiceCategory` row with its `attribute_schema`
2. Add relevant `Skill` rows
3. No database migrations needed

**Fields crucial for:**

| Purpose | Fields |
|---|---|
| **Matching** | `Listing.category_id`, `Location.geo_point` (radius), `Listing.attributes` (skills/amenities), `Listing.budget_min/max`, `Listing.engagement_type`, `Profile.is_available`, `UserSkill.*`, `Profile.average_rating` |
| **Safety** | `User.is_verified`, `Verification.type/status`, `User.phone` (verified), `Profile.avatar_url` (real photo), `Report.*` |
| **Analytics** | `Listing.view_count`, `Listing.application_count`, `UserRole.category_id` (users per category), `Application.status` (conversion), `User.last_login_at` (activity/churn), `Review.rating` (quality) |

---

## 3. Tech Stack Recommendations

### 3.1 Recommended Stack

| Layer | Technology | Justification |
|---|---|---|
| **Mobile App** | **Flutter (Dart)** | Single codebase for Android (priority) and iOS (future). Strong performance on low-end devices. Growing developer community in East Africa. Excellent offline-first support. |
| **Web App** | **Next.js (React)** | SEO-friendly server-side rendering for public listing pages. React ecosystem is the most popular in East Africa. Shared component library with admin panel. |
| **Admin Panel** | **React (Ant Design / MUI)** | Rapid development of data-heavy dashboards. Same React skills as web app team. |
| **Backend API** | **NestJS (Node.js / TypeScript)** | Structured, modular framework. TypeScript catches errors early. Excellent for REST + WebSocket. Large ecosystem. Easy to hire Node.js developers in Kenya. Built-in support for guards, interceptors, pipes (useful for RBAC, validation). |
| **ORM** | **Prisma** | Type-safe database access. Auto-generated migrations. Works well with PostgreSQL and NestJS. |
| **Database** | **PostgreSQL 16** | Robust relational DB. JSONB for flexible attributes. PostGIS extension for geo-spatial queries. Full-text search (tsvector) for MVP search. Battle-tested at scale. |
| **Cache / Session** | **Redis** | OTP storage with TTL, session caching, rate limiting, pub/sub for real-time chat, API response caching. |
| **Object Storage** | **AWS S3 / Cloudflare R2 / DigitalOcean Spaces** | Cheap, reliable storage for images and documents. S3-compatible API. CDN integration for fast image delivery. |
| **Search (Phase 2)** | **Elasticsearch / OpenSearch** | When PostgreSQL full-text search reaches its limits: fuzzy matching, relevance scoring, faceted search, autocomplete. |
| **Authentication** | **Custom JWT + OTP** | Phone-based OTP via Africa's Talking (best SMS coverage in Kenya). JWT access + refresh tokens. Optional social login (Google) in Phase 2. |
| **SMS / OTP** | **Africa's Talking** | Best coverage and pricing for Kenya/East Africa. SMS, USSD, and WhatsApp channel support. Local company, KES billing. |
| **Push Notifications** | **Firebase Cloud Messaging (FCM)** | Free, reliable push for Android. Works with Flutter via `firebase_messaging` package. |
| **Email** | **SendGrid (free tier) / Mailgun** | Transactional emails for receipts, verification links. |
| **WhatsApp** | **WhatsApp Business API (via Africa's Talking or 360dialog)** | For OTP delivery and notifications to users who prefer WhatsApp. Phase 2 for richer interactions. |
| **Real-time** | **Socket.IO (on NestJS)** | WebSocket server for live chat. Fallback to long-polling for poor connections. Redis adapter for horizontal scaling. |
| **Deployment** | **DigitalOcean / AWS** | See section below. |
| **CI/CD** | **GitHub Actions** | Free for public repos, affordable for private. Automates testing, building, deploying. |
| **Monitoring** | **Sentry (errors) + Grafana Cloud free tier (metrics)** | Error tracking with stack traces. Basic metrics dashboard. |

### 3.2 Deployment Architecture

**Recommended: DigitalOcean** (cost-effective for MVP, has Nairobi-adjacent region in progress; use Amsterdam/London region with CDN for now)

| Service | DigitalOcean Product | Est. Monthly Cost |
|---|---|---|
| API Server | App Platform or Droplet (2 vCPU, 4GB) | $24–48 |
| PostgreSQL | Managed Database (1GB RAM) | $15 |
| Redis | Managed Redis (1GB) | $15 |
| Object Storage | Spaces (250GB) | $5 |
| CDN | Spaces CDN (included) | $0 |
| Domain + SSL | Let's Encrypt (free) | $0 |
| **Total MVP** | | **~$60–85/month** |

**Alternative: AWS** (more services, more complex, can start with free tier)
- EC2 or ECS Fargate for API
- RDS PostgreSQL
- ElastiCache Redis
- S3 + CloudFront
- Higher ceiling for scaling but more expensive and complex for a small team

### 3.3 Justification Summary

- **Cost-effectiveness:** DigitalOcean is 40-60% cheaper than AWS for small workloads. Flutter saves building separate Android and iOS apps.
- **Developer availability in East Africa:** JavaScript/TypeScript (NestJS), React, Flutter, and PostgreSQL all have strong developer communities in Nairobi and the broader region. NestJS in particular has gained traction in Kenyan tech companies.
- **Scalability path:** PostgreSQL handles millions of records. NestJS is modular — services can be extracted to microservices later. Redis + Socket.IO scales horizontally. Elasticsearch can be added when search complexity demands it. Flutter supports iOS expansion.

---

## 4. Matching & Recommendation Logic

### 4.1 Common Matching Framework

All categories use the same scoring engine with weighted factors. The weights differ by category.

```
match_score = Σ (weight_i × factor_score_i) for all applicable factors
```

**Universal factors:**

| Factor | Scoring Logic | Weight Range |
|---|---|---|
| **Location proximity** | Score = max(0, 1 - distance/max_radius). If within area boundary, score = 1.0. | 0.20 – 0.35 |
| **Category match** | Binary: listing category matches search category. Required filter (not weighted). | Filter (required) |
| **Skills / Attributes** | Jaccard similarity: `|intersection| / |union|` of required vs. offered skills/attributes. | 0.15 – 0.25 |
| **Budget alignment** | Score = 1.0 if budget ranges overlap; decreasing if partially outside range. | 0.10 – 0.20 |
| **Availability** | Date/time overlap between seeker's need and provider's availability. | 0.10 – 0.20 |
| **Rating** | Normalized: `average_rating / 5.0`. New users get a neutral score (0.6). | 0.05 – 0.15 |
| **Profile completeness** | Percentage of profile fields filled + photo + verification. | 0.05 – 0.10 |
| **Recency** | Decay function: `1 / (1 + days_since_posted * 0.05)`. Newer listings rank higher. | 0.05 – 0.10 |
| **Engagement history** | Response rate, acceptance rate from past applications. | 0.05 (Phase 2) |

### 4.2 Category-Specific Weight Profiles

```yaml
domestic_services:  # house help, nanny, caregiver, cleaner
  location: 0.30     # Must be nearby or willing to commute/live-in
  skills: 0.25       # Specific duties matter (cooking, childcare, elderly care)
  availability: 0.15 # Full-time vs part-time is crucial
  budget: 0.10
  rating: 0.10
  completeness: 0.05
  recency: 0.05

housing_rental:     # tenant ↔ landlord
  location: 0.35     # Location is the #1 factor in housing
  attributes: 0.25   # Bedrooms, amenities, furnished, etc.
  budget: 0.20       # Rent range is a hard constraint
  recency: 0.10      # Recent listings most relevant
  rating: 0.05       # Landlord rating matters but less than attributes
  completeness: 0.05

skilled_trades:     # fundi, plumber, electrician
  location: 0.25     # Willing to travel within area
  skills: 0.25       # Specific trade skills
  availability: 0.15 # "Need a plumber tomorrow" — urgency matters
  rating: 0.15       # Trust is critical for fundis
  budget: 0.10
  recency: 0.05
  completeness: 0.05

professional_services:  # tutor, freelancer, tech support
  skills: 0.30       # Exact skill match is most important
  rating: 0.20       # Portfolio/reputation matters
  budget: 0.15
  location: 0.10     # Can be remote
  availability: 0.10
  recency: 0.10
  completeness: 0.05
```

### 4.3 Implementation (MVP)

For MVP, the matching runs as a **SQL query with scoring**:

```sql
SELECT l.id, l.title, 
  -- Location score
  (1.0 - LEAST(ST_Distance(loc.geo_point, ST_MakePoint(:lng, :lat)::geography) / :max_radius, 1.0)) 
    * :w_location AS location_score,
  -- Budget score
  CASE WHEN l.budget_max >= :budget_min AND l.budget_min <= :budget_max THEN 1.0
       ELSE 0.0 END * :w_budget AS budget_score,
  -- Rating score  
  (COALESCE(p.average_rating, 3.0) / 5.0) * :w_rating AS rating_score,
  -- Recency score
  (1.0 / (1.0 + EXTRACT(DAY FROM NOW() - l.created_at) * 0.05)) * :w_recency AS recency_score
  -- (Skills scored in application layer for JSONB flexibility)
FROM listings l
JOIN locations loc ON l.location_id = loc.id
JOIN profiles p ON l.user_id = p.user_id
WHERE l.category_id = :category_id
  AND l.status = 'active'
  AND ST_DWithin(loc.geo_point, ST_MakePoint(:lng, :lat)::geography, :max_radius_meters)
ORDER BY (location_score + budget_score + rating_score + recency_score) DESC
LIMIT 20 OFFSET :offset;
```

Skills/attributes matching is done in the application layer (NestJS) because JSONB containment queries are better handled with flexible logic:

```typescript
function scoreSkills(requiredSkills: string[], providerSkills: string[]): number {
  const intersection = requiredSkills.filter(s => providerSkills.includes(s));
  const union = new Set([...requiredSkills, ...providerSkills]);
  return union.size > 0 ? intersection.length / union.size : 0;
}
```

### 4.4 Evolution Path to ML

**Phase 2 — Behavioral signals:**
- Track which listings users click, save, apply to, and ignore
- Use click-through rate (CTR) and application rate to re-weight factors
- Collaborative filtering: "Users who hired this house help also hired..."

**Phase 3 — ML ranking:**
- Train a learning-to-rank model (LightGBM / XGBoost) on historical match data
- Features: all current factors + behavioral signals + user demographics
- Deploy as a microservice that re-ranks the top N candidates from SQL
- A/B test ML ranking vs. rule-based ranking

This progression avoids overcomplicating the MVP while building the data foundation for ML.

---

## 5. Security, Trust & Safety

### 5.1 User Verification

| Level | What | How | When |
|---|---|---|---|
| **Level 0** | Phone number | OTP via SMS at registration | Required for all users |
| **Level 1** | Email | Verification link sent to email | Optional but encouraged |
| **Level 2** | National ID / Passport | Upload photo of ID → manual review by admin | Required for providers before first engagement |
| **Level 3** | Selfie verification | Upload selfie → compare with ID photo (manual or automated) | Encouraged for higher trust scores |
| **Level 4** | References | Contact details of past employers/clients → admin may call/verify | Optional, shown as badge |
| **Level 5** | Background check | Partner with a background check service (e.g., background check providers in Kenya) | Phase 2, opt-in for premium providers |

Verified users get visible badges on their profile and rank higher in search results.

### 5.2 Data Protection & Access Control

**Role-Based Access Control (RBAC):**

```
Roles: user, provider, admin, super_admin

user:
  - Read own profile, listings, applications, conversations
  - Create/edit own listings, applications
  - View public profiles of other users (limited fields)

provider (extends user):
  - Same as user + additional provider-specific endpoints

admin:
  - Read all profiles, listings, applications, reports
  - Approve/reject verifications
  - Moderate content (hide listings, suspend users)
  - View analytics dashboard

super_admin:
  - All admin permissions
  - Manage admin accounts
  - System configuration
  - Category management
```

**Data visibility rules:**
- Phone numbers are **never** shown publicly. Users communicate via in-app messaging.
- Full name is shown only after both parties express interest (mutual reveal).
- ID documents are accessible **only** to admins with verification privileges and are stored encrypted.
- Location is shown at the estate/area level publicly; exact address is shared only after matching.
- Messages are stored encrypted at rest and visible only to conversation participants.
- Profile view: public fields (display name, bio, avatar, skills, rating, verification badges) vs. private fields (phone, email, date of birth, ID documents, exact address).

### 5.3 Secure Storage

- ID documents and sensitive files: Stored in a **separate, access-restricted S3 bucket** with server-side encryption (AES-256).
- Access via pre-signed URLs with short TTL (5 minutes), generated only for authorized admin users.
- Database: Encryption at rest enabled on the managed database.
- Passwords (if any): Hashed with **bcrypt** (cost factor 12).
- JWT tokens: Short-lived access tokens (15 minutes), long-lived refresh tokens (30 days) stored securely on-device.

### 5.4 Content Moderation

- **Automated:** Basic profanity filter on listing titles, descriptions, and messages. Flag listings with suspicious patterns (e.g., price = 0, excessive contact info in description).
- **User-driven:** Report button on every profile, listing, and message. Reports create `Report` records for admin review.
- **Admin review queue:** Dashboard showing flagged content sorted by severity. Admin can: warn user, edit content, hide listing, suspend user.
- **Review moderation:** Reviews are visible immediately but can be flagged. Admin can hide inappropriate reviews.

### 5.5 Reporting & Blocking

- Any user can **report** another user or listing with a reason (harassment, fraud, spam, fake profile, other).
- Any user can **block** another user → hides their content, prevents messaging, prevents applications on each other's listings.
- Repeated reports against a user trigger automatic temporary suspension pending admin review.
- **Emergency:** Provide clear link/number for reporting safety concerns to local authorities (e.g., gender-based violence hotline).

### 5.6 Compliance

- **Kenya Data Protection Act (2019):** 
  - Users must consent to data collection (clear privacy policy, consent checkbox during registration).
  - Users can request data export and deletion ("right to be forgotten").
  - Data processing must be lawful, fair, and transparent.
  - Appointment of a Data Protection Officer if/when required by scale.
  - Register with the Office of the Data Protection Commissioner (ODPC) before processing personal data.
- **Communications Authority of Kenya:** Compliance with any regulations on SMS/communication services.
- **Terms of Service:** Clear terms that platform is a marketplace, not an employer. Users are responsible for their own employment terms.

---

## 6. MVP vs. Future Phases

### 6.1 Phase 1 — MVP (Months 1–4)

**Goal:** Launch with core categories, validate product-market fit in Nairobi.

**Core features:**
- User registration & login (phone + OTP)
- Profile creation (client and/or provider, multi-role)
- **3 starting categories:** House Helps, Nannies/Babysitters, Fundis (plumbers, electricians, carpenters)
- **1 housing category:** Rental apartments/houses (tenant ↔ landlord)
- Posting listings/jobs/requests with category-specific dynamic forms
- Basic search & filtering (category, location area, budget range, keywords)
- Geo-based search using PostGIS (radius or area-based)
- Provider profiles with skills, experience, availability
- Simple matching: filtered search + sorted by relevance score (rule-based)
- In-app messaging (text only)
- Ratings & reviews after engagement
- Basic phone verification (OTP)
- Push notifications (new messages, new applications, new listings in your area)
- Basic admin panel: user list, listing list, verification queue, reports queue

**Architectural components:**
- Flutter Android app
- Next.js web app (responsive, listing pages)
- NestJS API (monolithic, modular)
- PostgreSQL + PostGIS
- Redis (OTP, cache, sessions)
- S3-compatible storage (images)
- Socket.IO for chat
- Africa's Talking for SMS
- Firebase for push notifications
- React admin panel

**Data model:** Full schema as described in Section 2 — designed for extensibility from day one.

---

### 6.2 Phase 2 — Growth (Months 5–9)

**Goal:** Expand categories, add monetization, improve search and trust.

**Core features:**
- **New categories:** Caregivers, Cleaners, Gardeners, Drivers, Tutors, Short-term rentals, Shared housing
- In-app payments via M-Pesa (Daraja API) and card (Flutterwave)
  - Payment for featured listings
  - Optional secure deposit escrow for rentals and high-value services
  - Subscription plans for providers (visibility boost)
- Advanced search: Elasticsearch integration for fuzzy search, autocomplete, relevance ranking
- ID verification (upload + manual admin review)
- Selfie verification
- Enhanced notifications: WhatsApp messages for critical alerts
- Saved searches and alerts ("Notify me when new 2BR apartments are listed in Kilimani")
- Favorite/shortlist providers and listings
- Image messaging in chat
- Listing analytics for posters (views, applications, conversion)
- Admin analytics dashboard (users per category, active listings, match rates)
- Email notifications (weekly digest of new matches)

**Architectural additions:**
- Elasticsearch cluster (managed, e.g., Elastic Cloud or AWS OpenSearch)
- Payment microservice (separate from core API for isolation and PCI considerations)
- WhatsApp Business API integration
- Analytics event pipeline (simple: API logs → PostgreSQL views; advanced: event queue → data warehouse)
- Background job queue (Bull/BullMQ on Redis) for: email digests, listing expiration, notification batching

**Data model changes:**
- Add `PaymentTransaction` table
- Add `Subscription` table (user subscriptions to plans)
- Add `SavedSearch` table (user_id, search criteria JSONB, notification preferences)
- Add `Favorite` table (user_id, listing_id or user_id)
- No changes to core Listing/User/Profile schema — new categories are just new `ServiceCategory` rows

**Migration considerations to anticipate early:**
- Design the `Listing.attributes` JSONB schema validation in application code from MVP, so Phase 2 categories slot in cleanly.
- Build the notification service as an abstraction layer from MVP (interface with pluggable channels), so adding WhatsApp is just a new channel implementation.
- Structure the NestJS app as modules from day one (auth, users, listings, search, chat, notifications, reviews) so extracting to microservices later is straightforward.

---

### 6.3 Phase 3 — Scale & Optimize (Months 10–18)

**Core features:**
- **New categories:** Freelancers, Tech Support, Office/co-working space, Event venues
- ML-based recommendations (collaborative filtering, learning-to-rank)
- Background checks integration (partnership with local provider)
- Multi-language support (English + Swahili; framework: i18n in Flutter + Next.js)
- Offline mode for Android app (cached listings, queue actions for sync)
- iOS app launch (Flutter — same codebase)
- Expansion to other Kenyan cities (Mombasa, Kisumu, Nakuru)
- Provider badges and levels (based on completed jobs, ratings, verification)
- Dispute resolution workflow (integrated in admin panel)
- API for third-party integrations (property management systems, HR systems)
- Rate limiting and anti-abuse improvements

**Architectural additions:**
- ML recommendation microservice (Python, FastAPI, LightGBM)
- Data warehouse (e.g., BigQuery or PostgreSQL analytics replica)
- CDN optimization for multiple regions
- Horizontal scaling: multiple API instances behind load balancer
- Database read replicas for search-heavy queries
- Monitoring upgrade: Datadog or Grafana Cloud paid tier

**Data model changes:**
- Add `UserBadge` table
- Add `DisputeCase` table  
- Add `AuditLog` table (for compliance and admin action tracking)
- Potential partitioning of `Listing` and `Message` tables by date for performance

---

### 6.4 Phase Summary Table

| Feature | MVP | Phase 2 | Phase 3 |
|---|---|---|---|
| Categories | 4 (house help, nanny, fundi, rental) | +7 more | +4 more, open-ended |
| Registration | Phone OTP | + email verification | + social login |
| Search | PostgreSQL + PostGIS | + Elasticsearch | + ML ranking |
| Payments | None | M-Pesa + card | + escrow, subscriptions |
| Verification | Phone only | + ID upload, selfie | + background checks |
| Messaging | Text chat | + images | + voice notes, templates |
| Notifications | SMS + push | + WhatsApp + email | + smart batching |
| Languages | English | English | + Swahili |
| Platforms | Android + web | Android + web | + iOS |
| Admin | Basic CRUD | + analytics, payments | + disputes, ML config |
| Architecture | Monolith (modular) | + Elasticsearch, payment service | + ML service, data warehouse |

---

## 7. Admin & Operations Tools

### 7.1 Admin Dashboard — Module Breakdown

The admin panel is a React web application accessible only to authenticated admin users. It communicates with the same NestJS API via admin-scoped endpoints protected by RBAC guards.

#### 7.1.1 User Management
- **User list** with search, filter by role/category/status/verification level
- **User detail view:** profile info, roles, listings, applications, reviews, verification status, reports
- **Actions:** suspend user, deactivate user, reset verification status, impersonate user (view-only, for debugging)
- **Bulk actions:** send notification to a segment of users, export user list

#### 7.1.2 Verification & Approval Workflow
```
New ID Upload → Pending Review Queue → Admin Reviews Document → Approve/Reject
                                         ↓
                                    Admin clicks "Verify"
                                         ↓
                              Verification record updated
                              User gets "Verified" badge
                              Notification sent to user
```
- Queue sorted by: oldest first, provider type priority (e.g., domestic workers prioritized)
- Admin can add notes, request re-upload, or reject with reason
- Dashboard shows: pending count, average review time, daily throughput

#### 7.1.3 Category Management
- **CRUD for ServiceCategory:** add, edit, reorder, deactivate categories and subcategories
- **Attribute schema editor:** JSON-based form builder for defining category-specific listing fields
  - Define field name, type (text, number, select, multi-select, boolean, date), options, required/optional
- **Skill management:** add/edit/deactivate skills per category
- **Category analytics:** number of users, listings, applications, avg time to match, per category

#### 7.1.4 Listing Management
- **Listing queue** (if moderation is enabled for certain categories): approve, reject, request edits
- **All listings view:** search, filter by category/status/location/date
- **Actions:** deactivate listing, edit listing, feature/un-feature listing, extend listing
- **Duplicate detection:** flag listings with very similar titles/descriptions from different accounts

#### 7.1.5 Reports & Complaints
- **Report queue:** sorted by severity (multiple reports = higher priority)
- **Report detail:** reporter info, reported user/listing, reason, screenshots
- **Actions:** dismiss report, warn user, hide content, suspend user, ban user
- **Dispute resolution (Phase 3):** mediation workflow between two users, with timeline and resolution tracking

#### 7.1.6 Metrics & Analytics Dashboard

**Key metrics per category:**

| Metric | Description |
|---|---|
| Total users | Registered users by role (client/provider) per category |
| Active users | Users who logged in within last 30 days |
| Active listings | Listings with status = 'active' |
| New listings / day | Trend over time |
| Applications / listing | Average, helps measure engagement |
| Match rate | % of listings that reach 'filled' status |
| Avg time to fill | Days from listing creation to 'filled' |
| Review completion | % of matches that result in a review |
| Average rating | Per category, per provider |
| User retention | 30/60/90-day retention by cohort |
| Churn indicators | Users who haven't returned in 30+ days |

**Dashboard views:**
- **Overview:** total users, total listings, total matches, trend charts
- **Per-category drilldown:** all metrics above, filtered by category
- **Geographic view:** activity heatmap by county/area
- **Revenue (Phase 2+):** payments processed, subscription revenue, featured listing revenue

#### 7.1.7 Content Moderation
- **Profile review:** flagged profiles (auto or user-reported), review photos, bio text
- **Message review:** only when a conversation is reported — admin can view reported messages (not all messages)
- **Review moderation:** flagged reviews, admin can hide or delete with reason
- **Automated flags:** profiles without photos after 7 days, listings with contact info in description (bypassing messaging)

#### 7.1.8 System Configuration
- **Feature flags:** enable/disable features per category or globally (e.g., "payments enabled", "ID verification required")
- **Notification templates:** edit SMS, email, push notification templates
- **Rate limit configuration:** adjust API rate limits
- **Listing rules:** set expiry durations per category, max listings per user, moderation requirements

### 7.2 Operations Tooling Summary

| Tool | Purpose | Phase |
|---|---|---|
| Admin Panel (React) | All admin operations above | MVP |
| Sentry | Error tracking, crash reports | MVP |
| Grafana / CloudWatch | Server metrics, API latency, DB performance | MVP |
| Database admin (pgAdmin or DBeaver) | Direct DB access for engineers (not admins) | MVP |
| Bull Board | Monitor background job queues | Phase 2 |
| Elasticsearch Kibana | Search analytics, query debugging | Phase 2 |
| Analytics dashboard (Metabase or custom) | Business metrics, SQL-based reports | Phase 2 |
| Log aggregation (CloudWatch Logs or Loki) | Centralized logging | Phase 2 |

---

## 8. Example User Journeys

### 8.1 House Help Looking for Work

```
1. Mary downloads the app on her Android phone
2. She registers with her phone number → receives OTP → verifies
3. She creates her profile:
   - Name: Mary W.
   - Roles: Provider → House Help, Provider → Nanny
   - Skills: Cooking, Cleaning, Laundry, Childcare (toddler)
   - Experience: 3 years
   - Location: Kilimani, Nairobi
   - Availability: Full-time, live-out
   - Expected salary: KES 12,000–15,000/month
   - Uploads profile photo
4. She uploads her National ID for verification → status: pending
5. Admin reviews and approves her ID → Mary gets "Verified" badge
6. She browses listings: "House Help Needed" in her area
7. She filters: location = Kilimani/Kileleshwa, salary ≥ 12,000, live-out
8. She sees 5 matching jobs → taps one → reads details
9. She clicks "Express Interest" → writes a short cover message
10. The employer (Mrs. Kamau) receives a notification
11. Mrs. Kamau views Mary's profile, sees her ratings (4.5★ from 2 previous jobs)
12. Mrs. Kamau starts a chat with Mary → they discuss details
13. They agree on terms → Mrs. Kamau marks the listing as "Filled"
14. After 2 weeks, both leave reviews for each other
```

### 8.2 Landlord Posting a Unit and Finding a Tenant

```
1. James (landlord) registers on the web app with his phone number
2. He creates a profile: Role = Client → Rental
3. He clicks "Post Listing" → selects category: "Rental - Apartment"
4. Dynamic form appears with rental-specific fields:
   - Title: "Spacious 2BR Apartment in South B"
   - Location: South B, Nairobi
   - Rent: KES 25,000/month
   - Attributes: 2 bedrooms, 1 bathroom, unfurnished
   - Amenities: Water, Parking, Security, Near shopping
   - Available from: April 1, 2026
   - Uploads 6 photos of the apartment
5. Listing goes live (or pending moderation)
6. Tenants searching for "2BR apartments in South B under 30K" see his listing
7. 4 tenants express interest
8. James reviews their profiles → shortlists 2
9. He chats with both, arranges viewing via messaging
10. He accepts one tenant → marks listing as "Filled"
11. Both parties leave reviews
```

### 8.3 Parent Searching for a Nanny

```
1. Susan (parent) opens the app → she already has an account
2. She posts a listing: "Looking for experienced nanny in Lavington"
   - Category: Nanny
   - Attributes: age group = toddler (2 years old), live-in, experience with infants preferred
   - Budget: KES 15,000–20,000/month
   - Start date: ASAP
3. The system also shows her "Recommended Providers" — nannies in her area 
   with matching skills and good ratings
4. She browses recommended nannies → finds 3 with "Verified" badges
5. She views their profiles: skills, experience, reviews from other parents
6. She sends a message to 2 of them
7. One nanny responds quickly → they arrange an interview
8. Susan hires the nanny → marks her listing as "Filled"
9. After 1 month, Susan leaves a review: "Excellent with my toddler, very reliable. 5★"
```

### 8.4 User Searching for a Fundi (Plumber)

```
1. John's kitchen sink is leaking → he opens the app
2. He goes to "Find a Fundi" → selects "Plumber"
3. He sees a quick-post form:
   - What do you need? "Kitchen sink leak repair"
   - When? "Tomorrow morning"
   - Location: Westlands, Nairobi
   - Budget: KES 1,000–3,000 (one-time job)
4. He also browses available plumbers in Westlands
5. The search shows plumbers sorted by: proximity, rating, response rate
6. He sees Peter (Plumber, 4.8★, 47 completed jobs, "Verified")
7. He taps "Contact" → sends a message describing the problem with a photo
8. Peter responds within 30 minutes: "I can come tomorrow at 9am. KES 2,000."
9. John accepts → Peter comes and fixes the sink
10. John leaves a review: "Fast, professional, fair price. 5★"
11. Peter's completed job count increments, his profile ranking improves
```

---

## 9. API Structure Overview (NestJS Modules)

```
src/
├── app.module.ts
├── common/                    # Shared utilities, guards, filters, interceptors
│   ├── guards/
│   │   ├── jwt-auth.guard.ts
│   │   └── roles.guard.ts
│   ├── filters/
│   │   └── http-exception.filter.ts
│   ├── interceptors/
│   │   └── transform.interceptor.ts
│   ├── decorators/
│   │   ├── roles.decorator.ts
│   │   └── current-user.decorator.ts
│   └── pipes/
│       └── validation.pipe.ts
├── auth/                      # Authentication module
│   ├── auth.module.ts
│   ├── auth.controller.ts     # POST /auth/otp/request, /auth/otp/verify, /auth/refresh
│   ├── auth.service.ts
│   └── strategies/
│       └── jwt.strategy.ts
├── users/                     # User management
│   ├── users.module.ts
│   ├── users.controller.ts    # GET/PUT /users/me, GET /users/:id (public profile)
│   └── users.service.ts
├── profiles/                  # Profile management
│   ├── profiles.module.ts
│   ├── profiles.controller.ts # POST/PUT /profiles, GET /profiles/:id
│   └── profiles.service.ts
├── categories/                # Service categories & skills
│   ├── categories.module.ts
│   ├── categories.controller.ts # GET /categories, GET /categories/:id/skills
│   └── categories.service.ts
├── listings/                  # Listings (jobs, rentals, services)
│   ├── listings.module.ts
│   ├── listings.controller.ts # CRUD /listings, GET /listings/search
│   ├── listings.service.ts
│   └── listing-search.service.ts  # Search & matching logic
├── applications/              # Applications / expressions of interest
│   ├── applications.module.ts
│   ├── applications.controller.ts
│   └── applications.service.ts
├── reviews/                   # Ratings & reviews
│   ├── reviews.module.ts
│   ├── reviews.controller.ts  # POST /reviews, GET /reviews?user_id=...
│   └── reviews.service.ts
├── chat/                      # Messaging (REST + WebSocket)
│   ├── chat.module.ts
│   ├── chat.controller.ts     # GET /conversations, GET /conversations/:id/messages
│   ├── chat.gateway.ts        # WebSocket gateway
│   └── chat.service.ts
├── notifications/             # Notification dispatch
│   ├── notifications.module.ts
│   ├── notifications.service.ts
│   └── channels/
│       ├── sms.channel.ts     # Africa's Talking
│       ├── push.channel.ts    # Firebase
│       ├── email.channel.ts   # SendGrid
│       └── whatsapp.channel.ts # Phase 2
├── verification/              # User verification & documents
│   ├── verification.module.ts
│   ├── verification.controller.ts
│   └── verification.service.ts
├── reports/                   # User reports & moderation
│   ├── reports.module.ts
│   ├── reports.controller.ts
│   └── reports.service.ts
├── admin/                     # Admin-specific endpoints
│   ├── admin.module.ts
│   ├── admin-users.controller.ts
│   ├── admin-listings.controller.ts
│   ├── admin-verification.controller.ts
│   ├── admin-reports.controller.ts
│   ├── admin-categories.controller.ts
│   └── admin-analytics.controller.ts
├── upload/                    # File upload handling
│   ├── upload.module.ts
│   ├── upload.controller.ts   # POST /upload/image, /upload/document
│   └── upload.service.ts      # S3 integration
└── config/                    # Configuration
    ├── database.config.ts
    ├── redis.config.ts
    ├── jwt.config.ts
    └── app.config.ts
```

---

## 10. Key Technical Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Monolith vs. microservices | **Modular monolith** (MVP), extract services later | Small team, fast iteration, avoid distributed system complexity early |
| REST vs. GraphQL | **REST** with optional GraphQL layer (Phase 2) | Simpler, cacheable, easier to debug. GraphQL useful later for complex client queries |
| Relational vs. NoSQL | **PostgreSQL** (relational + JSONB hybrid) | ACID compliance for transactions, JSONB for flexible category attributes, PostGIS for geo, full-text search built-in |
| Single Listing table vs. per-category tables | **Single table + JSONB attributes** | Extensible without migrations, unified search, simpler API. Category-specific validation in application layer |
| Phone vs. email as primary auth | **Phone (OTP)** | Higher penetration in Kenya, works for users without email, aligns with M-Pesa ecosystem |
| Flutter vs. React Native vs. native | **Flutter** | Better performance on low-end devices, growing East African developer pool, single codebase for Android + future iOS |
| Search engine for MVP | **PostgreSQL full-text + PostGIS** | Avoids additional infrastructure. Sufficient for initial scale. Migrate to Elasticsearch when needed |
| Real-time messaging | **Socket.IO on NestJS** | Integrated with main backend, WebSocket with long-polling fallback, Redis adapter for scaling |
| Cloud provider | **DigitalOcean** (MVP) | Cost-effective, simpler UX for small team. Migrate to AWS if needed for advanced services |

---

This architecture provides a solid, extensible foundation that can launch quickly with a small team, serve users with varying digital literacy and device capabilities, and scale gracefully as the platform grows across categories and geographies.
