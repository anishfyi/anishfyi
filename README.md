<div>
<picture><source media="(prefers-color-scheme: dark)" srcset="header/hero-dark.svg"><img src="header/hero-light.svg" alt="Anish Kr Singh. I build backend systems and tools for artificial intelligence (AI), and I co-founded Velofy, an applied AI and security lab in Delhi. Based in Gurugram, India." width="100%" height="290" align="top"></picture>
<a href="https://anishfyi.com"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-site-dark.svg"><img src="header/link-site-light.svg" alt="anishfyi.com, my website" width="33.33%" height="52" align="top"></picture></a><a href="https://velofy.co"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-velofy-dark.svg"><img src="header/link-velofy-light.svg" alt="Velofy, the lab I co-founded" width="33.33%" height="52" align="top"></picture></a><a href="https://www.linkedin.com/in/anishfyi"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-linkedin-dark.svg"><img src="header/link-linkedin-light.svg" alt="My LinkedIn profile" width="33.33%" height="52" align="top"></picture></a>
<a href="https://x.com/anishfyi"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-x-dark.svg"><img src="header/link-x-light.svg" alt="My X profile" width="33.33%" height="52" align="top"></picture></a><a href="https://cal.com/anishfyi"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-call-dark.svg"><img src="header/link-call-light.svg" alt="Book a call on cal.com" width="33.33%" height="52" align="top"></picture></a><a href="mailto:hey@anishfyi.com"><picture><source media="(prefers-color-scheme: dark)" srcset="header/link-email-dark.svg"><img src="header/link-email-light.svg" alt="Email hey@anishfyi.com" width="33.33%" height="52" align="top"></picture></a>
<picture><source media="(prefers-color-scheme: dark)" srcset="header/graph-dark.svg"><img src="header/graph-light.svg" alt="My GitHub contributions for the three most recent years, one cell per day, stronger gold on busier days, with the all-time total. Refreshed daily." width="100%" height="298" align="top"></picture>
</div>

## What I work on

I work on backend systems and applied artificial intelligence (AI) at [FableRoom](https://fableroom.com). Before that I spent two and a half years on the integrations team at Fyle.

At [Velofy](https://velofy.co), the lab I co-founded, we study how models find and fix vulnerabilities and build the tools agents run on.

- **AI tooling and harness engineering.** Agent harnesses, context engineering, semantic layers, and plugins for Claude Code.
- **Backend.** Four years of backend work: Django, FastAPI and PostgreSQL.
- **Security-minded engineering.** I decide first what a system may never do, then write the code that enforces it: a read-only database role for an agent that queries data, and a signature check on every inbound webhook.
- **Languages.** Python, TypeScript and Rust, plus Swift and C++.

## Open source

Three of my own repositories. curl_reap and trove have project pages on [anishfyi.com](https://anishfyi.com/projects/).

| Project | What it does | Links |
| --- | --- | --- |
| [**curl_reap**](https://github.com/anishfyi/curl_reap) | Python scraping with a browser-exact fingerprint. Its own transport sends a captured browser's Transport Layer Security (TLS) handshake byte for byte, with self-healing selectors and a concurrent crawler on top. | [Page](https://anishfyi.com/projects/curl_reap/), [docs](https://velofy.co/curl_reap/) |
| [**trove**](https://github.com/anishfyi/trove) | Repository index and session memory for coding agents. A Rust engine indexes a repository into layered summaries, and a Claude Code plugin keeps decisions, gotchas and conventions as plain files. | [Page](https://anishfyi.com/projects/trove/), [docs](https://velofy.co/trove/) |
| [**querion**](https://github.com/anishfyi/querion) | A read-only analyst for questions about your data. Ask about a Postgres database in plain English and get the number, a table and the Structured Query Language (SQL) it ran. | [Page](https://velofy.co/open-source/querion/), [docs](https://velofy.co/querion/) |

Built at Velofy and documented on [velofy.co](https://velofy.co/open-source/):

| Project | What it does | Links |
| --- | --- | --- |
| [**Troy**](https://velofy.co/open-source/troy/) | A Chromium browser your agent joins, already signed in. An agent attaches over the Chrome DevTools Protocol (CDP) to the tabs you already use. | [Website](https://troy.velofy.co), [docs](https://velofy.co/troy/), [source](https://github.com/velofy/troy) |
| [**terbium**](https://velofy.co/open-source/terbium/) | Parses documents into rows. It rebuilds the tables in a Portable Document Format (PDF) file from the position of every word, scores its confidence, and sends only the tables it cannot resolve to a model. | [Docs](https://velofy.co/terbium/), [source](https://github.com/velofy/terbium) |
| [**glep**](https://velofy.co/open-source/glep/) | Indexed grep and glob for coding agents. One trigram index narrows each search to the files that can match, with output byte-compatible with ripgrep and no daemon. | [Docs](https://velofy.co/glep/), [source](https://github.com/velofy/glep) |

## Now at Velofy

- [**Troy**](https://troy.velofy.co): a Chromium browser that agents attach to, inside the session you are already signed into.
- [**Kestrel**](https://kestrel.velofy.co): sends one coding task to several agents, then a judge picks the diff.
- [**Agent teardowns**](https://velofy.co/research/papers/): how OpenClaw, Muse, Instinct and dots are built, with architecture diagrams.
- [**The Bulletin**](https://velofy.co/bulletin/): reviews of the latest AI models, with a scoreboard of independent benchmarks.
- [**Zero-days found by AI**](https://velofy.co/journal/zero-days-found-by-ai/): new on the journal, a sourced review of the zero-days that AI systems have found.

The lab also makes [Numera](https://numera.velofy.co) and [Whiteboard](https://whiteboard.velofy.co).

## Merged contributions

Pull requests merged into other people's projects.

| Project | Pull request | What changed |
| --- | --- | --- |
| [**facebook/pyrefly**](https://github.com/facebook/pyrefly)<br>Meta's Python type checker and language server | [#4754](https://github.com/facebook/pyrefly/pull/4754) | Variance inference now skips `__new__`, as it already did `__init__`, so constructor parameters no longer make an otherwise covariant type parameter invariant. Landed as [`39b9689`](https://github.com/facebook/pyrefly/commit/39b9689ef12d071a13bb1371e6781db99c9089f3). |
| [**svix/svix-webhooks**](https://github.com/svix/svix-webhooks)<br>The open source webhooks service | [#2604](https://github.com/svix/svix-webhooks/pull/2604) | Ruby library: integer and boolean query parameters no longer raise a `TypeError` before the request is sent. |
| [**svix/svix-webhooks**](https://github.com/svix/svix-webhooks)<br>The open source webhooks service | [#2605](https://github.com/svix/svix-webhooks/pull/2605) | Ruby library: struct enums accept symbol keys, so a symbol-keyed `config` keeps its type discriminator. |
| [**svix/svix-webhooks**](https://github.com/svix/svix-webhooks)<br>The open source webhooks service | [#2607](https://github.com/svix/svix-webhooks/pull/2607) | Ruby library: generated models accept the JavaScript Object Notation (JSON) generator state, so they serialize when nested in arrays and objects. |
| [**robocurve/inspect-robots**](https://github.com/robocurve/inspect-robots)<br>Open source evals for physical AI | [#335](https://github.com/robocurve/inspect-robots/pull/335) | The `capx` plugin passes `-P effort=` to the model exactly as typed, matching the agent plugin, and an invalid value gives a guided error instead of a traceback. |
| [**nodemaven/nodemaven-python**](https://github.com/nodemaven/nodemaven-python)<br>Python client for the NodeMaven proxy gateway | [#8](https://github.com/nodemaven/nodemaven-python/pull/8) | Quoted the extras install line so the quickstart works in zsh, with a test that fails on the unquoted form. |

## Writing

Selected essays from [anishfyi.com/writings](https://anishfyi.com/writings/).

- [**Why your scraper gets a 403 and your browser does not**](https://anishfyi.com/writings/why-your-scraper-gets-a-403/). The block usually happens in the TLS handshake, before any header is read.
- [**Parse first, escalate only what you must**](https://anishfyi.com/writings/parse-first-escalate-only-what-you-must/). Rebuilding tables from word geometry, scoring confidence, and sending only the hard pages to a model.
- [**Building Querion: a Read-Only, Natural-Language Data Analyst**](https://anishfyi.com/writings/querion-read-only-analyst/). Letting a language model query production data without ever letting it write.
- [**Trove: Giving Claude Code a Persistent Memory**](https://anishfyi.com/writings/trove-persistent-memory-claude-code/). A file-based memory index that reloads into context every session.
- [**Verifying Inbound Webhooks with HMAC Signatures**](https://anishfyi.com/writings/hmac-webhook-verification/). Why every inbound webhook needs a hash-based message authentication code (HMAC) check, and how to verify one safely in Django.
- [**Zero-Downtime Database Migrations in Django**](https://anishfyi.com/writings/zero-downtime-migrations/). Shipping schema changes to a live Postgres database without dropped requests.

## Get in touch

For backend and applied AI roles, [book a call](https://cal.com/anishfyi) or write to [hey@anishfyi.com](mailto:hey@anishfyi.com). For Velofy, write to [anish@velofy.co](mailto:anish@velofy.co).

[anishfyi.com](https://anishfyi.com) · [LinkedIn](https://www.linkedin.com/in/anishfyi) · [X](https://x.com/anishfyi)
