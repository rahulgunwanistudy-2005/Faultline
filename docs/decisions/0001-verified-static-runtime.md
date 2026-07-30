# ADR 0001: Use one zero-build verified runtime

## Status

Accepted; revised during the v0.2.0 security audit.

## Decision

Serve the competition interface as static HTML/CSS/JavaScript from FastAPI. Remove the duplicate, unverified Next.js/React tree from the release.

## Why

- Judge Mode must not fail because of a frontend package install, CDN, or server-rendering issue.
- One deployable runtime eliminates drift between two interfaces.
- The removed tree had no lockfile and was not part of the tested deployment path.
- Static JavaScript syntax, generated-fixture integrity, HTTP routes, and API behavior can be verified deterministically.

## Consequence

Product migration to another frontend framework must be a separate, fully tested change with its own dependency lockfile and security review. There is no second interface to mirror in this release.
