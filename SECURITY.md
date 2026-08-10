# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

This is a demonstration repository. If you find a security issue in this demo
code, please open a private security advisory via the
[Security tab](../../security/advisories/new), or contact the repository owner
directly.

If you believe you have found a vulnerability in **GitHub Copilot**, the
**GitHub Copilot SDK**, or another Microsoft or GitHub product rather than in
this demo, please report it through the appropriate vendor channel instead:

- Microsoft — [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md)
- GitHub — [https://github.com/security](https://github.com/security)

## ⚠️ Intentional Vulnerabilities

This repository **deliberately** contains insecure and inefficient code
patterns so they can be caught live during code review and static analysis
demonstrations. These are documented in the *Security Notes* section of the
[README](README.md) and include missing input validation, a missing null
check, an N+1 query, and a hardcoded threshold.

**This code is not intended for production use.** Please do not file
vulnerability reports for the documented demo issues — but do report anything
*not* on that list.

## Supported Versions

Only the latest commit on `main` is maintained. This is demo content and
carries no support or security-patch commitment.
