# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Use the **Report a vulnerability** button in the Security tab of this repository to open a private
advisory. Include what you found, how to reproduce it and the impact you expect. You will get a
first answer within 72 hours.

## Scope notes

RepoDoctor reads the repository it is pointed at and never executes its code. The exceptions are
plugins: files passed with `--plugin` and packages installed in the `repodoctor.checks` entry point
group run as normal Python code, so only load plugins you trust. Project configuration files can
not load plugins on their own, by design.
