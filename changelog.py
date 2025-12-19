#!/usr/bin/env python3
"""
Release Notes Scraper
Scrapes release notes from documentation pages or XML feeds and outputs in various formats.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
import json
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

# GCP Service Groups (domains)
SERVICE_GROUPS = {
    'apps': [
        'application-design-center', 'apphub', 'api-gateway', 'cloud-build', 'cloud-deploy',
        'cloud-functions', 'cloud-run', 'cloud-sdk', 'cloud-tasks', 'cloud-trace', 'deployment-manager',
        'endpoints', 'eventarc', 'source-repositories', 'workflows'
    ],
    'apigee': [
        'apigee'
    ],
    'databases': [
        'alloydb', 'bigquery', 'data-fusion', 'firestore', 'spanner', 'cloud-sql',
        'data-catalog', 'database-migration', 'dataflow', 'dataproc', 'datastore',
        'memorystore-memcached', 'memorystore-redis'
    ],
    'security': [
        'binary-authorization', 'certificate-authority', 'cloud-armor', 'cloud-kms',
        'iam', 'identity-platform', 'recaptcha', 'secret-manager',
        'security-command-center', 'vpc-service-controls'
    ],
    'networking': [
        'cloud-cdn', 'cloud-dns', 'cloud-interconnect', 'load-balancing', 'cloud-nat',
        'cloud-router', 'service-mesh', 'vpc', 'network-intelligence', 'network-tiers',
        'service-directory'
    ],
    'storage': [
        'artifact-registry', 'cloud-storage', 'container-registry', 'filestore',
        'managed-lustre', 'transfer-appliance'
    ],
    'compute': [
        'bare-metal', 'cloud-hub', 'cloud-tpu', 'compute-engine', 'confidential-space',
        'distributed-cloud-edge', 'anthos-bare-metal', 'anthos-vmware', 'vmware-engine',
        'workstations'
    ],
    'gke': [
        'gke', 'gke-rapid', 'gke-regular', 'gke-stable', 'gke-extended', 'gke-nochannel'
    ],
    'operations': [
        'cloud-logging', 'cloud-monitoring', 'cloud-observability', 'cloud-profiler',
        'cloud-scheduler', 'config-connector', 'resource-manager'
    ],
    'ai': [
        'ai-app-builder', 'antigravity', 'dialogflow', 'document-ai', 'gemini-cli', 'gemini-code-assist',
        'speech-to-text', 'talent-solution', 'text-to-speech', 'translation',
        'vertex-ai', 'video-intelligence'
    ],
    'specialized': [
        'cloud-composer', 'healthcare-api', 'blockchain-node-engine'
    ],
    'workspace': [
        'apps-script', 'cloud-search', 'docs-api', 'workspace-blog'
    ],
    'firebase': [
        'firebase', 'firebase-android', 'firebase-ios', 'firebase-js', 'firebase-admin',
        'firebase-cpp', 'firebase-unity', 'firebase-flutter', 'firestore', 'firebase-extensions'
    ],
}

# GCP Service XML Feed URLs
SERVICE_FEEDS = {
    # Applications & Development
    'application-design-center': 'https://cloud.google.com/application-design-center/docs/release-notes',
    'apphub': 'https://cloud.google.com/feeds/apphub-release-notes.xml',
    'api-gateway': 'https://cloud.google.com/feeds/api-gateway-release-notes.xml',
    'apigee': 'https://cloud.google.com/feeds/apigee-release-notes.xml',
    'cloud-build': 'https://cloud.google.com/feeds/cloud-build-release-notes.xml',
    'cloud-deploy': 'https://cloud.google.com/feeds/deploy-release-notes.xml',
    'cloud-functions': 'https://cloud.google.com/feeds/cloud-functions-release-notes.xml',
    'cloud-run': 'https://cloud.google.com/feeds/cloud-run-release-notes.xml',
    'cloud-sdk': 'https://cloud.google.com/sdk/docs/release-notes',
    'cloud-tasks': 'https://cloud.google.com/feeds/cloud-tasks-release-notes.xml',
    'cloud-trace': 'https://cloud.google.com/feeds/cloud-trace-release-notes.xml',
    'deployment-manager': 'https://cloud.google.com/feeds/deployment-manager-release-notes.xml',
    'endpoints': 'https://cloud.google.com/feeds/endpoints-release-notes.xml',
    'eventarc': 'https://cloud.google.com/feeds/eventarc-release-notes.xml',
    'source-repositories': 'https://cloud.google.com/feeds/source-repositories-release-notes.xml',
    'workflows': 'https://cloud.google.com/feeds/workflows-release-notes.xml',
    'workstations': 'https://cloud.google.com/feeds/workstations-release-notes.xml',
    
    # Databases & Data Analytics
    'alloydb': 'https://cloud.google.com/feeds/alloydb-release-notes.xml',
    'bigquery': 'https://cloud.google.com/feeds/bigquery-release-notes.xml',
    'data-fusion': 'https://cloud.google.com/feeds/cloud-data-fusion-release-notes.xml',
    'firestore': 'https://cloud.google.com/feeds/cloud-firestore-release-notes.xml',
    'spanner': 'https://cloud.google.com/feeds/cloud-spanner-release-notes.xml',
    'cloud-sql': 'https://cloud.google.com/feeds/cloud-sql-release-notes.xml',
    'data-catalog': 'https://cloud.google.com/feeds/data-catalog-release-notes.xml',
    'database-migration': 'https://cloud.google.com/feeds/database-migration-service-release-notes.xml',
    'dataflow': 'https://cloud.google.com/feeds/dataflow-release-notes.xml',
    'dataproc': 'https://cloud.google.com/feeds/cloud-dataproc-release-notes.xml',
    'datastore': 'https://cloud.google.com/feeds/cloud-datastore-release-notes.xml',
    'memorystore-memcached': 'https://cloud.google.com/feeds/memorystore-memcached-release-notes.xml',
    'memorystore-redis': 'https://cloud.google.com/feeds/memorystore-redis-release-notes.xml',
    
    # Security & Identity
    'binary-authorization': 'https://cloud.google.com/feeds/binary-authorization-release-notes.xml',
    'certificate-authority': 'https://cloud.google.com/feeds/certificate-authority-service-release-notes.xml',
    'cloud-armor': 'https://cloud.google.com/feeds/google-cloud-armor-release-notes.xml',
    'cloud-kms': 'https://cloud.google.com/feeds/cloud-kms-release-notes.xml',
    'iam': 'https://cloud.google.com/feeds/cloud-iam-release-notes.xml',
    'identity-platform': 'https://cloud.google.com/feeds/identityplatform-release-notes.xml',
    'recaptcha': 'https://cloud.google.com/feeds/recaptcha-enterprise-release-notes.xml',
    'secret-manager': 'https://cloud.google.com/feeds/secret-manager-release-notes.xml',
    'security-command-center': 'https://cloud.google.com/feeds/scc-release-notes.xml',
    'vpc-service-controls': 'https://cloud.google.com/feeds/vpc-service-controls-release-notes.xml',
    
    # Networking
    'cloud-cdn': 'https://cloud.google.com/feeds/cloud-cdn-release-notes.xml',
    'cloud-dns': 'https://cloud.google.com/feeds/cloud-dns-release-notes.xml',
    'cloud-interconnect': 'https://cloud.google.com/feeds/cloud-interconnect-release-notes.xml',
    'load-balancing': 'https://cloud.google.com/feeds/cloud-load-balancing-release-notes.xml',
    'cloud-nat': 'https://cloud.google.com/feeds/cloud-nat-release-notes.xml',
    'cloud-router': 'https://cloud.google.com/feeds/cloud-router-release-notes.xml',
    'service-mesh': 'https://cloud.google.com/feeds/servicemesh-release-notes.xml',
    'vpc': 'https://cloud.google.com/feeds/vpc-release-notes.xml',
    'network-intelligence': 'https://cloud.google.com/feeds/networkintelligence-release-notes.xml',
    'network-tiers': 'https://cloud.google.com/feeds/network-tiers-release-notes.xml',
    'service-directory': 'https://cloud.google.com/feeds/servicedirectory-release-notes.xml',
    
    # Storage
    'artifact-registry': 'https://cloud.google.com/feeds/artifactregistry-release-notes.xml',
    'cloud-storage': 'https://cloud.google.com/feeds/cloud-storage-release-notes.xml',
    'container-registry': 'https://cloud.google.com/feeds/container-registry-release-notes.xml',
    'filestore': 'https://cloud.google.com/feeds/cloud-filestore-release-notes.xml',
    'managed-lustre': 'https://cloud.google.com/feeds/parallelstore-release-notes.xml',
    'transfer-appliance': 'https://cloud.google.com/feeds/transfer-appliance-release-notes.xml',
    
    # Compute / Infrastructure
    'bare-metal': 'https://cloud.google.com/feeds/bare-metal-solution-release-notes.xml',
    'cloud-hub': 'https://cloud.google.com/feeds/cloud-hub-release-notes.xml',
    'cloud-tpu': 'https://cloud.google.com/feeds/cloud-tpu-release-notes.xml',
    'compute-engine': 'https://cloud.google.com/feeds/compute-engine-release-notes.xml',
    'confidential-space': 'https://cloud.google.com/feeds/confidential-space-release-notes.xml',
    'distributed-cloud-edge': 'https://cloud.google.com/feeds/distributed-cloud-edge-release-notes.xml',
    'anthos-bare-metal': 'https://cloud.google.com/feeds/anthos-clusters-bare-metal-release-notes.xml',
    'anthos-vmware': 'https://cloud.google.com/feeds/anthos-clusters-vmware-release-notes.xml',
    'vmware-engine': 'https://cloud.google.com/feeds/vmware-engine-release-notes.xml',
    
    # GKE
    'gke': 'https://cloud.google.com/feeds/kubernetes-engine-release-notes.xml',
    'gke-rapid': 'https://cloud.google.com/feeds/kubernetes-engine-rapid-channel-release-notes.xml',
    'gke-regular': 'https://cloud.google.com/feeds/kubernetes-engine-regular-channel-release-notes.xml',
    'gke-stable': 'https://cloud.google.com/feeds/kubernetes-engine-stable-channel-release-notes.xml',
    'gke-extended': 'https://cloud.google.com/feeds/kubernetes-engine-extended-channel-release-notes.xml',
    'gke-nochannel': 'https://cloud.google.com/feeds/kubernetes-engine-no-channel-release-notes.xml',
    
    # Management & Operations
    'cloud-logging': 'https://cloud.google.com/feeds/cloud-logging-release-notes.xml',
    'cloud-monitoring': 'https://cloud.google.com/feeds/cloud-monitoring-release-notes.xml',
    'cloud-observability': 'https://cloud.google.com/feeds/stackdriver-release-notes.xml',
    'cloud-profiler': 'https://cloud.google.com/feeds/cloud-profiler-release-notes.xml',
    'cloud-scheduler': 'https://cloud.google.com/feeds/cloud-scheduler-release-notes.xml',
    'config-connector': 'https://cloud.google.com/feeds/config-connector-release-notes.xml',
    'resource-manager': 'https://cloud.google.com/feeds/resource-manager-release-notes.xml',
    
    # AI & Machine Learning
    'ai-app-builder': 'https://cloud.google.com/feeds/generative-ai-app-builder-release-notes.xml',
    'antigravity': 'https://antigravity.google/changelog',  # No XML feed, uses HTML
    'dialogflow': 'https://cloud.google.com/feeds/dialogflow-release-notes.xml',
    'document-ai': 'https://cloud.google.com/feeds/document-ai-release-notes.xml',
    'gemini-cli': 'https://github.com/google-gemini/gemini-cli/releases.atom',
    'gemini-code-assist': 'https://cloud.google.com/feeds/gemini-code-assist-release-notes.xml',
    'speech-to-text': 'https://cloud.google.com/feeds/speech-to-text-release-notes.xml',
    'talent-solution': 'https://cloud.google.com/feeds/talent-solution-release-notes.xml',
    'text-to-speech': 'https://cloud.google.com/feeds/text-to-speech-release-notes.xml',
    'translation': 'https://cloud.google.com/feeds/cloud-translation-release-notes.xml',
    'vertex-ai': 'https://cloud.google.com/feeds/vertex-ai-release-notes.xml',
    'video-intelligence': 'https://cloud.google.com/feeds/video-intelligence-release-notes.xml',
    
    # Specialized & Other Services
    'cloud-composer': 'https://cloud.google.com/feeds/cloud-composer-release-notes.xml',
    'healthcare-api': 'https://cloud.google.com/feeds/healthcare-api-release-notes.xml',
    'blockchain-node-engine': 'https://cloud.google.com/feeds/blockchain-node-engine-release-notes.xml',
    
    # Workspace
    'apps-script': 'https://developers.google.com/feeds/apps-script-release-notes.xml',
    'cloud-search': 'https://developers.google.com/feeds/cloud-search-release-notes.xml',
    'docs-api': 'https://developers.google.com/feeds/docs-release-notes.xml',
    'workspace-blog': 'http://feeds.feedburner.com/GoogleAppsUpdates',
    
    # Firebase
    'firebase': 'https://firebase.google.com/support/release-notes',
    'firebase-android': 'https://firebase.google.com/support/release-notes/android',
    'firebase-ios': 'https://firebase.google.com/support/release-notes/ios',
    'firebase-js': 'https://firebase.google.com/support/release-notes/js',
    'firebase-admin': 'https://firebase.google.com/support/release-notes/admin/node',
    'firebase-cpp': 'https://firebase.google.com/support/release-notes/cpp',
    'firebase-unity': 'https://firebase.google.com/support/release-notes/unity',
    'firebase-flutter': 'https://firebase.google.com/support/release-notes/flutter',
    'firebase-extensions': 'https://firebase.google.com/support/release-notes/extensions',
}

# Blog URLs for --blogs option
BLOG_URLS = {
    'app-dev': 'https://cloud.google.com/blog/products/application-development',
    'app-mod': 'https://cloud.google.com/blog/products/application-modernization',
    'infra': 'https://cloud.google.com/blog/products/infrastructure',
    'containers': 'https://cloud.google.com/blog/products/containers-kubernetes',
    'ai-ml': 'https://cloud.google.com/blog/products/ai-machine-learning',
    'dev-blog': 'https://developers.googleblog.com/',
    'medium-ml': 'https://medium.com/feed/google-cloud/tagged/machine-learning',
    'medium-k8s': 'https://medium.com/feed/google-cloud/tagged/kubernetes',
    'medium-appdev': 'https://medium.com/feed/google-cloud/tagged/gcp-app-dev',
}

# HTML fallback URLs for services without XML feeds or where XML feeds are broken
SERVICE_HTML_FALLBACKS = {
    'application-design-center': 'https://cloud.google.com/application-design-center/docs/release-notes',
    'api-gateway': 'https://cloud.google.com/api-gateway/docs/release-notes',
    'cloud-deploy': 'https://cloud.google.com/deploy/docs/release-notes',
    'cloud-sdk': 'https://cloud.google.com/sdk/docs/release-notes',
    'antigravity': 'https://antigravity.google/changelog',
    # AI & Machine Learning fallbacks
    'ai-app-builder': 'https://cloud.google.com/generative-ai-app-builder/docs/release-notes',
    'dialogflow': 'https://cloud.google.com/dialogflow/docs/release-notes',
    'document-ai': 'https://cloud.google.com/document-ai/docs/release-notes',
    'gemini-code-assist': 'https://cloud.google.com/gemini/docs/codeassist/release-notes',
    'speech-to-text': 'https://cloud.google.com/speech-to-text/docs/release-notes',
    'talent-solution': 'https://cloud.google.com/talent-solution/docs/release-notes',
    'text-to-speech': 'https://cloud.google.com/text-to-speech/docs/release-notes',
    'translation': 'https://cloud.google.com/translate/docs/release-notes',
    'vertex-ai': 'https://cloud.google.com/vertex-ai/docs/release-notes',
    'video-intelligence': 'https://cloud.google.com/video-intelligence/docs/release-notes',
    # Compute / Infrastructure fallbacks
    'bare-metal': 'https://cloud.google.com/bare-metal/docs/release-notes',
    'cloud-hub': 'https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes',
    'anthos-bare-metal': 'https://cloud.google.com/anthos/clusters/docs/bare-metal/latest/release-notes',
    'anthos-vmware': 'https://cloud.google.com/anthos/clusters/docs/on-prem/latest/release-notes',
    # Networking fallbacks
    'cloud-nat': 'https://cloud.google.com/nat/docs/release-notes',
    'network-tiers': 'https://cloud.google.com/network-tiers/docs/release-notes',
    # Database fallbacks
    'database-migration': 'https://cloud.google.com/database-migration/docs/release-notes',
    'memorystore-memcached': 'https://cloud.google.com/memorystore/docs/memcached/release-notes',
    'memorystore-redis': 'https://cloud.google.com/memorystore/docs/redis/release-notes',
    # Specialized & Other Services fallbacks
    'healthcare-api': 'https://cloud.google.com/healthcare-api/docs/release-notes',
    'blockchain-node-engine': 'https://cloud.google.com/blockchain-node-engine/docs/release-notes',
}

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_packages = []
    
    try:
        import requests
    except ImportError:
        missing_packages.append('requests')
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_packages.append('beautifulsoup4')
    
    if missing_packages:
        print("Error: Required packages not installed.", file=sys.stderr)
        print(f"Missing packages: {', '.join(missing_packages)}", file=sys.stderr)
        print("Please install using uv:", file=sys.stderr)
        print(f"  uv pip install {' '.join(missing_packages)}", file=sys.stderr)
        print("\nOr install all requirements:", file=sys.stderr)
        print("  uv pip install -r requirements.txt", file=sys.stderr)
        print("\nIf you're using a virtual environment, make sure it's activated.", file=sys.stderr)
        sys.exit(1)
    
    return True

# Valid categories for filtering
VALID_CATEGORIES = [
    'ga',
    'public-preview',
    'breaking',
    'security',
    'deprecated',
    'fixed',
    'issue',
    'change',
    'announcement',
    'libraries',
    'update',
]

class ReleaseNotesScraper:
    """Scraper for release notes from various documentation sites or XML feeds."""
    
    # Common selectors for different documentation platforms
    PLATFORM_SELECTORS = {
        'google_cloud': {
            'container': ['main', 'article', '[role="main"]', '.devsite-article-body', 'div.release-notes-container'],
            'date_headers': ['h2', 'h3'],
            'content': ['p', 'ul', 'ol', 'div'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2024
                r'(\d{4}-\d{2}-\d{2})',       # 2024-01-15
                r'(\d{1,2}/\d{1,2}/\d{4})',    # 01/15/2024
            ]
        },
        'firebase': {
            'container': ['main', 'article', '.devsite-article-body', '[role="main"]'],
            'date_headers': ['h2', 'h3', 'h4'],
            'content': ['p', 'ul', 'ol', 'li', 'div'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2024
                r'(\d{4}-\d{2}-\d{2})',       # 2024-01-15
            ]
        },
        'antigravity': {
            'container': ['main', 'article', '.changelog', '[role="main"]', 'body'],
            'date_headers': ['h2', 'h3', 'h4', 'time'],
            'content': ['p', 'ul', 'ol', 'li', 'div', 'section'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2024
                r'(\d{4}-\d{2}-\d{2})',       # 2024-01-15
                r'(\d{1,2}\s+\w+\s+\d{4})',   # 15 January 2024
            ]
        },
        'generic': {
            'container': ['main', 'article', '.content', '#content', '.release-notes'],
            'date_headers': ['h2', 'h3', 'h4'],
            'content': ['p', 'ul', 'li', 'div'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ]
        }
    }
    
    def __init__(self, url: str, months: int = None, days: int = None, start_date: datetime = None, end_date: datetime = None, categories: List[str] = None, service_name: str = None, verbose: bool = False):
        """Initialize the scraper with URL and time range."""
        # Import here after dependency check
        import requests
        from bs4 import BeautifulSoup
        
        self.requests = requests
        self.BeautifulSoup = BeautifulSoup
        
        self.url = url
        self.months = months
        self.days = days
        self.start_date = start_date
        self.end_date = end_date or datetime.now()
        self.categories = [c.lower() for c in categories] if categories else None
        self.service_name = service_name
        self.verbose = verbose
        
        # Calculate cutoff date based on days, months, or start_date
        if start_date:
            self.cutoff_date = start_date
        elif days:
            # Use start of day N days ago (midnight) for more intuitive behavior
            # e.g., "-d 2" includes all of today, yesterday, and the day before
            cutoff = datetime.now() - timedelta(days=days)
            self.cutoff_date = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        elif months:
            cutoff = datetime.now() - timedelta(days=months * 30)
            self.cutoff_date = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to 12 months
            self.months = 12
            cutoff = datetime.now() - timedelta(days=12 * 30)
            self.cutoff_date = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.releases = []
        self.platform = self._detect_platform(url)
        self.is_xml_feed = self._is_xml_url(url)
        self.used_fallback = False
        
    def _detect_platform(self, url: str) -> str:
        """Detect the documentation platform based on URL."""
        if 'cloud.google.com/blog' in url:
            return 'cloud_blog'
        if 'developers.googleblog.com' in url:
            return 'developers_blog'
        if 'medium.com/feed/' in url:
            return 'medium_feed'  # RSS feed - use XML parser
        if 'medium.com/google-cloud' in url:
            return 'medium_blog'  # HTML - requires Selenium
        if 'cloud.google.com' in url or 'developers.google.com' in url:
            return 'google_cloud'
        if 'firebase.google.com' in url:
            return 'firebase'
        if 'antigravity.google' in url:
            return 'antigravity'
        return 'generic'
    
    def _is_xml_url(self, url: str) -> bool:
        """Check if the URL is an XML feed."""
        # AntiGravity uses embedded JS data, not XML
        if 'antigravity.google' in url:
            return False
        # Medium RSS feeds use /feed/ path
        if 'medium.com/feed/' in url:
            return True
        # Feedburner feeds are XML/Atom
        if 'feeds.feedburner.com' in url or 'feedburner.google.com' in url:
            return True
        return url.endswith('.xml') or url.endswith('.atom') or '/feeds/' in url
    
    def _is_antigravity_url(self, url: str) -> bool:
        """Check if the URL is AntiGravity changelog."""
        return 'antigravity.google' in url
    
    def _is_blog_feed(self) -> bool:
        """Check if the current URL is a blog-style feed where we should only use titles.
        
        Blog feeds contain full article content in their RSS, but we only want
        to show the title and link, not the entire article text.
        """
        url = self.url
        # Medium RSS feeds
        if 'medium.com/feed/' in url:
            return True
        # Feedburner feeds (like workspace-blog)
        if 'feeds.feedburner.com' in url or 'feedburner.google.com' in url:
            return True
        return False
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats."""
        date_str = date_str.strip()
        
        # Try common date formats
        formats = [
            '%B %d, %Y',      # January 15, 2024
            '%b %d, %Y',      # Jan 15, 2024
            '%Y-%m-%d',       # 2024-01-15
            '%m/%d/%Y',       # 01/15/2024
            '%d/%m/%Y',       # 15/01/2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def _fetch_date_from_url(self, url: str) -> Optional[datetime]:
        """Fetch article page to extract date."""
        try:
            if self.verbose:
                print(f"    Fetching date from: {url}", file=sys.stderr)
            
            response = self.requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = self.BeautifulSoup(response.content, 'html.parser')
            
            # Developers Blog specific
            if 'developers.googleblog.com' in url:
                # Look for date-time class or published-date
                # Format: MAY 13, 2025
                for cls in ['date-time', 'published-date']:
                    elem = soup.find(class_=cls)
                    if elem:
                        date_str = elem.get_text(strip=True)
                        try:
                            # Handle "MAY 13, 2025" -> "May 13, 2025"
                            # .title() would make it "May 13, 2025"
                            return datetime.strptime(date_str.title(), '%B %d, %Y')
                        except ValueError:
                            pass
            
            # Generic / Cloud Blog
            # Look for meta tags
            for meta in soup.find_all('meta'):
                prop = meta.get('property', '')
                name = meta.get('name', '')
                content = meta.get('content')
                if content and ('published_time' in prop or 'published_time' in name or 'date' in prop or 'date' in name):
                    try:
                        # Try parsing ISO format
                        return datetime.fromisoformat(content.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                            
            return None
        except Exception:
            return None
    
    def _categorize_item(self, element=None, text: str = None) -> str:
        """Categorize a release note item based on its element class or content."""
        
        # First check if we have an element with specific classes
        if element:
            element_classes = element.get('class', [])
            class_str = ' '.join(element_classes) if element_classes else ''
            
            # Check for specific div classes
            if 'release-feature' in class_str:
                element_text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
                if '(Preview)' in element_text or '(preview)' in element_text:
                    return 'public-preview'
                else:
                    return 'ga'
            elif 'release-changed' in class_str:
                return 'change'
            elif 'release-announcement' in class_str:
                return 'announcement'
            elif 'release-breaking' in class_str: # New breaking change class
                return 'breaking'
            elif 'release-issue' in class_str:
                return 'issue'
        
        # If no element or no matching class, fall back to text analysis
        if not text and element and hasattr(element, 'get_text'):
            text = element.get_text(strip=True)
        
        if not text:
            return 'update'
        
        text_lower = text.lower()
        
        # Check for specific patterns (most specific to least specific)
        
        # Security takes highest priority
        if any(keyword in text_lower for keyword in ['security', 'vulnerability', 'cve', 'patch']):
            return 'security'
        
        # Breaking changes
        if any(keyword in text_lower for keyword in ['breaking change', 'breaking change:', 'migration required', 'major version update']):
            return 'breaking'
        
        # Check for preview indicators (but only if not already categorized by div class)
        if any(keyword in text_lower for keyword in ['(preview)', 'public preview', 'in preview', 'preview)', 'early access', 'beta']):
            return 'public-preview'
        
        # GA/Generally Available
        if any(keyword in text_lower for keyword in ['generally available', 'general availability', '(ga)', 'is now ga', 'is in ga', 'in general availability']):
            return 'ga'
        
        # Deprecated
        if any(keyword in text_lower for keyword in ['deprecated', 'deprecation', 'obsolete', 'removed', 'discontinued']):
            return 'deprecated'
        
        # Fixed/Bug fixes
        if any(keyword in text_lower for keyword in ['fixed', 'fix:', 'resolved', 'bug']):
            return 'fixed'
        
        # Issue
        if any(keyword in text_lower for keyword in ['issue', 'known issue', 'workaround']):
            return 'issue'
        
        # Change (significant changes)
        if any(keyword in text_lower for keyword in ['changed:', 'migration required', 'version updates']):
            return 'change'
        
        # Announcements
        if any(keyword in text_lower for keyword in ['announced', 'announcement', 'introducing']):
            return 'announcement'
        
        # Libraries/SDKs
        if any(keyword in text_lower for keyword in ['library', 'sdk', 'api', 'client library', 'framework']):
            return 'libraries'
        
        # Default to update for everything else
        return 'update'
    
    def scrape(self) -> List[Dict]:
        """Main scraping method with fallback support."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Try XML feed first
        if self.is_xml_feed:
            try:
                response = self.requests.get(self.url, headers=headers, timeout=30)
                response.raise_for_status()
                return self._parse_xml_feed(response.content)
            except self.requests.RequestException as e:
                # Check if it's a 404 error and we have a fallback
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                    fallback_url = self._get_fallback_url()
                    if fallback_url:
                        if self.verbose:
                            print(f"  XML feed not available, trying HTML fallback: {fallback_url}", file=sys.stderr)
                        return self._scrape_html(fallback_url, headers)
                    else:
                        print(f"Error fetching URL: {e}", file=sys.stderr)
                        return []
                else:
                    print(f"Error fetching URL: {e}", file=sys.stderr)
                    return []
            except Exception as e:
                print(f"Error parsing XML content: {e}", file=sys.stderr)
                return []
        
        # Check if it's AntiGravity - use special JS extraction method
        if self._is_antigravity_url(self.url):
            return self._scrape_antigravity_js(headers)
        
        # Blog scraping
        if self.platform == 'cloud_blog':
            return self._scrape_cloud_blog(headers)
        if self.platform == 'developers_blog':
            return self._scrape_developers_blog(headers)
        if self.platform == 'medium_blog':
            return self._scrape_medium_blog(headers)
        
        # Direct HTML scraping
        return self._scrape_html(self.url, headers)
    
    def _scrape_cloud_blog(self, headers: dict) -> List[Dict]:
        """Scrape Google Cloud Blog."""
        try:
            response = self.requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = self.BeautifulSoup(response.content, 'html.parser')
            
            releases = []
            
            # Method 1: Try to extract from AF_initDataCallback JSON
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'AF_initDataCallback' in script.string:
                    match = re.search(r'data:(\[.*\])\}\);', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            self._extract_articles_from_json(data, releases)
                        except Exception as e:
                            if self.verbose:
                                print(f"  JSON parsing error in Cloud Blog: {e}", file=sys.stderr)
            
            # Method 2: Fallback to HTML parsing
            if not releases:
                if self.verbose:
                    print("  Fallback to HTML parsing for Cloud Blog...", file=sys.stderr)
                
                # Look for article cards (c-wiz components usually rendered as divs with specific classes)
                # Based on analysis, class 'u2M0Kb' contains article cards
                cards = soup.find_all('div', class_='u2M0Kb')
                for card in cards:
                    title_elem = card.find('h5')
                    link_elem = card.find('a', class_='w7DBpd')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href')
                        if url and url.startswith('/'):
                            url = 'https://cloud.google.com' + url
                            
                        # Date is hard to extract from HTML reliably without JS rendering
                        # We'll use None or today's date if strict filtering is not needed
                        # For now, let's skip date filtering for fallback items if date is missing
                        releases.append({
                            'date': None,
                            'date_str': 'Recent',
                            'items': [{
                                'text': title,
                                'category': 'announcement',
                                'urls': [url]
                            }],
                            'url': self.url
                        })
            
            # Filter by date if we have dates
            filtered = []
            
            # Determine if we should be strict about missing dates
            strict_mode = self.days is not None or self.start_date is not None
            
            for release in releases:
                if release['date']:
                    if release['date'] >= self.cutoff_date:
                        if self.end_date is None or release['date'] <= self.end_date:
                            filtered.append(release)
                elif not strict_mode:
                    # Include undated items only if we are not in strict mode
                    filtered.append(release)
                elif self.verbose:
                    print(f"    Skipping undated item (strict mode): {release['items'][0]['text'][:50]}...", file=sys.stderr)
            
            return filtered
            
        except Exception as e:
            print(f"Error scraping Cloud Blog: {e}", file=sys.stderr)
            return []

    def _extract_articles_from_json(self, obj, releases):
        """Recursively find articles in Cloud Blog JSON structure."""
        if isinstance(obj, list):
            # Check if this list looks like an article entry
            # ["Category", "Title", null, [], null, 5, null, "URL", [1765846800], ...]
            if len(obj) > 8 and isinstance(obj[1], str) and isinstance(obj[7], str) and isinstance(obj[0], str):
                if obj[7].startswith('https://cloud.google.com/blog/'):
                    title = obj[1]
                    url = obj[7]
                    timestamp = None
                    if isinstance(obj[8], list) and len(obj[8]) > 0:
                        timestamp = obj[8][0]
                    
                    date = None
                    date_str = 'Recent'
                    if timestamp:
                        try:
                            # timestamp is in seconds
                            date = datetime.fromtimestamp(timestamp)
                            date_str = date.strftime('%B %d, %Y')
                        except ValueError:
                            pass
                    
                    releases.append({
                        'date': date,
                        'date_str': date_str,
                        'items': [{
                            'text': title,
                            'category': 'announcement',
                            'urls': [url]
                        }],
                        'url': self.url
                    })
            
            for item in obj:
                self._extract_articles_from_json(item, releases)

    def _parse_relative_date(self, relative_str: str) -> Optional[datetime]:
        """Parse relative date strings like '6d ago', '2h ago', 'Dec 10', etc."""
        relative_str = relative_str.strip().lower()
        now = datetime.now()
        
        # Handle "X ago" patterns
        ago_match = re.match(r'(\d+)\s*(d|h|m|min|hr|day|hour|minute|week|w)s?\s*ago', relative_str, re.IGNORECASE)
        if ago_match:
            value = int(ago_match.group(1))
            unit = ago_match.group(2).lower()
            
            if unit in ('d', 'day'):
                return now - timedelta(days=value)
            elif unit in ('h', 'hr', 'hour'):
                return now - timedelta(hours=value)
            elif unit in ('m', 'min', 'minute'):
                return now - timedelta(minutes=value)
            elif unit in ('w', 'week'):
                return now - timedelta(weeks=value)
        
        # Handle "just now" or "now"
        if 'just now' in relative_str or relative_str == 'now':
            return now
        
        # Handle "yesterday"
        if 'yesterday' in relative_str:
            return now - timedelta(days=1)
        
        # Handle absolute dates like "Dec 10" or "Dec 10, 2024"
        # Try formats with year first
        date_formats = [
            '%b %d, %Y',      # Dec 10, 2024
            '%B %d, %Y',      # December 10, 2024
            '%b %d %Y',       # Dec 10 2024
            '%B %d %Y',       # December 10 2024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(relative_str, fmt)
            except ValueError:
                continue
        
        # Handle dates without year (assume current year, or previous year if date is in future)
        date_formats_no_year = [
            '%b %d',          # Dec 10
            '%B %d',          # December 10
        ]
        
        for fmt in date_formats_no_year:
            try:
                parsed = datetime.strptime(relative_str, fmt)
                # Add current year
                parsed = parsed.replace(year=now.year)
                # If the date is in the future, it's probably from last year
                if parsed > now:
                    parsed = parsed.replace(year=now.year - 1)
                return parsed
            except ValueError:
                continue
        
        return None

    def _scrape_medium_blog(self, headers: dict) -> List[Dict]:
        """Scrape Medium Google Cloud blog posts using Selenium for JS rendering."""
        try:
            # Medium requires JavaScript rendering - use Selenium
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
            except ImportError:
                print("Error: Selenium is required for Medium blog scraping.", file=sys.stderr)
                print("Install it with: uv pip install selenium", file=sys.stderr)
                return []
            
            if self.verbose:
                print(f"  Using Selenium for Medium blog: {self.url}", file=sys.stderr)
            
            # Set up headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(self.url)
                
                # Wait for content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                
                # Give extra time for dynamic content
                import time
                time.sleep(2)
                
                # Get page source after JS rendering
                page_source = driver.page_source
            finally:
                driver.quit()
            
            soup = self.BeautifulSoup(page_source, 'html.parser')
            
            releases = []
            
            if self.verbose:
                print(f"  Scraping Medium blog: {self.url}", file=sys.stderr)
            
            # Medium articles are typically in article tags or divs with specific data attributes
            # Look for article cards - Medium uses various structures
            
            # Method 1: Look for article elements
            articles = soup.find_all('article')
            
            for article in articles:
                # Find title - usually in h2 or h3 within the article
                title_elem = article.find(['h2', 'h3', 'h1'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                # Find link
                link_elem = article.find('a', href=True)
                link = ''
                if link_elem:
                    href = link_elem.get('href', '')
                    if href.startswith('/'):
                        link = 'https://medium.com' + href
                    elif href.startswith('http'):
                        link = href
                    else:
                        link = 'https://medium.com/google-cloud/' + href
                
                # Find date - Medium shows relative dates like "6d ago", "Dec 10", etc.
                date = None
                date_str = 'Recent'
                
                # Look for time elements or spans with date-like text
                time_elem = article.find('time')
                if time_elem:
                    date_text = time_elem.get('datetime') or time_elem.get_text(strip=True)
                    if date_text:
                        # Try ISO format first
                        try:
                            date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                            if date.tzinfo:
                                date = date.replace(tzinfo=None)
                            date_str = date.strftime('%B %d, %Y')
                        except ValueError:
                            # Try relative date parsing
                            date = self._parse_relative_date(date_text)
                            if date:
                                date_str = date.strftime('%B %d, %Y')
                
                # If no time element, look for text patterns in spans
                if not date:
                    for span in article.find_all('span'):
                        span_text = span.get_text(strip=True)
                        # Look for patterns like "6d ago", "Dec 10", "2h ago"
                        if re.match(r'^\d+[dhm]\s*ago$', span_text, re.IGNORECASE) or \
                           re.match(r'^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+', span_text, re.IGNORECASE) or \
                           'ago' in span_text.lower():
                            date = self._parse_relative_date(span_text)
                            if date:
                                date_str = date.strftime('%B %d, %Y')
                                break
                
                # If still no date, look in the article text for date patterns
                if not date:
                    article_text = article.get_text()
                    # Look for relative date patterns
                    relative_match = re.search(r'(\d+[dhm]\s*ago|\d+\s*(?:day|hour|minute|week)s?\s*ago)', article_text, re.IGNORECASE)
                    if relative_match:
                        date = self._parse_relative_date(relative_match.group(1))
                        if date:
                            date_str = date.strftime('%B %d, %Y')
                    else:
                        # Look for date like "Dec 10"
                        date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,?\s+\d{4})?)', article_text, re.IGNORECASE)
                        if date_match:
                            date = self._parse_relative_date(date_match.group(1))
                            if date:
                                date_str = date.strftime('%B %d, %Y')
                
                releases.append({
                    'date': date,
                    'date_str': date_str,
                    'items': [{
                        'text': title,
                        'category': 'announcement',
                        'urls': [link] if link else []
                    }],
                    'url': self.url
                })
            
            # Method 2: If no articles found, try looking for div-based cards
            if not releases:
                if self.verbose:
                    print("  Trying alternative Medium parsing...", file=sys.stderr)
                
                # Look for links that look like article links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    # Medium article links typically have a specific pattern
                    if '/google-cloud/' in href and not href.endswith('/all') and '?' not in href:
                        title_elem = link.find(['h2', 'h3', 'h1', 'p'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title and len(title) > 15:
                                full_url = href if href.startswith('http') else 'https://medium.com' + href
                                
                                # Check for duplicates
                                is_duplicate = any(
                                    r['items'][0]['text'] == title for r in releases
                                )
                                if not is_duplicate:
                                    releases.append({
                                        'date': None,
                                        'date_str': 'Recent',
                                        'items': [{
                                            'text': title,
                                            'category': 'announcement',
                                            'urls': [full_url]
                                        }],
                                        'url': self.url
                                    })
            
            if self.verbose:
                print(f"  Found {len(releases)} articles from Medium", file=sys.stderr)
            
            # Filter by date
            filtered = []
            strict_mode = self.days is not None or self.start_date is not None
            
            for release in releases:
                if release['date']:
                    if release['date'] >= self.cutoff_date:
                        if self.end_date is None or release['date'] <= self.end_date:
                            filtered.append(release)
                elif not strict_mode:
                    filtered.append(release)
                elif self.verbose:
                    print(f"    Skipping undated item (strict mode): {release['items'][0]['text'][:50]}...", file=sys.stderr)
            
            return filtered
            
        except Exception as e:
            print(f"Error scraping Medium blog: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return []

    def _scrape_developers_blog(self, headers: dict) -> List[Dict]:
        """Scrape Google Developers Blog."""
        try:
            response = self.requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = self.BeautifulSoup(response.content, 'html.parser')
            
            releases = []
            
            # Look for post-item (Latest blogs list) - these have dates
            posts = soup.find_all('div', class_='post-item')
            for post in posts:
                link_elem = post.find('a', class_='post-item__link')
                date_elem = post.find('div', class_='post-item__top')
                
                if link_elem:
                    title_elem = link_elem.find(class_='glue-headline')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href')
                        if link.startswith('/'):
                            link = 'https://developers.googleblog.com' + link
                        
                        date = None
                        date_str = 'Recent'
                        if date_elem:
                            raw_date = date_elem.get_text(strip=True)
                            try:
                                # Format: DEC. 16, 2025
                                clean_date = raw_date.replace('.', '')
                                date = datetime.strptime(clean_date, '%b %d, %Y')
                                date_str = date.strftime('%B %d, %Y')
                            except ValueError:
                                date_str = raw_date
                        
                        releases.append({
                            'date': date,
                            'date_str': date_str,
                            'items': [{
                                'text': title,
                                'category': 'announcement',
                                'urls': [link]
                            }],
                            'url': self.url
                        })
            
            # Look for glue-card items (Carousel/Featured) - usually no date visible on home
            cards = soup.find_all('a', class_='glue-card')
            for card in cards:
                title_elem = card.find(class_='post-title')
                if not title_elem:
                    # Try finding headline if post-title not found
                    title_elem = card.find(class_='glue-headline')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = card.get('href')
                    if link.startswith('/'):
                        link = 'https://developers.googleblog.com' + link
                    
                    # Check for duplicates
                    is_duplicate = False
                    for r in releases:
                        if r['items'][0]['text'] == title:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        # Fetch date from article page since it's not on the main page for carousel items
                        date = self._fetch_date_from_url(link)
                        date_str = date.strftime('%B %d, %Y') if date else 'Featured'
                        
                        releases.append({
                            'date': date,
                            'date_str': date_str,
                            'items': [{
                                'text': title,
                                'category': 'announcement',
                                'urls': [link]
                            }],
                            'url': self.url
                        })

            # Filter by date
            filtered = []
            
            # Determine if we should be strict about missing dates
            strict_mode = self.days is not None or self.start_date is not None
            
            for release in releases:
                if release['date']:
                    if release['date'] >= self.cutoff_date:
                        if self.end_date is None or release['date'] <= self.end_date:
                            filtered.append(release)
                elif not strict_mode:
                    # Include undated items only if we are not in strict mode
                    # This prevents "Featured" items from showing up in "-d 1" queries
                    filtered.append(release)
                elif self.verbose:
                    print(f"    Skipping undated item (strict mode): {release['items'][0]['text'][:50]}...", file=sys.stderr)
            
            return filtered
            
        except Exception as e:
            print(f"Error scraping Developers Blog: {e}", file=sys.stderr)
            return []
    
    def _get_fallback_url(self) -> Optional[str]:
        """Get the HTML fallback URL for the current service."""
        if self.service_name and self.service_name in SERVICE_HTML_FALLBACKS:
            return SERVICE_HTML_FALLBACKS[self.service_name]
        return None
    
    def _scrape_html(self, url: str, headers: dict) -> List[Dict]:
        """Scrape release notes from an HTML page."""
        try:
            response = self.requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            self.used_fallback = True
            
            # Suppress XMLParsedAsHTMLWarning
            import warnings
            from bs4 import XMLParsedAsHTMLWarning
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
                soup = self.BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Update platform detection based on actual URL being scraped
            self.platform = self._detect_platform(url)
            
            # Get platform-specific selectors
            selectors = self.PLATFORM_SELECTORS[self.platform]
            
            # Find the main content area
            content_area = None
            for selector in selectors['container']:
                content_area = soup.select_one(selector)
                if content_area:
                    break
            
            if not content_area:
                content_area = soup.body or soup
            
            # Use platform-specific parsing
            if self.platform == 'firebase':
                self._parse_firebase_releases(content_area, selectors)
            elif self.platform == 'antigravity':
                self._parse_antigravity_releases(content_area, selectors)
            else:
                # Try multiple strategies to find release notes
                self._parse_structured_releases(content_area, selectors)
            
            if not self.releases:
                self._parse_unstructured_releases(content_area, selectors)
            
            # Add fallback URL to items that have no URLs
            for release in self.releases:
                for item in release.get('items', []):
                    if not item.get('urls') or len(item['urls']) == 0:
                        item['urls'] = [url]  # Use the page URL as fallback
            
            # Filter by date
            filtered_releases = self._filter_by_date(self.releases)
            
            # Filter by category
            filtered_releases = self._filter_by_category(filtered_releases)
            
            return filtered_releases
            
        except self.requests.RequestException as e:
            print(f"Error fetching HTML fallback URL: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error parsing HTML content: {e}", file=sys.stderr)
            return []
    
    def _filter_by_date(self, releases: List[Dict]) -> List[Dict]:
        """Filter releases by date range."""
        filtered = []
        for release in releases:
            if release['date']:
                if release['date'] >= self.cutoff_date:
                    if self.end_date is None or release['date'] <= self.end_date:
                        filtered.append(release)
        return filtered
    
    def _filter_by_category(self, releases: List[Dict]) -> List[Dict]:
        """Filter releases by category."""
        if not self.categories:
            return releases
        
        filtered = []
        for release in releases:
            # Filter items within each release
            filtered_items = [
                item for item in release['items']
                if item['category'].lower() in self.categories
            ]
            
            if filtered_items:
                filtered_release = release.copy()
                filtered_release['items'] = filtered_items
                filtered.append(filtered_release)
        
        return filtered
    
    def _parse_xml_feed(self, content: bytes) -> List[Dict]:
        """Parse an XML/Atom/RSS feed."""
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}", file=sys.stderr)
            return []
        
        releases = []
        
        # Handle Atom feeds (most Google Cloud feeds)
        # Namespace handling for Atom and RSS content module
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }
        
        # Try Atom format first
        entries = root.findall('.//atom:entry', namespaces)
        if not entries:
            # Try without namespace (some feeds don't use namespace prefix)
            entries = root.findall('.//entry')
        if not entries:
            # Try RSS format
            entries = root.findall('.//item')
        
        for entry in entries:
            # Get title
            title = None
            title_elem = entry.find('atom:title', namespaces)
            if title_elem is None:
                title_elem = entry.find('title')
            if title_elem is not None:
                title = title_elem.text or ''
            
            # Get published/updated date
            # Priority: pubDate (RSS) > published (Atom) > updated (Atom)
            # pubDate and published are publication dates, updated is last-modified
            date_elem = entry.find('pubDate')  # RSS format - check first
            if date_elem is None:
                date_elem = entry.find('atom:published', namespaces)
            if date_elem is None:
                date_elem = entry.find('published')
            if date_elem is None:
                date_elem = entry.find('atom:updated', namespaces)
            if date_elem is None:
                date_elem = entry.find('updated')
            
            parsed_date = None
            date_str = ''
            if date_elem is not None and date_elem.text:
                date_str = date_elem.text
                parsed_date = self._parse_xml_date(date_str)
            
            # Get content - try multiple sources
            # Priority: content:encoded (RSS) > content (Atom) > summary > description
            content_text = ''
            
            # Try content:encoded first (common in RSS feeds like feedburner)
            content_elem = entry.find('content:encoded', namespaces)
            if content_elem is not None and content_elem.text:
                content_text = content_elem.text
            
            # Try other content elements
            if not content_text:
                content_elem = entry.find('atom:content', namespaces)
                if content_elem is None:
                    content_elem = entry.find('content')
                if content_elem is None:
                    content_elem = entry.find('atom:summary', namespaces)
                if content_elem is None:
                    content_elem = entry.find('summary')
                if content_elem is None:
                    content_elem = entry.find('description')  # RSS format
                
                if content_elem is not None:
                    content_text = content_elem.text or ''
            
            # Get link
            link = ''
            link_elem = entry.find('atom:link', namespaces)
            if link_elem is None:
                link_elem = entry.find('link')
            if link_elem is not None:
                link = link_elem.get('href', '') or link_elem.text or ''
            
            # Also try feedburner:origLink for feedburner feeds
            if not link:
                origlink_elem = entry.find('{http://rssnamespace.org/feedburner/ext/1.0}origLink')
                if origlink_elem is not None and origlink_elem.text:
                    link = origlink_elem.text
            
            if parsed_date:
                # Check if this is a blog feed - if so, just use title
                if self._is_blog_feed():
                    # For blog feeds, only use the title - don't include full article content
                    clean_title = self._strip_html_tags(title) if title else ''
                    if clean_title:
                        items = [{
                            'text': clean_title,
                            'category': self._categorize_item(text=clean_title),
                            'urls': [link.strip()] if link else []
                        }]
                    else:
                        items = []
                else:
                    # For release notes, parse the full content
                    items = self._parse_xml_content(content_text, title, link)
                
                if items:
                    releases.append({
                        'date': parsed_date,
                        'date_str': parsed_date.strftime('%B %d, %Y'),
                        'items': items,
                        'url': link or self.url
                    })
        
        # Filter by date
        filtered = self._filter_by_date(releases)
        
        # Filter by category
        return self._filter_by_category(filtered)
    
    def _parse_xml_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from XML feed formats. Returns timezone-naive datetime."""
        date_str = date_str.strip()
        
        # Common XML/Atom date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # 2024-01-15T10:30:00.000Z
            '%Y-%m-%dT%H:%M:%SZ',          # 2024-01-15T10:30:00Z
            '%Y-%m-%dT%H:%M:%S%z',         # 2024-01-15T10:30:00+00:00
            '%Y-%m-%dT%H:%M:%S.%f%z',      # 2024-01-15T10:30:00.000+00:00
            '%a, %d %b %Y %H:%M:%S %Z',    # RSS format: Mon, 15 Jan 2024 10:30:00 GMT
            '%a, %d %b %Y %H:%M:%S %z',    # RSS format with timezone
            '%Y-%m-%d',                     # Simple date
        ]
        
        parsed_date = None
        
        for fmt in formats:
            try:
                # Handle timezone offset format (+00:00)
                if '+' in date_str and ':' in date_str.split('+')[-1]:
                    # Remove colon from timezone for %z parsing
                    parts = date_str.rsplit('+', 1)
                    if len(parts) == 2:
                        date_str_fixed = parts[0] + '+' + parts[1].replace(':', '')
                        try:
                            parsed_date = datetime.strptime(date_str_fixed, fmt)
                            break
                        except ValueError:
                            pass
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        # Try to extract just the date part if no format matched
        if parsed_date is None:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
            if date_match:
                try:
                    parsed_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Convert to naive datetime (remove timezone info) for consistent comparison
        if parsed_date is not None and parsed_date.tzinfo is not None:
            parsed_date = parsed_date.replace(tzinfo=None)
        
        return parsed_date
    
    def _parse_xml_content(self, content: str, title: str = '', entry_link: str = '') -> List[Dict]:
        """Parse HTML content from XML feed entry."""
        import html as html_module
        
        items = []
        
        # Clean up entry_link (strip whitespace)
        entry_link = entry_link.strip() if entry_link else ''
        
        if not content:
            if title:
                # Clean the title as well in case it contains HTML
                clean_title = self._strip_html_tags(title)
                items.append({
                    'text': clean_title,
                    'category': self._categorize_item(text=clean_title),
                    'urls': [entry_link] if entry_link else []
                })
            return items
        
        # Unescape HTML entities first (handles double-encoded content from RSS feeds)
        content = html_module.unescape(content)
        
        # Parse HTML content
        soup = self.BeautifulSoup(content, 'html.parser')
        
        # Extract all URLs from the content using BeautifulSoup
        all_urls = []
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    # Relative URL - prepend cloud.google.com
                    href = 'https://cloud.google.com' + href
                elif href.startswith('#'):
                    # Anchor link - skip these as they're not useful without context
                    continue
                elif not href.startswith('http'):
                    # Other relative URL (no leading slash) - skip
                    continue
                
                # Skip image URLs (blogger images, etc.) - they're not useful as documentation links
                if not any(img_host in href for img_host in ['blogger.googleusercontent.com', 'bp.blogspot.com', '/img/', '.png', '.jpg', '.gif', '.jpeg', '.webp']):
                    all_urls.append(href)
        
        # Also extract URLs using regex as fallback (in case BeautifulSoup missed some)
        url_pattern = re.compile(r'https?://[^\s"<>\]]+')
        regex_urls = url_pattern.findall(content)
        for url in regex_urls:
            # Clean up the URL (remove trailing punctuation)
            url = url.rstrip('.,;:!?)\'"]')
            # Skip image URLs
            if url and url not in all_urls:
                if not any(img_host in url for img_host in ['blogger.googleusercontent.com', 'bp.blogspot.com', '/img/', '.png', '.jpg', '.gif', '.jpeg', '.webp']):
                    all_urls.append(url)
        
        # For feedburner/blog style content, use the whole content as a single item
        # This is better than splitting by <li> which fragments the content
        # Check if this looks like blog/announcement content (has headers or long divs)
        has_headers = bool(soup.find_all(['h1', 'h2', 'h3', 'h4']))
        has_long_content = len(soup.get_text(strip=True)) > 200
        
        # For GCP release notes XML feeds, look for specific div classes first
        release_divs = soup.find_all('div', class_=['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'])
        if release_divs:
            for div in release_divs:
                text = div.get_text(strip=True)
                # Extra safeguard: strip any remaining HTML tags
                text = self._strip_html_tags(text)
                links = [a.get('href') for a in div.find_all('a') if a.get('href')]
                # Normalize all URLs
                links = self._normalize_urls(links)
                if text and len(text) > 5:
                    items.append({
                        'text': text,
                        'category': self._categorize_item(element=div, text=text),
                        'urls': links if links else self._normalize_urls(all_urls[:3])
                    })
        
        # If no release divs, and content looks like blog/announcement, use whole content
        if not items and (has_headers or has_long_content):
            text = soup.get_text(separator=' ', strip=True)
            # Extra safeguard: strip any remaining HTML tags (handles edge cases)
            text = self._strip_html_tags(text)
            text = re.sub(r'\s+', ' ', text)
            if text and len(text) > 10:
                items.append({
                    'text': text,
                    'category': self._categorize_item(text=text),
                    'urls': all_urls[:5] if all_urls else ([entry_link] if entry_link else [])
                })
        
        # Otherwise try list items
        if not items:
            list_items = soup.find_all('li')
            if list_items:
                for li in list_items:
                    text = li.get_text(strip=True)
                    text = self._strip_html_tags(text)
                    links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                    # Normalize all URLs
                    links = self._normalize_urls(links)
                    if text and len(text) > 5:
                        items.append({
                            'text': text,
                            'category': self._categorize_item(element=li, text=text),
                            'urls': links
                        })
        
        # If no list items found, use paragraphs
        if not items:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                text = self._strip_html_tags(text)
                links = [a.get('href') for a in p.find_all('a') if a.get('href')]
                # Normalize all URLs
                links = self._normalize_urls(links)
                if text and len(text) > 10:
                    items.append({
                        'text': text,
                        'category': self._categorize_item(element=p, text=text),
                        'urls': links
                    })
        
        # Final fallback: use the whole content as plain text
        if not items:
            text = soup.get_text(separator=' ', strip=True)
            text = self._strip_html_tags(text)
            text = re.sub(r'\s+', ' ', text)
            if text and len(text) > 10:
                items.append({
                    'text': text,
                    'category': self._categorize_item(text=text),
                    'urls': all_urls[:5] if all_urls else ([entry_link] if entry_link else [])
                })
        
        # Ensure all items have URLs - use all_urls or entry_link as fallback
        # Also normalize any remaining relative URLs
        for item in items:
            if not item.get('urls') or len(item['urls']) == 0:
                if all_urls:
                    item['urls'] = self._normalize_urls(all_urls[:5])  # Limit to 5 URLs
                elif entry_link:
                    item['urls'] = [entry_link]
            else:
                # Normalize existing URLs
                item['urls'] = self._normalize_urls(item['urls'])
        
        return items
    
    def _scrape_antigravity_js(self, headers: dict) -> List[Dict]:
        """Scrape AntiGravity changelog by extracting data from JavaScript bundle.
        
        AntiGravity is a JavaScript SPA (Angular) that embeds changelog data
        directly in its compiled JavaScript bundle. This method:
        1. Fetches the main page to find the current JS bundle filename
        2. Fetches the JS bundle
        3. Extracts the embedded changelog data using regex
        4. Parses it into our standard release format
        """
        try:
            # Step 1: Fetch the main page to find the JS bundle filename
            response = self.requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Find the main JS bundle (e.g., main-WHICPWHT.js)
            js_bundle_match = re.search(r'src="(main-[A-Za-z0-9]+\.js)"', response.text)
            if not js_bundle_match:
                if self.verbose:
                    print("  Could not find JS bundle in AntiGravity page", file=sys.stderr)
                return []
            
            js_bundle_name = js_bundle_match.group(1)
            js_bundle_url = f"https://antigravity.google/{js_bundle_name}"
            
            if self.verbose:
                print(f"  Found JS bundle: {js_bundle_name}", file=sys.stderr)
            
            # Step 2: Fetch the JS bundle
            js_response = self.requests.get(js_bundle_url, headers=headers, timeout=30)
            js_response.raise_for_status()
            js_content = js_response.text
            
            # Step 3: Extract the changelog data
            # The data is in a variable like: var j9={title:"...",sections:[...]}
            # We need to find and extract the sections array
            
            # Find the changelog data pattern - looking for the sections array
            # Pattern: sections:[{version:"...",description:"...",accordion:{...}}]
            changelog_match = re.search(
                r'var\s+\w+\s*=\s*\{[^}]*title:\s*"Google Antigravity Changelog"[^}]*sections:\s*(\[[^\]]*\{[^}]*version:[^}]*\}[^\]]*\])',
                js_content,
                re.DOTALL
            )
            
            if not changelog_match:
                # Try alternative pattern - extract by finding the semicolon-delimited statement
                # Split by semicolons and find the one containing changelog sections
                statements = js_content.split(';')
                changelog_statement = None
                for stmt in statements:
                    if 'Google Antigravity Changelog' in stmt and 'sections:' in stmt:
                        changelog_statement = stmt
                        break
                
                if not changelog_statement:
                    if self.verbose:
                        print("  Could not find changelog data in JS bundle", file=sys.stderr)
                    return []
                
                # Extract sections from the statement
                sections_start = changelog_statement.find('sections:[')
                if sections_start == -1:
                    return []
                
                # Find the matching closing bracket
                sections_str = self._extract_js_array(changelog_statement[sections_start + 9:])
            else:
                sections_str = changelog_match.group(1)
            
            # Step 4: Parse the sections into releases
            releases = self._parse_antigravity_sections(sections_str if 'sections_str' in dir() else js_content)
            
            # Filter by date
            filtered_releases = self._filter_by_date(releases)
            
            # Filter by category
            filtered_releases = self._filter_by_category(filtered_releases)
            
            return filtered_releases
            
        except self.requests.RequestException as e:
            print(f"Error fetching AntiGravity data: {e}", file=sys.stderr)
            return []
        except Exception as e:
            if self.verbose:
                print(f"Error parsing AntiGravity JS: {e}", file=sys.stderr)
            return []
    
    def _extract_js_array(self, js_str: str) -> str:
        """Extract a JavaScript array from a string, handling nested brackets."""
        depth = 0
        start = 0
        for i, char in enumerate(js_str):
            if char == '[':
                if depth == 0:
                    start = i
                depth += 1
            elif char == ']':
                depth -= 1
                if depth == 0:
                    return js_str[start:i+1]
        return js_str
    
    def _parse_antigravity_sections(self, js_content: str) -> List[Dict]:
        """Parse AntiGravity changelog sections from JavaScript content."""
        releases = []
        
        # Extract individual section objects using regex
        # Each section has: version:"X.Y.Z<br>Mon DD, YYYY", description:"...", accordion:{...}
        
        # Pattern for version with date
        version_pattern = re.compile(
            r'version:\s*"([^"]*?)<br>([^"]*?)"[^}]*?description:\s*"([^"]*?)"[^}]*?accordion:\s*\{[^}]*?changes:\s*"([^"]*?)"[^}]*?items:\s*\[(.*?)\]\s*\}',
            re.DOTALL
        )
        
        # Also try simpler pattern if the above doesn't match
        simple_version_pattern = re.compile(
            r'\{[^{]*?version:\s*"([^"]+)"[^}]*?description:\s*"([^"]+)"',
            re.DOTALL
        )
        
        matches = version_pattern.findall(js_content)
        
        if not matches:
            # Try the simpler pattern
            simple_matches = simple_version_pattern.findall(js_content)
            for version_raw, description in simple_matches:
                # Parse the version string (e.g., "1.11.17<br>Dec 8, 2025")
                if '<br>' in version_raw:
                    version, date_str = version_raw.split('<br>', 1)
                else:
                    version = version_raw
                    date_str = ""
                
                # Try to parse the date
                parsed_date = self._parse_antigravity_date(date_str)
                
                if parsed_date:
                    items = [{
                        'text': f"<strong>{version}</strong>: {description}",
                        'category': self._categorize_item(text=description),
                        'urls': ['https://antigravity.google/changelog']
                    }]
                    
                    releases.append({
                        'date': parsed_date,
                        'date_str': date_str.strip(),
                        'items': items,
                        'url': self.url
                    })
        else:
            for version, date_str, description, changes, items_str in matches:
                # Parse the date
                parsed_date = self._parse_antigravity_date(date_str)
                
                if parsed_date:
                    items = []
                    
                    # Add the main changes as an item
                    if changes:
                        # Clean HTML from changes
                        changes_text = re.sub(r'<[^>]+>', ' ', changes).strip()
                        changes_text = re.sub(r'\\/', '/', changes_text)  # Unescape slashes
                        if changes_text:
                            items.append({
                                'text': f"<strong>{version}</strong>: {changes_text}",
                                'category': self._categorize_item(text=description + " " + changes_text),
                                'urls': ['https://antigravity.google/changelog']
                            })
                    
                    # Parse accordion items (Improvements, Fixes, Patches)
                    item_pattern = re.compile(r'\{title:\s*"([^"]+)"[^}]*accordion_items:\s*\[(.*?)\]\s*\}', re.DOTALL)
                    for item_title, accordion_items in item_pattern.findall(items_str):
                        # Extract individual accordion items
                        text_pattern = re.compile(r'\{text:\s*"([^"]+)"\}')
                        for item_text in text_pattern.findall(accordion_items):
                            if item_text:
                                category = 'update'
                                if item_title.lower() == 'improvements':
                                    category = 'ga'
                                elif item_title.lower() == 'fixes':
                                    category = 'fixed'
                                elif item_title.lower() == 'patches':
                                    category = 'fixed'
                                
                                items.append({
                                    'text': f"[{item_title}] {item_text}",
                                    'category': category,
                                    'urls': ['https://antigravity.google/changelog']
                                })
                    
                    if items:
                        releases.append({
                            'date': parsed_date,
                            'date_str': date_str.strip(),
                            'items': items,
                            'url': self.url
                        })
        
        # If regex parsing didn't work well, try a more direct approach
        if not releases:
            releases = self._parse_antigravity_direct(js_content)
        
        return releases
    
    def _parse_antigravity_direct(self, js_content: str) -> List[Dict]:
        """Direct parsing of AntiGravity changelog from JS content."""
        releases = []
        
        # Find all version/date patterns
        # Format: "1.11.17<br>Dec 8, 2025"
        version_date_pattern = re.compile(r'"(\d+\.\d+\.\d+)<br>(\w+\s+\d+,\s+\d{4})"')
        
        for match in version_date_pattern.finditer(js_content):
            version = match.group(1)
            date_str = match.group(2)
            
            parsed_date = self._parse_antigravity_date(date_str)
            
            if parsed_date:
                # Find the description that follows
                desc_start = match.end()
                desc_match = re.search(r'description:\s*"([^"]+)"', js_content[desc_start:desc_start+500])
                description = desc_match.group(1) if desc_match else f"Version {version}"
                
                # Find changes text
                changes_match = re.search(r'changes:\s*"<p>([^<]+)</p>"', js_content[desc_start:desc_start+2000])
                changes_text = changes_match.group(1) if changes_match else ""
                
                items = [{
                    'text': f"<strong>v{version}</strong> - {description}: {changes_text}".strip(),
                    'category': self._categorize_item(text=description + " " + changes_text),
                    'urls': ['https://antigravity.google/changelog']
                }]
                
                # Find improvements, fixes, patches
                items_section = js_content[desc_start:desc_start+3000]
                
                for section_name, category in [('Improvements', 'ga'), ('Fixes', 'fixed'), ('Patches', 'fixed')]:
                    section_pattern = re.compile(
                        rf'title:\s*"{section_name}"[^]]*accordion_items:\s*\[([^\]]*)\]',
                        re.DOTALL
                    )
                    section_match = section_pattern.search(items_section)
                    if section_match:
                        item_texts = re.findall(r'text:\s*"([^"]+)"', section_match.group(1))
                        for item_text in item_texts:
                            if item_text:
                                items.append({
                                    'text': f"[{section_name}] {item_text}",
                                    'category': category,
                                    'urls': ['https://antigravity.google/changelog']
                                })
                
                releases.append({
                    'date': parsed_date,
                    'date_str': date_str,
                    'items': items,
                    'url': self.url
                })
        
        return releases
    
    def _parse_antigravity_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from AntiGravity format (e.g., 'Dec 8, 2025')."""
        date_str = date_str.strip()
        
        formats = [
            '%b %d, %Y',      # Dec 8, 2025
            '%B %d, %Y',      # December 8, 2025
            '%Y-%m-%d',       # 2025-12-08
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def _parse_firebase_releases(self, content_area, selectors):
        """Parse Firebase-specific release notes format."""
        # Firebase uses a different structure - look for version headers
        # Common patterns: "Version X.Y.Z - Month DD, YYYY" or just date headers
        
        # First, try to find version sections (h2/h3 with version numbers)
        for header_tag in ['h2', 'h3', 'h4']:
            headers = content_area.find_all(header_tag)
            
            for header in headers:
                header_text = header.get_text(strip=True)
                
                # Try to extract date from header text
                # Firebase formats: "November 20, 2025", "2025-11-20", "Version X.Y.Z - November 20, 2025"
                date_found = None
                date_str = None
                
                for pattern in selectors['date_patterns']:
                    match = re.search(pattern, header_text)
                    if match:
                        date_str = match.group(1)
                        date_found = self._parse_date(date_str)
                        break
                
                if date_found:
                    # Collect all content after this header until next same-level header
                    items = []
                    sibling = header.find_next_sibling()
                    
                    while sibling and sibling.name != header_tag:
                        # Check for list items
                        if sibling.name in ['ul', 'ol']:
                            for li in sibling.find_all('li', recursive=False):
                                text = li.get_text(strip=True)
                                html_content = str(li)
                                links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                                if text and len(text) > 5:
                                    items.append({
                                        'text': html_content,
                                        'category': self._categorize_item(element=li, text=text),
                                        'urls': links
                                    })
                        elif sibling.name == 'li':
                            text = sibling.get_text(strip=True)
                            html_content = str(sibling)
                            links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                            if text and len(text) > 5:
                                items.append({
                                    'text': html_content,
                                    'category': self._categorize_item(element=sibling, text=text),
                                    'urls': links
                                })
                        elif sibling.name in ['p', 'div']:
                            text = sibling.get_text(strip=True)
                            # Skip short divs or empty paragraphs
                            if text and len(text) > 10:
                                html_content = str(sibling)
                                links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                                items.append({
                                    'text': html_content,
                                    'category': self._categorize_item(element=sibling, text=text),
                                    'urls': links
                                })
                        
                        sibling = sibling.find_next_sibling()
                    
                    # If no items found from siblings, check nested content
                    if not items:
                        # Look for lists within the header's parent section
                        parent_section = header.parent
                        if parent_section:
                            for ul in parent_section.find_all(['ul', 'ol']):
                                for li in ul.find_all('li', recursive=False):
                                    text = li.get_text(strip=True)
                                    html_content = str(li)
                                    links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                                    if text and len(text) > 5:
                                        items.append({
                                            'text': html_content,
                                            'category': self._categorize_item(element=li, text=text),
                                            'urls': links
                                        })
                    
                    # If still no items, use the header text itself as a release note
                    if not items and len(header_text) > 15:
                        items.append({
                            'text': header_text,
                            'category': self._categorize_item(text=header_text),
                            'urls': []
                        })
                    
                    if items:
                        self.releases.append({
                            'date': date_found,
                            'date_str': date_str,
                            'items': items,
                            'url': self.url
                        })
        
        # Also try to parse table-based release notes (some Firebase pages use tables)
        tables = content_area.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Try to find date in first cell
                    first_cell = cells[0].get_text(strip=True)
                    for pattern in selectors['date_patterns']:
                        match = re.search(pattern, first_cell)
                        if match:
                            date_str = match.group(1)
                            date_found = self._parse_date(date_str)
                            if date_found:
                                # Use remaining cells as content
                                content_text = ' '.join(c.get_text(strip=True) for c in cells[1:])
                                if content_text and len(content_text) > 10:
                                    links = [a.get('href') for a in row.find_all('a') if a.get('href')]
                                    links = self._normalize_urls(links)
                                    self.releases.append({
                                        'date': date_found,
                                        'date_str': date_str,
                                        'items': [{
                                            'text': content_text,
                                            'category': self._categorize_item(text=content_text),
                                            'urls': links
                                        }],
                                        'url': self.url
                                    })
                            break

    def _parse_structured_releases(self, content_area, selectors):
        """Parse releases with clear date headers."""
        for header_tag in selectors['date_headers']:
            headers = content_area.find_all(header_tag)
            
            for header in headers:
                header_text = header.get_text(strip=True)
                
                # Try to extract date from header
                for pattern in selectors['date_patterns']:
                    match = re.search(pattern, header_text)
                    if match:
                        date_str = match.group(1)
                        parsed_date = self._parse_date(date_str)
                        
                        if parsed_date:
                            # Get content after this header until next header
                            items = []
                            sibling = header.find_next_sibling()
                            
                            while sibling and sibling.name != header.name:
                                # Stop if we hit a higher-level header (e.g. h1 when processing h2)
                                if sibling.name in selectors['date_headers'] and sibling.name < header.name:
                                    break
                                
                                # Check for specific release divs
                                div_classes = sibling.get('class', [])
                                if any(cls in ['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'] for cls in div_classes):
                                    text_content = str(sibling) # Get full HTML
                                    text = sibling.get_text(strip=True)
                                    links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                                    links = self._normalize_urls(links)
                                    if text and len(text) > 10:
                                        items.append({
                                            'text': text_content,
                                            'category': self._categorize_item(element=sibling, text=text),
                                            'urls': links
                                        })
                                
                                elif sibling.name in ['p', 'ul', 'ol', 'li', 'div']:
                                    if sibling.name in ['ul', 'ol']:
                                        for li in sibling.find_all('li'):
                                            text_content = str(li)
                                            li_text = li.get_text(strip=True)
                                            li_links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                                            li_links = self._normalize_urls(li_links)
                                            if li_text:
                                                items.append({
                                                    'text': text_content,
                                                    'category': self._categorize_item(element=li, text=li_text),
                                                    'urls': li_links
                                                })
                                    else:
                                        text_content = str(sibling)
                                        text = sibling.get_text(strip=True)
                                        links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                                        links = self._normalize_urls(links)
                                        if text and len(text) > 10:
                                            items.append({
                                                'text': text_content,
                                                'category': self._categorize_item(element=sibling, text=text),
                                                'urls': links
                                            })
                                sibling = sibling.find_next_sibling()
                            
                            if items:
                                self.releases.append({
                                    'date': parsed_date,
                                    'date_str': date_str,
                                    'items': items,
                                    'url': self.url
                                })
                            break
    
    def _parse_unstructured_releases(self, content_area, selectors):
        """Parse releases without clear structure."""
        # Look for specific release divs first
        release_divs = content_area.find_all('div', class_=['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'])
        for div in release_divs:
            # Try to find a date near this div
            parent = div.parent
            date_found = None
            date_str = None
            
            # Look for date in parent or siblings
            for elem in [div.previous_sibling, parent, div.next_sibling]:
                if elem and hasattr(elem, 'get_text'):
                    text = elem.get_text(strip=True)
                    for pattern in selectors['date_patterns']:
                        match = re.search(pattern, text)
                        if match:
                            date_str = match.group(1)
                            date_found = self._parse_date(date_str)
                            break
                if date_found:
                    break
            
            if date_found and date_found >= self.cutoff_date:
                text_content = str(div)
                text = div.get_text(strip=True)
                links = [a.get('href') for a in div.find_all('a') if a.get('href')]
                links = self._normalize_urls(links)
                if text and len(text) > 20:
                    # Check if we already have this content
                    is_duplicate = False
                    for release in self.releases:
                        for item in release.get('items', []):
                            if item['text'] == text_content:
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        self.releases.append({
                            'date': date_found,
                            'date_str': date_str,
                            'items': [{
                                'text': text_content,
                                'category': self._categorize_item(element=div, text=text),
                                'urls': links
                            }],
                            'url': self.url
                        })
    
        # Continue with existing text-based parsing
        all_text_elements = content_area.find_all(string=True)
        
        for nav_string in all_text_elements:
            text_str = str(nav_string).strip()
            if not text_str:
                continue
                
            for pattern in selectors['date_patterns']:
                matches = re.findall(pattern, text_str)
                for match in matches:
                    parsed_date = self._parse_date(match)
                    if parsed_date and parsed_date >= self.cutoff_date:
                        parent = nav_string.parent
                        if parent and parent.name not in ['script', 'style']:
                            text_content = str(parent)
                            content = parent.get_text(strip=True)
                            links = [a.get('href') for a in parent.find_all('a') if a.get('href')]
                            links = self._normalize_urls(links)
                            if content and len(content) > 20:
                                is_duplicate = False
                                for release in self.releases:
                                    for item in release.get('items', []):
                                        if item['text'] == text_content:
                                            is_duplicate = True
                                            break
                                
                                if not is_duplicate:
                                    self.releases.append({
                                        'date': parsed_date,
                                        'date_str': match,
                                        'items': [{
                                            'text': text_content,
                                            'category': self._categorize_item(element=parent, text=content),
                                            'urls': links
                                        }],
                                        'url': self.url
                                    })
    
    def _strip_html_tags(self, text: str) -> str:
        """Strip HTML tags from text using regex as a fallback."""
        import html as html_module
        
        if not text:
            return text
        
        # Unescape HTML entities
        text = html_module.unescape(text)
        
        # Strip HTML tags using regex
        # Handle style attributes with quotes
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _normalize_urls(self, urls: list, base_host: str = 'https://cloud.google.com') -> list:
        """Convert relative URLs to absolute and filter out invalid ones."""
        normalized = []
        for url in urls:
            if not url:
                continue
            url = url.strip()
            
            # Skip anchor-only links
            if url.startswith('#'):
                continue
            
            # Convert relative URLs to absolute
            if url.startswith('/'):
                url = base_host + url
            elif not url.startswith('http'):
                # Skip other relative URLs without protocol
                continue
            
            # Skip image URLs
            if any(img_ext in url.lower() for img_ext in ['.png', '.jpg', '.gif', '.jpeg', '.webp', '.svg', '.ico']):
                continue
            if any(img_host in url for img_host in ['blogger.googleusercontent.com', 'bp.blogspot.com']):
                continue
            
            if url not in normalized:
                normalized.append(url)
        
        return normalized
    
    def format_output(self, releases: List[Dict], format_type: str) -> str:
        """Format the scraped releases based on the specified format."""
        if format_type == 'json':
            return self._format_json(releases)
        elif format_type == 'markdown':
            return self._format_markdown(releases)
        elif format_type == 'html':
            return self._format_html(releases)
        else:
            return self._format_text(releases)
    
    def _clean_text(self, html_text: str) -> str:
        """Clean HTML text and add proper spacing."""
        import html as html_module
        
        # First unescape any HTML entities (handles double-encoded content)
        unescaped = html_module.unescape(html_text)
        
        # Parse HTML and get text
        soup = self.BeautifulSoup(unescaped, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Get text with separator to preserve word boundaries
        text = soup.get_text(separator=' ', strip=True)
        
        # Fallback: If text still contains HTML-like tags, strip them with regex
        # This handles cases where BeautifulSoup doesn't recognize malformed HTML
        if '<' in text and '>' in text:
            text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common spacing issues from HTML parsing
        # Add space after colons that are followed by uppercase letters
        text = re.sub(r':([A-Z])', r': \1', text)
        # Add space after periods that are followed by uppercase letters
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        # Fix "See X" patterns that got merged
        text = re.sub(r'([a-z])See ', r'\1. See ', text)
        text = re.sub(r'([a-z])For ', r'\1. For ', text)
        
        # Remove specific URLs that clutter output
        text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
        
        return text.strip()
    
    def _format_text(self, releases: List[Dict]) -> str:
        """Format releases as plain text with improved readability."""
        output = []
        
        # Header
        output.append("")
        output.append("╔" + "═" * 78 + "╗")
        output.append("║" + " RELEASE NOTES SUMMARY ".center(78) + "║")
        output.append("╠" + "═" * 78 + "╣")
        output.append("║" + f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(78) + "║")
        if hasattr(self, 'group_name') and self.group_name:
            output.append("║" + f"  Service Group: {self.group_name} ({len(self.service_names)} services)".ljust(78) + "║")
        if self.start_date:
            end_str = self.end_date.strftime('%Y-%m-%d') if self.end_date else 'today'
            output.append("║" + f"  Date Range: {self.start_date.strftime('%Y-%m-%d')} to {end_str}".ljust(78) + "║")
        elif self.days:
            output.append("║" + f"  Time Range: Last {self.days} day(s)".ljust(78) + "║")
        else:
            output.append("║" + f"  Time Range: Last {self.months} month(s)".ljust(78) + "║")
        output.append("╚" + "═" * 78 + "╝")
        output.append("")
        
        if not releases:
            output.append("  No releases found in the specified time range.")
            return "\n".join(output)
        
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        # Group releases by date
        current_date = None
        for release in releases:
            date_str = release['date_str']
            service = release.get('service', '')
            
            # Print date header if new date
            if date_str != current_date:
                current_date = date_str
                output.append("")
                output.append("┌" + "─" * 78 + "┐")
                # Use ljust(77) to account for emoji 📅 being 2 columns wide but 1 character
                output.append("│" + f"  📅 {date_str}".ljust(77) + "│")
                output.append("└" + "─" * 78 + "┘")
            
            # Print service subheader for group queries
            if hasattr(self, 'group_name') and self.group_name and service:
                output.append(f"\n  ▸ {service}")
                output.append("  " + "─" * 40)
            
            for item in release['items']:
                text = self._clean_text(item['text'])
                category = item['category'].upper()
                
                # Category emoji/icon mapping for visual distinction
                category_icons = {
                    'GA': '✅',
                    'PUBLIC-PREVIEW': '🔮',
                    'BREAKING': '⚠️ ',
                    'SECURITY': '🔒',
                    'DEPRECATED': '⛔',
                    'FIXED': '🔧',
                    'ISSUE': '🐛',
                    'CHANGE': '🔄',
                    'ANNOUNCEMENT': '📢',
                    'LIBRARIES': '📦',
                    'UPDATE': '📝',
                }
                icon = category_icons.get(category, '•')
                
                # Format category badge
                badge = f"[{category}]"
                
                # Add source/service name for blog items if we're in blog mode
                if hasattr(self, 'group_name') and self.group_name == 'Google Blogs' and service:
                    display_service = service
                    # Map internal service names to friendlier names
                    service_map = {
                        'app-dev': 'App Dev',
                        'app-mod': 'App Mod',
                        'infra': 'Infra',
                        'containers': 'Containers',
                        'ai-ml': 'AI/ML',
                        'dev-blog': 'Dev Blog',
                    }
                    if service in service_map:
                        display_service = service_map[service]
                    badge = f"{badge} [{display_service}]"
                
                # Word wrap long text
                max_width = 70
                prefix = f"    {icon} {badge} "
                indent = " " * len(prefix)
                
                # Wrap text
                words = text.split()
                lines = []
                current_line = prefix
                
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_width + len(prefix):
                        if current_line == prefix:
                            current_line += word
                        else:
                            current_line += " " + word
                    else:
                        lines.append(current_line)
                        current_line = indent + word
                
                if current_line.strip():
                    lines.append(current_line)
                
                for line in lines:
                    output.append(line)
                
                # Add links if present (compact format)
                if item.get('urls'):
                    urls = item['urls'][:3]  # Limit to 3 links
                    if urls:
                        output.append(f"         ↳ See: {urls[0]}")
                        if len(urls) > 1:
                            for url in urls[1:]:
                                output.append(f"              {url}")
                
                output.append("")  # Blank line between items
        
        # Statistics section
        output.append("")
        output.append("┌" + "─" * 78 + "┐")
        # Use ljust(77) to account for emoji 📊 being 2 columns wide but 1 character
        output.append("│" + "  📊 STATISTICS".ljust(77) + "│")
        output.append("├" + "─" * 78 + "┤")
        
        total_items = sum(len(r['items']) for r in releases)
        output.append("│" + f"  Total Releases: {len(releases)}".ljust(78) + "│")
        output.append("│" + f"  Total Items: {total_items}".ljust(78) + "│")
        output.append("│" + "".ljust(78) + "│")
        
        # Count by category
        category_counts = {}
        for release in releases:
            for item in release['items']:
                category = item['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            output.append("│" + "  By Category:".ljust(78) + "│")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                bar_width = min(count * 2, 30)
                bar = "█" * bar_width
                output.append("│" + f"    {category:<15} {count:>3} {bar}".ljust(78) + "│")
        
        output.append("└" + "─" * 78 + "┘")
        output.append("")
        
        return "\n".join(output)
    
    def _format_markdown(self, releases: List[Dict]) -> str:
        """Format releases as Markdown, extracting URLs from the text."""
        output = []
        output.append("# Release Notes Summary\n")
        if hasattr(self, 'group_name') and self.group_name:
            output.append(f"**Service Group:** {self.group_name}  ")
            output.append(f"**Services:** {', '.join(sorted(self.service_names))}  ")
        else:
            output.append(f"**Source:** [{self.url}]({self.url})  ")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        if self.start_date:
            end_str = self.end_date.strftime('%Y-%m-%d') if self.end_date else 'today'
            output.append(f"**Date range:** {self.start_date.strftime('%Y-%m-%d')} to {end_str}\n")
        else:
            output.append(f"**Time range:** Last {self.months} months\n")
        output.append("---\n")
        
        if not releases:
            output.append("*No releases found in the specified time range.*")
            return "\n".join(output)
        
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        for release in releases:
            service_badge = f" `{release.get('service', '')}`" if release.get('service') and hasattr(self, 'group_name') and self.group_name else ""
            output.append(f"\n## {release['date_str']}{service_badge}\n")
            for item in release['items']:
                # Use BeautifulSoup to get plain text, and remove the specific URL
                text = self.BeautifulSoup(item['text'], 'html.parser').get_text(strip=True)
                text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
                badge = f"`{item['category']}`"
                output.append(f"- {badge} {text}")
                if item.get('urls'):
                    for url in item['urls']:
                        output.append(f"  - [Link]({url})")
            output.append("")
        
        # Add statistics
        output.append("\n---\n")
        output.append("## Statistics\n")
        output.append(f"- **Total releases:** {len(releases)}")
        
        total_items = sum(len(r['items']) for r in releases)
        output.append(f"- **Total items:** {total_items}")
        
        # Count by category
        category_counts = {}
        for release in releases:
            for item in release['items']:
                category = item['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            output.append("\n### Items by category\n")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                output.append(f"- `{category}`: {count}")
        
        return "\n".join(output)
    
    def _format_json(self, releases: List[Dict]) -> str:
        """Format releases as JSON, extracting URLs from the text."""
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        # Convert datetime objects to strings for JSON serialization
        json_releases = []
        for release in releases:
            json_items = []
            for item in release['items']:
                # Use BeautifulSoup to get plain text for JSON, and remove the specific URL
                text = self.BeautifulSoup(item['text'], 'html.parser').get_text(strip=True)
                text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
                json_item = {
                    'text': text,
                    'category': item['category'],
                    'urls': item.get('urls', [])
                }
                json_items.append(json_item)
                
            json_release = {
                'date': release['date'].isoformat() if release['date'] else None,
                'date_str': release['date_str'],
                'items': json_items,
                'url': release.get('url', self.url)
            }
            json_releases.append(json_release)
        
        output = {
            'metadata': {
                'source': self.url,
                'generated': datetime.now().isoformat(),
                'time_range_months': self.months,
                'cutoff_date': self.cutoff_date.isoformat()
            },
            'statistics': {
                'total_releases': len(releases),
                'total_items': sum(len(r['items']) for r in releases)
            },
            'releases': json_releases
        }
        
        return json.dumps(output, indent=2)
    
    def _format_html(self, releases: List[Dict]) -> str:
        """Format releases as HTML with URLs included."""
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('<head>')
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append('    <title>Release Notes Summary</title>')
        html.append('    <style>')
        html.append('        body {')
        html.append('            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;')
        html.append('            line-height: 1.6;')
        html.append('            max-width: 1200px;')
        html.append('            margin: 0 auto;')
        html.append('            padding: 20px;')
        html.append('            background: #f5f5f5;')
        html.append('        }')
        html.append('        .header {')
        html.append('            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);')
        html.append('            color: white;')
        html.append('            padding: 30px;')
        html.append('            border-radius: 10px;')
        html.append('            margin-bottom: 30px;')
        html.append('        }')
        html.append('        .header h1 {')
        html.append('            margin: 0;')
        html.append('            font-size: 2em;')
        html.append('        }')
        html.append('        .meta {')
        html.append('            opacity: 0.9;')
        html.append('            margin-top: 10px;')
        html.append('        }')
        html.append('        .release-date {')
        html.append('            background: white;')
        html.append('            border-radius: 8px;')
        html.append('            padding: 20px;')
        html.append('            margin-bottom: 20px;')
        html.append('            box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
        html.append('        }')
        html.append('        .release-date h2 {')
        html.append('            color: #333;')
        html.append('            margin-top: 0;')
        html.append('            border-bottom: 2px solid #667eea;')
        html.append('            padding-bottom: 10px;')
        html.append('        }')
        html.append('        .release-item {')
        html.append('            margin: 15px 0;')
        html.append('            padding: 10px;')
        html.append('            background: #f9f9f9;')
        html.append('            border-left: 4px solid #ccc;')
        html.append('            border-radius: 4px;')
        html.append('        }')
        html.append('        .release-item.ga { border-left-color: #4CAF50; }')
        html.append('        .release-item.publicpreview { border-left-color: #FF9800; }')
        html.append('        .release-item.change { border-left-color: #2196F3; }')
        html.append('        .release-item.announcement { border-left-color: #9C27B0; }')
        html.append('        .release-item.breaking { border-left-color: #f44336; }')
        html.append('        .release-item.deprecated { border-left-color: #f44336; }')
        html.append('        .release-item.fixed { border-left-color: #00BCD4; }')
        html.append('        .release-item.update { border-left-color: #795548; }')
        html.append('        .release-item.libraries { border-left-color: #607D8B; }')
        html.append('        .release-item.security { border-left-color: #E91E63; }')
        html.append('        .release-item.issue { border-left-color: #ffc107; }')
        html.append('        .category {')
        html.append('            display: inline-block;')
        html.append('            padding: 2px 8px;')
        html.append('            border-radius: 3px;')
        html.append('            font-size: 0.85em;')
        html.append('            font-weight: bold;')
        html.append('            margin-right: 10px;')
        html.append('        }')
        html.append('        .category.ga { background: #4CAF50; color: white; }')
        html.append('        .category.publicpreview { background: #FF9800; color: white; }')
        html.append('        .category.change { background: #2196F3; color: white; }')
        html.append('        .category.announcement { background: #9C27B0; color: white; }')
        html.append('        .category.breaking { background: #E91E63; color: white; }')
        html.append('        .category.deprecated { background: #f44336; color: white; }')
        html.append('        .category.fixed { background: #00BCD4; color: white; }')
        html.append('        .category.update { background: #795548; color: white; }')
        html.append('        .category.libraries { background: #607D8B; color: white; }')
        html.append('        .category.security { background: #E91E63; color: white; }')
        html.append('        .category.issue { background: #ffc107; color: white; }')
        html.append('        .stats {')
        html.append('            background: white;')
        html.append('            border-radius: 8px;')
        html.append('            padding: 20px;')
        html.append('            margin-top: 30px;')
        html.append('            box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
        html.append('        }')
        html.append('        .stats h2 {')
        html.append('            color: #333;')
        html.append('            margin-top: 0;')
        html.append('        }')
        html.append('        a {')
        html.append('            color: #667eea;')
        html.append('            text-decoration: none;')
        html.append('        }')
        html.append('        a:hover {')
        html.append('            text-decoration: underline;')
        html.append('        }')
        html.append('        .source-link {')
        html.append('            margin-top: 20px;')
        html.append('            text-align: center;')
        html.append('        }')
        html.append('        .item-source {')
        html.append('            font-size: 0.8em;')
        html.append('            margin-top: 5px;')
        html.append('            opacity: 0.7;')
        html.append('        }')
        html.append('        .no-results {')
        html.append('            background: #fff3cd;')
        html.append('            border: 1px solid #ffc107;')
        html.append('            border-radius: 5px;')
        html.append('            padding: 20px;')
        html.append('            margin: 20px 0;')
        html.append('            text-align: center;')
        html.append('        }')
        html.append('    </style>')
        html.append('</head>')
        html.append('<body>')
        html.append('    <div class="header">')
        html.append('        <h1>Release Notes Summary</h1>')
        html.append('        <div class="meta">')
        html.append(f'            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        if hasattr(self, 'group_name') and self.group_name:
            html.append(f'            <p>Service Group: <strong>{self.group_name}</strong> ({len(self.service_names)} services)</p>')
            html.append(f'            <p>Services: {", ".join(sorted(self.service_names))}</p>')
        else:
            html.append(f'            <p>Source: <a href="{self.url}" style="color: white; text-decoration: underline;">{self.url}</a></p>')
        if self.start_date:
            end_str = self.end_date.strftime('%Y-%m-%d') if self.end_date else 'today'
            html.append(f'            <p>Date range: {self.start_date.strftime("%Y-%m-%d")} to {end_str}</p>')
        else:
            html.append(f'            <p>Time range: Last {self.months} months</p>')
        html.append('        </div>')
        html.append('    </div>')
        
        if not releases:
            html.append('    <div class="no-results">')
            html.append('        <h2>No Release Notes Found</h2>')
            html.append('        <p>No release notes were found in the specified time range.</p>')
            html.append('        <p>This could be due to:</p>')
            html.append('        <ul style="text-align: left; display: inline-block;">')
            html.append('            <li>No releases in the past ' + str(self.months) + ' months</li>')
            html.append('            <li>Different page structure than expected</li>')
            html.append('            <li>Content loaded dynamically via JavaScript</li>')
            html.append('        </ul>')
            html.append('    </div>')
        else:
            # Add release notes with URLs
            for release in releases:
                html.append('    <div class="release-date">')
                service_badge = f' <span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 10px;">{release.get("service", "")}</span>' if release.get('service') and hasattr(self, 'group_name') and self.group_name else ""
                html.append(f'        <h2>{release["date_str"]}{service_badge}</h2>')
                for item in release['items']:
                    category_class = item['category'].replace('-', '')
                    html.append(f'        <div class="release-item {category_class}">')
                    html.append(f'            <span class="category {category_class}">{item["category"].replace("-", " ").upper()}</span>')
                    html.append(f'            {item["text"]}') # Use the raw HTML content
                    html.append('        </div>')
                html.append('    </div>')
        
        # Add statistics
        html.append('    <div class="stats">')
        html.append('        <h2>Summary Statistics</h2>')
        html.append(f'        <p><strong>Total Releases:</strong> {len(releases)}</p>')
        
        total_items = sum(len(r['items']) for r in releases)
        html.append(f'        <p><strong>Total Items:</strong> {total_items}</p>')
        
        if releases:
            date_range_start = min(r['date'] for r in releases if r['date'])
            date_range_end = max(r['date'] for r in releases if r['date'])
            html.append(f'        <p><strong>Date Range:</strong> {date_range_start.strftime("%Y-%m-%d")} to {date_range_end.strftime("%Y-%m-%d")}</p>')
        else:
            cutoff = self.cutoff_date.strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            html.append(f'        <p><strong>Search Range:</strong> {cutoff} to {today}</p>')
        
        # Category breakdown
        if releases:
            category_counts = {}
            for release in releases:
                for item in release['items']:
                    category = item['category']
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                html.append('        <h3>Items by Category</h3>')
                html.append('        <ul>')
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    display_name = category.replace('-', ' ').title()
                    if category == 'ga':
                        display_name = 'GA (Generally Available)'
                    elif category == 'public-preview':
                        display_name = 'Public Preview'
                    elif category == 'breaking':
                        display_name = 'Breaking'
                    html.append(f'            <li><strong>{display_name}:</strong> {count}</li>')
                html.append('        </ul>')
        
        html.append('    </div>')
        
        html.append('    <div class="source-link">')
        html.append(f'        <a href="{self.url}" target="_blank">View Full Release Notes</a>')
        html.append('    </div>')
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)

def list_services():
    """Print list of available services with their groups."""
    # Build reverse lookup: service -> group
    service_to_group = {}
    for group, services in SERVICE_GROUPS.items():
        for service in services:
            service_to_group[service] = group
    
    print("Available GCP services:")
    print("-" * 60)
    
    # Find the longest service name for alignment
    max_len = max(len(s) for s in SERVICE_FEEDS.keys())
    
    for service in sorted(SERVICE_FEEDS.keys()):
        group = service_to_group.get(service, 'unknown')
        print(f"  {service:<{max_len}}  [{group}]")
    print("-" * 60)
    print(f"Total: {len(SERVICE_FEEDS)} services")
    print(f"\nUse --list-groups to see all service groups")


def list_groups():
    """Print list of available service groups."""
    print("Available service groups:")
    print("=" * 60)
    for group, services in sorted(SERVICE_GROUPS.items()):
        print(f"\n{group}:")
        print("-" * 40)
        for service in sorted(services):
            print(f"  {service}")
    print("\n" + "=" * 60)
    print(f"Total: {len(SERVICE_GROUPS)} groups, {sum(len(s) for s in SERVICE_GROUPS.values())} services")


def main():
    """Main entry point for the script."""
    # Check dependencies before doing anything else
    check_dependencies()
    
    parser = argparse.ArgumentParser(
        description='Scrape release notes from documentation pages or XML feeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use a service name (reads from XML feed by default)
  %(prog)s -s cloud-run
  %(prog)s -s gke -m 6 -o html -f gke_notes.html
  
  # Use a custom URL
  %(prog)s -u https://example.com/release-notes
  %(prog)s -u https://cloud.google.com/feeds/cloud-run-release-notes.xml
  
  # Filter by time range
  %(prog)s -s cloud-run -d 7        # Last 7 days
  %(prog)s -s bigquery -d 30        # Last 30 days
  %(prog)s -s gke -m 3              # Last 3 months
  
  # Filter by date range
  %(prog)s -s cloud-run --start-date 2024-01-01 --end-date 2024-06-30
  %(prog)s -s bigquery --start-date 2024-06-01
  
  # Query a service group (all services in that domain)
  %(prog)s -g gke -d 14             # All GKE channels, last 14 days
  %(prog)s -g ai -m 1               # All AI/ML services, last month
  %(prog)s -g security -c breaking  # Security services, breaking changes only
  %(prog)s -g databases -o html -f db.html
  
  # Scrape blogs
  %(prog)s --blogs                  # Scrape all configured Google blogs
  
  # List available services and groups
  %(prog)s --list-services          # Shows all services with their group
  %(prog)s --list-groups            # Shows all groups: ai, apps, compute,
                                    # databases, gke, networking, operations,
                                    # sdk, security, specialized, storage, workspace

Output formats:
  text     - Plain text (default)
  json     - JSON format
  markdown - Markdown format
  html     - Styled HTML page
        """
    )
    
    # Source options (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        '-s', '--service',
        choices=list(SERVICE_FEEDS.keys()),
        metavar='SERVICE',
        help='GCP service name (use --list-services to see all options)'
    )
    source_group.add_argument(
        '-g', '--group',
        metavar='GROUP[,GROUP,...]',
        help='Service group(s) to query, comma-separated (e.g., apps,security). Use --list-groups to see all options'
    )
    source_group.add_argument(
        '-u', '--url',
        help='URL of the release notes page or XML feed to scrape'
    )
    source_group.add_argument(
        '--list-services',
        action='store_true',
        help='List all available GCP service names'
    )
    source_group.add_argument(
        '--list-groups',
        action='store_true',
        help='List all available service groups'
    )
    source_group.add_argument(
        '--blogs',
        action='store_true',
        help='Scrape official Google Cloud and Developers blogs'
    )
    
    # Date filtering options
    date_group = parser.add_argument_group('date filtering')
    date_group.add_argument(
        '-d', '--days',
        type=int,
        help='Number of days to look back'
    )
    date_group.add_argument(
        '-m', '--months',
        type=int,
        help='Number of months to look back (default: 12 if no other date option specified)'
    )
    date_group.add_argument(
        '--start-date',
        help='Start date for filtering (format: YYYY-MM-DD)'
    )
    date_group.add_argument(
        '--end-date',
        help='End date for filtering (format: YYYY-MM-DD, default: today)'
    )
    
    # Category filtering
    parser.add_argument(
        '-c', '--category',
        action='append',
        choices=VALID_CATEGORIES,
        metavar='CATEGORY',
        help='Filter by category (can be used multiple times). Options: ' + ', '.join(VALID_CATEGORIES)
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        choices=['text', 'json', 'markdown', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Output file path (if not specified, prints to stdout)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Handle --list-services and --list-groups
    if args.list_services:
        list_services()
        sys.exit(0)
    
    if args.list_groups:
        list_groups()
        sys.exit(0)
    
    # Determine URLs to scrape
    urls = []
    service_names = []
    
    if args.service:
        urls = [SERVICE_FEEDS[args.service]]
        service_names = [args.service]
    elif args.group:
        # Parse comma-separated groups
        group_names = [g.strip() for g in args.group.split(',')]
        
        # Validate all group names
        invalid_groups = [g for g in group_names if g not in SERVICE_GROUPS]
        if invalid_groups:
            parser.error(f"Invalid group(s): {', '.join(invalid_groups)}. Use --list-groups to see available groups.")
        
        # Combine services from all specified groups (avoid duplicates while preserving order)
        services = []
        seen = set()
        for group in group_names:
            for service in SERVICE_GROUPS[group]:
                if service not in seen:
                    services.append(service)
                    seen.add(service)
        
        urls = [SERVICE_FEEDS[s] for s in services]
        service_names = services
    elif args.url:
        urls = [args.url]
        service_names = ['custom']
    elif args.blogs:
        urls = list(BLOG_URLS.values())
        service_names = list(BLOG_URLS.keys())
    else:
        parser.error("Either --service, --group, --url, or --blogs is required")
    
    # Parse date arguments
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            parser.error(f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD")
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            parser.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
    
    # Validate date range
    if start_date and end_date and start_date > end_date:
        parser.error("Start date must be before end date")
    
    # Handle days/months vs date range
    days = args.days
    months = args.months
    
    # Validate that only one time option is used
    time_options_count = sum(1 for x in [days, months, start_date] if x is not None)
    if time_options_count > 1:
        parser.error("Use only one of --days, --months, or --start-date")
    
    # Default to 12 months if no time option specified
    if not start_date and not months and not days:
        months = 12
    
    # Parse group names for display
    group_display = None
    if args.group:
        group_names = [g.strip() for g in args.group.split(',')]
        group_display = ', '.join(group_names) if len(group_names) > 1 else group_names[0]
    
    if args.verbose:
        if len(urls) > 1:
            print(f"Scraping {len(urls)} services in group '{group_display if group_display else 'blogs'}':", file=sys.stderr)
            for name in service_names:
                print(f"  - {name}", file=sys.stderr)
        else:
            print(f"Scraping: {urls[0]}", file=sys.stderr)
        if start_date:
            print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {(end_date or datetime.now()).strftime('%Y-%m-%d')}", file=sys.stderr)
        elif days:
            print(f"Time range: Last {days} day(s)", file=sys.stderr)
        else:
            print(f"Time range: Last {months} month(s)", file=sys.stderr)
        print(f"Output format: {args.output}", file=sys.stderr)
    
    # Scrape all URLs and combine results
    all_releases = []
    for url, service_name in zip(urls, service_names):
        if args.verbose and len(urls) > 1:
            print(f"Fetching: {service_name} ({url})...", file=sys.stderr)
        
        scraper = ReleaseNotesScraper(
            url,
            months=months,
            days=days,
            start_date=start_date,
            end_date=end_date,
            categories=args.category,
            service_name=service_name,
            verbose=args.verbose
        )
        releases = scraper.scrape()
        
        # Add service name to each release for multi-service queries
        for release in releases:
            release['service'] = service_name
        
        all_releases.extend(releases)
        
        if args.verbose and len(urls) > 1:
            fallback_note = " (via HTML fallback)" if scraper.used_fallback else ""
            print(f"  Found {len(releases)} releases{fallback_note}", file=sys.stderr)
    
    if args.verbose:
        print(f"Total: {len(all_releases)} releases", file=sys.stderr)
    
    # Create a scraper instance for formatting (uses the last URL for metadata)
    # For group queries, we'll customize the output
    format_scraper = ReleaseNotesScraper(urls[0], months=months, days=days, start_date=start_date, end_date=end_date, categories=args.category)
    
    # Add group info for formatting
    if args.group:
        format_scraper.group_name = group_display
        format_scraper.service_names = service_names
    elif args.blogs:
        format_scraper.group_name = 'Google Blogs'
        format_scraper.service_names = service_names
    else:
        format_scraper.group_name = None
        format_scraper.service_names = service_names
    
    # Format output
    output = format_scraper.format_output(all_releases, args.output)
    
    # Write output
    if args.file:
        try:
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"{args.output.upper()} output saved to {args.file}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == '__main__':
    main()
