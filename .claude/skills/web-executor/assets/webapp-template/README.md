# Web App Template

A modern, responsive starter template for web applications.

## Features

- ⚡ **Fast**: Optimized for performance
- 📱 **Responsive**: Works on all devices
- 🎨 **Modern**: Clean, beautiful design
- 🚀 **Ready to use**: Just customize and deploy

## Files

- `index.html` - Main HTML structure
- `styles.css` - Modern CSS styling with CSS variables
- `script.js` - Interactive JavaScript features

## Usage

1. Copy this template to your project directory
2. Customize the content in `index.html`
3. Modify colors and styles in `styles.css` (see CSS variables in `:root`)
4. Add your functionality in `script.js`
5. Deploy using the `deploy_webapp.py` script

## Customization

### Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --text-color: #1f2937;
    --bg-color: #f9fafb;
}
```

### Content

Update the text and structure in `index.html` to match your needs.

## Deployment

Use the web-executor deployment script:

```bash
python .claude/skills/web-executor/scripts/deploy_webapp.py <your-app-directory>
```

---

*Part of the Web Executor skill*
