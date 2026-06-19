# Automated Network Request Management - Project Documentation

## 1. Introduction

| Property | Value |
|----------|-------|
| Project Title | Automated Network Request Management System |
| Platform | ServiceNow (dev402064.service-now.com) |
| Instance URL | https://dev402064.service-now.com |
| Service Portal URL | https://dev402064.service-now.com/sp |
| Catalog Item Direct Link | https://dev402064.service-now.com/sp?id=sc_cat_item&sys_id=78cb2f99472dc3509127d44a516d4394 |

---

## 2. Project Overview

### Purpose
Streamline and automate the end-to-end lifecycle of network-related service requests using ServiceNow.

### Key Features
- Network Request catalog item in Service Catalog
- Dynamic forms with show/hide fields based on request type
- Automated approval routing
- Email notifications at key lifecycle stages
- Automatic task creation on approval
- Status tracking through request lifecycle
- Role-based access with user groups (Network Team, Approvers, Requesters)

---

## 3. Architecture

### Tables

#### u_network_request (Network Request)

| Field | Type | Label |
|-------|------|-------|
| u_number | String | Request Number |
| u_request_type | Choice | Request Type |
| u_access_level | Choice | Access Level |
| u_device | Choice | Device |
| u_device_other | String | Device (Other) |
| u_business_justification | String (4000) | Business Justification |
| u_urgency | Choice | Urgency |
| u_portal_details | String (1000) | Portal Details |
| u_requested_for | Reference (sys_user) | Requested For |
| u_requested_for_email | String | Requester Email |
| u_requested_for_phone | String | Requester Phone |
| u_requested_for_username | String | Requester Username |
| u_approval_state | String | Approval State |
| u_approver | Reference (sys_user) | Approver |
| u_approval_notes | String (4000) | Approval Notes |
| u_network_group | Reference (sys_user_group) | Network Group |
| u_department | String | Department |
| u_location | Reference (cmn_location) | Location |
| u_short_description | String (255) | Short Description |
| u_description | String (4000) | Description |

#### u_network_task (Network Task)

| Field | Type | Label |
|-------|------|-------|
| u_network_request | Reference (u_network_request) | Network Request |
| u_task_type | String | Task Type |
| u_configuration_item | Reference (cmdb_ci) | Configuration Item |
| u_work_notes | String (4000) | Work Notes |
| u_implementation_plan | String (4000) | Implementation Plan |
| u_rollback_plan | String (4000) | Rollback Plan |

#### u_network_database (Network Database)

| Field | Type | Label |
|-------|------|-------|
| u_request_number | String | Request Number |
| u_assignment_group | Reference (sys_user_group) | Assignment Group |
| u_customer_document | String | Customer Document |
| u_assigned_to | Reference (sys_user) | Assigned to |
| u_device_details | String | Device Details |
| u_date_of_enquiry | Date | Date of Enquiry |
| u_customer_address | String | Customer Address |
| u_approval_state | String | Work Status |
| u_requested_for | String | Requested For |

### Choice Lists

#### u_request_type
| Value | Label |
|-------|-------|
| firewall_rule | Firewall Rule Change |
| vlan_config | VLAN Configuration |
| access_port | Access Port Configuration |
| routing_change | Routing Change |
| dns_change | DNS Change |
| load_balancer | Load Balancer Change |
| vpn_tunnel | VPN Tunnel |
| other | Other |

#### u_access_level
| Value | Label |
|-------|-------|
| read_only | Read Only |
| read_write | Read/Write |
| admin | Admin |
| deny | Deny |

#### u_urgency
| Value | Label |
|-------|-------|
| critical | Critical |
| high | High |
| moderate | Moderate |
| low | Low |

#### u_device
| Value | Label |
|-------|-------|
| router | Router |
| switch | Switch |
| firewall | Firewall |
| load_balancer | Load Balancer |
| access_point | Access Point |
| server | Server |
| other | Other |

---

## 4. Service Catalog

### Catalog Item: Network Request
- Name: Network Request
- Catalog: Service Catalog
- Category: Network Standard Changes
- Type: Item
- Active: Yes

### Variables

| Variable | Type | Mandatory | Order |
|----------|------|-----------|-------|
| u_short_description | String | Yes | 50 |
|| u_new_relocation | String | Yes | 100 |
| u_device_type | String | Yes | 200 |
| u_relocation_address | String | No | 250 |
| u_address | String | No | 300 |
| u_device_details | String | No | 400 |
| u_other_specify | String | No | 500 |
| u_justification | Multi Line Text | Yes | 600 |
| u_description | Multi Line Text | Yes | 700 |
| u_opened_by | Reference (sys_user) | Yes | 800 |
| u_email | String | No | 810 |
| u_username | String | No | 820 |
| u_phone | String | No | 830 |
| u_proof_document | Attachment | No | 900 |

---

## 5. Automation

### Business Rules

| Name | Table | When | Description |
|------|-------|------|-------------|
| Network Request - Set Initial State | u_network_request | before insert | Sets approval state to "pending", auto-populates requester info |
| Network Request - Auto Populate Requester | u_network_request | before insert | Auto-populates requester details from logged-in user |
| Network Request - Create Fulfillment Task | u_network_request | after update | Creates u_network_task when approval state changes to "approved" |
| Network Task - Complete Request | u_network_task | after update | Closes parent request when all tasks are closed |

### Client Scripts

| Name | Type | Description |
|------|------|-------------|
| Auto-populate User Details | onChange | Auto-populates Email, Username, Phone when "Opened on behalf of" changes |

### UI Policies

| Name | Description |
|------|-------------|
| Show device_other when device=other | Makes device_other visible and mandatory when device = 'other' |
| Show Other Specify when device type is Others | Makes u_other_specify visible when device type is 'Others' |

---

## 6. Email Notifications

| Notification | Table | Event |
|-------------|-------|-------|
| Network Request - Submitted | u_network_request | network_request.submitted |
| Network Request - Approval Required | u_network_request | network_request.approval_required |
| Network Request - Approved | u_network_request | network_request.approved |
| Network Request - Rejected | u_network_request | network_request.rejected |
| Network Task - Assigned | u_network_task | network_task.assigned |
| Network Request - Completed | u_network_request | network_request.completed |

---

## 7. User Groups

| Group | Description | Roles |
|-------|-------------|-------|
| Network Team | Network fulfillment team | itil |
| Network Approvers | Approvers for network change requests | itil, approval_user |
| Network Requesters | Users who can submit network requests | itil |

---

## 8. Request Lifecycle

1. User submits request via Service Portal
2. Business Rule auto-populates requester info
3. Business Rule sets initial approval state to "pending"
4. Email notification sent to requester
5. Approval routing to Manager/Network Security
5a. If Approved: Business Rule creates Fulfillment Task, email sent to Network Team
5b. If Rejected: Email sent to requester, request closed
6. Engineer works task, updates work notes
7. Engineer closes task
8. Business Rule checks if all tasks closed
9. If all closed: Request marked Completed
10. Email notification sent to requester

---

## 9. How to Test

1. Navigate to https://dev402064.service-now.com/sp
2. Search for "Network Request" in Service Catalog
3. Fill required fields and submit
4. Verify: request created with "pending" approval state
5. Open request, change Approval State to "approved"
6. Verify: fulfillment task automatically created
7. Close the task
8. Verify: parent request changes to "completed"

---

## 10. Known Issues

- ACLs cannot be created via REST API (ServiceNow security constraint). Default ACLs are active.
- Service Portal Dashboard widget needs manual creation in ServicePortal Designer.
- Flow Designer flow for approval routing needs UI configuration (Business Rules handle the logic as alternative).
- **Select Box dropdowns**: The three dropdown variables (u_new_relocation, u_device_type, u_relocation_address) were changed from Select Box (type 5) to String (type 3) because the Service Portal's Select Box rendering requires specific choice_table configuration that couldn't be set via REST API. To restore dropdowns: edit each variable in the ServiceNow UI, change type back to "Select Box", and add choices manually.

---

## 11. Future Enhancements

- Integration with network tools (Cisco DNA Center, Ansible, Terraform)
- Integration Hub orchestration flows
- Reporting dashboards for request volume and SLA compliance
- Expansion to device provisioning and access requests
- Multi-level approvals based on risk/cost thresholds
- Scheduled changes integration with Change Management
