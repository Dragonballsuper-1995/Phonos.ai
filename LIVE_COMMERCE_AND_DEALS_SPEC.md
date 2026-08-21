# 🛍️ Live E-Commerce, Deals & Price Tracking Architecture Specification
> **Document Status:** On Hold / Deferred Architecture Reference  
> **Target Scope:** Real-time Indian E-Commerce Integration (Amazon PA-API, Flipkart Affiliate API, Bank Discount Parsers, Price Drop History)  
> **Project:** Phonos.ai

---

## 1. Overview & Business Value

When activated in future milestones, this subsystem empowers Phonos.ai to dynamically verify live real-time stock availability, live flash-sale prices, coupon codes, and bank card offers across major Indian e-commerce platforms (Amazon India, Flipkart, Croma, Reliance Digital).

---

## 2. API Architecture & Data Providers

### A. Amazon Product Advertising API (PA-API v5)
- **Endpoint:** `https://webservices.amazon.in/paapi5/getitems`
- **Key Data Fields:**
  - `Offers.Listings.Price.Amount`: Current selling price.
  - `Offers.Listings.SavingBasis.Amount`: Original MRP.
  - `Offers.Listings.Promotions`: Lightning deals, coupon codes (e.g. ₹1,000 off coupon).
  - `Offers.Listings.DeliveryInfo.IsPrimeEligible`: Instant/Prime availability.
- **Affiliate Tagging:** `AssociateTag` parameter embedded on all outgoing purchase URLs.

### B. Flipkart Affiliate API
- **Endpoint:** `https://affiliate-api.flipkart.net/affiliate/1.0/product.json`
- **Key Data Fields:**
  - `flipkartSellingPrice`: Live discounted price.
  - `flipkartSpecialPrice`: Sale/Big Billion Days price.
  - `inStock`: Live inventory status.
  - `bankOffers`: Active instant discounts (e.g. "10% Instant Discount on HDFC Bank Credit Cards").

---

## 3. Database Schema (When Ready to Implement)

```sql
-- Live E-commerce Price & Offer Snapshots
CREATE TABLE IF NOT EXISTS phone_live_deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_id INTEGER REFERENCES phones(id),
    store_name TEXT NOT NULL,          -- 'Amazon India' | 'Flipkart' | 'Croma'
    listing_title TEXT,
    mrp REAL,
    selling_price REAL NOT NULL,
    effective_price REAL,              -- Price after coupon/bank discount
    bank_offer_text TEXT,              -- '₹3,000 Instant Discount on ICICI Cards'
    coupon_discount REAL DEFAULT 0.0,
    affiliate_url TEXT NOT NULL,
    in_stock BOOLEAN DEFAULT 1,
    last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 30-Day & 90-Day Historical Price Tracking
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_id INTEGER REFERENCES phones(id),
    store_name TEXT NOT NULL,
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Price Drop Alert Subscriptions
CREATE TABLE IF NOT EXISTS price_drop_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_id INTEGER REFERENCES phones(id),
    user_email TEXT NOT NULL,
    target_price REAL NOT NULL,
    current_price_at_creation REAL NOT NULL,
    is_triggered BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Frontend UI Components (Design Mockup)

1. **Deal Badge on Result Cards (`PhoneRow.tsx`):**
   - Highlighting live active deal: `🔥 ₹3,000 Bank Discount Available on Amazon`.
2. **Effective Price Breakdown:**
   - Base Price: `₹44,999`
   - Coupon: `- ₹1,000`
   - Bank Offer: `- ₹3,000 (HDFC / ICICI)`
   - **Net Effective Price: ₹40,999**
3. **Price History Sparkline (`PhoneReport.tsx`):**
   - 30-day interactive SVG mini-chart showing all-time low vs current price.
4. **"Set Price Drop Alert" Modal:**
   - Simple email + target budget trigger.

---

## 5. Background Poller Worker (Architecture)
- **Schedule:** Run every 6 hours via Celery/Redis or Cloudflare Workers.
- **Throttling:** Max 1 request/sec per API key to stay within Amazon/Flipkart rate limits.
- **Alert Dispatcher:** Send transactional email via Resend / AWS SES when `selling_price <= target_price`.
