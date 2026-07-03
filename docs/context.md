# Context: Mutual Fund FAQ Assistant (Groww RAG Chatbot)

---

## 1. Project Background

This project builds a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. It is powered by a **Retrieval-Augmented Generation (RAG)** architecture that fetches verified information exclusively from official public financial sources.

The assistant is designed to serve as a compliant, transparent, and legally safe information tool — one that delivers **objective financial facts**, not opinions or investment advice. This makes it suitable for deployment in customer-facing scenarios within a regulated fintech environment.

---

## 2. Problem Being Solved

Retail investors and support teams frequently encounter repetitive, factual queries about mutual fund schemes:

- What is the expense ratio of a scheme?
- What is the exit load for early redemption?
- What is the minimum SIP amount?
- What is the lock-in period for ELSS funds?
- How do I download my capital gains statement?

Currently, users must navigate multiple AMC websites, AMFI portals, and SEBI documents to find this information. The assistant centralizes this knowledge retrieval, providing **concise, source-backed answers in real time**.

---

## 3. Objective

Design and implement a lightweight RAG-based assistant that:

- Answers **factual queries** about mutual fund schemes
- Retrieves information from a **curated corpus of official documents**
- Provides **concise responses (≤ 3 sentences)** with exactly **one citation link** per answer
- Includes a **"Last updated from sources: \<date\>"** footer with every response
- **Refuses** any advisory, comparative, or speculative queries politely

---

## 4. Target Users

| User Type | Use Case |
|---|---|
| **Retail Investors** | Comparing scheme parameters (expense ratio, exit load, lock-in) without seeking advice |
| **Customer Support Teams** | Quickly resolving repetitive factual queries from investors |
| **Content Teams** | Verifying factual accuracy of published mutual fund content |

---

## 5. System Architecture (RAG Approach)

```
┌─────────────────────────────────────────────────────┐
│                   User Interface (UI)               │
│  - Welcome message                                  │
│  - 3 example questions                              │
│  - Disclaimer: "Facts-only. No investment advice."  │
└──────────────────────┬──────────────────────────────┘
                       │ User Query
                       ▼
┌─────────────────────────────────────────────────────┐
│               Query Classification Layer            │
│  - Factual query → proceed to retrieval             │
│  - Advisory/comparative query → trigger refusal     │
└──────────────────────┬──────────────────────────────┘
                       │ Factual Query
                       ▼
┌─────────────────────────────────────────────────────┐
│              Retrieval Engine (RAG Core)            │
│  - Embed query using sentence transformer           │
│  - Search vector store (FAISS / Chroma)             │
│  - Retrieve top-k relevant document chunks          │
└──────────────────────┬──────────────────────────────┘
                       │ Retrieved Chunks + Source URL
                       ▼
┌─────────────────────────────────────────────────────┐
│           Response Generation (LLM Layer)           │
│  - Generate ≤ 3 sentence factual answer             │
│  - Attach exactly 1 citation link                   │
│  - Append "Last updated from sources: <date>"       │
└──────────────────────┬──────────────────────────────┘
                       │ Final Response
                       ▼
                   User Interface
```

---

## 6. Data Corpus & Sources

### 6.1 Source Selection Criteria

- **Only official public sources** are permitted
- Third-party blogs, aggregator sites, or forums are **strictly prohibited**
- All Groww scheme links used are sourced from: https://groww.in/mutual-funds/amc

### 6.2 Approved Source Categories

| Source Type | Description | Examples |
|---|---|---|
| **Groww Scheme Pages** | Live scheme detail pages (NAV, expense ratio, exit load, riskometer) | groww.in/mutual-funds/... |
| **Scheme Factsheets** | Monthly fund performance & portfolio details | AMC website PDFs |
| **KIM** | Key Information Memorandum — summarizes scheme terms | AMC website |
| **SID** | Scheme Information Document — full legal scheme detail | AMC website / SEBI |
| **AMC FAQ / Help Pages** | Common investor questions answered by the fund house | AMC support pages |
| **AMFI Guidance Pages** | Industry-level regulatory guidance and definitions | amfiindia.com |
| **SEBI Regulatory Pages** | Regulator's circulars and investor education resources | sebi.gov.in |
| **Statement & Tax Guides** | Instructions for downloading CAMS/KARVY/AMC statements | AMC / CAMS / KFintech |

### 6.3 Selected AMCs & Corpus URLs

The RAG chatbot corpus covers **2 AMCs** with **20 scheme URLs** sourced from Groww.

---

#### 🏦 Union Mutual Fund

| # | Fund Name | Groww URL |
|---|---|---|
| 1 | Union Small Cap Fund | https://groww.in/mutual-funds/union-small-and-midcap-fund-direct-growth |
| 2 | Union Liquid Fund | https://groww.in/mutual-funds/union-liquid-fund-direct-growth |
| 3 | Union Midcap Fund | https://groww.in/mutual-funds/union-midcap-fund-direct-growth |
| 4 | Union Flexi Cap Fund | https://groww.in/mutual-funds/union-equity-fund-direct-growth |
| 5 | Union Active Momentum Fund | https://groww.in/mutual-funds/union-active-momentum-fund-direct-growth |
| 6 | Union Children's Fund | https://groww.in/mutual-funds/union-childrens-fund-direct-growth |
| 7 | Union Multi Asset Allocation Fund | https://groww.in/mutual-funds/union-multi-asset-allocation-fund-direct-growth |
| 8 | Union Multicap Fund | https://groww.in/mutual-funds/union-multicap-fund-direct-growth |
| 9 | Union Gold ETF FoF | https://groww.in/mutual-funds/union-gold-etf-fof-direct-growth |
| 10 | Union Innovation & Opportunities Fund | https://groww.in/mutual-funds/union-innovation-opportunities-fund-direct-growth |

---

#### 🏦 HDFC Mutual Fund

| # | Fund Name | Groww URL |
|---|---|---|
| 1 | HDFC Silver ETF FoF | https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth |
| 2 | HDFC Mid Cap Fund | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |
| 3 | HDFC Flexi Cap Fund | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 4 | HDFC Defence Fund | https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth |
| 5 | HDFC Small Cap Fund | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 6 | HDFC Gold ETF Fund of Fund | https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth |
| 7 | HDFC Short Term Debt Fund | https://groww.in/mutual-funds/hdfc-short-term-opportunities-fund-direct-growth |
| 8 | HDFC Balanced Advantage Fund | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |
| 9 | HDFC NIFTY 50 Index Fund | https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth |
| 10 | HDFC Pharma And Healthcare Fund | https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth |

---

## 7. Functional Requirements

### 7.1 Answerable Query Types (Facts-Only)

The assistant must accurately respond to queries such as:

| Query Type | Example |
|---|---|
| Expense Ratio | "What is the expense ratio of [Fund Name]?" |
| Exit Load | "What is the exit load for [Fund Name]?" |
| Minimum SIP Amount | "What is the minimum SIP amount for [Fund Name]?" |
| ELSS Lock-in Period | "What is the lock-in period for ELSS funds?" |
| Riskometer Classification | "What is the risk level of [Fund Name]?" |
| Benchmark Index | "What index does [Fund Name] track?" |
| Document Download | "How do I download my capital gains statement?" |

### 7.2 Response Format

Every factual response must follow this structure:

```
[Answer in ≤ 3 sentences]

Source: [Single citation URL]

Last updated from sources: [DD-MMM-YYYY]
```

### 7.3 Refusal Handling

The assistant must **politely refuse** all non-factual, advisory, or comparative queries:

| Refused Query Type | Example |
|---|---|
| Investment advice | "Should I invest in this fund?" |
| Fund comparison | "Which fund is better — A or B?" |
| Return predictions | "Will this fund give good returns?" |
| Risk opinions | "Is this fund safe for me?" |

**Refusal Response Template:**

```
I'm designed to answer facts-only questions about mutual fund schemes.
I cannot provide investment advice or recommendations.

For guidance, please visit: [AMFI / SEBI educational resource link]

Facts-only. No investment advice.
```

---

## 8. User Interface Requirements

The UI must be **minimal and clean**, containing:

- **Welcome message** introducing the assistant
- **3 example questions** to guide users
- **Persistent disclaimer banner**: `"Facts-only. No investment advice."`
- **Chat interface** for query input and response display
- **Source citation** visible in every response

---

## 9. Constraints

### 9.1 Data & Source Constraints

- ✅ Use only official sources: AMC, AMFI, SEBI
- ❌ Do NOT use third-party blogs, news aggregators, or comparison portals

### 9.2 Privacy & Security Constraints

The assistant must **never collect, store, or process** any of the following user data:

| Sensitive Data Type | Examples |
|---|---|
| Government IDs | PAN number, Aadhaar number |
| Financial Account Info | Bank account numbers, folio numbers |
| Authentication Data | OTPs, passwords |
| Personal Contact Info | Email addresses, phone numbers |

### 9.3 Content Constraints

- ❌ No investment advice or recommendations
- ❌ No performance comparisons or return calculations
- ✅ For performance-related queries, provide a **link to the official factsheet only**
- ✅ All responses must be **short, factual, and verifiable**
- ✅ Every answer must include a **source link** and **last updated date**

---

## 10. Expected Deliverables

| Deliverable | Description |
|---|---|
| **RAG Application** | Working chatbot with retrieval + generation pipeline |
| **Indexed Corpus** | Vector store of 15–25 official document chunks |
| **README** | Setup instructions, AMC/scheme selection, architecture overview, known limitations |
| **Disclaimer Snippet** | Embedded in UI: `"Facts-only. No investment advice."` |
| **Refusal Logic** | Classifier or prompt-based system to detect and refuse advisory queries |

---

## 11. Success Criteria

| Criterion | Description |
|---|---|
| **Retrieval Accuracy** | Correct factual information retrieved from the official corpus |
| **Response Compliance** | Facts-only; ≤ 3 sentences; exactly 1 citation per response |
| **Refusal Accuracy** | Advisory queries are consistently and politely refused |
| **Privacy Safety** | No PII collected or processed at any point |
| **UI Quality** | Clean, minimal, disclaimer-visible, and user-friendly |
| **Source Traceability** | Every answer traceable to an official document |

---

## 12. Out of Scope

The following are **explicitly excluded** from this project:

- Live market data or real-time NAV lookup
- Portfolio tracking or personalized account management
- Return calculators or SIP projectors
- Investment advisory or financial planning
- Integration with brokerage or trading systems
- Schemes outside of the 20 selected funds (Union MF × 10, HDFC MF × 10)
- Any AMC other than Union Mutual Fund and HDFC Mutual Fund

---

## 13. Key Terminology

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — combines document retrieval with LLM generation |
| **AMC** | Asset Management Company — the fund house managing the scheme |
| **AMFI** | Association of Mutual Funds in India — the industry self-regulatory body |
| **SEBI** | Securities and Exchange Board of India — the market regulator |
| **SID** | Scheme Information Document — the legal prospectus for a mutual fund |
| **KIM** | Key Information Memorandum — a summarized version of the SID |
| **ELSS** | Equity Linked Savings Scheme — tax-saving mutual fund with a 3-year lock-in |
| **NAV** | Net Asset Value — the per-unit price of a mutual fund scheme |
| **SIP** | Systematic Investment Plan — regular (e.g., monthly) investment in a fund |
| **Exit Load** | Fee charged when redeeming units before a specified period |
| **Riskometer** | SEBI-mandated risk classification label (Low / Moderate / High / Very High) |
| **Expense Ratio** | Annual fee charged by the fund house as a % of AUM |

---

## 14. Compliance Notes

> **Legal Disclaimer**: This assistant is built strictly for informational and educational purposes. It does not constitute financial advice, investment recommendations, or a solicitation to buy/sell any financial instrument. Users should consult a SEBI-registered investment advisor (RIA) before making investment decisions.

- All responses are sourced from publicly available official documents.
- The system does not generate opinions, predictions, or recommendations.
- The system must comply with SEBI's investor communication guidelines and AMFI's code of conduct for mutual fund information dissemination.

---

*Generated from: problemstatement.txt*
*Last updated: 2026-06-30 — Corpus updated with 20 Groww fund URLs (Union MF × 10, HDFC MF × 10)*
