
# gcp-changelog

A command-line tool to track and monitor Google Cloud Platform release notes.

## What This Program Does

This is a **release notes scraper** that automatically downloads and organizes release notes from Google Cloud services via their XML feeds or HTML pages.

### Features:

- **100+ GCP Services**: Built-in support for Cloud Run, GKE, BigQuery, Vertex AI, and many more
- **Service Groups**: Query multiple services at once by domain (AI, Security, Networking, etc.)
- **XML Feed Parsing**: Reads directly from Google's official release notes XML feeds
- **HTML Fallback**: Automatically falls back to HTML scraping when XML feeds are unavailable
- **Smart Categorization**: Automatically tags items as GA, Preview, Breaking Changes, Security, etc.
- **Flexible Filtering**: Filter by days, months, or specific date ranges
- **Category Filtering**: Filter by release type (GA, preview, breaking, security, etc.)
- **Multiple Output Formats**: Text, Markdown, JSON, or styled HTML

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# Get Cloud Run release notes (last 12 months)
./gcp-changelog.py -s cloud-run

# Get release notes from last 7 days
./gcp-changelog.py -s cloud-run -d 7

# Get GKE notes for last 6 months as HTML
./gcp-changelog.py -s gke -m 6 -o html -f gke_notes.html

# Query all AI services at once
./gcp-changelog.py -g ai -m 3

# List all available services and groups
./gcp-changelog.py --list-services
./gcp-changelog.py --list-groups
```

## Command Line Reference

```
usage: gcp-changelog.py [-h] [-s SERVICE | -g GROUP | -u URL | --list-services | --list-groups]
                        [-d DAYS] [-m MONTHS] [--start-date START_DATE] [--end-date END_DATE]
                        [-c CATEGORY] [-o {text,json,markdown,html}] [-f FILE] [-v]

Scrape release notes from documentation pages or XML feeds

options:
  -h, --help            show this help message and exit
  -s, --service SERVICE
                        GCP service name (use --list-services to see all options)
  -g, --group GROUP     Service group to query (use --list-groups to see all options)
  -u, --url URL         URL of the release notes page or XML feed to scrape
  --list-services       List all available GCP service names
  --list-groups         List all available service groups
  -c, --category CATEGORY
                        Filter by category (can be used multiple times)
  -o, --output {text,json,markdown,html}
                        Output format (default: text)
  -f, --file FILE       Output file path (if not specified, prints to stdout)
  -v, --verbose         Enable verbose output

date filtering:
  -d, --days DAYS       Number of days to look back
  -m, --months MONTHS   Number of months to look back (default: 12)
  --start-date START_DATE
                        Start date for filtering (format: YYYY-MM-DD)
  --end-date END_DATE   End date for filtering (format: YYYY-MM-DD, default: today)
```

## Usage Examples

### Using Service Names (Recommended)

```bash
# Cloud Run release notes
./gcp-changelog.py -s cloud-run

# GKE release notes for last 6 months
./gcp-changelog.py -s gke -m 6

# Release notes from last 30 days
./gcp-changelog.py -s bigquery -d 30

# BigQuery notes as JSON
./gcp-changelog.py -s bigquery -o json -f bigquery.json

# Vertex AI notes as HTML
./gcp-changelog.py -s vertex-ai -o html -f vertex.html
```

### Service Groups

Query multiple services at once by domain:

```bash
# All AI/ML service updates
./gcp-changelog.py -g ai -m 3

# All security service updates
./gcp-changelog.py -g security -c breaking -c deprecated

# All GKE channel updates from last 14 days
./gcp-changelog.py -g gke -d 14

# All database updates as HTML
./gcp-changelog.py -g databases -o html -f db_updates.html

# List available groups
./gcp-changelog.py --list-groups
```

Available groups:
| Group | Services |
|-------|----------|
| `apps` | apphub, api-gateway, apigee, cloud-build, cloud-functions, cloud-run, cloud-tasks, cloud-trace, eventarc, workflows |
| `databases` | alloydb, bigquery, data-fusion, firestore, spanner, cloud-sql, data-catalog, database-migration, dataflow, dataproc, datastore, memorystore-memcached, memorystore-redis |
| `security` | binary-authorization, certificate-authority, cloud-armor, cloud-kms, iam, identity-platform, recaptcha, secret-manager, security-command-center, vpc-service-controls |
| `networking` | cloud-cdn, cloud-dns, cloud-interconnect, load-balancing, cloud-nat, cloud-router, service-mesh, vpc, network-intelligence, network-tiers, service-directory |
| `storage` | artifact-registry, cloud-storage, container-registry, filestore, managed-lustre, transfer-appliance |
| `compute` | bare-metal, cloud-hub, cloud-tpu, compute-engine, confidential-space, distributed-cloud-edge, anthos-bare-metal, anthos-vmware, vmware-engine |
| `gke` | gke, gke-rapid, gke-regular, gke-stable, gke-extended, gke-nochannel |
| `operations` | cloud-logging, cloud-monitoring, cloud-observability, cloud-profiler, cloud-scheduler, config-connector, resource-manager |
| `ai` | ai-app-builder, dialogflow, document-ai, gemini-code-assist, speech-to-text, talent-solution, text-to-speech, translation, vertex-ai, video-intelligence |
| `specialized` | cloud-composer, healthcare-api, blockchain-node-engine |
| `workspace` | apps-script, cloud-search, docs-api |
| `sdk` | cloud-sdk |

### Date Range Filtering

```bash
# Last 7 days
./gcp-changelog.py -s cloud-run -d 7

# Last 30 days
./gcp-changelog.py -s bigquery -d 30

# Notes from January to June 2024
./gcp-changelog.py -s cloud-run --start-date 2024-01-01 --end-date 2024-06-30

# Notes since June 2024
./gcp-changelog.py -s bigquery --start-date 2024-06-01

# Last 3 months
./gcp-changelog.py -s gke -m 3
```

### Category Filtering

```bash
# Only GA and Preview features
./gcp-changelog.py -s cloud-run -c ga -c public-preview

# Only breaking changes and deprecations
./gcp-changelog.py -s gke -c breaking -c deprecated

# Security updates only
./gcp-changelog.py -s compute-engine -c security
```

Available categories: `ga`, `public-preview`, `breaking`, `security`, `deprecated`, `fixed`, `issue`, `change`, `announcement`, `libraries`, `update`

### Using Custom URLs

```bash
# Custom XML feed URL
./gcp-changelog.py -u https://cloud.google.com/feeds/cloud-run-release-notes.xml

# HTML release notes page
./gcp-changelog.py -u https://cloud.google.com/run/docs/release-notes
```

### Output Formats

```bash
# Plain text (default)
./gcp-changelog.py -s cloud-run

# Markdown (great for docs)
./gcp-changelog.py -o markdown -s cloud-run -f notes.md

# JSON (for automation)
./gcp-changelog.py -s cloud-run -o json -f notes.json

# HTML (styled webpage)
./gcp-changelog.py -s cloud-run -o html -f notes.html
```

## What It Categorizes

The scraper automatically detects and labels:

| Category | Description |
|----------|-------------|
| `ga` | Generally Available features |
| `public-preview` | Preview/Beta features |
| `breaking` | Breaking changes |
| `security` | Security patches |
| `deprecated` | Deprecated features |
| `fixed` | Bug fixes |
| `change` | Significant changes |
| `announcement` | Announcements |
| `issue` | Known issues |
| `libraries` | SDK/Library updates |
| `update` | General updates |

## Real-World Use Cases

- **DevOps Teams**: Stay current with cloud service updates
- **Security Teams**: Quickly identify security patches across services
- **Product Managers**: Track new feature releases
- **Developers**: Find breaking changes before upgrading
- **Technical Writers**: Aggregate changes for documentation

## Installation

```bash
# Clone the repository
git clone https://github.com/dazdaz/gcp-changelog
cd gcp-changelog

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


# Google Cloud Release Notes URLs

Applications & Development

AppHub
HTML: https://cloud.google.com/app-hub/docs/release-notes
XML: https://cloud.google.com/feeds/apphub-release-notes.xml

API Gateway
HTML: https://cloud.google.com/api-gateway/docs/release-notes
XML: https://cloud.google.com/feeds/api-gateway-release-notes.xml

Apigee
HTML: https://cloud.google.com/apigee/docs/release-notes
XML: https://cloud.google.com/feeds/apigee-release-notes.xml

Cloud Build
HTML: https://cloud.google.com/build/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-build-release-notes.xml

Cloud Functions
HTML: https://cloud.google.com/functions/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-functions-release-notes.xml

Cloud Run
HTML: https://cloud.google.com/run/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-run-release-notes.xml

Cloud Tasks
HTML: https://cloud.google.com/tasks/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-tasks-release-notes.xml

Cloud Trace
HTML: https://cloud.google.com/trace/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-trace-release-notes.xml

Eventarc
HTML: https://cloud.google.com/eventarc/docs/release-notes
XML: https://cloud.google.com/feeds/eventarc-release-notes.xml

Workflows
HTML: https://cloud.google.com/workflows/docs/release-notes
XML: https://cloud.google.com/feeds/workflows-release-notes.xml

Databases & Data Analytics

AlloyDB for PostgreSQL
HTML: https://cloud.google.com/alloydb/docs/release-notes
XML: https://cloud.google.com/feeds/alloydb-release-notes.xml

BigQuery
HTML: https://cloud.google.com/bigquery/docs/release-notes
XML: https://cloud.google.com/feeds/bigquery-release-notes.xml

Cloud Data Fusion
HTML: https://cloud.google.com/data-fusion/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-data-fusion-release-notes.xml

Cloud Firestore
HTML: https://cloud.google.com/firestore/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-firestore-release-notes.xml

Cloud Spanner
HTML: https://cloud.google.com/spanner/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-spanner-release-notes.xml

Cloud SQL
HTML: https://cloud.google.com/sql/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-sql-release-notes.xml

Data Catalog
HTML: [suspicious link removed]
XML: https://cloud.google.com/feeds/data-catalog-release-notes.xml

Database Migration Service
HTML: https://cloud.google.com/database-migration/docs/release-notes
XML: https://cloud.google.com/feeds/database-migration-service-release-notes.xml

Dataflow
HTML: https://cloud.google.com/dataflow/docs/release-notes
XML: https://cloud.google.com/feeds/dataflow-release-notes.xml

Dataproc
HTML: https://cloud.google.com/dataproc/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-dataproc-release-notes.xml

Datastore
HTML: https://cloud.google.com/datastore/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-datastore-release-notes.xml

Memorystore for Memcached
HTML: https://cloud.google.com/memorystore/docs/memcached/release-notes
XML: https://cloud.google.com/feeds/memorystore-memcached-release-notes.xml

Memorystore for Redis
HTML: https://cloud.google.com/memorystore/docs/redis/release-notes
XML: https://cloud.google.com/feeds/memorystore-redis-release-notes.xml

Security & Identity

Binary Authorization
HTML: https://cloud.google.com/binary-authorization/docs/release-notes
XML: https://cloud.google.com/feeds/binary-authorization-release-notes.xml

Certificate Authority Service
HTML: https://cloud.google.com/certificate-authority-service/docs/release-notes
XML: https://cloud.google.com/feeds/certificate-authority-service-release-notes.xml

Cloud Armor
HTML: https://cloud.google.com/armor/docs/release-notes
XML: https://cloud.google.com/feeds/google-cloud-armor-release-notes.xml

Cloud KMS
HTML: https://cloud.google.com/kms/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-kms-release-notes.xml

IAM
HTML: https://cloud.google.com/iam/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-iam-release-notes.xml

Identity Platform
HTML: https://cloud.google.com/identity-platform/docs/release-notes
XML: https://cloud.google.com/feeds/identityplatform-release-notes.xml

reCAPTCHA Enterprise

HTML: https://cloud.google.com/recaptcha-enterprise/docs/release-notes
XML: https://cloud.google.com/feeds/recaptcha-enterprise-release-notes.xml

Secret Manager
HTML: https://cloud.google.com/secret-manager/docs/release-notes
XML: https://cloud.google.com/feeds/secret-manager-release-notes.xml

Security Command Center
HTML: https://cloud.google.com/security-command-center/docs/release-notes
XML: https://cloud.google.com/feeds/scc-release-notes.xml

VPC Service Controls

HTML: https://cloud.google.com/vpc-service-controls/docs/release-notes
XML: https://cloud.google.com/feeds/vpc-service-controls-release-notes.xml

Networking

Cloud CDN
HTML: https://cloud.google.com/cdn/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-cdn-release-notes.xml

Cloud DNS
HTML: https://cloud.google.com/dns/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-dns-release-notes.xml

Cloud Interconnect
HTML: https://cloud.google.com/network-connectivity/docs/interconnect/release-notes
XML: https://cloud.google.com/feeds/cloud-interconnect-release-notes.xml

Cloud Load Balancing
HTML: https://cloud.google.com/load-balancing/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-load-balancing-release-notes.xml

Cloud NAT
HTML: https://cloud.google.com/nat/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-nat-release-notes.xml

Cloud Router
HTML: https://cloud.google.com/router/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-router-release-notes.xml

Cloud Service Mesh
HTML: https://cloud.google.com/service-mesh/docs/release-notes
XML: https://cloud.google.com/feeds/servicemesh-release-notes.xml

Cloud Virtual Private Cloud
HTML: https://cloud.google.com/vpc/docs/release-notes
XML: https://cloud.google.com/feeds/vpc-release-notes.xml

Network Intelligence Center
HTML: https://cloud.google.com/network-intelligence-center/docs/release-notes
XML: https://cloud.google.com/feeds/networkintelligence-release-notes.xml

Network Service Tiers
HTML: https://cloud.google.com/network-tiers/docs/release-notes
XML: https://cloud.google.com/feeds/network-tiers-release-notes.xml

Service Directory
HTML: https://cloud.google.com/service-directory/docs/release-notes
XML: https://cloud.google.com/feeds/servicedirectory-release-notes.xml

Storage
Artifact Registry
HTML: https://cloud.google.com/artifact-registry/docs/release-notes
XML: https://cloud.google.com/feeds/artifactregistry-release-notes.xml

Cloud Storage
HTML: https://cloud.google.com/storage/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-storage-release-notes.xml

Container Registry
HTML: https://cloud.google.com/container-registry/docs/release-notes
XML: https://cloud.google.com/feeds/container-registry-release-notes.xml

Filestore
HTML: https://cloud.google.com/filestore/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-filestore-release-notes.xml

Managed Lustre
HTML: https://cloud.google.com/managed-lustre/docs/release-notes
XML: https://cloud.google.com/feeds/parallelstore-release-notes.xml

Transfer Appliance
HTML: https://cloud.google.com/transfer-appliance/docs/release-notes
XML: https://cloud.google.com/feeds/transfer-appliance-release-notes.xml

Compute / Infrastructure

Bare Metal Solution
HTML: https://cloud.google.com/bare-metal/docs/release-notes
XML: https://cloud.google.com/feeds/bare-metal-solution-release-notes.xml

Cloud Hub
HTML: https://cloud.google.com/hub/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-hub-release-notes.xml

Cloud TPU
HTML: https://cloud.google.com/tpu/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-tpu-release-notes.xml

Compute Engine
HTML: https://cloud.google.com/compute/docs/release-notes
XML: https://cloud.google.com/feeds/compute-engine-release-notes.xml

Confidential Space
HTML: https://cloud.google.com/confidential-computing/confidential-space/docs/release-notes
XML: https://cloud.google.com/feeds/confidential-space-release-notes.xml

Google Distributed Cloud Connected
HTML: https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes
XML: https://cloud.google.com/feeds/distributed-cloud-edge-release-notes.xml

Google Distributed Cloud Edge
HTML: https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes
XML: https://cloud.google.com/feeds/distributed-cloud-edge-release-notes.xml

Google Distributed Cloud Bare Metal

HTML: https://cloud.google.com/kubernetes-engine/distributed-cloud/bare-metal/docs/release-notes
XML: https://cloud.google.com/feeds/anthos-clusters-bare-metal-release-notes.xml

HTML: https://cloud.google.com/kubernetes-engine/distributed-cloud/vmware/docs/release-notes
XML: https://cloud.google.com/feeds/anthos-clusters-vmware-release-notes.xml

VMware Engine
HTML: https://cloud.google.com/vmware-engine/docs/release-notes
XML: https://cloud.google.com/feeds/vmware-engine-release-notes.xml

Google Kubernetes Engine (GKE)

Main GKE Notes
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes
XML: https://cloud.google.com/feeds/kubernetes-engine-release-notes.xml

GKE Rapid
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid
XML: https://cloud.google.com/feeds/kubernetes-engine-rapid-channel-release-notes.xml

GKE Regular
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes-regular
XML: https://cloud.google.com/feeds/kubernetes-engine-regular-channel-release-notes.xml

GKE Stable
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes-stable
XML: https://cloud.google.com/feeds/kubernetes-engine-stable-channel-release-notes.xml

GKE Extended
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes-extended
XML: https://cloud.google.com/feeds/kubernetes-engine-extended-channel-release-notes.xml

GKE Nochannel
HTML: https://cloud.google.com/kubernetes-engine/docs/release-notes-nochannel
XML: https://cloud.google.com/feeds/kubernetes-engine-no-channel-release-notes.xml

Management & Operations

Cloud Logging
HTML: https://cloud.google.com/logging/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-logging-release-notes.xml

Cloud Monitoring
HTML: https://cloud.google.com/monitoring/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-monitoring-release-notes.xml

Cloud Observability
HTML: https://cloud.google.com/stackdriver/docs/release-notes
XML: https://cloud.google.com/feeds/stackdriver-release-notes.xml

Cloud Profiler
HTML: https://cloud.google.com/profiler/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-profiler-release-notes.xml

Cloud Scheduler
HTML: https://cloud.google.com/scheduler/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-scheduler-release-notes.xml

Config Connector
HTML: https://cloud.google.com/config-connector/docs/release-notes
XML: https://cloud.google.com/feeds/config-connector-release-notes.xml

Resource Manager
HTML: https://cloud.google.com/resource-manager/docs/release-notes
XML: https://cloud.google.com/feeds/resource-manager-release-notes.xml

AI & Machine Learning
Antigravity (Preview)

HTML: https://antigravity.google/
XML: No Official Feed

HTML: https://cloud.google.com/generative-ai-app-builder/docs/release-notes
XML: https://cloud.google.com/feeds/generative-ai-app-builder-release-notes.xml

Dialogflow
HTML: https://cloud.google.com/dialogflow/docs/release-notes
XML: https://cloud.google.com/feeds/dialogflow-release-notes.xml

Document AI
HTML: https://cloud.google.com/document-ai/docs/release-notes
XML: https://cloud.google.com/feeds/document-ai-release-notes.xml

Gemini Code Assist
HTML: https://cloud.google.com/gemini/docs/codeassist/release-notes
XML: https://cloud.google.com/feeds/gemini-code-assist-release-notes.xml

Speech-to-Text
HTML: https://cloud.google.com/speech-to-text/docs/release-notes
XML: https://cloud.google.com/feeds/speech-to-text-release-notes.xml

Talent Solution
HTML: https://cloud.google.com/talent-solution/docs/release-notes
XML: https://cloud.google.com/feeds/talent-solution-release-notes.xml

Text-to-Speech
HTML: https://cloud.google.com/text-to-speech/docs/release-notes
XML: https://cloud.google.com/feeds/text-to-speech-release-notes.xml

Translation
HTML: https://cloud.google.com/translate/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-translation-release-notes.xml

Vertex AI
HTML: https://cloud.google.com/vertex-ai/docs/release-notes
XML: https://cloud.google.com/feeds/vertex-ai-release-notes.xml

Video Intelligence API
HTML: https://cloud.google.com/video-intelligence/docs/release-notes
XML: https://cloud.google.com/feeds/video-intelligence-release-notes.xml

Specialized & Other Services

Cloud Composer
HTML: https://cloud.google.com/composer/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-composer-release-notes.xml

Healthcare API
HTML: https://cloud.google.com/healthcare/docs/release-notes
XML: https://cloud.google.com/feeds/healthcare-api-release-notes.xml

Web3
Blockchain Node Engine
HTML: https://cloud.google.com/blockchain-node-engine/docs/release-notes
XML: https://cloud.google.com/feeds/blockchain-node-engine-release-notes.xml

Workspace

Apps Script
HTML: https://developers.google.com/apps-script/release-notes
XML: https://developers.google.com/feeds/apps-script-release-notes.xml

Google Cloud Search API
HTML: https://developers.google.com/workspace/cloud-search/release-notes
XML: https://developers.google.com/feeds/cloud-search-release-notes.xml

Google Docs API
HTML: https://developers.google.com/workspace/docs/release-notes
XML: https://developers.google.com/feeds/docs-release-notes.xml

Unsupported / Experimental / Firebase
Cloud SDK
HTML: https://cloud.google.com/sdk/docs/release-notes
XML: https://cloud.google.com/feeds/cloud-sdk-release-notes.xml

Gemini CLI
HTML: https://github.com/google-gemini/gemini-cli/releases
XML: https://github.com/google-gemini/gemini-cli/releases.atom

Gemini API
HTML: https://ai.google.dev/gemini-api/docs/changelog
XML: https://ai.google.dev/gemini-api/docs/changelog.xml

Firebase (General)
HTML: https://firebase.google.com/support/releases
XML: No Official Feed

Firebase (iOS)
HTML: https://firebase.google.com/support/release-notes/ios
XML: https://github.com/firebase/firebase-ios-sdk/releases.atom

Firebase (Android)
HTML: https://firebase.google.com/support/release-notes/android
XML: https://github.com/firebase/firebase-android-sdk/releases.atom

Firebase (JS)
HTML: https://firebase.google.com/support/release-notes/js
XML: https://github.com/firebase/firebase-js-sdk/releases.atom

Firebase (Flutter)
HTML: https://firebase.google.com/support/release-notes/flutter
XML: https://github.com/firebase/flutterfire/releases.atom

Firebase (C++)
HTML: https://firebase.google.com/support/release-notes/cpp-relnotes
XML: https://github.com/firebase/firebase-cpp-sdk/releases.atom

Firebase (Unity)
HTML: https://firebase.google.com/support/release-notes/unity
XML: https://github.com/firebase/firebase-unity-sdk/releases.atom
