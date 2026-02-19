# Fanvue Copilot — Pre-Written Council Question Sessions

Use these as starter questions to exercise the council against real Fanvue engineering problems. Each session targets a different problem domain and complexity level.

---

## Session 1: Payment Recovery Pipeline
**Domain**: Payments & Billing | **Severity**: P1-URGENT

> Our Stripe subscription dunning flow is losing 12% of churned subscribers who had valid cards that temporarily declined. We retry 3 times over 7 days, then cancel. Competitors recover 60% of these.
>
> Design a smart dunning pipeline that:
> 1. Classifies decline reasons (insufficient funds vs. card expired vs. fraud)
> 2. Picks optimal retry timing per decline type
> 3. Sends targeted win-back emails/push notifications
> 4. Integrates with Stripe's Smart Retries but adds our own logic layer
> 5. Tracks recovery rate per cohort in our analytics warehouse
>
> Constraints: Must work with Stripe Connect (creators are connected accounts), must not violate card network retry rules, budget < $200/mo in additional infra.

---

## Session 2: Content Moderation at Scale
**Domain**: Content Delivery + Identity & Compliance | **Severity**: P2-NORMAL

> Fanvue processes ~50,000 media uploads per day (images + video). Currently, moderation is a bottleneck:
> - AI auto-mod (AWS Rekognition) catches ~70% of violations
> - Human reviewers handle the rest (8-person team, 4-hour SLA)
> - False positive rate is 15%, causing creator frustration
> - We need to add CSAM detection (PhotoDNA hash matching) as a legal requirement
>
> Design a moderation pipeline that:
> 1. Reduces human review queue by 50%
> 2. Brings false positive rate below 5%
> 3. Maintains <2 hour SLA for content going live
> 4. Integrates PhotoDNA/NCMEC reporting as a hard gate
> 5. Gives creators transparency into why content was flagged
>
> Consider: multi-model ensemble (Rekognition + custom model), confidence thresholds, appeal workflow, audit trail for legal.

---

## Session 3: Real-Time Creator Analytics
**Domain**: Data & Analytics + Creator Tools | **Severity**: P2-NORMAL

> Creators want real-time analytics (subscriber count, revenue, top content, engagement rate) but our current pipeline has 6-hour lag because it runs through nightly dbt jobs in Snowflake.
>
> Design a real-time analytics system that:
> 1. Shows subscriber count and revenue within 30 seconds of an event
> 2. Updates engagement metrics (likes, comments, tips) in near-real-time
> 3. Maintains historical accuracy (eventual consistency OK for real-time, but daily rollups must be exact)
> 4. Doesn't break our existing Snowflake/dbt warehouse
> 5. Serves the creator dashboard API at <100ms p99
>
> Budget: <$1,500/mo additional infrastructure. Current stack: PostgreSQL (primary), Snowflake (warehouse), Redis (cache), Next.js frontend.
>
> Key question: Do we stream from Postgres CDC, or does the application emit events? Or both?

---

## Session 4: Migration from Monolith to Service Mesh
**Domain**: Infrastructure & DevOps + API & Integration | **Severity**: P2-NORMAL

> Fanvue's Node.js monolith is hitting scaling walls:
> - 4-minute deploy times (full restart)
> - Payment code changes risk breaking content delivery
> - Single Postgres connection pool contention at peak hours
> - Team of 18 engineers stepping on each other's PRs
>
> Plan a phased migration that:
> 1. Extracts Payments as the first service (highest risk, highest value)
> 2. Defines the service boundary and API contract
> 3. Handles the distributed transaction problem (subscription created → access granted → content unlocked)
> 4. Maintains zero-downtime during migration
> 5. Doesn't require rewriting the monolith — strangler fig pattern
>
> Include: service mesh choice (Istio vs. Linkerd vs. none), database per service strategy, shared auth/session handling, observability across services, and a realistic timeline for an 18-person team.

---

## Session 5: Geo-Expansion Compliance Architecture
**Domain**: Identity & Compliance + Payments & Billing + Infrastructure | **Severity**: P1-URGENT

> Fanvue is expanding from UK/US to EU (GDPR), Australia (eSafety), and Brazil (LGPD). Each jurisdiction has different rules for:
> - Age verification (UK: mandatory, AU: upcoming, EU: varies by country)
> - Data residency (EU: must store PII in EU, Brazil: similar requirements)
> - Content rules (AU eSafety: specific prohibited categories, Germany: NetzDG)
> - Tax (EU VAT MOSS, Brazil: IOF + ISS, AU: GST)
> - Payout (different banking rails, FX conversion, tax withholding)
>
> Design the compliance architecture that:
> 1. Detects user jurisdiction reliably (IP + billing address + ID document)
> 2. Enforces per-jurisdiction content rules without duplicating business logic
> 3. Routes PII storage to correct region (multi-region Postgres or separate clusters?)
> 4. Handles tax calculation and reporting per jurisdiction
> 5. Manages creator payouts with correct withholding per country
>
> Constraint: Must be extensible — we'll add 5 more countries in the next 12 months. Architecture should handle N jurisdictions without N codepaths.
