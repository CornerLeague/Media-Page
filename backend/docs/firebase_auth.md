# Backend Firebase Authentication

The FastAPI backend validates incoming requests using Firebase ID tokens. By default, the middleware requires a real Firebase
ID token that can be verified with the Firebase Admin SDK.

## Local development helpers

Mock Firebase tokens (e.g., tokens that begin with `mock-firebase-token-`) are **rejected by default**. To opt in during local
development, set the `ALLOW_FIREBASE_MOCK_TOKENS` environment variable to a truthy value:

```bash
export ALLOW_FIREBASE_MOCK_TOKENS=true
```

When this flag is enabled, the middleware accepts mock tokens and injects a deterministic development user so that local
clients can exercise authenticated endpoints without depending on Firebase. The flag is automatically treated as enabled
when either of the following configuration settings is true:

- `FIREBASE_USE_EMULATOR=true`
- `BYPASS_AUTH_IN_DEVELOPMENT=true`

For any other environment (staging, production, CI), leave `ALLOW_FIREBASE_MOCK_TOKENS` unset or explicitly set it to `false`
to ensure that only verified Firebase ID tokens are accepted.

## Recommended practices

- Never enable mock tokens in production deployments.
- Prefer the Firebase emulator when available so that token verification still flows through Firebase-provided tooling.
- Rotate the flag off before running end-to-end tests that rely on real Firebase tokens.
