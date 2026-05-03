# Error Output Style Guide

## Table of Contents

- [Overview](#overview)
- [Generic Project Templates](#generic-project-templates)
- [OWASP Security Principles](#owasp-security-principles)
- [Error Message Structure](#error-message-structure)
- [Structured Logging Standards](#structured-logging-standards)
- [Implementation Guidelines](#implementation-guidelines)
- [Examples](#examples)
- [Common Anti-Patterns](#common-anti-patterns)
- [Related Documents](#related-documents)

## Overview

This guide defines error‑output standards for all homelab tools, scripts, and apps.
It enforces secure handling and clear diagnostics for troubleshooting and reporting.

**Key Objectives:**

- Prevent information disclosure to potential attackers
- Provide meaningful guidance for legitimate users and operators
- Enable statistical analysis and pattern detection
- Support automated error handling and alerting
- Maintain consistency across all system components

## Generic Project Templates

This section provides reusable error message templates and code snippets that can be applied across all project components regardless of technology stack.

### Universal Error Message Template

**Standard Format for All Project Components:**

```text
[COMPONENT-CATEGORY-###] [SEVERITY]: [BRIEF_DESCRIPTION]
Expected: [WHAT_SHOULD_EXIST]
Found: [WHAT_ACTUALLY_EXISTS]
Missing: [WHAT_IS_MISSING]
Action: [SPECIFIC_COMMAND_OR_STEP]
Reference: [DOCUMENTATION_LINK]
```

### Generic Error Categories

#### CONFIG-001 Series: Configuration Issues

```bash
# Template for missing configuration files
echo "[$(basename "$0")-CONFIG-001] ERROR: Required configuration file not found"
echo "Expected: Configuration file at ${EXPECTED_PATH}"
echo "Found: Directory exists at $(dirname "${EXPECTED_PATH}"), file missing"
echo "Missing: $(basename "${EXPECTED_PATH}") configuration file"
echo "Action: Copy template from ${TEMPLATE_PATH} to ${EXPECTED_PATH}"
echo "Reference: ${DOCS_BASE_URL}/#configuration-setup"
```

#### AUTH-001 Series: Authentication/Authorization Issues

```bash
# Template for credential/permission failures
echo "[$(basename "$0")-AUTH-001] ERROR: Authentication failed"
echo "Expected: Valid SSH key or credential for target system"
echo "Found: Connection attempt rejected by target"
echo "Missing: Properly configured authentication method"
echo "Action: Run ssh-copy-id user@target or configure credential store"
echo "Reference: ${DOCS_BASE_URL}/#ssh-setup"
```

#### NETWORK-001 Series: Connectivity Issues

```bash
# Template for network/service connectivity
echo "[$(basename "$0")-NETWORK-001] ERROR: Service connection failed"
echo "Expected: Service responding on specified endpoint"
echo "Found: Connection timeout or rejection"
echo "Missing: Network connectivity or service availability"
echo "Action: Check service status with systemctl status SERVICE_NAME"
echo "Reference: ${DOCS_BASE_URL}/#network-troubleshooting"
```

#### RESOURCE-001 Series: Resource Availability

```bash
# Template for resource constraints
echo "[$(basename "$0")-RESOURCE-001] ERROR: Insufficient resources available"
echo "Expected: Minimum system requirements met"
echo "Found: Current resource allocation below threshold"
echo "Missing: Additional CPU/memory/storage capacity"
echo "Action: Free resources or upgrade system specifications"
echo "Reference: ${DOCS_BASE_URL}/#system-requirements"
```

### Cross-Platform Error Handling Functions

**Bash/Shell Implementation:**

```bash
#!/bin/bash
# Generic error handling functions for all shell scripts

# Set global error handling variables
readonly SCRIPT_NAME="$(basename "$0")"
readonly DOCS_BASE_URL="https://homelab-docs"
readonly LOG_LEVEL="${LOG_LEVEL:-ERROR}"

# Generic error reporting function
report_error() {
    local error_code="$1"
    local brief_desc="$2"
    local expected="$3"
    local found="$4"
    local missing="$5"
    local action="$6"
    local reference="${7:-${DOCS_BASE_URL}/#troubleshooting}"

    {
        echo "[${SCRIPT_NAME}-${error_code}] ${LOG_LEVEL}: ${brief_desc}"
        echo "Expected: ${expected}"
        echo "Found: ${found}"
        echo "Missing: ${missing}"
        echo "Action: ${action}"
        echo "Reference: ${reference}"
    } >&2

    # Log to structured format if logging is configured
    if [[ -n "${STRUCTURED_LOG_FILE:-}" ]]; then
        log_structured_error "$error_code" "$brief_desc" "$expected" "$found" "$missing" "$action" "$reference"
    fi
}

# Structured logging function
log_structured_error() {
    local error_code="$1"
    local brief_desc="$2"
    local expected="$3"
    local found="$4"
    local missing="$5"
    local action="$6"
    local reference="$7"

    cat >> "${STRUCTURED_LOG_FILE}" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "level": "${LOG_LEVEL}",
  "component": "${SCRIPT_NAME}",
  "error_code": "${SCRIPT_NAME}-${error_code}",
  "message": "${brief_desc}",
  "context": {
    "expected": "${expected}",
    "found": "${found}",
    "missing": "${missing}"
  },
  "resolution": "${action}",
  "reference": "${reference}",
  "session_id": "${SESSION_ID:-unknown}",
  "user": "${USER:-unknown}"
}
EOF
}

# File existence validation with standardized error
validate_file_exists() {
    local file_path="$1"
    local file_description="$2"
    local template_path="${3:-}"

    if [[ ! -f "$file_path" ]]; then
        local expected="$file_description at $file_path"
        local found="Directory $(dirname "$file_path") exists: $(test -d "$(dirname "$file_path")" && echo "yes" || echo "no")"
        local missing="$(basename "$file_path") file"
        local action="Create file: ${template_path:+cp $template_path $file_path}"

        report_error "CONFIG-001" "Required file not found" "$expected" "$found" "$missing" "$action"
        return 1
    fi
    return 0
}

# Service status validation
validate_service_status() {
    local service_name="$1"
    local expected_status="${2:-active}"

    if ! systemctl is-active --quiet "$service_name"; then
        local current_status
        current_status="$(systemctl is-active "$service_name" 2>/dev/null || echo "unknown")"

        local expected="Service $service_name in $expected_status state"
        local found="Service status: $current_status"
        local missing="Active service instance"
        local action="Start service: sudo systemctl start $service_name"

        report_error "RESOURCE-001" "Service not available" "$expected" "$found" "$missing" "$action"
        return 1
    fi
    return 0
}

# Network connectivity validation
validate_connectivity() {
    local target_host="$1"
    local target_port="${2:-22}"
    local timeout="${3:-5}"

    if ! timeout "$timeout" bash -c "</dev/tcp/$target_host/$target_port" 2>/dev/null; then
        local expected="Network connectivity to $target_host:$target_port"
        local found="Connection timeout or rejection"
        local missing="Network path or service availability"
        local action="Check network: ping $target_host && telnet $target_host $target_port"

        report_error "NETWORK-001" "Connection failed" "$expected" "$found" "$missing" "$action"
        return 1
    fi
    return 0
}
```

**PowerShell Implementation:**

```powershell
# Generic error handling functions for PowerShell scripts

# Global variables
$Script:ScriptName = $MyInvocation.MyCommand.Name
$Script:DocsBaseUrl = "https://homelab-docs"
$Script:LogLevel = $env:LOG_LEVEL ?? "ERROR"

function Report-Error {
    param(
        [string]$ErrorCode,
        [string]$BriefDescription,
        [string]$Expected,
        [string]$Found,
        [string]$Missing,
        [string]$Action,
        [string]$Reference = "$Script:DocsBaseUrl/#troubleshooting"
    )

    $ErrorMessage = @"
[$Script:ScriptName-$ErrorCode] $Script:LogLevel: $BriefDescription
Expected: $Expected
Found: $Found
Missing: $Missing
Action: $Action
Reference: $Reference
"@

    Write-Error $ErrorMessage

    # Log to structured format if configured
    if ($env:STRUCTURED_LOG_FILE) {
        Write-StructuredError $ErrorCode $BriefDescription $Expected $Found $Missing $Action $Reference
    }
}

function Write-StructuredError {
    param(
        [string]$ErrorCode,
        [string]$BriefDescription,
        [string]$Expected,
        [string]$Found,
        [string]$Missing,
        [string]$Action,
        [string]$Reference
    )

    $LogEntry = @{
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        level = $Script:LogLevel
        component = $Script:ScriptName
        error_code = "$Script:ScriptName-$ErrorCode"
        message = $BriefDescription
        context = @{
            expected = $Expected
            found = $Found
            missing = $Missing
        }
        resolution = $Action
        reference = $Reference
        session_id = $env:SESSION_ID ?? "unknown"
        user = $env:USERNAME ?? "unknown"
    } | ConvertTo-Json -Compress

    Add-Content -Path $env:STRUCTURED_LOG_FILE -Value $LogEntry
}

function Test-FileExists {
    param(
        [string]$FilePath,
        [string]$FileDescription,
        [string]$TemplatePath = ""
    )

    if (-not (Test-Path $FilePath -PathType Leaf)) {
        $Expected = "$FileDescription at $FilePath"
        $Found = "Directory $(Split-Path $FilePath) exists: $(Test-Path (Split-Path $FilePath))"
        $Missing = "$(Split-Path $FilePath -Leaf) file"
        $Action = if ($TemplatePath) { "Copy-Item $TemplatePath $FilePath" } else { "Create file at $FilePath" }

        Report-Error "CONFIG-001" "Required file not found" $Expected $Found $Missing $Action
        return $false
    }
    return $true
}
```

### Usage Examples Across Project Components

**Ansible Playbook Error Handling:**

```yaml
- name: Validate required configuration file exists
  ansible.builtin.stat:
    path: "{{ config_file_path }}"
  register: config_file_check
  failed_when: false

- name: Report configuration file error
  ansible.builtin.fail:
    msg: |
      [ANSIBLE-CONFIG-001] ERROR: Required configuration file not found
      Expected: Configuration file at {{ config_file_path }}
      Found: Directory {{ config_file_path | dirname }} exists: {{ ansible_check_mode | ternary('check_mode', 'yes' if config_file_check.stat.isdir else 'no') }}
      Missing: {{ config_file_path | basename }} configuration file
      Action: Create file using template: ansible-playbook -e config_template=true site.yml
      Reference: {{ docs_base_url }}/#ansible-configuration
  when: not config_file_check.stat.exists
```

**Terraform Error Handling:**

```hcl
# locals.tf - Error message templates
locals {
  error_templates = {
    config_missing = "[TERRAFORM-CONFIG-001] ERROR: Required configuration missing"
    resource_conflict = "[TERRAFORM-RESOURCE-001] ERROR: Resource conflict detected"
    auth_failed = "[TERRAFORM-AUTH-001] ERROR: Provider authentication failed"
  }

  docs_base_url = "https://homelab-docs"
}

# validation.tf - Input validation with standardized errors
variable "ssh_key_path" {
  description = "Path to SSH public key for instance access"
  type        = string

  validation {
    condition = fileexists(var.ssh_key_path)
    error_message = <<EOF
${local.error_templates.config_missing}
Expected: SSH public key file at ${var.ssh_key_path}
Found: File does not exist at specified path
Missing: SSH public key for instance authentication
Action: Generate key with: ssh-keygen -t ed25519 -f ${var.ssh_key_path}
Reference: ${local.docs_base_url}/#ssh-key-generation
EOF
  }
}
```

### Integration with Existing Style Guides

**For AI-Generated Code:**
AI assistants (Augment, Copilot) must use these generic templates when generating error handling code.
Reference this guide in AI instruction documents and ensure generated code follows the standardized format.

**For Linting Integration:**
Configure linters to validate error message format compliance. Add custom linting rules that check for:

- Proper error code format: `[COMPONENT-CATEGORY-###]`
- Required fields: Expected, Found, Missing, Action, Reference
- Consistent severity levels: ERROR, WARNING, INFO, CRITICAL
- Security compliance: No sensitive information disclosure

**For Monitoring Integration:**
Structure error outputs for automated parsing by monitoring systems:

- Use consistent JSON format for machine-readable logs
- Include correlation IDs for distributed tracing
- Implement statistical sampling for high-volume operations
- Enable automatic alerting based on error patterns and frequency

## OWASP Security Principles

### Information Disclosure Prevention

**NEVER include in error messages:**

- Stack traces, database dumps, or debugging information
- File paths, directory structures, or system architecture details
- Software versions, module names, or internal component identifiers
- Database types, connection strings, or schema information
- API keys, passwords, tokens, or other sensitive credentials
- Session identifiers or user-specific data

**ALWAYS implement:**

- Generic error messages for end users
- Detailed logging for operators (separate from user-facing messages)
- Consistent error responses to prevent information leakage
- Default deny access patterns in security controls

### Error Message Consistency

**Maintain uniform responses for:**

- Authentication failures (`Invalid credentials` not `Invalid username` vs `Invalid password`)
- Authorization denials (`Access denied` not `File not found` vs `Permission denied`)
- Resource availability (`Resource unavailable` not specific error reasons)
- Input validation (`Invalid input format` not field-specific details)

## Error Message Structure

### Standard Format

```text
[ERROR_CODE] [SEVERITY]: [USER_MESSAGE]
Context: [CONTEXT_INFORMATION]
Resolution: [ACTIONABLE_GUIDANCE]
Reference: [DOCUMENTATION_LINK]
```

### Field Definitions

**ERROR_CODE**: Standardized identifier for programmatic handling

- Format: `[COMPONENT]-[CATEGORY]-[NUMBER]` (e.g., `ANSIBLE-CONFIG-001`)
- Categories: `CONFIG`, `AUTH`, `NETWORK`, `RESOURCE`, `VALIDATION`, `SYSTEM`
- Numbers: Zero-padded 3-digit sequential identifier

**SEVERITY**: Risk and urgency level

- `CRITICAL`: System failure, immediate action required
- `ERROR`: Component failure, affects functionality
- `WARNING`: Potential issue, monitoring recommended
- `INFO`: Informational message, no action required

**USER_MESSAGE**: Human-readable description (non-technical)

- Clear, concise explanation of the problem
- Focus on impact rather than technical details
- Avoid jargon and implementation specifics

**CONTEXT_INFORMATION**: Relevant environmental details

- Which configuration files are missing vs present
- Expected vs actual file locations
- Service states and dependencies
- Resource availability status

**ACTIONABLE_GUIDANCE**: Specific next steps

- Required configuration changes
- Files to create or modify
- Commands to execute
- Services to restart or check

**DOCUMENTATION_LINK**: Reference to detailed guidance

- Link to relevant documentation section
- Troubleshooting guides
- Configuration examples

## Structured Logging Standards

### JSON Log Format

```json
{
  "timestamp": "2025-01-08T14:30:00Z",
  "level": "ERROR",
  "component": "ansible-playbook",
  "error_code": "ANSIBLE-CONFIG-001",
  "message": "Configuration file validation failed",
  "context": {
    "playbook": "windows-laptop-setup.yml",
    "missing_files": ["/etc/ansible/hosts"],
    "present_files": ["/etc/ansible/ansible.cfg"],
    "expected_location": "/etc/ansible/hosts",
    "current_location": "undefined"
  },
  "resolution": "Create missing inventory file at /etc/ansible/hosts",
  "session_id": "abc123-def456",
  "user_id": "automation-user",
  "trace_id": "789xyz"
}
```

### Field Standards

**timestamp**: ISO 8601 format with UTC timezone
**level**: One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**component**: System component generating the error
**error_code**: Standardized error identifier
**message**: User-friendly error description
**context**: Structured data about the error condition
**resolution**: Specific remediation steps
**session_id**: Unique identifier for the execution session
**user_id**: Operator or service account identifier
**trace_id**: Correlation identifier for distributed operations

## Implementation Guidelines

### Error Code Assignment

**Component Prefixes:**

- `ANSIBLE-*`: Ansible playbooks and roles
- `TERRAFORM-*`: Infrastructure as code
- `DOCKER-*`: Docker Swarm operations
- `SCRIPT-*`: Bash and PowerShell scripts
- `CONFIG-*`: Configuration file issues
- `AUTH-*`: Authentication and authorization
- `NETWORK-*`: Network connectivity and DNS
- `STORAGE-*`: File system and storage issues

**Category Guidelines:**

- `CONFIG`: Missing files, invalid syntax, parameter errors
- `AUTH`: Credential failures, permission denials, certificate issues
- `NETWORK`: Connectivity failures, DNS resolution, timeout errors
- `RESOURCE`: Insufficient capacity, unavailable services, dependency failures
- `VALIDATION`: Input validation, schema compliance, format errors
- `SYSTEM`: Operating system errors, hardware failures, kernel issues

### Statistical Error Capture

**Implement sampling for high-volume operations:**

- Random sampling: 10% of log entries for non-critical operations
- Rate limiting: Maximum 100 error logs per minute per component
- Burst handling: Capture all errors in first 5 minutes of failure
- Pattern detection: Track error frequency and categorize trends

**Error aggregation fields:**

- `error_pattern`: Categorized error type for trend analysis
- `error_frequency`: Number of occurrences within time window
- `failure_correlation`: Related errors in the same session
- `resolution_success`: Whether suggested resolution resolved the issue

### Environment-Specific Logging

**Development Environment:**

- Log level: `DEBUG` and above
- Include detailed context and stack traces
- Log all configuration attempts and validation steps
- Capture performance metrics and timing information

**Staging Environment:**

- Log level: `INFO` and above
- Include operational context without sensitive data
- Log deployment steps and validation results
- Capture integration test outcomes

**Production Environment:**

- Log level: `WARNING` and above
- Minimal context to prevent information disclosure
- Focus on operational issues and security events
- Implement log retention and archival policies

## Examples

### Good Error Messages

**Configuration File Missing:**

```text
[CONFIG-FILE-001] ERROR: Required configuration file not found
Context: Expected ansible.cfg at /etc/ansible/ansible.cfg, found inventory at /etc/ansible/hosts
Resolution: Create ansible.cfg file using template from docs/templates/ansible.cfg.example
Reference: https://homelab-docs/ansible-setup#configuration
```

**Authentication Failure:**

```text
[AUTH-CRED-001] ERROR: Authentication failed
Context: SSH key authentication to control node failed, password authentication disabled
Resolution: Verify SSH public key is added to ~/.ssh/authorized_keys on target host
Reference: https://homelab-docs/ssh-setup#key-management
```

**Service Dependency:**

```text
[DOCKER-DEPEND-001] WARNING: Required service not responding
Context: Service dependency check failed, Docker Swarm cluster status degraded
Resolution: Check service status: docker service ls
Reference: https://homelab-docs/docker-swarm-troubleshooting#services
```

### Poor Error Messages (Anti-Patterns)

**Information Disclosure:**

```text
❌ ERROR: Connection failed to postgres://user:password@10.10.40.30:5432/homelab_db
❌ FATAL: /home/admin/.ssh/id_rsa_infrastructure_deploy_key not found
❌ Stack trace: File "/usr/lib/python3.11/site-packages/ansible/playbook.py", line 127
```

**Inconsistent Responses:**

```text
❌ "User 'admin' not found" vs "Invalid password for existing user"
❌ "File '/etc/config.yml' does not exist" vs "Access denied to configuration file"
❌ "Connection timeout to srv-pve-01.local" vs "Host unreachable: 10.10.40.15"
```

**Unhelpful Messages:**

```text
❌ "An error occurred"
❌ "Operation failed"
❌ "Something went wrong"
❌ "Error code 127"
```

## Common Anti-Patterns

### Information Leakage

**Avoid revealing:**

- Internal IP addresses (`10.10.40.30` → `control node`)
- File system paths (`/home/admin/.ssh/` → `SSH configuration directory`)
- Service versions (`PostgreSQL 13.7` → `database service`)
- System architecture (`x86_64 Ubuntu 22.04.3` → `target system`)

### Inconsistent Error Handling

**Prevent timing attacks:**

- Ensure equal response times for valid/invalid users
- Use consistent message formats for similar error types
- Implement uniform HTTP status codes for equivalent failures

### Missing Context

**Always include:**

- Which files are missing vs which exist
- Expected configuration vs current state
- Required dependencies vs available services
- Suggested remediation steps with specific commands

## Related Documents

- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Ansible Style Guide](ansible-style-guide.md) - Ansible-specific error handling
- [Bash Style Guide](bash-style-guide.md) - Shell script error patterns
- [Linting Standards](linting-standards.md) - Automated error detection

---

**Document Version**: 1.0
**Last Updated**: 2025-01-08
**Next Review**: 2025-04-08
**Author**: Infrastructure Security Team
**Purpose**: Standardize error output for security compliance and operational effectiveness
