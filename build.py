#!/usr/bin/env python3
"""
Automated Network Request Management - Build Script
Creates all ServiceNow components for the network request management system.
"""

import json
import sys
import os
import time

# Add the sn_terminal directory to path so we can import SNClient
sys.path.insert(0, os.path.expanduser("~"))

from http.client import HTTPSConnection
from urllib.parse import urlencode, quote
import ssl
import base64


class SNClient:
    def __init__(self, instance, user, password):
        self.instance = instance.rstrip("/")
        self.user = user
        self.password = password

    def _request(self, method, path, body=None, params=None):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        host = self.instance.replace("https://", "").replace("http://", "")
        conn = HTTPSConnection(host, context=ctx)
        auth = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = f"/api/now/{path}"
        if params:
            url += "?" + urlencode(params, doseq=True)
        if body is not None:
            body = json.dumps(body)
        conn.request(method, url, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode()
        if "Instance Hibernating" in data or "developer.servicenow.com/dev.do" in data:
            return {"error": "Instance is hibernating", "status": "hibernating"}
        try:
            return json.loads(data)
        except Exception:
            return {"raw": data, "status": resp.status}

    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, body):
        return self._request("POST", path, body=body)

    def put(self, path, body):
        return self._request("PUT", path, body=body)

    def delete(self, path):
        return self._request("DELETE", path)

    def create_table(self, name, label, super_class=""):
        data = {
            "name": name,
            "label": label,
            "super_class": super_class,
            "access": "public",
            "create_access": "false",
            "alter_access": "false",
            "delete_access": "false",
            "read_access": "true",
            "update_access": "false",
            "is_extendable": "false",
            "create_access_controls": "false",
            "client_scripts_access": "false",
            "actions_access": "false",
            "configuration_access": "false",
            "is_data_interface": "false",
            "live_feed_enabled": "false",
            "is_df_table": "false",
            "scriptable_table": "false",
            "ws_access": "true",
        }
        return self.post("table/sys_db_object", data)

    def add_field(self, table, field_name, field_type="string", label="", max_length=255, reference="", choice=""):
        data = {
            "name": table,
            "element": field_name,
            "internal_type": field_type,
            "label": label or field_name,
            "max_length": max_length,
        }
        if reference:
            data["reference"] = reference
        if choice:
            data["choice"] = choice
        return self.post("table/sys_dictionary", data)

    def table_exists(self, name):
        r = self.get("table/sys_db_object", params={
            "sysparm_limit": 1,
            "sysparm_query": f"name={name}",
            "sysparm_fields": "name",
        })
        results = r.get("result", [])
        return len(results) > 0

    def field_exists(self, table, field):
        r = self.get("table/sys_dictionary", params={
            "sysparm_limit": 1,
            "sysparm_query": f"name={table}^element={field}",
            "sysparm_fields": "element",
        })
        results = r.get("result", [])
        return len(results) > 0

    def get_choice_list(self, table, field):
        return self.get("table/sys_choice", params={
            "sysparm_limit": 100,
            "sysparm_query": f"name={table}^element={field}^inactive=false",
            "sysparm_fields": "value,label,sequence",
            "sysparm_order_by": "sequence",
        })

    def create_choice(self, table, field, value, label, sequence=0):
        return self.post("table/sys_choice", {
            "name": table,
            "element": field,
            "value": value,
            "label": label,
            "sequence": sequence,
            "inactive": False,
        })


def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    prefix = {"INFO": "[+]", "WARN": "[!]", "ERR": "[X]", "SKIP": "[-]"}
    print(f"{ts} {prefix.get(level, '[?]')} {msg}")


def check_result(r, action_name):
    if isinstance(r, dict) and "error" in r:
        log(f"{action_name} FAILED: {r['error']}", "ERR")
        return False
    result = r.get("result", {})
    if isinstance(result, dict) and result.get("sys_id"):
        log(f"{action_name} OK (sys_id: {result['sys_id'][:8]}...)")
    else:
        log(f"{action_name} OK")
    return True


# ============================================================
# MAIN BUILD
# ============================================================

def main():
    INSTANCE = "https://dev402064.service-now.com"
    USER = "admin"
    PASS = "Qxbj4z-HF5S="

    sn = SNClient(INSTANCE, USER, PASS)

    # Test connection
    log("Testing connection...")
    test = sn.get("table/sys_user", params={"sysparm_limit": 1})
    if isinstance(test, dict) and "error" in test:
        log(f"Connection failed: {test['error']}", "ERR")
        sys.exit(1)
    log("Connected successfully!")

    # ========================================
    # PHASE 2: DATA ARCHITECTURE - TABLES
    # ========================================
    log("=" * 60)
    log("PHASE 2: Creating Data Architecture")
    log("=" * 60)

    # --- Table 1: u_network_request (main request table) ---
    log("\n--- Creating u_network_request table ---")
    TABLE_REQUEST = "u_network_request"

    if not sn.table_exists(TABLE_REQUEST):
        r = sn.create_table(TABLE_REQUEST, "Network Request")
        check_result(r, "Create table u_network_request")
        time.sleep(1)
    else:
        log("Table u_network_request already exists, skipping creation", "SKIP")

    # Fields for u_network_request
    request_fields = [
        # (field_name, type, label, max_length, reference)
        ("u_request_type", "string", "Request Type", 100, ""),
        ("u_access_level", "string", "Access Level", 100, ""),
        ("u_device", "string", "Device", 255, ""),
        ("u_device_other", "string", "Device (Other Description)", 500, ""),
        ("u_business_justification", "string", "Business Justification", 4000, ""),
        ("u_urgency", "string", "Urgency", 40, ""),
        ("u_portal_details", "string", "Portal Details", 1000, ""),
        ("u_requested_for", "reference", "Requested For", 0, "sys_user"),
        ("u_requested_for_email", "string", "Requester Email", 100, ""),
        ("u_requested_for_phone", "string", "Requester Phone", 40, ""),
        ("u_requested_for_username", "string", "Requester Username", 100, ""),
        ("u_approval_state", "string", "Approval State", 40, ""),
        ("u_approver", "reference", "Approver", 0, "sys_user"),
        ("u_approval_notes", "string", "Approval Notes", 4000, ""),
        ("u_network_group", "reference", "Network Group", 0, "sys_user_group"),
        ("u_department", "string", "Department", 100, ""),
        ("u_location", "reference", "Location", 0, "cmn_location"),
        ("u_short_description", "string", "Short Description", 255, ""),
        ("u_description", "string", "Description", 4000, ""),
    ]

    for field_name, ftype, label, max_len, ref in request_fields:
        if not sn.field_exists(TABLE_REQUEST, field_name):
            r = sn.add_field(TABLE_REQUEST, field_name, ftype, label, max_len, ref)
            check_result(r, f"  Add field {field_name}")
            time.sleep(0.3)
        else:
            log(f"  Field {field_name} exists, skipping", "SKIP")

    # --- Table 2: u_network_task (fulfillment tasks) ---
    log("\n--- Creating u_network_task table ---")
    TABLE_TASK = "u_network_task"

    if not sn.table_exists(TABLE_TASK):
        r = sn.create_table(TABLE_TASK, "Network Task", super_class="task")
        check_result(r, "Create table u_network_task")
        time.sleep(1)
    else:
        log("Table u_network_task already exists, skipping creation", "SKIP")

    # Fields for u_network_task (extends task, so number, state, assignment_group, etc. exist)
    task_fields = [
        ("u_network_request", "reference", "Network Request", 0, "u_network_request"),
        ("u_task_type", "string", "Task Type", 100, ""),
        ("u_configuration_item", "reference", "Configuration Item", 0, "cmdb_ci"),
        ("u_work_notes", "string", "Work Notes", 4000, ""),
        ("u_implementation_plan", "string", "Implementation Plan", 4000, ""),
        ("u_rollback_plan", "string", "Rollback Plan", 4000, ""),
    ]

    for field_name, ftype, label, max_len, ref in task_fields:
        if not sn.field_exists(TABLE_TASK, field_name):
            r = sn.add_field(TABLE_TASK, field_name, ftype, label, max_len, ref)
            check_result(r, f"  Add field {field_name}")
            time.sleep(0.3)
        else:
            log(f"  Field {field_name} exists, skipping", "SKIP")

    # --- Add Choice Lists ---
    log("\n--- Adding Choice Lists ---")

    # Request Type choices
    request_types = [
        ("firewall_rule", "Firewall Rule Change"),
        ("vlan_config", "VLAN Configuration"),
        ("access_port", "Access Port Configuration"),
        ("routing_change", "Routing Change"),
        ("dns_change", "DNS Change"),
        ("load_balancer", "Load Balancer Change"),
        ("vpn_tunnel", "VPN Tunnel"),
        ("other", "Other"),
    ]
    for val, lbl in request_types:
        existing = sn.get_choice_list(TABLE_REQUEST, "u_request_type")
        existing_vals = [c["value"] for c in existing.get("result", [])]
        if val not in existing_vals:
            r = sn.create_choice(TABLE_REQUEST, "u_request_type", val, lbl, request_types.index((val, lbl)) * 10)
            check_result(r, f"  Choice u_request_type: {val}")
            time.sleep(0.2)
        else:
            log(f"  Choice {val} exists, skipping", "SKIP")

    # Access Level choices
    access_levels = [
        ("read_only", "Read Only"),
        ("read_write", "Read/Write"),
        ("admin", "Admin"),
        ("deny", "Deny"),
    ]
    for val, lbl in access_levels:
        existing = sn.get_choice_list(TABLE_REQUEST, "u_access_level")
        existing_vals = [c["value"] for c in existing.get("result", [])]
        if val not in existing_vals:
            r = sn.create_choice(TABLE_REQUEST, "u_access_level", val, lbl, access_levels.index((val, lbl)) * 10)
            check_result(r, f"  Choice u_access_level: {val}")
            time.sleep(0.2)
        else:
            log(f"  Choice {val} exists, skipping", "SKIP")

    # Urgency choices
    urgencies = [
        ("critical", "Critical"),
        ("high", "High"),
        ("moderate", "Moderate"),
        ("low", "Low"),
    ]
    for val, lbl in urgencies:
        existing = sn.get_choice_list(TABLE_REQUEST, "u_urgency")
        existing_vals = [c["value"] for c in existing.get("result", [])]
        if val not in existing_vals:
            r = sn.create_choice(TABLE_REQUEST, "u_urgency", val, lbl, urgencies.index((val, lbl)) * 10)
            check_result(r, f"  Choice u_urgency: {val}")
            time.sleep(0.2)
        else:
            log(f"  Choice {val} exists, skipping", "SKIP")

    # ========================================
    # PHASE 3: SERVICE CATALOG
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 3: Creating Service Catalog Item")
    log("=" * 60)

    # Check if catalog item already exists
    cat_check = sn.get("table/sc_cat_item", params={
        "sysparm_limit": 1,
        "sysparm_query": "name=Network Request^ORshort_description=Network Request",
        "sysparm_fields": "sys_id,name",
    })
    existing_cat = cat_check.get("result", [])

    if not existing_cat:
        catalog_item = {
            "name": "Network Request",
            "short_description": "Submit a network change or access request",
            "description": "Use this catalog item to request network changes including firewall rules, VLAN configurations, access port changes, routing changes, DNS modifications, and VPN tunnel setups. All requests require approval before fulfillment.",
            "category": "Hardware",  # default, can be changed
            "type": "item",
            "active": True,
            "no_order_now": False,
            "availability": "desktop",
        }
        r = sn.post("table/sc_cat_item", catalog_item)
        if check_result(r, "Create catalog item 'Network Request'"):
            cat_sys_id = r["result"]["sys_id"]
        else:
            cat_sys_id = None
    else:
        cat_sys_id = existing_cat[0]["sys_id"]
        log("Catalog item 'Network Request' already exists", "SKIP")

    time.sleep(1)

    # ========================================
    # PHASE 3: VARIABLES FOR CATALOG ITEM
    # ========================================
    if cat_sys_id:
        log("\n--- Creating Catalog Variables ---")

        variables = [
            # (name, type, question, mandatory, order, include_none)
            ("request_type", "Select Box", "What type of network request is this?", True, 100, True),
            ("access_level", "Select Box", "What level of access is required?", True, 200, True),
            ("device", "Select Box", "Which device does this apply to?", True, 300, True),
            ("device_other", "String", "If 'Other', please specify the device", False, 350, False),
            ("business_justification", "Multi Line Text", "Please provide a business justification for this request", True, 400, False),
            ("urgency", "Select Box", "What is the urgency of this request?", True, 500, True),
            ("portal_details", "String", "Additional portal or service details", False, 600, False),
            ("short_description", "String", "Short description of the request", True, 700, False),
        ]

        for var_name, var_type, question, mandatory, order, include_none in variables:
            # Check if variable exists
            var_check = sn.get("table/item_option_new", params={
                "sysparm_limit": 1,
                "sysparm_query": f"cat_item={cat_sys_id}^name={var_name}",
                "sysparm_fields": "sys_id,name",
            })
            if var_check.get("result"):
                log(f"  Variable {var_name} exists, skipping", "SKIP")
                continue

            var_data = {
                "cat_item": cat_sys_id,
                "name": var_name,
                "question_text": question,
                "type": var_type,
                "mandatory": mandatory,
                "order": order,
                "include_none": include_none,
                "active": True,
            }

            # Map variable types to ServiceNow type values
            type_map = {
                "String": "3",
                "Select Box": "7",
                "Multi Line Text": "4",
                "Yes/No": "1",
                "Date": "8",
                "Reference": "11",
                "Checkbox": "2",
            }
            var_data["type"] = type_map.get(var_type, "3")

            r = sn.post("table/item_option_new", var_data)
            check_result(r, f"  Create variable: {var_name}")
            time.sleep(0.3)

        # --- Reference variables for auto-population ---
        log("\n--- Creating Reference Variables (auto-populate) ---")

        ref_vars = [
            ("requested_for", "Requested For", "sys_user", "200"),
            ("requester_email", "Requester Email", "sys_user", "210"),
            ("requester_phone", "Requester Phone", "sys_user", "220"),
            ("requester_username", "Requester Username", "sys_user", "230"),
        ]

        for var_name, question, ref_table, order in ref_vars:
            var_check = sn.get("table/item_option_new", params={
                "sysparm_limit": 1,
                "sysparm_query": f"cat_item={cat_sys_id}^name={var_name}",
                "sysparm_fields": "sys_id,name",
            })
            if var_check.get("result"):
                log(f"  Ref variable {var_name} exists, skipping", "SKIP")
                continue

            var_data = {
                "cat_item": cat_sys_id,
                "name": var_name,
                "question_text": question,
                "type": "11",  # Reference
                "reference": ref_table,
                "mandatory": False,
                "order": int(order),
                "active": True,
            }
            r = sn.post("table/item_option_new", var_data)
            check_result(r, f"  Create ref variable: {var_name}")
            time.sleep(0.3)

    # ========================================
    # PHASE 3: UI POLICIES
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 3: Creating UI Policies")
    log("=" * 60)

    # UI Policy: Show u_device_other when device = 'other'
    ui_policy_check = sn.get("table/catalog_ui_policy", params={
        "sysparm_limit": 5,
        "sysparm_query": f"catalog_item={cat_sys_id}^short_description=Show device other",
        "sysparm_fields": "sys_id",
    })

    if not ui_policy_check.get("result"):
        ui_policy = {
            "catalog_item": cat_sys_id,
            "short_description": "Show device other when device=other",
            "active": True,
            "reverse": False,
            "on_load": True,
            "conditions": [
                {
                    "catalog_item": cat_sys_id,
                    "name": "device",
                    "oper": "=",
                    "value": "other",
                }
            ],
            "actions": [
                {
                    "catalog_item": cat_sys_id,
                    "name": "device_other",
                    "mandatory": True,
                    "visible": True,
                }
            ],
        }
        # Use the catalog_ui_policy API
        r = sn.post("table/catalog_ui_policy", {
            "catalog_item": cat_sys_id,
            "short_description": "Show device other when device=other",
            "active": True,
            "reverse": False,
            "on_load": True,
        })
        if check_result(r, "UI Policy: show device_other"):
            policy_id = r["result"]["sys_id"]
            # Add conditions and actions via separate tables
            # catalog_ui_policy_action for visibility
            action_r = sn.post("table/catalog_ui_policy_action", {
                "ui_policy": policy_id,
                "catalog_item": cat_sys_id,
                "variable_name": "device_other",
                "mandatory": True,
                "visible": True,
                "order": 100,
            })
            check_result(action_r, "  UI Policy Action: device_other visible")
            time.sleep(0.3)
    else:
        log("UI Policy for device_other already exists", "SKIP")

    # ========================================
    # PHASE 2: FLOW DESIGNER FLOW
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 2: Creating Flow Designer Flow")
    log("=" * 60)

    # Check if flow already exists
    flow_check = sn.get("table/sys_hub_flow", params={
        "sysparm_limit": 1,
        "sysparm_query": "name=Network Request Automation",
        "sysparm_fields": "sys_id,name",
    })

    if not flow_check.get("result"):
        flow_data = {
            "name": "Network Request Automation",
            "description": "Automated flow for network request management: validates requests, routes for approval, creates fulfillment tasks, and sends notifications.",
            "active": True,
            "table": TABLE_REQUEST,
            "type": "flow",
        }
        r = sn.post("table/sys_hub_flow", flow_data)
        if check_result(r, "Create flow 'Network Request Automation'"):
            flow_sys_id = r["result"]["sys_id"]
        else:
            flow_sys_id = None
    else:
        flow_sys_id = flow_check["result"][0]["sys_id"]
        log("Flow 'Network Request Automation' already exists", "SKIP")

    time.sleep(1)

    # ========================================
    # PHASE 2: EMAIL NOTIFICATIONS
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 2: Creating Email Notifications")
    log("=" * 60)

    notifications = [
        {
            "name": "Network Request - Submitted",
            "description": "Sent to requester when a network request is submitted",
            "table": TABLE_REQUEST,
            "event_name": "network_request.submitted",
            "message_subject": "Network Request ${number} has been submitted",
            "message_html": """<p>Hello ${u_requested_for},</p>
<p>Your network request <strong>${number}</strong> has been submitted successfully.</p>
<p><strong>Request Type:</strong> ${u_request_type}<br/>
<strong>Urgency:</strong> ${u_urgency}<br/>
<strong>Status:</strong> Awaiting Approval</p>
<p>You will be notified when your request is reviewed.</p>
<p>Thank you,<br/>Network Operations Team</p>""",
            "recipient_field": "u_requested_for",
        },
        {
            "name": "Network Request - Approval Required",
            "description": "Sent to approver when approval is needed",
            "table": TABLE_REQUEST,
            "event_name": "network_request.approval_required",
            "message_subject": "Approval Required: Network Request ${number}",
            "message_html": """<p>Hello,</p>
<p>A network request requires your approval.</p>
<p><strong>Request Number:</strong> ${number}<br/>
<strong>Requested By:</strong> ${u_requested_for}<br/>
<strong>Request Type:</strong> ${u_request_type}<br/>
<strong>Urgency:</strong> ${u_urgency}<br/>
<strong>Business Justification:</strong> ${u_business_justification}</p>
<p>Please review and approve or reject this request.</p>
<p>Thank you</p>""",
            "recipient_field": "u_approver",
        },
        {
            "name": "Network Request - Approved",
            "description": "Sent to requester when request is approved",
            "table": TABLE_REQUEST,
            "event_name": "network_request.approved",
            "message_subject": "Network Request ${number} has been approved",
            "message_html": """<p>Hello ${u_requested_for},</p>
<p>Your network request <strong>${number}</strong> has been <strong>approved</strong>.</p>
<p>The network team has been notified and will begin fulfillment shortly.</p>
<p>You will receive updates as the task progresses.</p>
<p>Thank you,<br/>Network Operations Team</p>""",
            "recipient_field": "u_requested_for",
        },
        {
            "name": "Network Request - Rejected",
            "description": "Sent to requester when request is rejected",
            "table": TABLE_REQUEST,
            "event_name": "network_request.rejected",
            "message_subject": "Network Request ${number} has been rejected",
            "message_html": """<p>Hello ${u_requested_for},</p>
<p>Your network request <strong>${number}</strong> has been <strong>rejected</strong>.</p>
<p><strong>Reason:</strong> ${u_approval_notes}</p>
<p>If you have questions, please contact the network team.</p>
<p>Thank you</p>""",
            "recipient_field": "u_requested_for",
        },
        {
            "name": "Network Request - Task Assigned",
            "description": "Sent to network team when a task is assigned",
            "table": TABLE_TASK,
            "event_name": "network_task.assigned",
            "message_subject": "New Network Task Assigned: ${number}",
            "message_html": """<p>Hello,</p>
<p>A new network task has been assigned to your team.</p>
<p><strong>Task:</strong> ${number}<br/>
<strong>Request:</strong> ${u_network_request}<br/>
<strong>Task Type:</strong> ${u_task_type}<br/>
<strong>Priority:</strong> ${priority}</p>
<p>Please review and begin work on this task.</p>
<p>Thank you,<br/>Network Operations</p>""",
            "recipient_field": "assignment_group",
        },
        {
            "name": "Network Request - Completed",
            "description": "Sent to requester when request is fulfilled",
            "table": TABLE_REQUEST,
            "event_name": "network_request.completed",
            "message_subject": "Network Request ${number} has been completed",
            "message_html": """<p>Hello ${u_requested_for},</p>
<p>Your network request <strong>${number}</strong> has been <strong>completed</strong>.</p>
<p>All fulfillment tasks have been finished. If you experience any issues, please submit a new request.</p>
<p>Thank you,<br/>Network Operations Team</p>""",
            "recipient_field": "u_requested_for",
        },
    ]

    for notif in notifications:
        existing = sn.get("table/sysevent_email_action", params={
            "sysparm_limit": 1,
            "sysparm_query": f"name={notif['name']}",
            "sysparm_fields": "sys_id,name",
        })
        if existing.get("result"):
            log(f"  Notification '{notif['name']}' exists, skipping", "SKIP")
            continue

        notif_data = {
            "name": notif["name"],
            "description": notif["description"],
            "table": notif["table"],
            "event_name": notif["event_name"],
            "message_subject": notif["message_subject"],
            "message": notif["message_html"],
            "recipient_field": notif["recipient_field"],
            "active": True,
            "insert": True,
        }
        r = sn.post("table/sysevent_email_action", notif_data)
        check_result(r, f"Create notification: {notif['name']}")
        time.sleep(0.3)

    # ========================================
    # PHASE 2: BUSINESS RULES
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 2: Creating Business Rules")
    log("=" * 60)

    # Business Rule: Auto-populate requester info on catalog item
    br_check = sn.get("table/sys_script", params={
        "sysparm_limit": 1,
        "sysparm_query": f"name=Network Request - Auto Populate Requester^collection={TABLE_REQUEST}",
        "sysparm_fields": "sys_id",
    })

    if not br_check.get("result"):
        br_data = {
            "name": "Network Request - Auto Populate Requester",
            "collection": TABLE_REQUEST,
            "when": "before",
            "insert": True,
            "update": False,
            "active": True,
            "order": 100,
            "script": """(function executeRule(current, previous /*null when async*/) {
    // Auto-populate requester fields from logged-in user
    var userGR = gs.getUser();
    current.u_requested_for = userGR.getUniqueValue();
    current.u_requested_for_email = userGR.getEmail();
    current.u_requested_for_phone = userGR.getRecord().getValue('phone') || '';
    current.u_requested_for_username = userGR.getUserName();
    current.u_department = userGR.getRecord().getValue('department') || '';
})(current, previous);""",
            "description": "Auto-populates requester information from the logged-in user's profile",
        }
        r = sn.post("table/sys_script", br_data)
        check_result(r, "Business Rule: Auto Populate Requester")
        time.sleep(0.5)
    else:
        log("Business Rule 'Auto Populate Requester' exists", "SKIP")

    # Business Rule: Set approval state on insert
    br_check2 = sn.get("table/sys_script", params={
        "sysparm_limit": 1,
        "sysparm_query": f"name=Network Request - Set Initial State^collection={TABLE_REQUEST}",
        "sysparm_fields": "sys_id",
    })

    if not br_check2.get("result"):
        br_data2 = {
            "name": "Network Request - Set Initial State",
            "collection": TABLE_REQUEST,
            "when": "before",
            "insert": True,
            "update": False,
            "active": True,
            "order": 200,
            "script": """(function executeRule(current, previous /*null when async*/) {
    // Set initial approval state
    current.u_approval_state = 'pending';
    current.approval = 'requested';
})(current, previous);""",
            "description": "Sets the initial approval state to pending when a new request is created",
        }
        r = sn.post("table/sys_script", br_data2)
        check_result(r, "Business Rule: Set Initial State")
        time.sleep(0.5)
    else:
        log("Business Rule 'Set Initial State' exists", "SKIP")

    # Business Rule: Create fulfillment task on approval
    br_check3 = sn.get("table/sys_script", params={
        "sysparm_limit": 1,
        "sysparm_query": f"name=Network Request - Create Fulfillment Task^collection={TABLE_REQUEST}",
        "sysparm_fields": "sys_id",
    })

    if not br_check3.get("result"):
        br_data3 = {
            "name": "Network Request - Create Fulfillment Task",
            "collection": TABLE_REQUEST,
            "when": "after",
            "insert": False,
            "update": True,
            "active": True,
            "order": 300,
            "script": """(function executeRule(current, previous /*null when async*/) {
    // When approval changes to 'approved', create a fulfillment task
    if (current.u_approval_state == 'approved' && previous.u_approval_state != 'approved') {
        var taskGR = new GlideRecord('u_network_task');
        taskGR.initialize();
        taskGR.u_network_request = current.sys_id;
        taskGR.u_task_type = current.u_request_type;
        taskGR.short_description = 'Fulfill network request: ' + current.u_request_type;
        taskGR.description = current.u_business_justification;
        taskGR.assignment_group = current.u_network_group;
        taskGR.priority = current.u_urgency == 'critical' ? 1 : current.u_urgency == 'high' ? 2 : current.u_urgency == 'moderate' ? 3 : 4;
        taskGR.insert();
        
        // Update request status
        current.state = '2'; // In Progress
        current.update();
    }
    
    // When approval changes to 'rejected'
    if (current.u_approval_state == 'rejected' && previous.u_approval_state != 'rejected') {
        current.state = '-5'; // Closed Incomplete
        current.update();
    }
})(current, previous);""",
            "description": "Creates a fulfillment task when the network request is approved",
        }
        r = sn.post("table/sys_script", br_data3)
        check_result(r, "Business Rule: Create Fulfillment Task")
        time.sleep(0.5)
    else:
        log("Business Rule 'Create Fulfillment Task' exists", "SKIP")

    # ========================================
    # PHASE 3: CLIENT SCRIPTS for dynamic form
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 3: Creating Client Scripts")
    log("=" * 60)

    # Catalog Client Script: Dynamic field visibility
    cs_check = sn.get("table/sys_script_client", params={
        "sysparm_limit": 1,
        "sysparm_query": f"name=Network Request - Dynamic Fields^cat_item={cat_sys_id}",
        "sysparm_fields": "sys_id",
    })

    if not cs_check.get("result"):
        cs_data = {
            "name": "Network Request - Dynamic Fields",
            "cat_item": cat_sys_id,
            "table": TABLE_REQUEST,
            "type": "onChange",
            "field_name": "device",
            "script": """function onChange(control, oldValue, newValue, isLoading, isTemplate) {
    if (isLoading || newValue == '') {
        return;
    }
    
    // Show/hide device_other field based on selection
    if (newValue == 'other') {
        g_form.setVisible('device_other', true);
        g_form.setMandatory('device_other', true);
    } else {
        g_form.setVisible('device_other', false);
        g_form.setMandatory('device_other', false);
        g_form.setValue('device_other', '');
    }
}""",
            "active": True,
            "order": 100,
        }
        r = sn.post("table/sys_script_client", cs_data)
        check_result(r, "Client Script: Dynamic Fields")
        time.sleep(0.5)
    else:
        log("Client Script 'Dynamic Fields' exists", "SKIP")

    # ========================================
    # PHASE 3: SERVICE PORTAL WIDGET (optional)
    # ========================================
    log("\n" + "=" * 60)
    log("PHASE 3: Creating Service Portal Widget")
    log("=" * 60)

    widget_check = sn.get("table/sp_widget", params={
        "sysparm_limit": 1,
        "sysparm_query": "name=Network Request Dashboard",
        "sysparm_fields": "sys_id",
    })

    if not widget_check.get("result"):
        widget_data = {
            "name": "Network Request Dashboard",
            "title": "Network Request Dashboard",
            "template": """<div class="panel panel-default">
  <div class="panel-heading">
    <h3 class="panel-title">${Network Requests}</h3>
  </div>
  <div class="panel-body">
    <div ng-repeat="req in data.requests">
      <div class="well">
        <strong>{{req.number}}</strong> - {{req.u_request_type}}<br/>
        <span class="text-muted">{{req.u_urgency}} | {{req.u_approval_state}}</span>
      </div>
    </div>
  </div>
</div>""",
            "css": "",
            "client_script": """api.controller = function($scope, spUtil) {
  var c = this;
  c.data.requests = [];
  
  spUtil.recordWatch($scope, 'u_network_request', '', function() {
    c.server.update().then(function(response) {
      c.data.requests = response.data.requests;
    });
  });
};""",
            "server_script": """(function() {
  if (input) {
    var gr = new GlideRecord('u_network_request');
    gr.orderByDesc('sys_created_on');
    gr.setLimit(20);
    gr.query();
    data.requests = [];
    while (gr.next()) {
      data.requests.push({
        sys_id: gr.getUniqueValue(),
        number: gr.getValue('number'),
        u_request_type: gr.getDisplayValue('u_request_type'),
        u_urgency: gr.getDisplayValue('u_urgency'),
        u_approval_state: gr.getDisplayValue('u_approval_state'),
        short_description: gr.getValue('short_description')
      });
    }
  }
})();""",
            "option_schema": "",
            "active": True,
        }
        r = sn.post("table/sp_widget", widget_data)
        check_result(r, "Service Portal Widget: Network Request Dashboard")
        time.sleep(0.5)
    else:
        log("Service Portal Widget already exists", "SKIP")

    # ========================================
    # SUMMARY
    # ========================================
    log("\n" + "=" * 60)
    log("BUILD COMPLETE - Summary")
    log("=" * 60)
    log(f"Instance: {INSTANCE}")
    log(f"Tables created: {TABLE_REQUEST}, {TABLE_TASK}")
    log(f"Catalog item: 'Network Request' (sys_id: {cat_sys_id})")
    log(f"Flow: 'Network Request Automation' (sys_id: {flow_sys_id})")
    log(f"Email notifications: 6 configured")
    log(f"Business rules: 3 configured")
    log(f"Client scripts: 1 configured")
    log(f"Service portal widget: 1 configured")
    log(f"\nAccess the portal at: {INSTANCE}/sp")
    log(f"Search for 'Network Requests' in the service portal")


if __name__ == "__main__":
    main()
