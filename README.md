**AUTOMATED NETWORK REQUEST MANAGEMENT**
=====================================

A ServiceNow project that automates the end-to-end lifecycle of network-related 
service requests — from catalog submission through approval, task generation, 
and fulfillment.

INSTANCE
--
- URL: https://dev402064.service-now.com
- Service Portal: https://dev402064.service-now.com/sp
- Catalog Item: https://dev402064.service-now.com/sp?id=sc_cat_item&sys_id=78cb2f99472dc3509127d44a516d4394

PROJECT STRUCTURE
--
- OBJECTIVE.md      - Business objectives and scope
- RULES.md          - Functional requirements and constraints
- APPROACH.md       - 5-phase implementation roadmap (559 lines)
- DOCUMENTATION.md  - Full technical documentation
- build.py          - Python build script (creates all components)
- fix_field_types.js - Fix Script for correcting field types (run in ServiceNow)
- service_now_config/ - JSON exports of all ServiceNow configurations

DATA MODEL
--
- u_network_request   - Main request table (26 fields)
- u_network_task      - Fulfillment task table (7 fields, extends task)
- u_network_database  - Customer/enquiry database table (10 fields)

COMPONENTS
--
- 1 Service Catalog item ("Network Request")
- 13 Catalog variables (dropdowns, strings, multi-line text, reference, attachment)
- 4 Business Rules (auto-population, state management)
- 6 Email Notifications
- 1 Flow Designer flow (approval routing)
- 1 Client Script (form validation)
- 2 UI Policies (conditional field visibility)
- 1 Service Portal Widget
- Choice lists for dropdown variables

VARIABLES
--
| Variable             | Type         | Mandatory |
|----------------------|--------------|-----------|
| u_new_relocation     | Select Box   | Yes       |
| u_device_type        | Select Box   | Yes       |
| u_relocation_address | Select Box   | No        |
| u_address            | String       | No        |
| u_device_details     | String       | No        |
| u_other_specify      | String       | No        |
| u_justification      | Multi Line   | Yes       |
| u_description        | Multi Line   | No        |
| u_opened_by          | Reference    | No        |
| u_email              | String       | No        |
| u_username           | String       | No        |
| u_phone              | String       | No        |
| u_proof_document     | Attachment   | No        |

HOW TO DEPLOY
--
1. Import service_now_config/ JSON files into ServiceNow
2. Run fix_field_types.js as a Fix Script (System Definition > Fix Scripts)
3. Navigate to the Service Portal to test the form

BUG NOTES
--
- The catalog variables may render as radio buttons instead of dropdowns if 
  field types are not set correctly. Run fix_field_types.js to resolve.
- The "Required Filled" label appears on some fields due to mandatory + 
  display value configuration. This is cosmetic only.
