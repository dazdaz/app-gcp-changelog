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
        'apphub', 'api-gateway', 'apigee', 'cloud-build', 'cloud-functions',
        'cloud-run', 'cloud-tasks', 'cloud-trace', 'eventarc', 'workflows'
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
        'distributed-cloud-edge', 'anthos-bare-metal', 'anthos-vmware', 'vmware-engine'
    ],
    'gke': [
        'gke', 'gke-rapid', 'gke-regular', 'gke-stable', 'gke-extended', 'gke-nochannel'
    ],
    'operations': [
        'cloud-logging', 'cloud-monitoring', 'cloud-observability', 'cloud-profiler',
        'cloud-scheduler', 'config-connector', 'resource-manager'
    ],
    'ai': [
        'ai-app-builder', 'dialogflow', 'document-ai', 'gemini-code-assist',
        'speech-to-text', 'talent-solution', 'text-to-speech', 'translation',
        'vertex-ai', 'video-intelligence'
    ],
    'specialized': [
        'cloud-composer', 'healthcare-api', 'blockchain-node-engine'
    ],
    'workspace': [
        'apps-script', 'cloud-search', 'docs-api'
    ],
    'firebase': [
        'firebase', 'firebase-android', 'firebase-ios', 'firebase-js', 'firebase-admin',
        'firebase-cpp', 'firebase-unity', 'firebase-flutter', 'firestore', 'firebase-extensions'
    ],
}

# GCP Service XML Feed URLs
SERVICE_FEEDS = {
    # Applications & Development
    'apphub': 'https://cloud.google.com/feeds/apphub-release-notes.xml',
    'api-gateway': 'https://cloud.google.com/feeds/api-gateway-release-notes.xml',
    'apigee': 'https://cloud.google.com/feeds/apigee-release-notes.xml',
    'cloud-build': 'https://cloud.google.com/feeds/cloud-build-release-notes.xml',
    'cloud-functions': 'https://cloud.google.com/feeds/cloud-functions-release-notes.xml',
    'cloud-run': 'https://cloud.google.com/feeds/cloud-run-release-notes.xml',
    'cloud-tasks': 'https://cloud.google.com/feeds/cloud-tasks-release-notes.xml',
    'cloud-trace': 'https://cloud.google.com/feeds/cloud-trace-release-notes.xml',
    'eventarc': 'https://cloud.google.com/feeds/eventarc-release-notes.xml',
    'workflows': 'https://cloud.google.com/feeds/workflows-release-notes.xml',
    
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
    'dialogflow': 'https://cloud.google.com/feeds/dialogflow-release-notes.xml',
    'document-ai': 'https://cloud.google.com/feeds/document-ai-release-notes.xml',
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
    
    # Firebase
    'firebase': 'https://firebase.google.com/feeds/release-notes.xml',
    'firebase-android': 'https://firebase.google.com/feeds/android-release-notes.xml',
    'firebase-ios': 'https://firebase.google.com/feeds/ios-release-notes.xml',
    'firebase-js': 'https://firebase.google.com/feeds/js-release-notes.xml',
    'firebase-admin': 'https://firebase.google.com/feeds/admin-release-notes.xml',
    'firebase-cpp': 'https://firebase.google.com/feeds/cpp-release-notes.xml',
    'firebase-unity': 'https://firebase.google.com/feeds/unity-release-notes.xml',
    'firebase-flutter': 'https://firebase.google.com/feeds/flutter-release-notes.xml',
    'firebase-extensions': 'https://firebase.google.com/feeds/extensions-release-notes.xml',
    
}

# HTML fallback URLs for services where XML feeds may not be available
SERVICE_HTML_FALLBACKS = {
    # Applications & Development
    'apphub': 'https://cloud.google.com/app-hub/docs/release-notes',
    'api-gateway': 'https://cloud.google.com/api-gateway/docs/release-notes',
    'apigee': 'https://cloud.google.com/apigee/docs/release-notes',
    'cloud-build': 'https://cloud.google.com/build/docs/release-notes',
    'cloud-functions': 'https://cloud.google.com/functions/docs/release-notes',
    'cloud-run': 'https://cloud.google.com/run/docs/release-notes',
    'cloud-tasks': 'https://cloud.google.com/tasks/docs/release-notes',
    'cloud-trace': 'https://cloud.google.com/trace/docs/release-notes',
    'eventarc': 'https://cloud.google.com/eventarc/docs/release-notes',
    'workflows': 'https://cloud.google.com/workflows/docs/release-notes',
    
    # Databases & Data Analytics
    'alloydb': 'https://cloud.google.com/alloydb/docs/release-notes',
    'bigquery': 'https://cloud.google.com/bigquery/docs/release-notes',
    'data-fusion': 'https://cloud.google.com/data-fusion/docs/release-notes',
    'firestore': 'https://cloud.google.com/firestore/docs/release-notes',
    'spanner': 'https://cloud.google.com/spanner/docs/release-notes',
    'cloud-sql': 'https://cloud.google.com/sql/docs/release-notes',
    'data-catalog': 'https://cloud.google.com/data-catalog/docs/release-notes',
    'database-migration': 'https://cloud.google.com/database-migration/docs/release-notes',
    'dataflow': 'https://cloud.google.com/dataflow/docs/release-notes',
    'dataproc': 'https://cloud.google.com/dataproc/docs/release-notes',
    'datastore': 'https://cloud.google.com/datastore/docs/release-notes',
    'memorystore-memcached': 'https://cloud.google.com/memorystore/docs/memcached/release-notes',
    'memorystore-redis': 'https://cloud.google.com/memorystore/docs/redis/release-notes',
    
    # Security & Identity
    'binary-authorization': 'https://cloud.google.com/binary-authorization/docs/release-notes',
    'certificate-authority': 'https://cloud.google.com/certificate-authority-service/docs/release-notes',
    'cloud-armor': 'https://cloud.google.com/armor/docs/release-notes',
    'cloud-kms': 'https://cloud.google.com/kms/docs/release-notes',
    'iam': 'https://cloud.google.com/iam/docs/release-notes',
    'identity-platform': 'https://cloud.google.com/identity-platform/docs/release-notes',
    'recaptcha': 'https://cloud.google.com/recaptcha-enterprise/docs/release-notes',
    'secret-manager': 'https://cloud.google.com/secret-manager/docs/release-notes',
    'security-command-center': 'https://cloud.google.com/security-command-center/docs/release-notes',
    'vpc-service-controls': 'https://cloud.google.com/vpc-service-controls/docs/release-notes',
    
    # Networking
    'cloud-cdn': 'https://cloud.google.com/cdn/docs/release-notes',
    'cloud-dns': 'https://cloud.google.com/dns/docs/release-notes',
    'cloud-interconnect': 'https://cloud.google.com/network-connectivity/docs/interconnect/release-notes',
    'load-balancing': 'https://cloud.google.com/load-balancing/docs/release-notes',
    'cloud-nat': 'https://cloud.google.com/nat/docs/release-notes',
    'cloud-router': 'https://cloud.google.com/network-connectivity/docs/router/release-notes',
    'service-mesh': 'https://cloud.google.com/service-mesh/docs/release-notes',
    'vpc': 'https://cloud.google.com/vpc/docs/release-notes',
    'network-intelligence': 'https://cloud.google.com/network-intelligence-center/docs/release-notes',
    'network-tiers': 'https://cloud.google.com/network-tiers/docs/release-notes',
    'service-directory': 'https://cloud.google.com/service-directory/docs/release-notes',
    
    # Storage
    'artifact-registry': 'https://cloud.google.com/artifact-registry/docs/release-notes',
    'cloud-storage': 'https://cloud.google.com/storage/docs/release-notes',
    'container-registry': 'https://cloud.google.com/container-registry/docs/release-notes',
    'filestore': 'https://cloud.google.com/filestore/docs/release-notes',
    'managed-lustre': 'https://cloud.google.com/parallelstore/docs/release-notes',
    'transfer-appliance': 'https://cloud.google.com/transfer-appliance/docs/release-notes',
    
    # Compute / Infrastructure
    'bare-metal': 'https://cloud.google.com/bare-metal/docs/release-notes',
    'cloud-hub': 'https://cloud.google.com/network-connectivity/docs/network-connectivity-center/release-notes',
    'cloud-tpu': 'https://cloud.google.com/tpu/docs/release-notes',
    'compute-engine': 'https://cloud.google.com/compute/docs/release-notes',
    'confidential-space': 'https://cloud.google.com/confidential-computing/confidential-space/docs/release-notes',
    'distributed-cloud-edge': 'https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes',
    'anthos-bare-metal': 'https://cloud.google.com/anthos/clusters/docs/bare-metal/latest/release-notes',
    'anthos-vmware': 'https://cloud.google.com/anthos/clusters/docs/on-prem/latest/release-notes',
    'vmware-engine': 'https://cloud.google.com/vmware-engine/docs/release-notes',
    
    # GKE
    'gke': 'https://cloud.google.com/kubernetes-engine/docs/release-notes',
    'gke-rapid': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid',
    'gke-regular': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-regular',
    'gke-stable': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-stable',
    'gke-extended': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-extended',
    'gke-nochannel': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-nochannel',
    
    # Management & Operations
    'cloud-logging': 'https://cloud.google.com/logging/docs/release-notes',
    'cloud-monitoring': 'https://cloud.google.com/monitoring/docs/release-notes',
    'cloud-observability': 'https://cloud.google.com/stackdriver/docs/release-notes',
    'cloud-profiler': 'https://cloud.google.com/profiler/docs/release-notes',
    'cloud-scheduler': 'https://cloud.google.com/scheduler/docs/release-notes',
    'config-connector': 'https://cloud.google.com/config-connector/docs/release-notes',
    'resource-manager': 'https://cloud.google.com/resource-manager/docs/release-notes',
    
    # AI & Machine Learning
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
    
    # Specialized & Other Services
    'cloud-composer': 'https://cloud.google.com/composer/docs/release-notes',
    'healthcare-api': 'https://cloud.google.com/healthcare-api/docs/release-notes',
    'blockchain-node-engine': 'https://cloud.google.com/blockchain-node-engine/docs/release-notes',
    
    # Workspace
    'apps-script': 'https://developers.google.com/apps-script/releases',
    'cloud-search': 'https://developers.google.com/cloud-search/docs/release-notes',
    'docs-api': 'https://developers.google.com/docs/api/release-notes',
    
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
            self.cutoff_date = datetime.now() - timedelta(days=days)
        elif months:
            self.cutoff_date = datetime.now() - timedelta(days=months * 30)
        else:
            # Default to 12 months
            self.months = 12
            self.cutoff_date = datetime.now() - timedelta(days=12 * 30)
        
        self.releases = []
        self.platform = self._detect_platform(url)
        self.is_xml_feed = self._is_xml_url(url)
        self.used_fallback = False
        
    def _detect_platform(self, url: str) -> str:
        """Detect the documentation platform based on URL."""
        if 'cloud.google.com' in url or 'developers.google.com' in url:
            return 'google_cloud'
        if 'firebase.google.com' in url:
            return 'firebase'
        return 'generic'
    
    def _is_xml_url(self, url: str) -> bool:
        """Check if the URL is an XML feed."""
        return url.endswith('.xml') or '/feeds/' in url
    
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
                            print(f"  XML feed not available, trying HTML fallback...", file=sys.stderr)
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
        
        # Direct HTML scraping
        return self._scrape_html(self.url, headers)
    
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
            
            # Use platform-specific parsing for Firebase
            if self.platform == 'firebase':
                self._parse_firebase_releases(content_area, selectors)
            else:
                # Try multiple strategies to find release notes
                self._parse_structured_releases(content_area, selectors)
            
            if not self.releases:
                self._parse_unstructured_releases(content_area, selectors)
            
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
        # Namespace handling for Atom
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
            date_elem = entry.find('atom:published', namespaces)
            if date_elem is None:
                date_elem = entry.find('published')
            if date_elem is None:
                date_elem = entry.find('atom:updated', namespaces)
            if date_elem is None:
                date_elem = entry.find('updated')
            if date_elem is None:
                date_elem = entry.find('pubDate')  # RSS format
            
            parsed_date = None
            date_str = ''
            if date_elem is not None and date_elem.text:
                date_str = date_elem.text
                parsed_date = self._parse_xml_date(date_str)
            
            # Get content
            content_elem = entry.find('atom:content', namespaces)
            if content_elem is None:
                content_elem = entry.find('content')
            if content_elem is None:
                content_elem = entry.find('atom:summary', namespaces)
            if content_elem is None:
                content_elem = entry.find('summary')
            if content_elem is None:
                content_elem = entry.find('description')  # RSS format
            
            content_text = ''
            if content_elem is not None:
                content_text = content_elem.text or ''
            
            # Get link
            link = ''
            link_elem = entry.find('atom:link', namespaces)
            if link_elem is None:
                link_elem = entry.find('link')
            if link_elem is not None:
                link = link_elem.get('href', '') or link_elem.text or ''
            
            if parsed_date:
                # Parse HTML content to extract items
                items = self._parse_xml_content(content_text, title)
                
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
    
    def _parse_xml_content(self, content: str, title: str = '') -> List[Dict]:
        """Parse HTML content from XML feed entry."""
        items = []
        
        if not content:
            if title:
                items.append({
                    'text': title,
                    'category': self._categorize_item(text=title),
                    'urls': []
                })
            return items
        
        # Parse HTML content
        soup = self.BeautifulSoup(content, 'html.parser')
        
        # Look for list items or paragraphs
        list_items = soup.find_all('li')
        if list_items:
            for li in list_items:
                text = li.get_text(strip=True)
                html_content = str(li)
                links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                if text and len(text) > 5:
                    items.append({
                        'text': html_content,
                        'category': self._categorize_item(element=li, text=text),
                        'urls': links
                    })
        
        # Also check for specific div classes
        release_divs = soup.find_all('div', class_=['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'])
        for div in release_divs:
            text = div.get_text(strip=True)
            html_content = str(div)
            links = [a.get('href') for a in div.find_all('a') if a.get('href')]
            if text and len(text) > 5:
                items.append({
                    'text': html_content,
                    'category': self._categorize_item(element=div, text=text),
                    'urls': links
                })
        
        # If no list items or divs found, use paragraphs
        if not items:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                html_content = str(p)
                links = [a.get('href') for a in p.find_all('a') if a.get('href')]
                if text and len(text) > 10:
                    items.append({
                        'text': html_content,
                        'category': self._categorize_item(element=p, text=text),
                        'urls': links
                    })
        
        # If still no items, use the whole content
        if not items:
            text = soup.get_text(strip=True)
            if text and len(text) > 10:
                items.append({
                    'text': content,
                    'category': self._categorize_item(text=text),
                    'urls': [a.get('href') for a in soup.find_all('a') if a.get('href')]
                })
        
        return items
    
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
                            
                            while sibling and sibling.name not in selectors['date_headers']:
                                # Check for specific release divs
                                div_classes = sibling.get('class', [])
                                if any(cls in ['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'] for cls in div_classes):
                                    text_content = str(sibling) # Get full HTML
                                    text = sibling.get_text(strip=True)
                                    links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
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
        # Parse HTML and get text
        soup = self.BeautifulSoup(html_text, 'html.parser')
        
        # Replace <a> tags with their text + URL in parentheses
        for a in soup.find_all('a'):
            href = a.get('href', '')
            link_text = a.get_text(strip=True)
            if href and link_text:
                a.replace_with(f"{link_text}")
        
        # Get text with separator to preserve word boundaries
        text = soup.get_text(separator=' ', strip=True)
        
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
                output.append("│" + f"  📅 {date_str}".ljust(78) + "│")
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
        output.append("│" + "  📊 STATISTICS".ljust(78) + "│")
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
        choices=list(SERVICE_GROUPS.keys()),
        metavar='GROUP',
        help='Service group to query (use --list-groups to see all options)'
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
        services = SERVICE_GROUPS[args.group]
        urls = [SERVICE_FEEDS[s] for s in services]
        service_names = services
    elif args.url:
        urls = [args.url]
        service_names = ['custom']
    else:
        parser.error("Either --service, --group, or --url is required (use --list-services or --list-groups to see options)")
    
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
    
    if args.verbose:
        if len(urls) > 1:
            print(f"Scraping {len(urls)} services in group '{args.group}':", file=sys.stderr)
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
        format_scraper.group_name = args.group
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

