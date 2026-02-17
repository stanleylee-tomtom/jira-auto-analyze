#!/usr/bin/env python3
"""Test Jira REST API connection."""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

cloud_id = os.getenv('ATLASSIAN_CLOUD_ID')
api_token = os.getenv('ATLASSIAN_API_TOKEN')
email = os.getenv('ATLASSIAN_EMAIL')
base_url = os.getenv('JIRA_SITE_URL', f'https://{cloud_id}')

print(f"Testing connection to: {base_url}")
print(f"Cloud ID: {cloud_id}")
print(f"Email: {email}")
print(f"Token: {api_token[:20]}...")

# Test 1: Check if site is reachable
print("\n1. Testing site reachability...")
try:
    response = requests.get(f"{base_url}/rest/api/3/myself", 
                           auth=HTTPBasicAuth(email, api_token),
                           headers={'Accept': 'application/json'},
                           timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Authenticated as: {data.get('displayName')}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")

# Test 2: Search for recent issues
print("\n2. Searching for recent issues...")
try:
    response = requests.get(
        f"{base_url}/rest/api/3/search",
        auth=HTTPBasicAuth(email, api_token),
        headers={'Accept': 'application/json'},
        params={'jql': 'order by created DESC', 'maxResults': 5},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        issues = data.get('issues', [])
        print(f"   ✓ Found {len(issues)} issues:")
        for issue in issues:
            print(f"     - {issue['key']}: {issue['fields']['summary']}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Search failed: {e}")

# Test 3: Try specific ticket
print("\n3. Testing specific ticket GOSDK-196630...")
try:
    response = requests.get(
        f"{base_url}/rest/api/3/issue/GOSDK-196630",
        auth=HTTPBasicAuth(email, api_token),
        headers={'Accept': 'application/json'},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found: {data['fields']['summary']}")
    elif response.status_code == 404:
        print(f"   ✗ Ticket does not exist or you don't have permission")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Fetch failed: {e}")

# Test 4: List projects
print("\n4. Listing available projects...")
try:
    response = requests.get(
        f"{base_url}/rest/api/3/project",
        auth=HTTPBasicAuth(email, api_token),
        headers={'Accept': 'application/json'},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"   ✓ Found {len(projects)} projects:")
        for proj in projects[:10]:
            print(f"     - {proj['key']}: {proj['name']}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
