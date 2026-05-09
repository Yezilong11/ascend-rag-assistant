# Remove Theme Toggle Icon Spec

## Why
The sun/moon theme toggle icon in the top-right corner is no longer needed and should be removed to simplify the UI, eliminate unused code, and prevent potential performance overhead or conflicts from residual event listeners and styles.

## What Changes
- Remove the theme toggle icon (sun/moon) from the DOM structure in the top-right corner
- Remove all JavaScript event listeners associated with the theme toggle functionality
- Remove all CSS styles related to the theme toggle icon
- Ensure no orphaned references remain in the codebase

## Impact
- Affected specs: UI Component Removal
- Affected code: Frontend components, JavaScript event handlers, CSS stylesheets

## REMOVED Requirements
### Requirement: Theme Toggle Icon
**Reason**: Icon is being removed from the UI entirely
**Migration**: Users will no longer be able to manually switch between light and dark modes via this icon

### Requirement: Theme Toggle Event Listeners
**Reason**: Associated functionality is being removed
**Migration**: Event listeners tied to the theme toggle will be cleaned up

### Requirement: Theme Toggle Styles
**Reason**: CSS rules for the toggle icon are no longer needed
**Migration**: All related CSS classes and rules will be removed
