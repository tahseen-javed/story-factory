# SETUP_YOUTUBE (browser only, once)

Goal: a refresh token that can upload videos, set thumbnails and add captions to your channel, nothing more.
Scopes: `https://www.googleapis.com/auth/youtube.upload` and `https://www.googleapis.com/auth/youtube.force-ssl`.

1. Google Cloud console -> New project `story-factory`.
2. APIs & Services -> Library -> YouTube Data API v3 -> Enable.
3. OAuth consent screen: External, app name `story-factory`, your email. Add the two scopes. Add your account as a test user, then **Publish app** so the status is **In production**. (Apps left in "Testing" get refresh tokens that expire after 7 days.)
4. Credentials -> Create credentials -> OAuth client ID -> Web application -> redirect URI `https://developers.google.com/oauthplayground`. Copy client id and secret.
5. OAuth Playground: gear -> "Use your own OAuth credentials" -> paste id/secret -> enter both scopes -> Authorize APIs -> pick your channel -> Exchange authorization code for tokens -> copy the refresh token.
6. GitHub secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

Behaviour (factory/publish.py): privacy PRIVATE, madeForKids=false, resumable upload, idempotent per video number, quota-aware (video insert 1,600, thumbnail 50, caption 400 of 10,000 daily units, Pacific-time reset). On `invalid_grant` the upload is skipped, the bundle is still delivered and the status says: "re-authorise YouTube (docs/SETUP_YOUTUBE.md step 5)".
