# Security policy

GroundTwin processes Bodengutachten, which are often confidential. Please report security problems
**privately**: on GitHub, open the repository's **Security** tab → **Report a vulnerability**. Do not
open a public issue for a vulnerability.

## Supported versions

Only the latest `main` receives fixes.

## Things to know before running it online

- There is no user management: one password (HTTP Basic, `GEO_AGENT_PASSWORT`) protects everything
  except the health check `/gesund` ([docs/22 §8](docs/22_deployment.md#8-security-data-and-license)).
- Run it on a network only with that password and with HTTPS (platform, reverse proxy or Cloudflare
  tunnel).
- Uploaded PDFs, projects and IFC files stay in the work folder (`GEO_AGENT_ARBEIT`); protect and back
  up that folder like the Gutachten themselves.
