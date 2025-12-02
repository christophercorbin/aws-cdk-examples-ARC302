# Security Logging Requirements

## Overview

This application implements comprehensive logging to support security investigations, audit requirements, and compliance obligations in accordance with AWS Well-Architected Framework best practice SEC04-BP01.

## CloudTrail Configuration

This application requires AWS CloudTrail to be enabled at the account level to log:
- DynamoDB API calls (PutItem, GetItem, DescribeTable, etc.)
- Lambda invocation events via IAM role assumptions
- VPC endpoint API calls
- API Gateway management operations

### CloudTrail Requirements

Ensure CloudTrail is configured with:
- **Multi-region trail enabled**: Captures events across all AWS regions
- **Log file validation enabled**: Ensures log integrity for forensic analysis
- **S3 bucket with appropriate retention policy**: Store logs for long-term compliance
- **CloudWatch Logs integration**: Enable real-time monitoring and alerting
- **Management events logging**: Track control plane operations
- **Data events logging** (optional): Track data plane operations for sensitive resources

## Application Logging Configuration

### Log Retention Policies

- **VPC Flow Logs**: 1 year retention in CloudWatch Logs
- **API Gateway Access Logs**: 1 year retention in CloudWatch Logs
- **Lambda Function Logs**: 1 year retention in CloudWatch Logs
- **CloudTrail Logs**: 7 years retention (as per compliance requirements)

### VPC Flow Logs

- **Purpose**: Network traffic visibility for security investigations
- **Captures**: Source/destination IPs, ports, protocols, packet counts, accept/reject decisions
- **Use Cases**: Detecting anomalous connections, investigating network-level threats, troubleshooting connectivity

### API Gateway Access Logs

- **Purpose**: Audit trail of API requests
- **Captures**: Caller identity, source IP, HTTP method, request time, resource path, response status, user agent
- **Format**: JSON with standard fields for easy parsing and analysis
- **Use Cases**: Security investigations, compliance audits, usage analysis

### Lambda Function Logs

- **Purpose**: Application-level security events and operational metrics
- **Captures**: Request context, source IP, user agent, operation results, errors
- **Format**: Structured JSON logging for CloudWatch Logs Insights queries
- **Use Cases**: Debugging, security event correlation, performance analysis

### DynamoDB Point-in-Time Recovery

- **Purpose**: Data protection and recovery from accidental modifications
- **Capability**: Restore table to any point in time within the last 35 days
- **Use Cases**: Recovering from accidental deletions, investigating data tampering, compliance requirements

## Log Analysis and Querying

### CloudWatch Logs Insights

Use CloudWatch Logs Insights to query logs across all log groups:

```sql
# Find all requests from a specific IP
fields @timestamp, source_ip, event, item_id
| filter source_ip = "<IP_ADDRESS>"
| sort @timestamp desc

# Find all errors in the last hour
fields @timestamp, error_type, error_message, request_id
| filter event = "error"
| sort @timestamp desc
| limit 100

# Analyze API Gateway access patterns
fields @timestamp, ip, httpMethod, resourcePath, status
| stats count() by ip, httpMethod
| sort count desc
```

## Security Investigation Procedures

### Incident Response Workflow

1. **Identify the incident**: Use CloudWatch alarms or security findings
2. **Gather context**: Query CloudTrail for API-level activity
3. **Analyze network traffic**: Review VPC Flow Logs for network-level indicators
4. **Review application logs**: Check Lambda logs for application-level events
5. **Correlate events**: Use X-Ray traces to understand request flow
6. **Document findings**: Export relevant logs for forensic analysis

### Log Retention and Compliance

- Logs are retained according to organizational security and compliance requirements
- CloudWatch Logs are encrypted at rest using AWS-managed keys
- Consider implementing AWS KMS customer-managed keys for additional control
- Implement log file integrity monitoring using CloudTrail log file validation

## Additional Security Considerations

- **Access Control**: Restrict access to log groups using IAM policies
- **Log Encryption**: All logs are encrypted at rest and in transit
- **Log Integrity**: CloudTrail log file validation ensures logs haven't been tampered with
- **Alerting**: CloudWatch alarms notify teams of security-relevant events
- **Centralization**: Consider using AWS Security Lake for centralized log management across accounts

## References

- [AWS Well-Architected Framework - SEC04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_detect_investigate_events_app_service_logging.html)
- [AWS Security Incident Response Guide](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)
- [CloudWatch Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
