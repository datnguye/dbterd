<div align="center">

# 🔒 Security Policy

**Keeping dbterd safe and secure for everyone**

We take the security of dbterd seriously and appreciate your help in keeping our community safe.

</div>

---

## 📋 Table of Contents

- [🔒 Security Policy](#-security-policy)
  - [📋 Table of Contents](#-table-of-contents)
  - [🛡️ Supported Versions](#️-supported-versions)
  - [🚨 Reporting a Vulnerability](#-reporting-a-vulnerability)
    - [🔐 Private Reporting (Recommended)](#-private-reporting-recommended)
    - [📧 Alternative Reporting Methods](#-alternative-reporting-methods)
    - [📋 What to Include in Your Report](#-what-to-include-in-your-report)
  - [⏱️ Response Timeline](#️-response-timeline)
  - [🛠️ Security Best Practices](#️-security-best-practices)
    - [For Users](#for-users)
    - [For Contributors](#for-contributors)
  - [🏆 Security Acknowledgments](#-security-acknowledgments)
  - [📞 Contact Information](#-contact-information)

---

## 🛡️ Supported Versions

We maintain security updates only for the latest version of dbterd:

| Version | Support Status | Security Updates | Notes |
|---------|----------------|------------------|-------|
| **Latest** | ✅ **Fully Supported** | ✅ Active | Current stable release |
| **All Previous** | ❌ **Not Supported** | ❌ None | Please upgrade to latest |

> [!IMPORTANT]
> **Security Policy**: Only the latest version receives security updates. Please upgrade to the newest release for security patches and bug fixes.

---

## 🚨 Reporting a Vulnerability

**We appreciate responsible disclosure of security vulnerabilities.** Your efforts help keep the dbterd community safe.

### 🔐 Private Reporting (Recommended)

The most secure way to report vulnerabilities is through GitHub's private vulnerability reporting system:

1. **Navigate to**: [Report Security Vulnerability](https://github.com/datnguye/dbterd/security/advisories/new)
2. **Use Title Format**: `[SECURITY] Brief description of the issue`
3. **Fill out all required fields** with detailed information
4. **Submit** - Only maintainers will have access to your report

### 📧 Alternative Reporting Methods

If GitHub's private reporting is unavailable:

- **Security Advisory**: [Create New Advisory](https://github.com/datnguye/dbterd/security/advisories/new/?title=[SEC])
- **Direct Contact**: Reach out to maintainers through secure channels

### 📋 What to Include in Your Report

To help us address the vulnerability quickly, please include:

**Required Information:**
- **Vulnerability Type**: (e.g., injection, authentication bypass, data exposure)
- **Affected Components**: Specific modules, functions, or endpoints
- **Attack Vector**: How the vulnerability can be exploited
- **Impact Assessment**: Potential consequences of exploitation
- **Affected Versions**: Which versions are vulnerable

**Helpful Additions:**
- **Proof of Concept**: Step-by-step reproduction steps
- **Suggested Fix**: If you have ideas for remediation
- **CVSS Score**: If you've calculated one
- **References**: Related CVEs or security advisories

---

## ⏱️ Response Timeline

We are committed to responding promptly to security reports:

| Timeline | Action |
|----------|--------|
| **24 hours** | Initial acknowledgment of your report |
| **72 hours** | Preliminary assessment and triage |
| **7 days** | Detailed analysis and response plan |
| **30 days** | Resolution target for most vulnerabilities |

> [!NOTE]
> **Complex vulnerabilities** may require additional time. We'll keep you informed throughout the process.

**Response Process:**
1. **Acknowledge** receipt of your report
2. **Validate** and reproduce the vulnerability
3. **Assess** impact and severity
4. **Develop** and test patches
5. **Coordinate** disclosure timeline
6. **Release** security updates
7. **Publish** security advisory (if applicable)

---

## 🛠️ Security Best Practices

### For Users

**Installation & Updates:**
- ✅ Always install from official sources (PyPI: `pip install dbterd`)
- ✅ Keep dbterd updated to the latest version
- ✅ Regularly update dependencies: `pip install dbt-artifacts-parser --upgrade`
- ✅ Use virtual environments to isolate dependencies

**Configuration Security:**
- 🔐 Never commit credentials or API keys to version control
- 🔐 Use environment variables for sensitive configuration
- 🔐 Implement proper access controls for dbt artifact files
- 🔐 Review generated ERDs before sharing publicly

**Runtime Security:**
- 🛡️ Run dbterd in secure, isolated environments
- 🛡️ Limit file system access permissions
- 🛡️ Monitor for unusual activity or errors
- 🛡️ Validate input files before processing

### For Contributors

**Development Security:**
- 🔒 Follow secure coding practices
- 🔒 Never commit secrets, keys, or credentials
- 🔒 Use dependency scanning tools
- 🔒 Implement input validation and sanitization
- 🔒 Write security-focused tests

**Code Review Requirements:**
- 👥 All changes require security-aware code review
- 👥 Pay special attention to file I/O operations
- 👥 Validate any external dependencies
- 👥 Test with malformed/malicious inputs

---

## 🏆 Security Acknowledgments

We believe in recognizing those who help improve our security:

**Hall of Fame** - Security researchers who have responsibly disclosed vulnerabilities:
- *Your name could be here! We appreciate responsible disclosure.*

**Recognition Process:**
- Public acknowledgment in release notes
- Credit in security advisories
- Optional listing in this document
- Our heartfelt gratitude! 🙏

---

## 📞 Contact Information

**Security Team:**
- **Primary Contact**: [@datnguye](https://github.com/datnguye)
- **GitHub Security**: [Security Tab](https://github.com/datnguye/dbterd/security)
- **Community**: [Discussions](https://github.com/datnguye/dbterd/discussions)

**For Non-Security Issues:**
- 🐛 [Bug Reports](https://github.com/datnguye/dbterd/issues)
- 💡 [Feature Requests](https://github.com/datnguye/dbterd/discussions)
- 📖 [Documentation](https://dbterd.datnguye.me/)

---

<div align="center">

**🔒 Security is a shared responsibility**

*Thank you for helping keep dbterd secure for everyone!*

---

**Last Updated**: June 2024 | **Policy Version**: 2.0

</div>
