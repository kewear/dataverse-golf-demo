"""Create all golf booking tables with zava_ prefix via Dataverse Web API."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.auth import get_token, load_env
import requests

load_env()
BASE_URL = os.environ["DATAVERSE_URL"].rstrip("/")
SOLUTION_NAME = "ZavaGolfBookings"

def headers():
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "MSCRM.SolutionName": SOLUTION_NAME,
    }

def create_table(schema_name, display_name, display_plural, description, columns):
    """Create a table with columns via EntityDefinitions."""
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": schema_name,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display_name, "LanguageCode": 1033}]},
        "DisplayCollectionName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display_plural, "LanguageCode": 1033}]},
        "Description": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": description, "LanguageCode": 1033}]},
        "HasActivities": False,
        "HasNotes": False,
        "OwnershipType": "UserOwned",
        "IsActivity": False,
        "Attributes": columns
    }
    resp = requests.post(f"{BASE_URL}/api/data/v9.2/EntityDefinitions", headers=headers(), json=payload)
    if resp.status_code in (200, 201, 204):
        print(f"  ✅ Created table: {schema_name}")
        return True
    else:
        print(f"  ❌ Failed to create {schema_name}: {resp.status_code} - {resp.text[:300]}")
        return False

def string_col(schema, display, max_length=100, is_primary=False):
    col = {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "ApplicationRequired" if is_primary else "None"},
        "MaxLength": max_length,
        "AttributeType": "String",
        "AttributeTypeName": {"Value": "StringType"},
        "FormatName": {"Value": "Text"},
    }
    if is_primary:
        col["IsPrimaryName"] = True
    return col

def integer_col(schema, display, min_val=0, max_val=2147483647):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "MinValue": min_val,
        "MaxValue": max_val,
        "AttributeType": "Integer",
        "AttributeTypeName": {"Value": "IntegerType"},
        "Format": "None",
    }

def boolean_col(schema, display, default=True):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "AttributeType": "Boolean",
        "AttributeTypeName": {"Value": "BooleanType"},
        "DefaultValue": default,
        "OptionSet": {
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
            "TrueOption": {"Value": 1, "Label": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Yes", "LanguageCode": 1033}]}},
            "FalseOption": {"Value": 0, "Label": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "No", "LanguageCode": 1033}]}}
        }
    }

def datetime_col(schema, display, date_only=False):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "AttributeType": "DateTime",
        "AttributeTypeName": {"Value": "DateTimeType"},
        "Format": "DateOnly" if date_only else "DateAndTime",
        "DateTimeBehavior": {"Value": "UserLocal"},
    }

def money_col(schema, display):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.MoneyAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "AttributeType": "Money",
        "AttributeTypeName": {"Value": "MoneyType"},
        "PrecisionSource": 2,
    }

def picklist_col(schema, display, options):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "ApplicationRequired"},
        "AttributeType": "Picklist",
        "AttributeTypeName": {"Value": "PicklistType"},
        "OptionSet": {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "IsGlobal": False,
            "OptionSetType": "Picklist",
            "Options": [
                {
                    "Value": opt["value"],
                    "Label": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": opt["label"], "LanguageCode": 1033}]}
                }
                for opt in options
            ]
        }
    }

def email_col(schema, display):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "MaxLength": 200,
        "AttributeType": "String",
        "AttributeTypeName": {"Value": "StringType"},
        "FormatName": {"Value": "Email"},
    }

def phone_col(schema, display):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema,
        "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": display, "LanguageCode": 1033}]},
        "RequiredLevel": {"Value": "None"},
        "MaxLength": 50,
        "AttributeType": "String",
        "AttributeTypeName": {"Value": "StringType"},
        "FormatName": {"Value": "Phone"},
    }


# ============================================================
# TABLE 1: zava_membership
# ============================================================
print("\n[1/5] Creating zava_membership...")
create_table(
    "zava_membership",
    "Golf Membership",
    "Golf Memberships",
    "Tracks membership status for golf course customers",
    [
        string_col("zava_name", "Membership Name", 100, is_primary=True),
        picklist_col("zava_status", "Status", [
            {"label": "Active", "value": 100000000},
            {"label": "Expired", "value": 100000001},
            {"label": "Suspended", "value": 100000002},
        ]),
        datetime_col("zava_startdate", "Start Date", date_only=True),
        datetime_col("zava_enddate", "End Date", date_only=True),
    ]
)

# ============================================================
# TABLE 2: zava_customer
# ============================================================
print("\n[2/5] Creating zava_customer...")
create_table(
    "zava_customer",
    "Golf Customer",
    "Golf Customers",
    "Golf course customers (members and guests)",
    [
        string_col("zava_name", "Full Name", 200, is_primary=True),
        email_col("zava_email", "Email"),
        phone_col("zava_phone", "Phone"),
    ]
)

# ============================================================
# TABLE 3: zava_rate
# ============================================================
print("\n[3/5] Creating zava_rate...")
create_table(
    "zava_rate",
    "Golf Rate",
    "Golf Rates",
    "Rate card for tee-time pricing by time of day",
    [
        string_col("zava_name", "Rate Name", 100, is_primary=True),
        integer_col("zava_startminute", "Start Minute", 0, 1440),
        integer_col("zava_endminute", "End Minute", 0, 1440),
        money_col("zava_amount", "Amount"),
        boolean_col("zava_isactive", "Is Active", default=True),
    ]
)

# ============================================================
# TABLE 4: zava_teetime
# ============================================================
print("\n[4/5] Creating zava_teetime...")
create_table(
    "zava_teetime",
    "Tee Time",
    "Tee Times",
    "Bookable tee-time slots at 10-minute intervals",
    [
        string_col("zava_name", "Tee Time Name", 100, is_primary=True),
        datetime_col("zava_date", "Date", date_only=True),
        integer_col("zava_time", "Time (Minutes)", 0, 1440),
        string_col("zava_displaytime", "Display Time", 20),
        integer_col("zava_maxplayers", "Max Players", 1, 10),
        integer_col("zava_currentplayers", "Current Players", 0, 10),
        boolean_col("zava_isavailable", "Is Available", default=True),
    ]
)

# ============================================================
# TABLE 5: zava_booking
# ============================================================
print("\n[5/5] Creating zava_booking...")
create_table(
    "zava_booking",
    "Tee Time Booking",
    "Tee Time Bookings",
    "Individual player bookings for tee-time slots",
    [
        string_col("zava_name", "Booking Name", 200, is_primary=True),
        boolean_col("zava_ismember", "Is Member", default=False),
        boolean_col("zava_isingoodstanding", "Is In Good Standing", default=False),
        money_col("zava_amountcharged", "Amount Charged"),
        picklist_col("zava_status", "Status", [
            {"label": "Confirmed", "value": 100000000},
            {"label": "Cancelled", "value": 100000001},
            {"label": "No-Show", "value": 100000002},
        ]),
        datetime_col("zava_bookedon", "Booked On"),
    ]
)

print("\n✅ All tables created. Now adding lookup relationships...")

# ============================================================
# LOOKUPS (created after tables exist)
# ============================================================
def create_lookup(primary_table, lookup_schema, lookup_display, referenced_table, referenced_table_primary_key):
    """Create a lookup column (Many-to-One relationship)."""
    payload = {
        "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
        "SchemaName": lookup_schema,
        "ReferencedEntity": referenced_table,
        "ReferencingEntity": primary_table,
        "Lookup": {
            "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
            "SchemaName": lookup_schema.replace("zava_", "zava_") if "zava_" in lookup_schema else lookup_schema,
            "DisplayName": {"@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": lookup_display, "LanguageCode": 1033}]},
            "RequiredLevel": {"Value": "None"},
        },
        "CascadeConfiguration": {
            "Assign": "NoCascade",
            "Delete": "RemoveLink",
            "Merge": "NoCascade",
            "Reparent": "NoCascade",
            "Share": "NoCascade",
            "Unshare": "NoCascade",
            "RollupView": "NoCascade",
        }
    }
    h = headers()
    resp = requests.post(f"{BASE_URL}/api/data/v9.2/RelationshipDefinitions", headers=h, json=payload)
    if resp.status_code in (200, 201, 204):
        print(f"  ✅ Lookup: {primary_table}.{lookup_schema} → {referenced_table}")
        return True
    else:
        print(f"  ❌ Failed lookup {lookup_schema}: {resp.status_code} - {resp.text[:300]}")
        return False

time.sleep(5)  # Wait for tables to be provisioned

# Customer → Membership
print("\nAdding lookups...")
create_lookup("zava_customer", "zava_customer_membership", "Membership", "zava_membership", "zava_membershipid")

# Booking → Customer
create_lookup("zava_booking", "zava_booking_customer", "Customer", "zava_customer", "zava_customerid")

# Booking → Tee Time
create_lookup("zava_booking", "zava_booking_teetime", "Tee Time", "zava_teetime", "zava_teetimeid")

# Booking → Rate
create_lookup("zava_booking", "zava_booking_rate", "Rate", "zava_rate", "zava_rateid")

# Booking → Membership
create_lookup("zava_booking", "zava_booking_membership", "Membership", "zava_membership", "zava_membershipid")

print("\n🎉 All tables and relationships created!")
