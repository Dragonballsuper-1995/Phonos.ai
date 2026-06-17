# **Technical Feasibility Study and Architecture Blueprint: AI-Powered Smartphone Recommender System**

The transition from rudimentary, keyword-based product search to intent-driven, generative retrieval systems represents the most significant paradigm shift in modern consumer technology. Traditional e-commerce search engines force users to translate their complex, multifaceted desires into rigid filter parameters. The proposed architecture—an AI-Powered Smartphone Recommender System—aims to invert this paradigm. By constructing a highly sophisticated, production-ready infrastructure, the system will seamlessly parse nuanced user intents, retrieve multimodal data from disparate sources, and generate grounded, highly specific product recommendations.  
This technical feasibility study provides an exhaustive, 360-degree blueprint for constructing this system. It encompasses a multi-tiered semantic routing engine, a robust hybrid retrieval-augmented generation (RAG) architecture, and a resilient data ingestion pipeline capable of unifying structured technical specifications, dynamic pricing data, and unstructured consumer sentiment. By migrating away from naive vector similarity and implementing state-of-the-art orchestration techniques—such as tri-hybrid search via PostgreSQL, Reciprocal Rank Fusion, and dynamic inference routing—this architecture actively resolves the most pressing bottlenecks in contemporary enterprise artificial intelligence deployments.

## **System Architecture and Technology Stack**

The foundation of a production-grade generative application relies on strictly decoupling the retrieval, generation, and orchestration layers. A naive RAG approach—embedding documents into a standalone vector database and querying them directly via cosine similarity—fails catastrophically in environments requiring exact specification matching and structured filtering1. The recommended technology stack leverages a consolidated, SQL-first hybrid architecture to ensure low latency, high precision, and deterministic data grounding.

### **The Backend and Orchestration Layer**

The backend architecture must support highly concurrent, asynchronous operations to manage parallel database queries, web scraping triggers, and downstream Large Language Model (LLM) invocations. Python, coupled with the FastAPI framework, is the optimal choice due to its native asynchronous support (asyncio) and seamless integration with the broader machine learning ecosystem.  
Rather than relying on bloated orchestration frameworks that obscure the underlying mechanics, the system should utilise native API clients managed through a custom semantic router2. The routing layer acts as a system brain, deploying a lightweight classification model to evaluate incoming queries based on their computational requirements, intent, and structural demands before dispatching them to the appropriate inference pathway4. This design pattern maps directly to enterprise-grade inference optimisation frameworks, enabling targeted compute allocation2.

### **The Database and Hybrid Retrieval Engine**

The most critical architectural decision involves the selection of the data storage and retrieval layer. While specialised standalone vector databases have gained popularity, they inherently struggle with structured meaning, strict filtering, and exact-match keyword searches1. Queries such as "best camera phone under £800" require deterministic numeric filtering and exact keyword matching, not merely fuzzy semantic proximity1. While enterprise options like Amazon OpenSearch Service excel at high-QPS hybrid retrieval, they introduce significant operational overhead and high baseline costs7.  
The optimal solution for this project is PostgreSQL, augmented with the pgvector extension for semantic search and the native tsvector data type for full-text lexical search8. This configuration enables a "tri-hybrid" retrieval pipeline within a single transactional database, drastically simplifying the infrastructure footprint while maximising retrieval precision8:

| Retrieval Modality | Underlying Mechanism | Primary Application within the System |
| :---- | :---- | :---- |
| **Structured SQL** | B-Tree Indexes, Boolean Logic | Deterministic constraints (e.g., price \<= 800, battery\_capacity \>= 5000\)1. |
| **Sparse Lexical** | tsvector, Inverted Indexes (GIN) | Exact term matching, catching model numbers and specific hardware identifiers (e.g., "A15 Bionic")8. |
| **Dense Semantic** | pgvector, HNSW Indexing | Capturing subjective user intent, sentiment, and conceptual similarity8. |

For the dense retrieval component, pgvector should be configured with Hierarchical Navigable Small World (HNSW) indexing rather than IVFFlat. IVFFlat divides the vector space into clusters using k-means and requires upfront tuning of lists and probe counts, which can compromise recall8. Conversely, HNSW builds a multi-layered graph that delivers superior recall at query time without necessitating complex tuning of the nprobe parameter, making it the definitive choice for production RAG systems where retrieval quality supersedes index build times8.

### **The Large Language Model Ecosystem**

A unified application does not necessitate a unified model. The application requires a Mixture-of-Models approach, orchestrated dynamically by the semantic router2.

* **Classification Layer:** A lightweight, standalone classifier (e.g., ModernBERT) integrated directly into the router to determine the query pathway in milliseconds5.  
* **Fast Path (Tier 1):** For simple, conversational, or highly deterministic queries, a highly quantised open-weight model (e.g., Llama-3-8B) served via an inference engine like vLLM provides optimal cost-to-performance ratios, lowering energy costs and ensuring sub-second latency4.  
* **Reasoning Path (Tiers 2 & 3):** For complex, multi-step queries requiring deep Chain-of-Thought reasoning or strict adherence to JSON schemas for function calling, frontier models such as GPT-4o or Claude 3.5 Sonnet are deployed4.

### **The Frontend Presentation Layer**

To effectively demonstrate technical proficiency to recruiters, the frontend must mirror enterprise-grade consumer applications. Next.js is recommended for its robust server-side rendering capabilities and seamless API route integration. The user interface must seamlessly handle asynchronous streaming responses from the backend, rendering Markdown and structured specification tables dynamically as the LLM generates tokens. The presentation of tables over un-ordered lists is vital for technical data, as structured tabular formats signal to both users and search engines that specific attributes are being directly compared12.

## **The Data Ingestion Pipeline**

The intelligence and authority of the recommender system are entirely contingent on the quality, freshness, and structural integrity of its underlying knowledge base. The pipeline must asynchronously ingest highly structured technical data from GSMArena, scrape dynamic pricing from official brand websites, and seamlessly blend this with unstructured, real-world sentiment extracted from YouTube tech reviews.

### **Scraping Structured Specifications: GSMArena**

GSMArena serves as the industry standard for raw hardware benchmarking and specifications. However, the platform operates with strict anti-bot protections, most notably Cloudflare, which actively blocks traditional headless browsers and naive scraping libraries14.

#### **Bypassing Protections and Infrastructure**

To bypass these restrictions, the ingestion pipeline must utilise a headless browser framework such as Playwright, integrated with stealth plugins like undetected-chromedriver15. Crucially, running this pipeline on commercial cloud infrastructure (AWS EC2, Google Cloud, DigitalOcean) will immediately trigger IP bans, as anti-bot systems maintain extensive blacklists of data centre IP ranges16. The solution necessitates the integration of rotating residential proxies, such as WebShare, which route requests through authentic consumer Internet Service Provider (ISP) addresses globally, effectively masking the automated nature of the traffic16.

#### **HTML Parsing and Extraction Logic**

The GSMArena Document Object Model is heavily nested and requires precise orchestration using BeautifulSoup18. The scraper must traverse the taxonomy from vendor lists to individual product pages.

* Device lists are encapsulated within \<div\> elements possessing the class makers, structured as unordered lists (\<ul\>) containing anchor tags (\<a\>) pointing to individual devices18.  
* The technical specification tables utilise complex hierarchical structures. The pipeline must target \<table\> elements and iterate through rows marked with the tr-hover and tr-toggle classes21.  
* A specific technical challenge arises because sub-rows frequently lack distinct hierarchical markers. For example, a row might contain a header like "Network", followed by sub-rows for "4G bands" and "5G bands" which do not explicitly belong to a parent container21. The parsing script must maintain a state machine that tracks the last observed major header and appends subsequent tr-toggle data points to the appropriate parent node in the resulting JSON payload21.

### **Scraping Dynamic Pricing: Official Brand Websites**

While GSMArena provides historical MSRPs, real-world recommendations require current pricing. Ingesting this data from official brand websites (e.g., Apple, Samsung, Google) introduces a different set of technical hurdles. Official storefronts are heavily reliant on dynamic JavaScript rendering, meaning simple HTTP GET requests via libraries like requests will return empty DOMs.  
The Playwright instances must be configured to await specific network idle states or the rendering of specific pricing DOM elements. Because brand websites frequently alter their class structures, the scraper should utilise robust XPath selectors targeting text patterns or specific data attributes (e.g., data-test-id="product-price") rather than fragile CSS classes. This data must be updated frequently via asynchronous cron jobs to maintain accuracy.

### **Scraping Unstructured Sentiment: YouTube Transcripts**

Integrating real-world reviews ensures the recommender system evaluates subjective metrics—such as camera shutter lag, battery degradation over time, and software bloatware—which are wholly absent from raw specification sheets.

#### **Rate Limits and Infrastructure Bottlenecks**

Extracting transcripts programmatically reveals severe limitations in official channels. The official YouTube Data API v3 enforces draconian quota limits, charging 200 units per caption download against a daily cap of 10,000 units, restricting ingestion to a mere 50 transcripts per day22. Furthermore, the official API prohibits downloading auto-generated captions or captions for videos not explicitly owned by the authenticated user22.  
To achieve scale, the architecture must abandon the official API in favour of third-party extraction tools or libraries like youtube-transcript-api17. Similar to the GSMArena pipeline, deploying open-source scraping libraries directly on cloud servers frequently results in RequestBlocked or IpBlocked exceptions16. YouTube has aggressively blacklisted IPs belonging to AWS, GCP, and Azure to prevent large-scale automated scraping16. Utilising managed proxy services or residential IP networks is mandatory to ensure sustained throughput16.

#### **Handling the Audio Fallback**

A significant percentage of technical reviews lack explicit closed captions, causing standard transcript APIs to fail silently. The pipeline must incorporate an AI fallback mechanism23. When native captions are absent, the system should programmatically download the audio stream and process it through a highly optimised instance of Faster-Whisper, transcribing the audio into timestamped JSON formats23. Services like Apify offer specific actors that handle this exact fallback mechanism, charging fractionally for cloud compute time23.

### **The Hidden Bottleneck: Entity Resolution**

The most formidable algorithmic challenge in the data ingestion pipeline is Entity Resolution—the process of programmatically identifying that a product mentioned in a YouTube transcript is the exact identical entity listed in the GSMArena database24.  
A YouTube reviewer might refer to a device as the "iPhone 15 PM" or "S24 Ultra," whereas the structured database lists "Apple iPhone 15 Pro Max" and "Samsung Galaxy S24 Ultra 5G." Naive exact-match SQL joins or simple string equality checks will fail catastrophically, creating fragmented data silos24.

#### **The Entity Resolution Pipeline**

The system requires a multi-stage pipeline independent of heavy machine learning models, relying instead on deterministic string matching and blocking algorithms24:

1. **Preprocessing & Normalisation:** All strings are converted to lowercase, with non-ASCII characters, punctuation, and generic tokens (e.g., "5G", "Smartphone", "Global") stripped to standardise the data space27.  
2. **Blocking:** Entity Resolution possesses a quadratic time complexity (![][image1]) if every transcript entity is compared against every GSMArena entity25. Blocking reduces this by grouping records based on shared criteria. For instance, extracting the manufacturer name "Samsung" restricts comparisons solely to the Samsung hardware block, exponentially reducing computational load25.  
3. **Fuzzy String Matching:** Within the blocks, the system applies phonetic and edit-distance algorithms via the RapidFuzz or RecordLinkage Python libraries24.  
   * *Jaro-Winkler Distance:* Optimal for short strings and names, as it heavily weights matching prefixes, correcting for typical transcription typographical errors25.  
   * *Token Sort Ratio:* Splits the string into constituent words, sorts them alphabetically, and compares them. This successfully matches "Ultra S24 Galaxy" with "Samsung Galaxy S24 Ultra"24.  
4. **Thresholding and Clustering:** Pairs scoring above a strict threshold (e.g., 85/100) are merged. The system assigns a unified Canonical ID to both the GSMArena specification row and the YouTube sentiment chunks24. This graph-like structure allows the downstream RAG system to explicitly link deterministic technical data with unstructured reviewer sentiment27.

## **The Routing Logic: Orchestrating the 3-Tier Input Engine**

The core value proposition of the system lies in its ability to adapt to varying degrees of user sophistication. Processing all queries through a single, static RAG prompt is computationally wasteful and practically ineffective4. Forcing a simple query through a complex Chain-of-Thought pipeline inflates latency and costs, while passing a complex analytical query to a small model guarantees hallucination4. The application requires a semantic router—a decision layer that evaluates the incoming prompt, determines its intent, and directs it to the appropriate operational workflow3.

### **The Semantic Router Architecture**

The semantic router operates as an LLM-aware API gateway3. When a query arrives, it is processed by a lightweight classification model. This model assesses the request and selects the optimal "route" based on predefined rules or embeddings3. The routing decision dynamically determines:

1. Which database retrieval method to invoke (Vector, Sparse, SQL, or Tri-Hybrid).  
2. Which LLM deployment lane to utilise (Fast/Cheap vs. Reasoning/Expensive)2.  
3. Which prompt template and JSON validation schema to enforce30.

### **Tier 1 (Easy): Persona-Driven Queries**

* **Example Query:** "I'm a gig worker on a £400 budget, I need something reliable."  
* **Routing Decision:** Routed to the Fast Path (e.g., Llama-3-8B).  
* **Retrieval Logic:** These queries lack strict technical parameters but carry strong thematic intents. The router bypasses strict SQL filtering and relies heavily on Dense Vector Retrieval (pgvector). The user's query is embedded and matched against the sentiment vectors extracted from YouTube transcripts (e.g., matching the concept of "gig worker" to reviews mentioning "great for Uber drivers," "insane battery life," or "cheap and reliable").  
* **Prompt Architecture:** The LLM is provided with the top\-![][image2] semantic chunks. The system prompt instructs the model to synthesise a conversational, empathetic response recommending devices that match the psychological and practical profile of the user, requiring minimal deep reasoning.

### **Tier 2 (Medium): Spec-Driven Queries**

* **Example Query:** "I need the best battery and a telephoto camera under £800."  
* **Routing Decision:** Routed to a function-calling enabled LLM.  
* **Retrieval Logic:** This tier represents the highest risk of retrieval failure if routed to a standard vector search1. Dense vectors cannot accurately compute mathematical thresholds like "under £800" or "\> 5000 mAh"1. The semantic router flags this as a structured extraction task.  
* **Prompt Architecture and JSON Schemas:** The query is passed to an LLM strictly to extract a structured JSON object detailing the user's parameters11. The system uses Python's Pydantic library to define a strict JSON Schema detailing expected parameters, constraints, and data types30.

By defining a Pydantic model, the backend automatically generates a schema that enforces data types (e.g., requiring price to be an integer) and restricts outputs via enums30.

| Schema Component | Functionality | Purpose in Recommender System |
| :---- | :---- | :---- |
| type | Defines data structure (e.g., object, integer) | Ensures the LLM does not return raw text when an integer is required30. |
| properties | Lists allowable fields (e.g., max\_price) | Constrains the LLM to only extract relevant data points30. |
| required | Enforces mandatory fields | Prevents the execution of SQL queries with missing critical parameters30. |

Once the LLM outputs the validated JSON, the backend deserialises this into deterministic SQL queries against the PostgreSQL database, executing an exact filter on the GSMArena data before applying any semantic ranking to the remaining subset1.

### **Tier 3 (Deep): Psychographic & Historical Queries**

* **Example Query:** "Upgrading from iPhone 11, hate heavy phones, passion for mobile gaming but dislike the 'gamer' aesthetic."  
* **Routing Decision:** Routed to the Frontier Reasoning Path (e.g., GPT-4o or Claude 3.5 Sonnet) using Chain-of-Thought reasoning and RAG-Fusion methodologies4.  
* **Retrieval Logic:** This requires understanding historical context, subjective weight preferences, performance requirements, and aesthetic sentiment. A single vector search will fail to capture all these dimensions simultaneously. The system employs **RAG-Fusion**32.  
* **RAG-Fusion Implementation:** The frontier LLM first generates multiple distinct search queries based on the single prompt (e.g., Query 1: "Lightweight smartphones 2024", Query 2: "Phones with superior thermal management and high-end SoCs", Query 3: "Minimalist design flagship phones")32.  
* These parallel queries are dispatched to the tri-hybrid PostgreSQL engine. The diverse sets of retrieved documents are then mathematically combined to ensure consensus documents rise to the top32. Finally, the frontier model is provided with the fused context and a Chain-of-Thought prompt to methodically reason through the trade-offs of each recommendation relative to the user's historical device.

## **Critical Challenges & Mitigation Strategies**

Building an orchestration engine of this complexity introduces significant points of failure. Anticipating and architecting mitigations for these bottlenecks demonstrates the engineering maturity expected of a Principal Architect.

### **Hurdle 1: The "Hybrid RAG" Wall and Multimodal Context Fragmentation**

**The Challenge:** Relying solely on vector embeddings for retrieval leads to catastrophic failure when users search for exact product identifiers (e.g., "S24") or strict numeric constraints1. Vectors understand fuzzy semantic meaning, not strict precision, leading to severe retrieval hallucinations1. Conversely, keyword search misses contextual synonyms34.  
**The Mitigation:** Implement a Tri-Hybrid Search architecture directly within PostgreSQL, fused via Reciprocal Rank Fusion8. The system avoids managing multiple disconnected databases by consolidating data in Postgres. The retrieval pipeline executes parallel queries using pgvector (cosine similarity) and tsvector (BM25 lexical scoring)8.  
Because cosine similarity scores and ts\_rank scores exist on fundamentally different mathematical scales and distributions, they cannot be simply normalised and averaged8. Normalisation introduces arbitrary scaling decisions8. Instead, the system applies Reciprocal Rank Fusion directly via SQL Common Table Expressions (CTEs)9. RRF operates purely on the rank position of the document, calculating a unified score based on the formula:  
![][image3]  
Where ![][image2] is a smoothing constant (industry standard is 60\) that prevents top-ranked products from excessively dominating the final score, allowing lower-ranked consensus items across both semantic and lexical lists to contribute meaningfully8. Furthermore, to optimise fusion quality, the backend should over-fetch candidates (e.g., fetching 20 results from each source to fuse into a final top 10), providing a richer signal for the RRF algorithm8.

### **Hurdle 2: Web Scraping IP Bans and Rate Limits**

**The Challenge:** The data ingestion pipeline relies on platforms that exhibit active hostility towards automated data extraction. GSMArena utilises Cloudflare to block headless browsers and data-centre IP ranges14. YouTube throttles API usage to negligible levels and blocks cloud-provider IPs from accessing undocumented transcript endpoints, returning RequestBlocked exceptions when scripts are deployed to AWS or Azure16.  
**The Mitigation:** The ingestion architecture must be entirely decoupled from the application serving layer and executed as asynchronous, fault-tolerant batch jobs.

* The scraping infrastructure will utilise Playwright bundled with evasion techniques to circumvent basic browser-fingerprinting bot detection15.  
* All outbound requests must be routed through a premium rotating residential proxy network16. By routing traffic through standard consumer ISP addresses rather than predictable data centres, the scrapers emulate authentic user traffic, neutralising Cloudflare's ASN-based blocking and YouTube's IP blacklisting16.  
* The pipeline will incorporate exponential backoff retry logic and strict concurrency limits to respect server load and avoid triggering behavioural heuristic bans16.

### **Hurdle 3: LLM Hallucinations on Technical Specifications**

**The Challenge:** Generative models are probabilistic engines, not relational databases. When asked to recommend a device, an LLM might confidently hallucinate battery capacities, mix up processor generations, or invent non-existent camera sensors36. In a recommender system designed to showcase technical authority, factual inaccuracies destroy user trust immediately.  
**The Mitigation:** Strict separation of retrieval, function-calling, and grounding generation11. The LLM is explicitly barred from relying on its internal parametric memory to quote technical specifications36. The semantic router enforces a strict structured output schema30. When the user asks for specifications, the LLM outputs a function call11. The backend executes the SQL query against the deterministic GSMArena data, retrieves the exact, verified hardware specifications, and injects them into the final prompt context11. The LLM's system prompt is strictly constrained to synthesise *only* the injected context, ensuring 100% factual fidelity and effectively eliminating specification hallucinations36.

## **Resume Impact: Strategic Positioning for Technical Recruiters**

To maximise the impact of this project in securing an AI/Software Engineering position, the presentation of the project must eschew generic descriptions in favour of highly specific, quantifiable architectural achievements. Recruiters and engineering managers look for candidates who understand production constraints—cost, latency, data integrity, and orchestration—rather than individuals who merely wrap commercial APIs.  
**Recommended Resume Bullet Points:**

* **Architected a Tri-Hybrid RAG Engine via PostgreSQL:** Engineered a unified search pipeline bypassing traditional vector DB limitations by combining pgvector (HNSW dense embeddings), tsvector (BM25 sparse search), and deterministic SQL filtering; fused parallel retrieval streams natively using Reciprocal Rank Fusion (RRF) CTEs, drastically improving exact-match retrieval precision over naive semantic search.  
* **Developed a Multi-Tier Semantic Routing Layer:** Designed a dynamic inference orchestrator that classifies query intent and complexity in real-time, routing basic queries to local, quantised open-weight models while reserving expensive frontier models and multi-query RAG-Fusion pipelines strictly for complex psychographic reasoning, thereby optimising computational overhead and API costs.  
* **Built an Autonomous, Evasion-Resilient ETL Pipeline:** Programmed a fault-tolerant asynchronous data ingestion engine using Playwright and residential proxy rotation to bypass strict Cloudflare and YouTube IP bans; implemented a deterministic Entity Resolution pipeline (Jaro-Winkler, Token-Sort Ratio) to flawlessly unify unstructured video transcript sentiment with highly structured GSMArena technical specifications.

#### **Works cited**

1. Why SQL \+ Vectors \+ Sparse Search Make Hybrid RAG Actually Work \- Reddit, [https://www.reddit.com/r/Rag/comments/1p9kei6/why\_sql\_vectors\_sparse\_search\_make\_hybrid\_rag/](https://www.reddit.com/r/Rag/comments/1p9kei6/why_sql_vectors_sparse_search_make_hybrid_rag/)  
2. vLLM Semantic Router: Open-Source LLM Router for Mixture-of-Models, [https://vllm-semantic-router.com/](https://vllm-semantic-router.com/)  
3. Semantic Routers: Quietly Making Your LLM Stack Not Fall Over | by Thinking Loop, [https://medium.com/@ThinkingLoop/semantic-routers-quietly-making-your-llm-stack-not-fall-over-7a4c19f3fae1](https://medium.com/@ThinkingLoop/semantic-routers-quietly-making-your-llm-stack-not-fall-over-7a4c19f3fae1)  
4. When to Reason: Semantic Router for vLLM \- arXiv, [https://arxiv.org/html/2510.08731v1](https://arxiv.org/html/2510.08731v1)  
5. vLLM Semantic Router: Next Phase in LLM inference, [https://vllm.ai/blog/2025-09-11-semantic-router](https://vllm.ai/blog/2025-09-11-semantic-router)  
6. Postgres Vector Store | Developer Documentation \- LlamaParse, [https://developers.llamaindex.ai/python/framework/integrations/vector\_stores/postgres/](https://developers.llamaindex.ai/python/framework/integrations/vector_stores/postgres/)  
7. AWS Vector Database Options: OpenSearch vs Bedrock Knowledge Bases vs Neptune Analytics \- BigData Boutique, [https://bigdataboutique.com/blog/aws-vector-database-options](https://bigdataboutique.com/blog/aws-vector-database-options)  
8. Building Hybrid Search for RAG: Combining pgvector and Full-Text Search with Reciprocal Rank Fusion \- DEV Community, [https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk)  
9. Hybrid Search in PostgreSQL: The Missing Manual \- ParadeDB, [https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual](https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual)  
10. Hybrid Search Using Postgres DB \- DZone, [https://dzone.com/articles/hybrid-search-using-postgres-db](https://dzone.com/articles/hybrid-search-using-postgres-db)  
11. Function calling using LLMs \- Martin Fowler, [https://www.martinfowler.com/articles/function-call-LLM.html](https://www.martinfowler.com/articles/function-call-LLM.html)  
12. Which is better for SEO HTML tables vs un ordered lists \- Webmasters Stack Exchange, [https://webmasters.stackexchange.com/questions/111095/which-is-better-for-seo-html-tables-vs-un-ordered-lists](https://webmasters.stackexchange.com/questions/111095/which-is-better-for-seo-html-tables-vs-un-ordered-lists)  
13. 11 Types of Product Tables Your Website Needs, [https://ninjatables.com/types-of-product-tables-your-business-needs/](https://ninjatables.com/types-of-product-tables-your-business-needs/)  
14. Jieyab89/OSINT-Cheat-sheet \- GitHub, [https://github.com/Jieyab89/OSINT-Cheat-sheet](https://github.com/Jieyab89/OSINT-Cheat-sheet)  
15. Recently Active 'web-scraping' Questions \- Stack Overflow, [https://stackoverflow.com/questions/tagged/web-scraping?tab=Active](https://stackoverflow.com/questions/tagged/web-scraping?tab=Active)  
16. Fixing YouTube Transcript API RequestBlocked Error: A Developer's Guide \- Medium, [https://medium.com/@lhc1990/fixing-youtube-transcript-api-requestblocked-error-a-developers-guide-83c77c061e7b](https://medium.com/@lhc1990/fixing-youtube-transcript-api-requestblocked-error-a-developers-guide-83c77c061e7b)  
17. YouTube Transcript Scraper \- Apify, [https://apify.com/naz\_here/youtube-transcript-scraper](https://apify.com/naz_here/youtube-transcript-scraper)  
18. Collect Data By Building A Web Crawler \- Kaggle, [https://www.kaggle.com/code/vigvisw/collect-data-by-building-a-web-crawler](https://www.kaggle.com/code/vigvisw/collect-data-by-building-a-web-crawler)  
19. JamesLi197412/web-scrapying-Gsmarena \- GitHub, [https://github.com/JamesLi197412/web-scrapying-Gsmarena](https://github.com/JamesLi197412/web-scrapying-Gsmarena)  
20. Python \- Getting all links from a div having a class \- Stack Overflow, [https://stackoverflow.com/questions/8616928/python-getting-all-links-from-a-div-having-a-class](https://stackoverflow.com/questions/8616928/python-getting-all-links-from-a-div-having-a-class)  
21. How to scrape a table with sub-rows that do not belong to any hierarchy? \- Stack Overflow, [https://stackoverflow.com/questions/70855140/how-to-scrape-a-table-with-sub-rows-that-do-not-belong-to-any-hierarchy](https://stackoverflow.com/questions/70855140/how-to-scrape-a-table-with-sub-rows-that-do-not-belong-to-any-hierarchy)  
22. Best YouTube transcript APIs compared (2026), [https://transcriptapi.com/blog/best-youtube-transcript-apis-compared](https://transcriptapi.com/blog/best-youtube-transcript-apis-compared)  
23. How to Extract YouTube Transcripts Without the YouTube API (2026) | Use Apify, [https://use-apify.com/blog/how-to-extract-youtube-transcripts-2026](https://use-apify.com/blog/how-to-extract-youtube-transcripts-2026)  
24. A Practical Guide To Entity Resolution in Python (No Database, No Machine Learning), [https://python.plainenglish.io/a-practical-guide-to-entity-resolution-in-python-no-database-no-machine-learning-89d55badaeac](https://python.plainenglish.io/a-practical-guide-to-entity-resolution-in-python-no-database-no-machine-learning-89d55badaeac)  
25. Entity Resolution — An Introduction | by Adrian Evensen | Medium, [https://medium.com/@adev94/entity-resolution-an-introduction-fb2394d9a04e](https://medium.com/@adev94/entity-resolution-an-introduction-fb2394d9a04e)  
26. Implementing entity resolution with Python Record Linkage \- Fivetran, [https://www.fivetran.com/learn/implementing-entity-resolution-with-python-record-linkage](https://www.fivetran.com/learn/implementing-entity-resolution-with-python-record-linkage)  
27. Name Matching Model for Entity Resolution (Part 2\) | by Joe Le | Medium, [https://medium.com/@vietexob/name-matching-model-for-entity-resolution-part-2-e070f5351c18](https://medium.com/@vietexob/name-matching-model-for-entity-resolution-part-2-e070f5351c18)  
28. Best Way to Match Product Names with Different Structures in Two Lists? \- Reddit, [https://www.reddit.com/r/PythonProjects2/comments/1j80ltb/best\_way\_to\_match\_product\_names\_with\_different/](https://www.reddit.com/r/PythonProjects2/comments/1j80ltb/best_way_to_match_product_names_with_different/)  
29. LLM routing strategies for quality in AI applications \- n8n Blog, [https://blog.n8n.io/llm-routing/](https://blog.n8n.io/llm-routing/)  
30. The guide to structured outputs and function calling with LLMs \- Agenta.ai, [https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)  
31. Diving into Function Calling and its JSON Schema in Semantic Kernel .NET, [https://devblogs.microsoft.com/agent-framework/diving-into-function-calling-and-its-json-schema-in-semantic-kernel-net/](https://devblogs.microsoft.com/agent-framework/diving-into-function-calling-and-its-json-schema-in-semantic-kernel-net/)  
32. GitHub \- Raudaschl/rag-fusion: RAG-Fusion: multi-query generation \+ Reciprocal Rank Fusion for better retrieval-augmented generation. Includes evaluation harness with NFCorpus/BEIR., [https://github.com/Raudaschl/rag-fusion](https://github.com/Raudaschl/rag-fusion)  
33. Optimizing Hybrid Search Query with Reciprocal Rank Fusion (RRF) | Server \- MariaDB, [https://mariadb.com/docs/server/reference/sql-structure/vectors/optimizing-hybrid-search-query-with-reciprocal-rank-fusion-rrf](https://mariadb.com/docs/server/reference/sql-structure/vectors/optimizing-hybrid-search-query-with-reciprocal-rank-fusion-rrf)  
34. Hybrid search with HNSW and BM25 reranking : r/Rag \- Reddit, [https://www.reddit.com/r/Rag/comments/1t6cmqf/hybrid\_search\_with\_hnsw\_and\_bm25\_reranking/](https://www.reddit.com/r/Rag/comments/1t6cmqf/hybrid_search_with_hnsw_and_bm25_reranking/)  
35. Hybrid search benefits: Why RAG systems need both methods \- Redis, [https://redis.io/blog/hybrid-search-benefits-rag-systems/](https://redis.io/blog/hybrid-search-benefits-rag-systems/)  
36. Vector Databases for RAG \- IBM, [https://www.ibm.com/think/topics/rag-vector-database](https://www.ibm.com/think/topics/rag-vector-database)  
37. Structuring LLM Responses with JSON Schemas | nuric Blog, [https://www.doc.ic.ac.uk/\~nuric/posts/coding/structuring-llm-responses-with-json-schema/](https://www.doc.ic.ac.uk/~nuric/posts/coding/structuring-llm-responses-with-json-schema/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAaCAYAAAAXHBSTAAADz0lEQVR4Xs2XS6hOURTH18kj8o7uJYorj0RRXilmRHkkKWJooGRmIDMlpVASEgMjmRgoiTD4MKCUUkykSCJKSijp4v8/6+x99vPc435X+dX/+85Za+332vucI9JI4fwODbaubKWOIxWTsjkk3Unj39BFBSi6EX/noNPQysA9GLrojc/YSjHNy7QA2ltdD4euQNNrt4wwF1H+JKtrZiI0DRoWOhIsg+5BM5sbSjrnQyed+4MIW+rcT0C5/ZIpHJMOOwt9gd5Bb6B+0bQY7wY5cEAvpLu0MRPHHl2C+hwfeQgdKHI9TqKho6Hj0DFosuNdD30W7fgcx264Cx2RQTQYX8tC6ENoBGtEJ3iFZw2jPAqZit/7op1PsQP6Bd0OHaKNhTOrmKltbNwyAXF38H8odEi91zqS2bd1E9ridfz8hk55PoNaWOlVXDOu7qzIFmitXnYF98x2qdtf7PgMU6DnooOTVFcdCnaU+yeVWgbWcFl08KMcG/N/hgkyVM1xRpnGpnX+895NbWO/KDooah/U60Uopg+vA3tJ1Uj511sN6kxtd0Jq2MGO+IOaBD2GxlT3LttEfe+hm6Lp+0o0Vb9CS+rQclVYr6tUneQg9NPeRd1UmD7cKxt8czS+2aId1PRTjC2kD7olOtvsBMucED2IyFzohtjJyfQszWbx+xDB2eDJ9QAaF/hc2CpXkpW9dex8lnxz7g17RFfCrGR4+KwWb1DtKco2i1SblrGI6iCoU17n4V57V6Upj27DKuiHcx/CN4VPomnrwtWjBkM0keE6m43XwVU8qDqapyIH9AzqsdZEAwG7od+FPrgNeDuQR9Ci2hR2S02+1d4th747jiScsecow+PSp661v9AU8h98zYNiaZ6MnAzuW4NZXe4vnpo87dq8hpUU4Z6K58Na+BrEt4WZta9saJdop+c5dhezJ7l3arRanGgFX7XcvTMStmuidTKl+SAvHwdR3yKD5ahoSg/IJuij6LKeFy34EhXTxhSqiRorDovunRAzo+HeoZ1H+hOxx3pUaQ7zWOHJ2gquDNNpJ7QVmiXtWmM6mc8GF34uMKXj1NL9az8nciQaNwfP/oSvW7TKqmLuDc6ceQb9O4ryVYqPlL7Q9S/gIbLO3hXOLLea0lZBPQh7isgDnjVfNO/xMXFRPFPpQqUB0yomqi9l4kPcPcjake2yxV2CiBHw8ZOBh85Qw9cxfhpZUt1I2Swpp7WlnA5Nbt/XFCnt3fm4vKcktUApQ2TzybvznpIB3IYqrGW0xcTny5WewJ2PbiBVKGWLaYryfU2R/xN/AIhXjTauUTvfAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAcCAYAAAC3f0UFAAABbUlEQVR4Xm1SrU6DUQxtE0hGNv4SAlmyd0Bh0DMYNEHgCI+wJ5iZJ2gswWMQnySZQiARECwWQcLg9Pber729NOk9bU9/942YiUhUnyRmlUBO4kgVN3HOL5IKBcsTE+qQZ92s0iXayDjE847QN7wrT4R9krEHXUK/oEeFMSnJNmGJaa/AAyP+O0KnfcK6h7EWd8xerlTvFzizlDDcngQrwLSEcot1GRIG0SbgAzpJDONIpmcYD4iN6lSiU8AceAxdQDegJ+CegNsumSR/Dr2DXqN0mEIsK/DYJ4kI+UhyoPx8xOesnZ3YdRPSfXfR7hL4A70h+QnLqa5iCliJyekY7hB7wxqywgXVB9KMdQUIC9FBX0j/AreYNlCKZBS+mn49kSGCsn8Hbgt4luNZmHbwDvrVbJ19n6TQ75+l8Uti1lp8tGJjqvfV7kt9vQXc2HZC7lA19QWhzsQ6NVxPpT3qbs2f2EHApq+JNQ5JLvYHpWMjzCUYxp8AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,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>