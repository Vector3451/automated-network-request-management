#!/usr/bin/env python3
"""Quick targeted check for existing Network Request components."""
import json, ssl, base64
from http.client import HTTPSConnection
from urllib.parse import urlencode

instance = 'https://dev402064.service-now.com'
auth = base64.b64encode(b'admin:Qxbj4z-HF5S=').decode()
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api(method, path, body=None, params=None):
    host = instance.replace('https://','')
    conn = HTTPSConnection(host, context=ctx)
    url = f'/api/now/{path}'
    if params:
        url += '?' + urlencode(params, doseq=True)
    body = json.dumps(body) if body else None
    conn.request(method, url, body=body, headers={
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    resp = conn.getresponse()
    data = resp.read().decode()
    if 'Instance Hibernating' in data:
        print('ERROR: Instance is hibernating!')
        return {'error': 'hibernating'}
    try:
        return json.loads(data)
    except:
        return {'raw': data[:500], 'status': resp.status}

# Check specific tables
for tbl in ['u_network_request', 'u_network_task', 'u_network_database']:
    r = api('GET', 'table/sys_db_object', {
        'sysparm_limit': 1,
        'sysparm_query': f'name={tbl}',
        'sysparm_fields': 'name,label'
    })
    exists = bool(r.get('result'))
    print(f'Table {tbl}: {"EXISTS" if exists else "NOT FOUND"}')

# Check catalog items
r = api('GET', 'table/sc_cat_item', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameLIKE Network Request',
    'sysparm_fields': 'sys_id,name'
})
print(f'Catalog items: {len(r.get("result", []))}')

# Check flows
r = api('GET', 'table/sys_hub_flow', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameLIKE Network',
    'sysparm_fields': 'sys_id,name,active'
})
print(f'Flows: {json.dumps(r.get("result", []), indent=2)}')

# Check notifications
r = api('GET', 'table/sysevent_email_action', {
    'sysparm_limit': 10,
    'sysparm_query': 'nameLIKE Network',
    'sysparm_fields': 'sys_id,name'
})
print(f'Email notifications: {len(r.get("result", []))}')

# Check business rules
r = api('GET', 'table/sys_script', {
    'sysparm_limit': 10,
    'sysparm_query': 'nameLIKE Network',
    'sysparm_fields': 'sys_id,name,collection'
})
print(f'Business rules: {json.dumps(r.get("result", []), indent=2)}')

# Check Fix Scripts to clean up any test data
r = api('GET', 'table/sys_script_fix', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameLIKE exec_client_script',
    'sysparm_fields': 'sys_id,name'
})
print(f'Stale fix scripts: {len(r.get("result", []))}')

# Check service portal widgets
r = api('GET', 'table/sp_widget', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameLIKE Network',
    'sysparm_fields': 'sys_id,name'
})
print(f'SP widgets: {json.dumps(r.get("result", []), indent=2)}')
