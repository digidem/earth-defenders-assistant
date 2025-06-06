# Credentials Directory

This directory contains sensitive credential files that are not tracked by Git.

## Structure

```
credentials/
├── google/
│   └── gen-lang-client-xxxx.json  (Google Cloud service account key)
└── other/
    └── (other credential files)
```

## Setup Instructions

1. Place your Google Cloud service account JSON file in the `google/` directory
2. Update your configuration to point to the correct credential file path
3. Never commit actual credential files to the repository

## Security Notes

- All `.json`, `.key`, `.pem`, and other credential files are automatically ignored by Git
- Only `.gitkeep`, `README.md`, and `.gitignore` files are tracked in this directory
- Always verify that sensitive files are not staged before committing
```