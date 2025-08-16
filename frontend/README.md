# JobPilot-OpenManus Frontend

A modern, responsive web interface for the JobPilot-OpenManus AI job hunting assistant, built with Solid.js and DaisyUI.

## 🚀 Tech Stack

- **Solid.js** - Reactive UI library
- **TypeScript** - Type safety and better DX
- **TailwindCSS** - Utility-first CSS framework
- **DaisyUI** - Beautiful UI components for Tailwind
- **Vite** - Fast build tool and dev server
- **PostCSS** - CSS processing
- **Autoprefixer** - Vendor prefixes

## 🎯 Features

- **Real-time Chat** - WebSocket-based communication with the AI agent
- **Live Browser Viewport** - See the agent browsing job sites in real-time
- **Activity Logging** - Track all agent actions and tool usage
- **Progress Tracking** - Visual progress indicators for long-running tasks
- **Theme Switching** - 29+ DaisyUI themes to choose from
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Type Safety** - Full TypeScript support throughout

## 📦 Installation

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## 🛠️ Development

1. **Start the development server:**

   ```bash
   npm run dev
   ```

   This will start the dev server at `http://localhost:3000` with:

   - Hot module replacement
   - Proxy to backend API at `http://localhost:8080`
   - WebSocket proxy for real-time communication

2. **Type checking:**
   ```bash
   npm run type-check
   ```

## 🏗️ Build

1. **Build for production:**

   ```bash
   npm run build
   ```

   Outputs to `dist/` directory

2. **Preview production build:**
   ```bash
   npm run preview
   ```

## 🏛️ Architecture

```
src/
├── components/           # Reusable UI components
│   ├── Header.tsx       # App header with theme switcher
│   ├── Chat.tsx         # Main chat interface
│   ├── BrowserViewport.tsx  # Live browser viewing
│   ├── ActivityLog.tsx  # Agent activity tracking
│   └── StatusPanel.tsx  # System status and quick actions
├── services/            # API and WebSocket services
│   ├── api.ts          # REST API client
│   └── websocket.ts    # WebSocket service with reconnection
├── types.ts            # TypeScript type definitions
├── index.css           # Global styles and Tailwind directives
├── main.tsx            # Application entry point
└── App.tsx             # Main application component
```

## 🎨 Styling

The project uses:

- **TailwindCSS** for utility-first styling
- **DaisyUI** for pre-built components and themes
- **Custom CSS classes** for specific JobPilot functionality

### Available Themes

DaisyUI provides 29 themes including:

- light, dark, cupcake, bumblebee, emerald, corporate
- synthwave, retro, cyberpunk, valentine, halloween
- And many more!

Switch themes using the theme dropdown in the header.

## 🔌 Backend Integration

The frontend communicates with the FastAPI backend through:

### REST API (`/api/*`)

- Health checks
- Job search requests
- Chat history

### WebSocket (`/ws`)

- Real-time chat messages
- Progress updates
- Tool usage notifications
- Browser activity events

## 📱 Component Structure

### Chat Component

- Message history with user/assistant/progress types
- Real-time message formatting
- Quick action buttons
- Progress indicator integration

### BrowserViewport Component

- Live browser status display
- URL tracking
- Content preview with truncation
- Visual status indicators

### ActivityLog Component

- Chronological activity tracking
- Different activity types (tool, error, browser, info)
- Automatic activity pruning (last 20 entries)
- Statistics summary

### StatusPanel Component

- System health monitoring
- WebSocket connection status
- Quick action shortcuts
- Manual refresh capabilities

## 🚦 Development Guidelines

1. **Use TypeScript** - All components should be fully typed
2. **Reactive Patterns** - Leverage Solid's fine-grained reactivity
3. **DaisyUI First** - Use DaisyUI components where possible
4. **Responsive Design** - Mobile-first approach with lg: breakpoints
5. **Accessibility** - Semantic HTML and ARIA labels
6. **Performance** - Lazy loading and code splitting where appropriate

## 🤝 Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test on multiple screen sizes
4. Ensure WebSocket error handling works
5. Update this README for significant changes

## 🐛 Common Issues

**WebSocket Connection Failed**

- Ensure the backend is running on port 8080
- Check firewall/proxy settings
- Verify WebSocket endpoint is accessible

**Build Errors**

- Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Check TypeScript errors: `npm run type-check`

**Styling Issues**

- Verify TailwindCSS classes are valid
- Check DaisyUI component documentation
- Ensure PostCSS is processing styles correctly
