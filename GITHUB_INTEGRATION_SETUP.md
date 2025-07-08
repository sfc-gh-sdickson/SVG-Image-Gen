# GitHub Integration Setup for Snowflake

This guide walks you through setting up GitHub integration in Snowflake for the SVG-Image-Gen project.

## Prerequisites

1. **Snowflake Account**: You need ACCOUNTADMIN privileges
2. **GitHub Account**: With appropriate repository access
3. **GitHub CLI**: For token management (optional but recommended)

## Step 1: Generate GitHub Personal Access Token

### Option A: Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI if not already installed
# Ubuntu/Debian:
sudo apt install gh

# macOS:
brew install gh

# Authenticate with GitHub
gh auth login

# Check authentication status
gh auth status

# Get current token (if already authenticated)
gh auth token
```

### Option B: Manual Token Creation

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Set Note: "Snowflake SVG-Image-Gen Integration"
4. Set Expiration: 90 days
5. Select these scopes:
   - `repo`: Full control of private repositories
   - `read:org`: Read-only access to organization membership
6. Click "Generate token"
7. Copy the token

## Step 2: Update SQL Integration Script

The `svggen_git_integration.sql` file has been updated with your current token. If you need to use a different token:

1. Replace the `PASSWORD` value in the SQL script
2. Update the `USERNAME` if needed
3. Update the `ORIGIN` URL to match your repository

## Step 3: Execute SQL Script in Snowflake

Run the following commands in Snowflake (as ACCOUNTADMIN):

```sql
-- Execute the integration setup
-- This creates the database, schema, secret, API integration, and Git repository

-- The script is located at: svggen_git_integration.sql
-- Run it in Snowflake SQL editor or via SnowSQL CLI
```

## Step 4: Verify Integration

### Check API Integration
```sql
SHOW API INTEGRATIONS LIKE 'git_api_integration';
```

### Check Git Repository
```sql
SHOW GIT REPOSITORIES LIKE 'svg_image_gen';
```

### Test Git Operations
```sql
-- List files in the repository
SELECT * FROM TABLE(INFORMATION_SCHEMA.GIT_FILES('svg_image_gen'));

-- Read a specific file
SELECT * FROM TABLE(INFORMATION_SCHEMA.GIT_READ_FILE('svg_image_gen', 'README.md'));
```

## Step 5: Test Integration with Python

Run the test script to verify the integration:

```bash
python admin_diagnostics.py
```

## Integration Features

### Available Operations

1. **Repository Management**:
   - Clone repositories
   - List files
   - Read file contents
   - Write files (with commit messages)
   - Create branches

2. **Authentication**:
   - Uses Snowflake secrets for token storage
   - Role-based access control
   - Secure credential management

3. **API Integration**:
   - Direct GitHub API access
   - Custom API provider configuration
   - Allowed prefix restrictions

### Security Considerations

1. **Token Security**:
   - Tokens are stored in Snowflake secrets
   - Encrypted at rest
   - Access controlled by roles

2. **Access Control**:
   - Only authorized roles can use the integration
   - Repository access is limited to specified prefixes
   - Audit logging available

3. **Token Rotation**:
   - Tokens expire after 90 days
   - Regular rotation recommended
   - Update secrets when tokens change

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify token has correct scopes
   - Check token expiration
   - Ensure repository access permissions

2. **Permission Errors**:
   - Verify ACCOUNTADMIN role
   - Check secret access permissions
   - Validate API integration configuration

3. **Repository Access**:
   - Confirm repository URL is correct
   - Check repository visibility (public/private)
   - Verify token has repository access

### Debug Commands

```sql
-- Check integration status
SHOW API INTEGRATIONS;

-- Check secrets
SHOW SECRETS;

-- Check Git repositories
SHOW GIT REPOSITORIES;

-- Test API connectivity
SELECT * FROM TABLE(INFORMATION_SCHEMA.GIT_FILES('svg_image_gen')) LIMIT 1;
```

## Next Steps

1. **Deploy to Snowflake**: Upload your application to Snowflake workspace
2. **Configure Application**: Update application to use the Git integration
3. **Test Operations**: Verify all Git operations work as expected
4. **Monitor Usage**: Set up monitoring for integration usage

## Support

For issues with the integration:
1. Check Snowflake logs for error messages
2. Verify GitHub token permissions
3. Test with simple operations first
4. Contact support if issues persist

---

**Last Updated**: 2024-12-19
**Version**: 1.0.0
