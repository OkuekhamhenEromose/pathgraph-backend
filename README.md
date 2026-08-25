# PathGraph — Career Path Navigator

**A graph-native application for discovering optimal software engineering career progression.**

Powered by **CognoDB** (openCypher/Bolt) • FastAPI • React + TypeScript • Tailwind CSS

---

## Problem

Software engineers struggle to understand what skills they need to acquire to transition between roles. Career ladders are opaque, skill dependencies are non-linear, and "what should I learn next?" is a relationship question, not a table lookup.

**Example:** A Senior Backend Engineer wants to become a Staff Backend Engineer. This requires:
- Knowing the promotion path (Senior → Staff → Principal)
- Knowing the required skills (System Design, Distributed Systems)
- Knowing the prerequisites for those skills (Microservices → System Design → Distributed Systems)
- Knowing which skills they already have vs. which are missing

This is a **network traversal problem**, not a CRUD problem.

---

## Why This Problem Is Relationship-Heavy

| Concept | Relationship Type | Natural Graph Structure |
|---------|-------------------|------------------------|
| Career progression | `PROMOTES_TO` | Directed acyclic graph of roles |
| Skill dependencies | `PREREQUISITE_FOR` | DAG of learning order |
| Role requirements | `REQUIRES` | Bipartite graph: roles ↔ skills |
| Person capabilities | `HAS_SKILL` | Person ↔ skill affinity network |
| Track membership | `BELONGS_TO` | Hierarchical classification |

Every core user question is a traversal:
- "What is the path from A to B?" → shortest path over promotions
- "What am I missing?" → set difference over transitive skill requirements
- "What should I learn first?" → topological sort over prerequisite DAG

---

## Why CognoDB?

For career path navigation, the value is not in **storing** roles and skills — it is in **traversing** the connections between them.

PostgreSQL can store the data, but it cannot express the questions naturally. Every core user question in our application is a traversal question:

&gt; *"What is the path?"*
&gt; *"What am I missing?"*
&gt; *"What comes first?"*

These are graph-native questions. CognoDB lets us write queries that read like the questions themselves, while PostgreSQL forces us to translate graph thinking into recursive set logic.

### Specific Advantages

| Feature | CognoDB Advantage |
|---------|-------------------|
| **Career paths** | `shortestPath()` over `PROMOTES_TO` is a single, readable query |
| **Skill prerequisites** | Transitive closure via `PREREQUISITE_FOR*1..5` is declarative |
| **Skill gaps** | `NOT (person)-[:HAS_SKILL]-&gt;(skill)` is a native graph operation |
| **Learning order** | `length(path)` gives topological ordering without complex algorithms |

---

## Why Not PostgreSQL/MySQL?

We do NOT claim graph databases are universally superior. We claim that for **career path navigation** — a domain defined by connected entities, hierarchical progression, and dependency chains — a graph model is more natural, expressive, and maintainable.

### Query Comparison 1: Find Career Path (Shortest Path)

**Question:** "I am a Senior Backend Engineer. What is the path to Principal Engineer?"

**PostgreSQL (Recursive CTE):**
```sql
WITH RECURSIVE career_path AS (
    SELECT from_role_id, to_role_id, 1 AS hop, ARRAY[from_role_id] AS path
    FROM role_progressions WHERE from_role_id = 'r-senior-be'
    UNION ALL
    SELECT rp.from_role_id, rp.to_role_id, cp.hop + 1, cp.path || rp.from_role_id
    FROM role_progressions rp
    JOIN career_path cp ON rp.from_role_id = cp.to_role_id
    WHERE rp.to_role_id != ALL(cp.path) AND cp.hop &lt; 6
)
SELECT path || to_role_id AS full_path, hop AS num_hops
FROM career_path WHERE to_role_id = 'r-principal' ORDER BY hop LIMIT 1;
