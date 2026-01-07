# Odoo 16 → 18 Upgrade Project

## Overview

This project documents the upgrade of custom Odoo modules from **Odoo 16** to **Odoo 18 Enterprise**.  
All custom modules were updated and tested for Odoo 18 compatibility, including models, views, wizards, and reports.

## Module Structure

Each custom module follows the standard Odoo structure:

my_module/
├── manifest.py # Module metadata (updated to 18.0.x.x.x)
├── models/ # Python models
├── views/ # XML views (forms, lists, kanbans)
├── wizards/ # Python & XML wizards
├── reports/ # Report templates and actions
├── security/ # Access control and record rules
└── data/ # Initial or demo data

markdown
Copy code

**Key updates for Odoo 18:**

- Replaced deprecated XML tags (e.g., `<tree>` → `<list>`)
- Verified all `_inherit` and `_name` definitions
- Updated computed fields, onchange methods, and constraints
- Ensured reports and wizards function correctly

## Running the Project

1. Place the custom modules inside the `custom/` folder of your Odoo 18 environment.
2. Restart Odoo and update the apps list.
3. Install the modules via the Odoo interface.
4. Ensure all dependencies (Enterprise and base modules) are installed.

## Testing Guidelines

- Install each module and confirm all **views load** without errors.
- Test **CRUD operations** (Create, Read, Update, Delete) for main models.
- Verify **workflow actions**, buttons, and state changes work as expected.
- Generate **all reports** to ensure correct output.
- Check for **console and server errors** during operation.

## Tips & Best Practices

- Keep a separate folder for custom modules and enterprise addons.
- Always update the `__manifest__.py` version when upgrading modules.
- Test on a fresh Odoo 18 database before deploying to production.
- Use the `no_create` option in views for fields that should not allow creation from UI.
- Follow Odoo 18 coding standards for any new modules.
