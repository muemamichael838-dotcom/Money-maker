# Deployment Fix: Money Maker 🤑 (v1.4) - Deep Diagnostics

## Problem
The dashboard remained unreachable (`ECONNREFUSED`) despite multiple startup fallback attempts. The root cause was invisible to the user.

## Solution
- **Live Debugging**: The "Engine Warming Up" screen now extracts and displays the last 10 lines of `dashboard.log`. This provides immediate transparency into Python tracebacks or dependency errors.
- **Aggressive Fallback**: Standardized the use of `0.0.0.0` for all internal service bindings and added `python -m hermes dashboard` as the final fail-safe in the startup chain.
- **UTF-8 Alignment**: Fixed an encoding bug in the health server that caused the "Money Maker 🤑" title to render as corrupt characters on some mobile browsers.

## UX Improvement
If the engine fails to start, the user will now see the exact Python error on the loading screen, allowing for immediate feedback and faster iteration.
