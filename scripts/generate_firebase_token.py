#!/usr/bin/env python3
"""
Script to generate Firebase Auth token for API testing.

Usage:
    python scripts/generate_firebase_token.py

Environment variables (optional):
    FIREBASE_EMAIL - User email for authentication
    FIREBASE_PASSWORD - User password for authentication
    FIREBASE_API_KEY - Firebase Web API Key (required)

If email/password are not provided via env vars, the script will prompt for them.
"""

import os
import subprocess
import sys
from getpass import getpass

import requests


def get_firebase_token(email: str, password: str, api_key: str) -> dict:
    """
    Authenticate with Firebase and get an ID token.

    Args:
        email: User email
        password: User password
        api_key: Firebase Web API Key

    Returns:
        dict with 'idToken', 'refreshToken', 'expiresIn', etc.

    Raises:
        Exception if authentication fails
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {"email": email, "password": password, "returnSecureToken": True}

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        error_data = response.json()
        error_message = error_data.get("error", {}).get("message", "Unknown error")
        raise Exception(f"Firebase authentication failed: {error_message}")

    return response.json()


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard using platform-specific commands.

    Args:
        text: Text to copy

    Returns:
        True if successful, False otherwise
    """
    try:
        # Try xclip (X11)
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode(),
            check=True,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        # Try wl-copy (Wayland)
        subprocess.run(
            ["wl-copy"], input=text.encode(), check=True, stderr=subprocess.DEVNULL
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        # Try pbcopy (macOS)
        subprocess.run(
            ["pbcopy"], input=text.encode(), check=True, stderr=subprocess.DEVNULL
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return False


def main():
    """Main function to generate Firebase token."""
    # Get Firebase API Key (required)
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        print(
            "Error: FIREBASE_API_KEY environment variable is required.", file=sys.stderr
        )
        print("\nGet your Web API Key from Firebase Console:", file=sys.stderr)
        print("  1. Go to Firebase Console > Project Settings", file=sys.stderr)
        print("  2. Under 'General' tab, find 'Web API Key'", file=sys.stderr)
        print("\nSet it with: export FIREBASE_API_KEY=your_api_key", file=sys.stderr)
        sys.exit(1)

    # Get email (from env or prompt)
    email = os.getenv("FIREBASE_EMAIL")
    if not email:
        email = input("Email: ").strip()
        if not email:
            print("Error: Email is required.", file=sys.stderr)
            sys.exit(1)

    # Get password (from env or prompt)
    password = os.getenv("FIREBASE_PASSWORD")
    if not password:
        password = getpass("Password: ")
        if not password:
            print("Error: Password is required.", file=sys.stderr)
            sys.exit(1)

    try:
        print("\nAuthenticating with Firebase...", file=sys.stderr)
        result = get_firebase_token(email, password, api_key)

        id_token = result["idToken"]
        refresh_token = result["refreshToken"]
        expires_in = result["expiresIn"]

        # Try to copy to clipboard
        clipboard_success = copy_to_clipboard(id_token)

        print("\n✓ Authentication successful!", file=sys.stderr)
        print(
            f"  Token expires in: {expires_in} seconds (~{int(expires_in) // 3600} hours)",
            file=sys.stderr,
        )

        if clipboard_success:
            print("\n📋 ID Token copied to clipboard!", file=sys.stderr)
        else:
            print(
                "\n⚠️  Could not copy to clipboard (install xclip, wl-clipboard, or use macOS)",
                file=sys.stderr,
            )

        print("\n" + "=" * 80, file=sys.stderr)
        print("ID Token (use this as Bearer token):", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print(id_token)
        print("=" * 80, file=sys.stderr)
        print("\nRefresh Token:", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print(refresh_token)
        print("=" * 80, file=sys.stderr)
        print("\nTo use with curl:", file=sys.stderr)
        print(
            f'  curl -H "Authorization: Bearer {id_token}" http://localhost:8000/api/v1/...',
            file=sys.stderr,
        )
        print("\nTo set as environment variable:", file=sys.stderr)
        print(f"  export BEARER_TOKEN='{id_token}'", file=sys.stderr)

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
