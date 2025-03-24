User Story: Create Export Data Validation Service
Description:
The goal of this user story is to ensure that data transfer between teams is valid by enforcing a predefined JSON structure. The schema is agreed upon in advance, and all development must adhere to it. The validation service will check data integrity before export and before import to prevent errors in the pipeline.

Acceptance Criteria:
Schema Repository Management

A dedicated GitHub repository is created to store the agreed-upon JSON schema.
Changes to the schema can only be made via pull requests, requiring approval from both teams.
CI/CD Process for Schema Validation

A CI/CD pipeline is set up for validating schema changes before they are merged.
Developers suggest a storage type (e.g., PostgreSQL, DynamoDB, or other) for maintaining schema versions if necessary.
Validation Service Implementation

A validation service is built to check the structure of export/import JSON files against the agreed schema.
The validation must occur:
Before data export (ensuring the data conforms to the schema before being sent).
Before data import (ensuring incoming data is valid before being processed).
Developers suggest the infrastructure for hosting and running the validation service (e.g., AWS Lambda, API Gateway, containerized service, etc.).
Error Handling & Reporting

If validation fails, the service must:
Provide clear error messages explaining why the data is invalid.
Log the validation results for debugging.
Optionally notify relevant teams via Slack, email, or another agreed method.
Scalability & Maintainability

The validation service should be extensible to support future changes in data structure with minimal rework.
It should support multiple versions of schemas (if necessary) to allow gradual transitions.
Developer Notes:
Developer will propose the best storage and infrastructure approach.
Initial implementation should focus on basic validation, with additional logic for edge cases added later.
Service must support automated tests in CI/CD to prevent schema-breaking changes.
