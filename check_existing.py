#!/usr/bin/env python3
"""Quick check of existing components on the ServiceNow instance."""
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

# Check existing custom tables
print('=== existing u_ tables ===')
r = api('GET', 'table/sys_db_object', {
    'sysparm_limit': 50,
    'sysparm_query': 'nameSTARTSWITHu_^ORnameSTARTSWITHx_',
    'sysparm_fields': 'name,label'
})
for t in r.get('result', []):
    print(f'  {t["name"]}: {t.get("label","")}')

# Check existing catalog items
print('\n=== existing Network Request catalog items ===')
r = api('GET', 'table/sc_cat_item', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameCONTAINSNetwork',
    'sysparm_fields': 'sys_id,name,sys_name'
})
for t in r.get('result', []):
    print(f'  {t["name"]}: {t.get("sys_id","")}')

# Check existing flows
print('\n=== existing flows ===')
r = api('GET', 'table/sys_hub_flow', {
    'sysparm_limit': 5,
    'sysparm_query': 'nameCONTAINSNetwork',
    'sysparm_fields': 'sys_id,name'
})
for t in r.get('result', []):
    print(f'  {t["name"]}: {t.get("sys_id","")}')

# Check existing notifications
print('\n=== existing Network email notifications ===')
r = api('GET', 'table/sysevent_email_action', {
    'sysparm_limit': 10,
    'sysparm_query': 'nameCONTAINSNetwork',
    'sysparm_fields': 'sys_id,name'
})
for t in r.get('result', []):
    print(f'  {t["name"]}: {t.get("sys_id","")}')

# Check existing business rules
print('\n=== existing Network business rules ===')
r = api('GET', 'table/sys_script', {
    'sysparm_limit': 10,
    'sysparm_query': 'nameCONTAINSNetwork',
    'sysparm_fields': 'sys_id,name,collection'
})
for t in r.get('result', []):
    print(f'  {t["name"]} ({t.get("collection","")}): {t.get("sys_id","")}')

print('\nDone.')
