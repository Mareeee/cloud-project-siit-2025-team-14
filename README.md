# Cloud Music Platform - Serverless Web App (AWS + Python Backend, Angular Frontend)

A cloud‑native web application for storing, sharing, and listening to music. The system is built on AWS with a Python backend and an Angular frontend. It supports multiple user roles (guest, authenticated user, administrator), music content management, discovery & filtering, ratings, subscriptions with notifications, a personalized feed, optional offline caching/download, and automatic lyrics transcription.

> This README explains how to set up the project locally, how to deploy backend resources to AWS with the CDK, and which features are implemented per the course specification.

---

## Table of Contents
- [Architecture at a Glance](#architecture-at-a-glance)
- [Key Features (as required by the spec)](#key-features-as-required-by-the-spec)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Local Setup & Running](#local-setup--running)
  - [Backend (Python + AWS)](#backend-python--aws)
  - [Frontend (Angular)](#frontend-angular)
- [Environment Configuration](#environment-configuration)
- [Deploying to AWS](#deploying-to-aws)
- [Development Workflow](#development-workflow)
- [Feature Details](#feature-details)
  - [Authentication & Roles](#authentication--roles)
  - [Content Management](#content-management)
  - [Discover (Genre Filtering)](#discover-genre-filtering)
  - [Ratings](#ratings)
  - [Subscriptions & Notifications](#subscriptions--notifications)
  - [Personalized Feed](#personalized-feed)
  - [Offline Caching & Downloads](#offline-caching--downloads)
  - [Lyrics Transcription](#lyrics-transcription)
- [Data & Storage Model](#data--storage-model)
- [API Gateway & Endpoints](#api-gateway--endpoints)

---

## Architecture at a Glance

**Cloud‑native, event‑driven** design on AWS:
- **API Gateway** exposes REST endpoints to the Angular frontend.
- **AWS Lambda (Python)** implements business logic for content, ratings, subscriptions, feed, and transcription orchestration.
- **DynamoDB** stores metadata (users, artists, albums, songs, ratings, feeds, links to genres, etc.).
- **Amazon S3** stores music files and cover images; presigned URLs are used for efficient upload/download/streaming.
- **Amazon SQS / SNS** enables asynchronous tasks (notifications, feed refresh, transcription triggers).
- **Amazon Cognito** (or custom authorizer) secures endpoints and validates tokens at the gateway layer.
- **CloudFront + S3 static hosting** (recommended) serves the Angular build for public access.
- **AWS CDK** (IaC) provisions all infrastructure.

---

## Key Features (as required by the spec)

The project implements the following capabilities corresponding to the course specification:

- **Registration & Login**: user registration and sign‑in, with secure token validation at API Gateway.
- **Artists CRUD (Admin)**: create, update, delete artists with biography and genres.
- **Content Upload (Admin)**: upload songs/albums with file metadata (name, type, size, created/modified); associate cover image, genres, artists, album membership.
- **Content View & Playback**: browse content and listen via the web player in the frontend.
- **Content Edit & Delete (Admin)**: modify metadata or replace files; removing content cleans up dependent metadata.
- **Discover / Filtering (User)**: filter by genre to list artists/albums and drill down into their content.
- **Ratings (User)**: rate songs with a simple multi‑level system (e.g., 1–3 or like/neutral/dislike).
- **Subscriptions (User)**: subscribe to artists/genres; receive notifications when new content is published.
- **Subscription Management (User)**: list and manage (unsubscribe) existing subscriptions.
- **Personalized Feed (User)**: aggregated per‑user recommendations based on ratings, subscriptions, and listening history/time‑of‑day patterns; feed updates as events occur.
- **Offline Caching (User)**: choose songs for local cached playback; download raw files when needed.
- **Lyrics Transcription (System)**: asynchronous audio transcription; users can listen even before transcription completes; retries & error handling supported.
- **API Gateway** front‑door; **separate storage for files and metadata**; **event‑driven communication** where it makes sense.
- **Infrastructure as Code** using **AWS CDK** (imperative), with optional declarative examples if desired.

---

## Tech Stack

- **Frontend**: Angular, RxJS, Angular Material, HTML/CSS/TypeScript
- **Backend**: Python (AWS Lambda), boto3
- **Infra**: AWS CDK (TypeScript or Python), API Gateway, DynamoDB, S3, SNS/SQS, Cognito, CloudWatch, CloudFront
- **Tooling**: Node.js + npm, Angular CLI, Python venv

---

## Repository Structure

```
.
├─ backend/                 # Python Lambdas, shared libs, CDK app for backend infra
│  ├─ backend_stack/        # (API Gateway, DynamoDB tables, S3, SNS/SQS)
│  └─ lambda/               # Individual function code (content, ratings, feed, etc.)
├─ frontend/                # Angular app
│  ├─ src/
│  └─ package.json
└─ README.md
```

---

## Prerequisites

- **AWS account** with programmatic access (Access Key ID / Secret Key) and a default region configured.
- **Node.js 18+** and **npm**.
- **Angular CLI** (`npm i -g @angular/cli`).
- **Python 3.11+**.

> If this is your first CDK deployment in the account/region, you may need `cdk bootstrap` before `cdk deploy`.

---

## Local Setup & Running

### Backend (Python + AWS)

1. **Navigate to backend and create/activate a virtual environment**  
   **Windows (PowerShell):**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
   **macOS/Linux (bash/zsh):**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Deploy all stacks**  
   ```bash
   cdk deploy --all
   ```
   This provisions API Gateway, Lambdas, DynamoDB tables, S3 buckets, SQS/SNS, Cognito, roles/policies, etc.

> After deploy, note any output values (API URL, bucket names, Cognito IDs) and configure them in the frontend environment files.

### Frontend (Angular)

1. **Install dependencies & run the dev server**
   ```bash
   cd frontend
   npm i
   ng s
   ```
   The app runs on `http://localhost:4200/` by default. Make sure the environment points to the deployed API Gateway URL and region.

---

## Environment Configuration

You’ll typically set the following in your backend CDK or Lambda env configuration and in the Angular environment files:

- **AWS Region** (e.g., `eu-central-1`)
- **S3 Buckets** for media and public assets
- **DynamoDB Table Names** (songs, artists, albums, ratings, subscriptions, feed, genre/artist catalogs)
- **API Gateway URL** (frontend `environment.ts`)
- **Cognito IDs / Auth settings** (User Pool ID, App Client ID), or custom authorizer config
- **Transcription/Notification topics/queues** (SNS/SQS ARNs)

> The CDK app should output/propagate the necessary env values; keep your Angular `environment.ts` in sync.

---

## Deploying to AWS

- **One‑shot**: from `/backend` run `cdk deploy --all` to provision/refresh all stacks.
- **Partial updates**: deploy specific stacks (e.g., `cdk deploy ApiStack`).
- **Teardown**: `cdk destroy --all` removes the infrastructure (be careful with data!).

> Large file uploads should use **presigned S3 URLs** rather than direct API Gateway requests to avoid payload limits.

---

## Development Workflow

- Commit PRs to feature branches, merge into `develop`, then promote to `main` once verified.
- Keep Lambdas small and focused; share common code via a `/backend/lambdas/shared` module.
- Emit **events** (SNS/SQS) on content changes to refresh feeds and send notifications.
- Guard all protected endpoints with **Cognito authorizers** at API Gateway (or a custom Lambda authorizer).

---

## Feature Details

### Authentication & Roles
- **Guest** can register or sign in.
- **User** can browse, play, rate, subscribe, manage subscriptions, download/cache, and view a personalized feed.
- **Admin** can manage artists, songs, and albums.

### Content Management
- Upload songs (and optionally batch upload albums) with metadata and cover art.
- Content may be linked to multiple artists and genres; songs may be part of an album or be singles.
- Admin can edit metadata or replace audio/cover; delete cascades related metadata.

### Discover (Genre Filtering)
- Genre‑based browsing to list artists/albums, then drill into their songs.
- Optimized DynamoDB access patterns via catalog tables and GSI where applicable.

### Ratings
- Single rating per user per song using a simple multi‑level scale (≥3 levels).

### Subscriptions & Notifications
- Subscribe to **artists** and/or **genres**.
- When new content is published, subscribers are notified via **email**.
- Users can list and unsubscribe from any subscription.

### Personalized Feed
- Feed considers:
  - past ratings,
  - active subscriptions,
  - listening history & time‑of‑day behavior.
- Feed entries refresh automatically on relevant events (uploads, ratings, listens, subscription changes).

### Offline Caching & Downloads
- Users can select songs for local cached playback (frontend stores a local copy).
- **Download** of the raw file is available where allowed.
- Fully offline mode is optional; basic caching suffices.

### Lyrics Transcription
- Asynchronous pipeline kicks off on upload.
- Users can play immediately; lyrics appear when ready.
- Retries & idempotency to handle processing errors.

---

## Data & Storage Model

- **DynamoDB** for metadata:
  - `Songs`, `Artists`, `Albums` tables
  - `GenreCatalog`, `ArtistCatalog` tables (many‑to‑many lookups)
  - `Ratings`, `Subscriptions`, `Feed` tables
  - GSIs for efficient queries (by song/artist/genre, user id, etc.).
- **S3** buckets for audio and cover images; filenames and presigned URLs managed by Lambdas.

---

## API Gateway & Endpoints

Representative endpoints (prefix omitted):
- `POST /auth/register`, `POST /auth/login`
- `GET /artists`, `POST /artists`, `PUT /artists/{id}`, `DELETE /artists/{id}`
- `GET /songs`, `POST /songs`, `PUT /songs/{id}`, `DELETE /songs/{id}`
- `GET /albums`, `POST /albums`, `PUT /albums/{id}`, `DELETE /albums/{id}`
- `GET /discover?genre=...`
- `POST /ratings` (create/update), `DELETE /ratings/{songId}`
- `GET /subscriptions`, `POST /subscriptions`, `DELETE /subscriptions/{id}`
- `GET /feed`
- `GET /lyrics/{songId}`
