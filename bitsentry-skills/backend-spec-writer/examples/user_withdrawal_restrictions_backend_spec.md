## Review Table

| Version | Date | Name | Role | Description |
| --- | --- | --- | --- | --- |
| 1.2 | 2025-11-10 | Technical Lead | Reviewer | Added some notes and comments |
| 1.2 | 2025-11-07 | Assistant | Editor | Added safeguards for banking and eaccount account management (add/update/delete) when redemption restrictions are enabled |
| 1.1 | 2025-11-04 | Assistant | Editor | Added eaccount whitelisting endpoints, updated redemption_restricted to banking_redemption_disabled, removed audit log references from sequence diagrams |
| 1.0 | 2025-10-30 | Engineer D | Author | Initial Draft |

## Approval Table

| Approved By | Approved At | Note |
| --- | --- | --- |
|  |  |  |

---

## Background

The Mobile App application's Payment Link allows merchants to accept digital payment payments through staff members or cashiers. Currently, these staff members have unrestricted access to critical account functions, creating significant financial risk. Staff can add personal bank accounts, redeem DigitalCurrency to their accounts, transfer funds via P2P, and potentially misappropriate company funds.

## Context

The current system lacks granular permission controls at the user level. Any user with access to a Payment Link account can:

- Add and use any bank account for redemption
- Transfer funds to e-accounts
- Initiate P2P transfers
- Make payments using company funds
- Export private keys (frontend concern, now addressed in this spec)

This creates a trust problem where business owners must rely entirely on staff honesty without technical safeguards.

## Objective

Implement a comprehensive restriction system that:

1. **Enforces banking and eaccount restrictions** - Control access to banking and eaccount redemptions separately
1. **Disables specific account features** - Granular control over e-account redemption, P2P transfers, payment capabilities, and private key export
1. **Ensures backward compatibility** - Existing unrestricted accounts continue functioning normally
1. **Provides restriction status visibility** - Users can check their restriction status via API

## Paradigm

We adopt a **DDD-lite approach with Hexagonal Architecture** principles:

- **Domain Layer**: User restrictions as first-class domain concepts
- **Application Layer**: Use cases for managing and enforcing restrictions
- **Infrastructure Layer**: Database persistence and API adapters
- **Separation of Concerns**: Restriction logic isolated from business operations

---

## Database Design

## Database Schema

```
Table userprofiles {
  id int [pk]
  user_uuid varchar [unique]
  account_id varchar [unique]
  // existing fields...

  indexes {
    user_uuid
    account_id
  }
}

Table user_restrictions {
  id int [pk, increment]
  user_uuid varchar [ref: > userprofiles.user_uuid, unique, note: "One restriction record per user"]
  banking_redemption_disabled boolean [default: false, note: "If true, banking redemptions are disabled"]
  eaccount_redemption_disabled boolean [default: false, note: "If true, eaccount redemptions are disabled"]
  p2p_transfer_disabled boolean [default: false]
  payment_disabled boolean [default: false]
  private_key_export_disabled boolean [default: false, note: "Prevents private key export"]
  updated_at timestamp
  updated_by varchar [ref: > profiles.admin_uuid, note: "Admin UUID who last updated restrictions"]

  indexes {
    user_uuid
  }
}

Table banking {
  id int [pk]
  account_id varchar [ref: > userprofiles.account_id]
  modified_by varchar [ref: > profiles.admin_uuid, note: "Admin UUID who modified"]

  indexes {
    account_id
    modified_by
  }
}

Table eaccounts {
  id int [pk]
  account_id varchar [ref: > userprofiles.account_id]
  modified_by varchar [ref: > profiles.admin_uuid, note: "Admin UUID who modified"]

  indexes {
    account_id
    modified_by
  }
}

Table profiles {
  admin_uuid varchar [pk]
}
```

---

## Activity Lifecycle

### User Restriction Activity Lifecycle

```mermaid
stateDiagram-v2
    [*] --> UNRESTRICTED: Default State
    
    UNRESTRICTED --> BANKING_RESTRICTED: Disable Banking Redemption
    BANKING_RESTRICTED --> UNRESTRICTED: Enable Banking Redemption
    
    UNRESTRICTED --> FEATURE_DISABLED: Disable Features
    FEATURE_DISABLED --> UNRESTRICTED: Enable All Features
    
    BANKING_RESTRICTED --> FULLY_RESTRICTED: Disable Additional Features
    FULLY_RESTRICTED --> BANKING_RESTRICTED: Enable Some Features
    FULLY_RESTRICTED --> UNRESTRICTED: Remove All Restrictions
    
    state FEATURE_DISABLED {
        [*] --> BANKING_DISABLED
        [*] --> EWALLET_DISABLED
        [*] --> P2P_DISABLED  
        [*] --> PAYMENT_DISABLED
        [*] --> PRIVATE_KEY_EXPORT_DISABLED
    }
    
    state FULLY_RESTRICTED {
        [*] --> ALL_FEATURES_DISABLED
    }
```

---

## API Endpoints

### Admin Management APIs

`POST /api/admin/users/{publicAddress}/restrictions`

Apply or update user restrictions.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| banking_redemption_disabled | boolean | N | Disable bank redemption |
| eaccount_redemption_disabled | boolean | N | Disable e-account redemption |
| p2p_transfer_disabled | boolean | N | Disable P2P transfers |
| payment_disabled | boolean | N | Disable payment capability |
| private_key_export_disabled | boolean | N | Disable private key export |
| reason | string | Y | Reason for changes |

**Response (200 OK)**

```
{
  "user_uuid": "usr_123",
  "restrictions": {
    "banking_redemption_disabled": true,
    "eaccount_redemption_disabled": true,
    "p2p_transfer_disabled": true,
    "payment_disabled": false,
    "private_key_export_disabled": true
  },
  "updated_at": "2025-10-30T10:00:00Z",
  "updated_by": "admin_456"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as UpdateRestrictions UseCase
    participant Repo as UserRepository
    participant DB as Database

    Admin->>API: POST /api/admin/users/{userUuid}/restrictions
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute UpdateRestrictions
    UC->>Repo: GetUser(userUuid)
    Repo->>DB: SELECT * FROM userprofiles
    DB-->>Repo: User Data
    Repo-->>UC: User Entity

    UC->>UC: Apply Restrictions
    UC->>Repo: SaveUser(user)
    Repo->>DB: UPDATE userprofiles SET restrictions
    DB-->>Repo: Success

    UC-->>API: Restrictions Updated
    API-->>Admin: 200 OK with Restrictions
```

---

`POST /api/admin/banks/{publicAddress}`

Add a new bank account for a user.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| asset | string | Y | Asset type (e.g., "idr") |
| account_nickname | string | N | Account nickname |
| bank_name | string | Y | Bank name |
| bank_account | string | Y | Bank account number |
| source | string | N | Bank account source (REDEMPTION or PAYMENT), defaults to REDEMPTION |

**Response (200 OK)**

```
{
  "bank_uuid": "bnk_789",
  "bank_name": "BCA",
  "bank_account": "1234567890",
  "bank_account_name": "John Doe",
  "account_nickname": "Personal BCA",
  "asset": "idr",
  "status": "VALIDATED",
  "modified_by": "admin_456"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as AddBankAccount UseCase
    participant BankRepo as BankRepository
    participant DB as Database
    participant Validator as Bank Validator

    Admin->>API: POST /api/admin/banks/{publicAddress}
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute AddBankAccount
    UC->>UC: Sanitize bank account number
    UC->>BankRepo: CheckDuplicateBank(publicAddress, bank_name, bank_account)
    BankRepo->>DB: SELECT * FROM banking
    DB-->>BankRepo: Duplicate Check Result
    BankRepo-->>UC: No Duplicate

    UC->>BankRepo: CheckExistingBank(bank_name, bank_account)
    BankRepo->>DB: SELECT * FROM banking WHERE bank_name AND bank_account
    DB-->>BankRepo: Existing Bank Data (if any)
    BankRepo-->>UC: Existing Bank Status

    UC->>BankRepo: CreateBankAccount(bank_uuid, publicAddress, details, adminUuid)
    BankRepo->>DB: INSERT INTO banking
    DB-->>BankRepo: Success

    alt Bank Account Not Previously Validated
        UC->>Validator: ValidateBankAccount(bank_name, bank_account, bank_uuid)
        Validator-->>UC: Validation Initiated
    end

    UC-->>API: Bank Account Created
    API-->>Admin: 200 OK with Bank Account Details
```

---

`DELETE /api/admin/banks/{bankUuid}`

Soft-delete a bank account.

**Response (200 OK)**

```
{
  "message": "Bank account deleted successfully",
  "bank_uuid": "bnk_789"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as DeleteBanking UseCase
    participant BankRepo as BankRepository
    participant DB as Database

    Admin->>API: DELETE /api/admin/banks/{bankUuid}
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute DeleteBanking
    UC->>BankRepo: GetBank(bankUuid)
    BankRepo->>DB: SELECT * FROM banking
    DB-->>BankRepo: Bank Data
    BankRepo-->>UC: Bank Entity

    UC->>UC: Validate Ownership
    UC->>DB: DELETE FROM banking WHERE uuid
    DB-->>UC: Bank Deleted
    UC-->>API: Deletion Confirmed
    API-->>Admin: 200 OK
```

---

`POST /api/admin/eaccounts/{publicAddress}`

Add a new e-account account for a user.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| provider | string | Y | E-account provider (OVO, GOPAY, SHOPEEPAY, DANA, LINKAJA) |
| phone_number | string | Y | Phone number (must start with 0) |
| label | string | Y | Account label/name |

**Response (200 OK)**

```
{
  "uuid": "ew_789",
  "provider": "OVO",
  "phone_number": "081234567890",
  "label": "Personal OVO",
  "status": "VALIDATED",
  "modified_by": "admin_456"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as AddEaccountAccount UseCase
    participant EaccountRepo as EaccountRepository
    participant DB as Database

    Admin->>API: POST /api/admin/eaccounts/{publicAddress}
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute AddEaccountAccount
    UC->>UC: Validate provider exists
    UC->>UC: Validate phone number format
    UC->>UC: Validate label format

    UC->>EaccountRepo: CreateEaccountAccount(eaccount_uuid, publicAddress, details, adminUuid)
    EaccountRepo->>DB: INSERT INTO eaccount_account
    DB-->>EaccountRepo: Success

    UC-->>API: Eaccount Account Created
    API-->>Admin: 200 OK with Eaccount Account Details
```

---

`DELETE /api/admin/eaccounts/{eaccountUuid}`

Soft-delete an e-account account.

**Response (200 OK)**

```
{
  "message": "E-account account deleted successfully",
  "uuid": "ew_789"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as DeleteEaccount UseCase
    participant EaccountRepo as EaccountRepository
    participant DB as Database

    Admin->>API: DELETE /api/admin/eaccounts/{eaccountUuid}
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute DeleteEaccount
    UC->>EaccountRepo: GetEaccount(uuid)
    EaccountRepo->>DB: SELECT * FROM eaccount_account
    DB-->>EaccountRepo: Eaccount Data
    EaccountRepo-->>UC: Eaccount Entity

    UC->>UC: Validate Ownership
    UC->>DB: UPDATE eaccount_account SET is_deleted=true
    DB-->>UC: Eaccount Soft Deleted
    UC-->>API: Deletion Confirmed
    API-->>Admin: 200 OK
```

---

`GET /api/admin/users/{userUuid}/restrictions`

Get the current restriction status for a user.

**Response (200 OK)**

```
{
  "user_uuid": "usr_123",
  "restrictions": {
    "banking_redemption_disabled": false,
    "eaccount_redemption_disabled": true,
    "p2p_transfer_disabled": true,
    "payment_disabled": false,
    "private_key_export_disabled": true
  },
  "updated_at": "2025-10-30T10:00:00Z",
  "updated_by": "admin_456"
}
```

**Response (404 Not Found)**

```
{
  "error": "USER_NOT_FOUND",
  "message": "User not found"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant Admin as Admin Client
    participant API as Admin API
    participant Auth as Auth Service
    participant UC as GetUserRestrictions UseCase
    participant DB as Database

    Admin->>API: GET /api/admin/users/{userUuid}/restrictions
    API->>Auth: Verify Admin Role
    Auth-->>API: Authorized

    API->>UC: Execute GetUserRestrictions
    UC->>DB: SELECT * FROM user_restrictions WHERE user_uuid
    DB-->>UC: Restriction Data

    UC-->>API: User Restrictions
    API-->>Admin: 200 OK with Restrictions
```

---

### Account Operation APIs (Modified)

`GET /api/account/v2/restrictions`

Get the current user's restriction status and whitelisted accounts.

**Response (200 OK)**

```
// Account with restriction
{
  "user_uuid": "usr_123",
  "restrictions": {
    "banking_redemption_disabled": true,
    "eaccount_redemption_disabled": true,
    "p2p_transfer_disabled": false,
    "payment_disabled": false,
    "private_key_export_disabled": true
  }
}

// Account without restriction
{
  "user_uuid": "usr_123",
  "restrictions": {}
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant UC as GetRestrictions UseCase
    participant DB as Database

    User->>API: GET /api/account/v2/restrictions
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>UC: Execute GetRestrictions(userUuid)
    UC->>DB: SELECT * FROM user_restrictions WHERE user_uuid
    DB-->>UC: Restriction Data

    UC->>DB: SELECT * FROM banking WHERE account_id AND is_whitelisted=true
    DB-->>UC: Whitelisted Banks

    UC->>DB: SELECT * FROM eaccounts WHERE account_id AND is_whitelisted=true
    DB-->>UC: Whitelisted Eaccounts

    UC->>UC: Calculate Permissions
    UC-->>API: Restriction Status
    API-->>User: 200 OK with Status
```

---

`POST /api/account/v2/redeem/initiate`

**Unified redeem endpoint** - Replaces deprecated `/redeem-to-bank/initiate` and `/redeem-to-eaccount/initiate`. Modified to enforce redemption restrictions.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| destination | string | Y | Destination type: "bank", "pay-bank", or "e-account" |
| destination_uuid | string | Y | Bank UUID or E-account UUID |
| ui_amount | string/number | Y | Redemption amount in UI units |
| memo | string | N | Optional memo/note |

**Response (200 OK)**

```
{
  "serializedTransaction": "base64_encoded_transaction",
  "redeemRequestUuid": "redeem_request_uuid_123",
  "seqNo": 42
}
```

**Response (403 Forbidden)**

```
{
  "error": "REDEMPTION_RESTRICTED",
  "message": "Bank account not whitelisted for redemption"
}
```

OR

```
{
  "error": "EWALLET_REDEMPTION_DISABLED",
  "message": "E-account redemption is disabled for this account"
}
```

---

`POST /api/account/v2/redeem-to-bank/initiate` (DEPRECATED)

**Deprecated** -**_DELETE THIS ENDPOINT AS SOON AS POSSIBLE_**

---

`POST /api/account/v2/redeem-to-eaccount/initiate` (DEPRECATED)

**Deprecated** -**_DELETE THIS ENDPOINT AS SOON AS POSSIBLE_**

---

**Banking Account Management APIs (Modified)**

`POST /api/account/v2/banking`

Add a new bank account with restriction enforcement.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| asset | string | Y | Asset type (e.g., "DigitalCurrency") |
| bank_name | string | Y | Bank name |
| bank_account | string | Y | Bank account number |
| account_holder | string | Y | Account holder name |

**Response (200 OK)**

```
{
  "uuid": "bnk_789",
  "bank_name": "BCA",
  "account_number": "1234567890",
  "account_holder": "John Doe"
}
```

**Response (403 Forbidden)**

```
{
  "error": "BANKING_MANAGEMENT_DISABLED",
  "message": "Banking account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Banking as AddBanking UseCase
    participant DB as Database

    User->>API: POST /api/account/v2/banking
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('BANKING_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT banking_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Banking Status

    alt Banking Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: Banking management disabled
    else Banking Allowed
        Check-->>API: Access Granted
        API->>Banking: Execute AddBanking
        Banking->>DB: Validate Bank Account
        Banking->>DB: INSERT INTO banking
        DB-->>Banking: Bank Created
        Banking-->>API: Bank Account Details
        API-->>User: 200 OK with Bank Account
    end
```

---

`POST /api/account/v2/banking/:bank_uuid/update`

Update an existing bank account with restriction enforcement.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| asset | string | Y | Asset type (e.g., "DigitalCurrency") |
| bank_name | string | Y | Bank name |
| bank_account | string | Y | Bank account number |
| account_holder | string | Y | Account holder name |

**Response (200 OK)**

```
{
  "uuid": "bnk_789",
  "bank_name": "BCA",
  "account_number": "1234567890",
  "account_holder": "John Doe",
  "is_whitelisted": false
}
```

**Response (403 Forbidden)**

```
{
  "error": "BANKING_MANAGEMENT_DISABLED",
  "message": "Banking account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Banking as EditBanking UseCase
    participant BankRepo as BankRepository
    participant DB as Database

    User->>API: POST /api/account/v2/banking/:bank_uuid/update
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('BANKING_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT banking_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Banking Status

    alt Banking Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: Banking management disabled
    else Banking Allowed
        Check-->>API: Access Granted
        API->>Banking: Execute EditBanking
        Banking->>BankRepo: GetBank(bankUuid)
        BankRepo->>DB: SELECT * FROM banking
        DB-->>BankRepo: Bank Data
        BankRepo-->>Banking: Bank Entity

        Banking->>Banking: Validate Ownership
        Banking->>DB: UPDATE banking SET account details
        DB-->>Banking: Bank Updated
        Banking-->>API: Updated Bank Account Details
        API-->>User: 200 OK with Bank Account
    end
```

---

`DELETE /api/account/v2/banking/:bank_uuid`

Delete a bank account with restriction enforcement.

**Response (200 OK)**

```
{
  "message": "Bank account deleted successfully",
  "uuid": "bnk_789"
}
```

**Response (403 Forbidden)**

```
{
  "error": "BANKING_MANAGEMENT_DISABLED",
  "message": "Banking account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Banking as DeleteBanking UseCase
    participant BankRepo as BankRepository
    participant DB as Database

    User->>API: DELETE /api/account/v2/banking/:bank_uuid
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('BANKING_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT banking_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Banking Status

    alt Banking Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: Banking management disabled
    else Banking Allowed
        Check-->>API: Access Granted
        API->>Banking: Execute DeleteBanking
        Banking->>BankRepo: GetBank(bankUuid)
        BankRepo->>DB: SELECT * FROM banking
        DB-->>BankRepo: Bank Data
        BankRepo-->>Banking: Bank Entity

        Banking->>Banking: Validate Ownership
        Banking->>DB: DELETE FROM banking WHERE uuid
        DB-->>Banking: Bank Deleted
        Banking-->>API: Deletion Confirmed
        API-->>User: 200 OK
    end
```

---

**E-Account Account Management APIs (Modified)**

`POST /api/account/v2/eaccount-account`

Add a new e-account account with restriction enforcement.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| provider | string | Y | E-account provider (e.g., "OVO", "GOPAY", "DANA") |
| phone_number | string | Y | Phone number (must start with 0) |
| label | string | Y | Account label/name |

**Response (200 OK)**

```
{
  "uuid": "ew_789",
  "provider": "OVO",
  "phone_number": "081234567890",
  "label": "Personal OVO",
  "is_whitelisted": false
}
```

**Response (403 Forbidden)**

```
{
  "error": "EWALLET_MANAGEMENT_DISABLED",
  "message": "E-account account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Eaccount as AddEaccount UseCase
    participant DB as Database

    User->>API: POST /api/account/v2/eaccount-account
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('EWALLET_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT eaccount_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Eaccount Status

    alt Eaccount Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: E-account management disabled
    else Eaccount Allowed
        Check-->>API: Access Granted
        API->>Eaccount: Execute AddEaccount
        Eaccount->>DB: Validate Phone Number Format
        Eaccount->>DB: INSERT INTO eaccounts
        DB-->>Eaccount: Eaccount Created
        Eaccount-->>API: Eaccount Account Details
        API-->>User: 200 OK with Eaccount Account
    end
```

---

`POST /api/account/v2/eaccount-account/:uuid/update`

Update an existing e-account account with restriction enforcement.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| provider | string | Y | E-account provider (e.g., "OVO", "GOPAY", "DANA") |
| phone_number | string | Y | Phone number (must start with 0) |
| label | string | Y | Account label/name |

**Response (200 OK)**

```
{
  "uuid": "ew_789",
  "provider": "OVO",
  "phone_number": "081234567890",
  "label": "Personal OVO",
  "is_whitelisted": false
}
```

**Response (403 Forbidden)**

```
{
  "error": "EWALLET_MANAGEMENT_DISABLED",
  "message": "E-account account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Eaccount as EditEaccount UseCase
    participant EaccountRepo as EaccountRepository
    participant DB as Database

    User->>API: POST /api/account/v2/eaccount-account/:uuid/update
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('EWALLET_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT eaccount_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Eaccount Status

    alt Eaccount Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: E-account management disabled
    else Eaccount Allowed
        Check-->>API: Access Granted
        API->>Eaccount: Execute EditEaccount
        Eaccount->>EaccountRepo: GetEaccount(uuid)
        EaccountRepo->>DB: SELECT * FROM eaccounts
        DB-->>EaccountRepo: Eaccount Data
        EaccountRepo-->>Eaccount: Eaccount Entity

        Eaccount->>Eaccount: Validate Ownership
        Eaccount->>DB: UPDATE eaccounts SET account details
        DB-->>Eaccount: Eaccount Updated
        Eaccount-->>API: Updated Eaccount Account Details
        API-->>User: 200 OK with Eaccount Account
    end
```

---

`DELETE /api/account/v2/eaccount-account/:uuid`

Delete an e-account account with restriction enforcement.

**Response (200 OK)**

```
{
  "message": "E-account account deleted successfully",
  "uuid": "ew_789"
}
```

**Response (403 Forbidden)**

```
{
  "error": "EWALLET_MANAGEMENT_DISABLED",
  "message": "E-account account management is disabled due to redemption restrictions"
}
```

**Sequence Diagram**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Eaccount as DeleteEaccount UseCase
    participant EaccountRepo as EaccountRepository
    participant DB as Database

    User->>API: DELETE /api/account/v2/eaccount-account/:uuid
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('EWALLET_MANAGEMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT eaccount_redemption_disabled FROM user_restrictions
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Eaccount Status

    alt Eaccount Redemption Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: E-account management disabled
    else Eaccount Allowed
        Check-->>API: Access Granted
        API->>Eaccount: Execute DeleteEaccount
        Eaccount->>EaccountRepo: GetEaccount(uuid)
        EaccountRepo->>DB: SELECT * FROM eaccounts
        DB-->>EaccountRepo: Eaccount Data
        EaccountRepo-->>Eaccount: Eaccount Entity

        Eaccount->>Eaccount: Validate Ownership
        Eaccount->>DB: UPDATE eaccounts SET is_deleted=true
        DB-->>Eaccount: Eaccount Soft Deleted
        Eaccount-->>API: Deletion Confirmed
        API-->>User: 200 OK
    end
```

---

`POST /api/account/v2/transfer/initiate`

P2P transfer initiation with restriction enforcement.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| destination_address | string | Y | Recipient's account identifier (Bank Network A or Bank Network B) |
| ui_amount | string/number | Y | Transfer amount in UI units |

**Response (200 OK)**

```
{
  "serializedTransaction": "base64_encoded_transaction",
  "uuid": "transfer_p2p_uuid_123",
  "seqNo": 42
}
```

**Response (403 Forbidden)**

```
{
  "error": "P2P_TRANSFER_DISABLED",
  "message": "P2P transfers are disabled for this account"
}
```

`POST /api/account/v2/transfer/send`

Execute P2P transfer after initiation.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| uuid | string | Y | Transfer UUID from initiate response |
| data | string | Y | Signed transaction data |
| save_destination | boolean | N | Save destination address for future use |
| address_name | string | N | Name for saved destination (required if save_destination=true) |

**Response (200 OK)**

```
{
  "signature": "tx_hash_123",
  "amount": "1000000",
  "message": "Transfering 1000000 DigitalCurrency to 0xabc... is IN_PROGRESS",
  "uuid": "activity_uuid_123",
  "activity": {
    "uuid": "activity_uuid_123"
  },
  "activity_uuid": "activity_uuid_123"
}
```

**Response (403 Forbidden)**

```
{
  "error": "P2P_TRANSFER_DISABLED",
  "message": "P2P transfers are disabled for this account"
}
```

**Sequence Diagram (Initiate)**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Transfer as TransferInitiate UseCase
    participant DB as Database

    User->>API: POST /api/account/v2/transfer/initiate
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('P2P')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT p2p_transfer_disabled FROM userprofiles
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: P2P Status

    alt P2P Transfer Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: P2P transfers disabled
    else P2P Transfer Allowed
        Check-->>API: Access Granted
        API->>Transfer: Execute TransferInitiate
        Transfer->>DB: Create TransferP2P Record
        Transfer->>Transfer: Build Unsigned Transaction
        Transfer-->>API: Serialized Transaction + UUID
        API-->>User: 200 OK with Transaction to Sign
    end
```

---

`POST /api/account/v2/pay/bank_transfer/initiate`

Payment via bank transfer with restrictions in place.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| bank_uuid | string | Y | Bank account UUID for payment |
| memo | string | N | Payment memo/note |

**Response (200 OK)**

```
{
  "uuid": "redeem_request_uuid_123",
  "status": "INITIATED",
  "activity": {
    "uuid": "activity_uuid_123",
    "owner": "user_account_id",
    "date_created": "2025-10-30T10:00:00Z",
    "source": "PaymentBankTransfer"
  },
  "temp_account": {
    "uuid": "temp_account_uuid_123",
    "account_id": "temp_account_address",
    "DigitalCurrency_balance_address": "temp_account_funds_address",
    "state": "PROVISIONED",
    "failure_operation": null,
    "error_description": null,
    "tx_hash_close": null
  },
  "bank": {
    "account_holder": "John Doe",
    "account_number": "1234567890",
    "bank_name": "BCA"
  }
}
```

**Response (403 Forbidden)**

```
{
  "error": "PAYMENT_DISABLED",
  "message": "Payments are disabled for this account"
}
```

`POST /api/account/v2/pay/bank_transfer/send`

Execute payment after initiation.

**Request**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| uuid | string | Y | Redeem request UUID from initiate |
| data | string | Y | Signed transaction data |

**Response (200 OK)**

```
{
  "uuid": "redeem_request_uuid_123",
  "status": "VALIDATED",
  "activity": {
    "uuid": "activity_uuid_123"
  }
}
```

**Response (403 Forbidden)**

```
{
  "error": "PAYMENT_DISABLED",
  "message": "Payments are disabled for this account"
}
```

**Sequence Diagram (Initiate)**

```mermaid
sequenceDiagram
    participant User as User Client
    participant API as Account API V2
    participant Auth as Auth Service
    participant Check as CheckFeatureAccess UseCase
    participant UserRepo as UserRepository
    participant Payment as PaymentBankTransferInitiate UseCase
    participant BankRepo as BankRepository
    participant DB as Database

    User->>API: POST /api/account/v2/pay/bank_transfer/initiate
    API->>Auth: Verify User Balance
    Auth-->>API: User Authenticated

    API->>Check: Execute CheckFeatureAccess('PAYMENT')
    Check->>UserRepo: GetUserRestrictions(userUuid)
    UserRepo->>DB: SELECT payment_disabled FROM userprofiles
    DB-->>UserRepo: Restriction Status
    UserRepo-->>Check: Payment Status

    alt Payment Disabled
        Check-->>API: 403 Forbidden
        API-->>User: Error: Payments disabled
    else Payment Allowed
        Check-->>API: Access Granted
        API->>Payment: Execute PaymentBankTransferInitiate
        Payment->>BankRepo: ValidateBankAccount
        BankRepo->>DB: SELECT FROM banking
        BankRepo-->>Payment: Bank Valid
        Payment->>DB: Create RedeemRequest (PaymentBankTransfer)
        Payment->>DB: Provision Temporary Account
        Payment-->>API: Payment Initiated
        API-->>User: 200 OK with Transaction Details
    end
```

---

## Security Considerations

### Authorization

- Only the ADMIN role can modify restrictions
- All changes require a reason
- No self-modification allowed
- Private key export requires password + 2FA even when not restricted

### Defense in Depth

- Database constraints enforce restrictions
- Application layer validates before operations
- API layer checks permissions
- Frontend hides disabled features
- Critical operations require additional authentication

---

## Testing Strategy

### Unit Tests

```typescript
describe('UserRestriction', () => {
  it('should prevent banking redemption when disabled', () => {
    const restriction = new UserRestriction({ 
      bankingRedemptionDisabled: true 
    });
    
    expect(restriction.canPerformBankingRedemption()).toBe(false);
  });

  it('should prevent eaccount redemption when disabled', () => {
    const restriction = new UserRestriction({ 
      eaccountRedemptionDisabled: true 
    });
    
    expect(restriction.canPerformEaccountRedemption()).toBe(false);
  });
  
  it('should prevent P2P transfers when disabled', () => {
    const restriction = new UserRestriction({ 
      p2pTransferDisabled: true 
    });
    
    expect(restriction.canPerformP2PTransfer()).toBe(false);
  });
  
  it('should prevent private key export when disabled', () => {
    const restriction = new UserRestriction({
      privateKeyExportDisabled: true
    });

    expect(restriction.canExportPrivateKey()).toBe(false);
  });

  it('should prevent banking account management when banking redemption disabled', () => {
    const restriction = new UserRestriction({
      bankingRedemptionDisabled: true
    });

    expect(restriction.canManageBankingAccounts()).toBe(false);
  });

  it('should prevent eaccount account management when eaccount redemption disabled', () => {
    const restriction = new UserRestriction({
      eaccountRedemptionDisabled: true
    });

    expect(restriction.canManageEaccountAccounts()).toBe(false);
  });
});
```

### Integration Tests

- Test restriction enforcement in the redemption flows (banking and eaccount)
- Test banking account management blocking (add/update/delete)
- Test eaccount account management blocking (add/update/delete)
- Test P2P transfer blocking
- Test payment blocking
- Test private key export blocking

### E2E Tests

- Complete banking redemption flow with restrictions
- Complete eaccount redemption flow with restrictions
- Banking account add/update/delete with restrictions
- Eaccount account add/update/delete with restrictions
- Admin restriction management flow
- P2P transfer with restrictions
- Payment with restrictions
- Private key export with restrictions
- Restriction status API

---

## Acceptance Criteria

1. ✅ Admin can enable/disable banking redemption restrictions for any user
1. ✅ Admin can enable/disable eaccount redemption restrictions for any user
1. ✅ Admin can enable/disable P2P transfer restrictions
1. ✅ Admin can enable/disable payment restrictions
1. ✅ Admin can enable/disable private key export restrictions
1. ✅ Banking redemptions can be disabled per user
1. ✅ E-account redemptions can be disabled per user
1. ✅ P2P transfers can be disabled per user
1. ✅ Payment capability can be disabled per user
1. ✅ Private key export can be disabled per user
1. ✅ Banking account management (add/update/delete) is blocked when banking_redemption_disabled is true
1. ✅ E-account account management (add/update/delete) is blocked when eaccount_redemption_disabled is true
1. ✅ Users can view their restriction status via API
1. ✅ System maintains backward compatibility
1. ✅ All sequences properly enforce restrictions
