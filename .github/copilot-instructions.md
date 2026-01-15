# Copilot Instructions for Outdoor Camping World Project

This project is a high-performance Outdoor Camping World Taiwan Edition website, leveraging an aged domain (est. 2004) to provide authoritative camping content.

## Project Architecture
- **Framework**: Astro (Static Site Generation - SSG).
- **Styling**: Tailwind CSS.
- **Data Source**: Local JSON files (`campgrounds.json`, `products.json`) processed via Python.
- **Deployment**: Vercel.

## Core Data Model
The application relies on pre-processed JSON data rather than a database.
- **`campgrounds.json`**: Primary data source. Contains camping ground details enriched with:
  - `altitude_tag`: 'high' (>1000m), 'low' (<500m), 'mid'.
  - `region_tag`: Geographic classification (North/Central/South/East).
- **`products.json`**: Affiliate product mappings keyed by tags (e.g., specific gear for high altitude).

## Development Guidelines
- **Data Processing**:
  - Use `prepare_data.py` to ingest CSV data and fetch metadata (e.g., elevation from Open-Meteo API).
  - Ensure API rate limiting (`time.sleep`) in scripts.
- **Component Design**:
  - Components should be static and lightweight.
  - Integration with affiliate links should be programmatic based on tags.
- **Project Structure (Expected)**:
  - `src/pages/[...slug].astro`: Dynamic routes for individual camp pages or SEO landing pages.
  - `src/data/`: Location for JSON data files.
  - `scripts/`: Location for Python data preparation scripts.

## Tech Stack Specifics
- **Astro**: Use `.astro` files for components. Prefer server-side data fetching at build time (`getStaticPaths`).
- **Tailwind**: Utility-first CSS for all styling.

## Context
- This is a "Vibe Coding" project using AI for rapid development.
- Focus on SEO performance and fast page loads (Core Web Vitals).
- Revenue models: Display Ads (AdSense) and Affiliate Marketing (Shopee/Klook).
