# Automated Network Request Management - Project Documentation

## Instance Information
- **Instance URL**: https://dev402064.service-now.com
- **Service Portal URL**: https://dev402064.service-now.com/sp

---

## Architecture Overview

### Data Model

#### Table: u_network_request (Network Request)
Custom table for storing network change requests.

| Field | Type | Label | Description |
|-------|------|-------|-------------|
| u_request_type | Choice (String) | Request Type | Type of network request (Firewall Rule, VLAN Config, etc.) |
| u_access_level | Choice (String) | Access Level | Level of access required (Read Only, Read/Write, Admin, Deny) |
| u_device | Choice (String) | Device | Target device (Router, Switch, Firewall, etc.) |
| u_device_other | String | Device (Other) | Free-text device description when "Other" is selected |
| u_business_justification | String (4000) | Business Justification | Business reason for the request |
| u_urgency | Choice (String) | Urgency | Priority level (Critical, High, Moderate, Low) |
| u_portal_details | String (1000) | Portal Details | Additional portal/service details |
| u_requested_for | Reference (sys_user) | Requested For | User on whose behalf the request is made |
| u_requested_for_email | String | Requester Email | Auto-populated email |
| u_requested_for_phone | String | Requester Phone | Auto-populated phone |
| u_requested_for_username | String | Requester Username | Auto-populated username |
| u_approval_state | String | Approval State | Current approval status (pending, approved, rejected, completed) |
| u_approver | Reference (sys_user) | Approver | Assigned approver |
| u_approval_notes | String (4000) | Approval Notes | Notes from approver |
| u_network_group | Reference (sys_user_group) | Network Group | Fulfillment team group |
| u_department | String | Department | Requester's department |
| u_location | Reference (cmn_location) | Location | Physical location |
| u_short_description | String (255) | Short Description | Brief summary |
| u_description | String (4000) | Description | Detailed description |

#### Table: u_network_task (Network Task)
Custom table extending `task` for fulfillment tasks.

| Field | Type | Label | Description |
|-------|------|-------|-------------|
| u_network_request | Reference (u_network_request) | Network Request | Parent request |
| u_task_type | String | Task Type | Type of fulfillment task |
| u_configuration_item | Reference (cmdb_ci) | Configuration Item | Related CI |
| u_work_notes | String (4000) | Work Notes | Engineer work notes |
| u_implementation_plan | String (4000) | Implementation Plan | How the change will be implemented |
| u_rollback_plan | String (4000) | Rollback Plan | How to revert if issues occur |

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

## Service Catalog

### Catalog Item: Network Request
- **Name**: Network Request
- **Short Description**: Submit a network change or access request
- **Type**: Item
- **Active**: Yes
- **Availability**: Desktop

### Variables

| Variable | Type | Mandatory | Order | Description |
|----------|------|-----------|-------|-------------|
| request_type | Select Box | Yes | 100 | What type of network request is this? |
| access_level | Select Box | Yes | 200 | What level of access is required? |
| device | Select Box | Yes | 300 | Which device does this apply to? |
| device_other | String | No | 350 | If 'Other', please specify the device |
| business_justification | Multi Line Text | Yes | 400 | Please provide a business justification |
| urgency | Select Box | Yes | 500 | What is the urgency of this request? |
| portal_details | String | No | 600 | Additional portal or service details |
| short_description | String | Yes | 700 | Short description of the request |
| requested_for | Reference (sys_user) | No | 800 | Requested For |
| requester_email | Reference (sys_user) | No | 810 | Requester Email |
| requester_phone | Reference (sys_user) | No | 820 | Requester Phone |
| requester_username | Reference (sys_user) | No | 830 | Requester Username |

---

## Automation

### Business Rules

| Name | Table | When | Insert | Update | Description |
|------|-------|------|--------|--------|-------------|
| Network Request - Auto Populate Requester | u_network_request | before | Yes | No | Auto-populates requester info from logged-in user |
| Network Request - Set Initial State | u_network_request | before | Yes | No | Sets initial approval state to "pending" |
| Network Request - Create Fulfillment Task | u_network_request | after | No | Yes | Creates u_network_task when request is approved |
| Network Task - Complete Request | u_network_task | after | No | Yes | Closes parent request when all tasks are closed |

### Client Scripts

| Name | Type | Field | Description |
|------|------|-------|-------------|
| Network Request - Dynamic Fields | onChange | device | Shows/hides device_other field when device = 'other' |

### UI Policies

| Name | Description |
|------|-------------|
| Show device_other when device=other | Makes device_other visible and mandatory when device selection is 'other' |

### Flow Designer

| Flow Name | Table | Trigger | Description |
|-----------|-------|---------|-------------|
| Network Request Automation | u_network_request | Record Created | Automated flow for request validation, approval routing, and notifications |

---

## Email Notifications

| Notification | Table | Event | Recipient |
|-------------|-------|-------|-----------|
| Network Request - Submitted | u_network_request | network_request.submitted | Requester |
| Network Request - Approval Required | u_network_request | network_request.approval_required | Approver |
| Network Request - Approved | u_network_request | network_request.approved | Requester |
| Network Request - Rejected | u_network_request | network_request.rejected | Requester |
| Network Task - Assigned | u_network_task | network_task.assigned | Assignment Group |
| Network Request - Completed | u_network_request | network_request.completed | Requester |

---

## Service Portal

### Widget: Network Request Dashboard
- Displays a list of recent network requests
- Shows request number, type, urgency, and approval state
- Color-coded labels for urgency and status
- Auto-refreshes on record changes

---

## Request Lifecycle

```
[User submits request via Service Portal]
         |
         v
[Business Rule: Auto-populate requester info]
         |
         v
[Business Rule: Set initial state to "pending"]
         |
         v
[Email: "Network Request - Submitted" to requester]
         |
         v
[Approval routing - Manager/Network Security reviews]
         |
         v
[Email: "Network Request - Approval Required" to approver]
         |
    +----+----+
    |         |
[Approved]  [Rejected]
    |         |
    v         v
[BR: Create   [Email: "Rejected"
 Fulfillment   to requester]
 Task]         |
    |         v
    v      [Request Closed]
[Email: "Task Assigned"
 to Network Team]
    |
    v
[Engineer works task, updates work notes]
    |
    v
[Engineer closes task]
    |
    v
[BR: Check if all tasks closed]
    |
    v
[If all closed: Request -> Completed]
    |
    v
[Email: "Network Request - Completed" to requester]
```

---

## How to Test

1. **Access Service Portal**: Navigate to https://dev402064.service-now.com/sp
2. **Browse Catalog**: Go to the Service Catalog and look under "Network Standard Changes" category
   - Or use the direct link: https://dev402064.service-now.com/sp?id=sc_cat_item&sys_id=78cb2f99472dc3509127d44a516d4394
3. **Submit Request**: Fill in the required fields:
   - Request Type: Select from dropdown
   - Access Level: Select from dropdown
   - Device: Select from dropdown (try "Other" to see dynamic field)
   - Business Justification: Enter text
   - Urgency: Select from dropdown
   - Short Description: Enter brief summary
4. **Verify**: Check that the request appears in the Network Request Dashboard widget
5. **Approve**: As an admin, navigate to the request record and set Approval State to "approved"
6. **Verify Task**: A fulfillment task should be automatically created
7. **Complete Task**: Close the task and verify the request is marked complete

---

## Files Generated

| File | Description |
|------|-------------|
| `build.py` | Main build script for the entire solution |
| `check_existing.py` | Pre-build check for existing components |
| `quick_check.py` | Quick verification of Network components |
| `OBJECTIVE.md` | Project objectives |
| `RULES.md` | Project rules and requirements |
| `APPROACH.md` | Detailed approach and phase breakdown |
| `DOCUMENTATION.md` | This file |

---

## Future Enhancements

1. **Integration with Network Tools**: Auto-provisioning via Cisco DNA Center, Ansible, or Terraform
2. **Integration Hub**: Orchestration flows for complex multi-step changes
3. **Reporting Dashboards**: Request volume, fulfillment times, SLA compliance
4. **Expansion**: Device provisioning, access requests, other IT services
5. **Advanced Approval Routing**: Multi-level approvals based on risk/cost thresholds
6. **Scheduled Changes**: Integration with Change Management for planned maintenance windows
