# Changelog

All notable changes to CereForge are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [1.2.0] — 2026-03-05

### Added
- `src/utils/errorUtils.js` — shared `extractErrorMessage(err, fallback)` utility that safely converts any API error response to a string, handling plain strings, 422 validation arrays (`[{field, message, type}]`), and undefined/null.

### Fixed
- React crash when posting or replying to comments: backend 422 validation errors return an array of objects, which React cannot render as a child directly. All error display paths now go through `extractErrorMessage`.
- Same fix applied across `PostDetail.jsx`, `Community.jsx`, `ForgotPassword.jsx`, and `Admin.jsx` — previously these all read `err.response?.data?.detail` directly without guarding against arrays.

---

## [1.1.0] — 2026-02-28

### Added
- Bookmark/Favorite system for community posts
- Search functionality and empty state improvements in the community forum
- Solution resubmission for tasks with retroactive XP and badge calculation
- Post deletion functionality for authors and admins
- Admin role flag in user profiles and UI-level permission checks
- Comprehensive CereForge Student Guide for faster onboarding
- Automated Puppeteer E2E tests for frontend verification
- Unit tests for backend community features (comments, deletion)
- Connection test utility for backend diagnostics

### Fixed
- Improved community post and comment loading logic to prevent concurrency errors
- Resolved port mismatch between frontend and backend in development
- Enhanced frontend status UI for completed tasks

## [1.0.0] — 2026-02-24

### Added
- Initial release of CereForge platform
- 12 AI engineering tasks across 4 tracks (LLM, RAG, Computer Vision, Agents)
- XP system with 5 rank tiers (Trainee → CereForge Elite)
- 12 unlockable badges with cinematic reveal animation
- Community Q&A forum with voting and accepted answers
- AI Mentor powered by Claude (Anthropic)
- 3 adaptive learning paths for all skill levels
- Google Colab integration for practical task completion
- Leaderboard with XP-based rankings
- Full JWT authentication with refresh token rotation
- Docker Compose for one-command local setup
- GitHub Actions CI/CD pipeline
- Production security headers and request tracing middleware
