# Corner League Media - Sports Platform

A modern sports media platform built with React, TypeScript, and Vite providing personalized team content and real-time sports information.

## Technology Stack

**Frontend Framework:** React 18 + TypeScript + Vite
**UI Library:** Radix UI + shadcn/ui components
**Styling:** Tailwind CSS with custom design system
**Routing:** React Router DOM
**State Management:** TanStack Query (React Query)
**Theme:** next-themes for dark/light mode support
**Build Tool:** Vite with SWC for fast compilation

## Project Structure

```
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # shadcn/ui component library
│   │   ├── AISummarySection.tsx
│   │   ├── BestSeatsSection.tsx
│   │   ├── FanExperiencesSection.tsx
│   │   ├── SportsFeedSection.tsx
│   │   ├── SportsFeedCard.tsx
│   │   ├── ThemeProvider.tsx
│   │   ├── ThemeToggle.tsx
│   │   └── TopNavBar.tsx
│   ├── pages/               # Page components
│   │   ├── Index.tsx        # Main dashboard page
│   │   └── NotFound.tsx     # 404 page
│   ├── App.tsx              # Root application component
│   ├── main.tsx             # Application entry point
│   ├── App.css              # Component-specific styles
│   └── index.css            # Global styles and design tokens
├── public/                  # Static assets
├── .claude/                 # Claude Code agent configurations
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── eslint.config.js         # ESLint configuration
```

## Development Scripts

```bash
# Development server (port 8080)
npm run dev

# Production build
npm run build

# Development build
npm run build:dev

# Lint code
npm run lint

# Preview production build
npm run preview
```

## Key Dependencies

**UI & Components:**
- `@radix-ui/*` - Headless UI components (30+ components)
- `lucide-react` - Icon library
- `class-variance-authority` - Component variants
- `clsx` & `tailwind-merge` - Class name utilities

**State & Data:**
- `@tanstack/react-query` - Server state management
- `react-hook-form` - Form handling
- `@hookform/resolvers` - Form validation
- `zod` - Schema validation

**UI Enhancements:**
- `next-themes` - Dark/light theme support
- `sonner` - Toast notifications
- `embla-carousel-react` - Carousel component
- `recharts` - Charts and data visualization
- `date-fns` - Date utilities

## Architecture Patterns

**Component Structure:**
- Functional components with TypeScript
- shadcn/ui design system components
- Custom application-specific components
- Reusable UI components in `/ui` folder

**Styling Approach:**
- Tailwind CSS with custom design tokens
- CSS variables for theming
- iOS-inspired Material design system
- Dark/light mode support via CSS custom properties

**State Management:**
- TanStack Query for server state
- React hooks for local state
- Theme context for dark/light mode

## Design System

**Color Palette:**
- Light theme: Light gray/beige background (#E8E5E1), deep black text
- Dark theme: Medium stone grey background, near-white text
- Accent colors: Deep black primary, subtle grays for hierarchy

**Typography:**
- Display: SF Pro Display (Apple system font fallback)
- Body: SF Pro Text (Apple system font fallback)
- Antialiased rendering

**Spacing System:**
- Section spacing: 4rem
- Component spacing: 2rem
- Element spacing: 1rem

**Animation:**
- Fast transitions: 0.15s
- Normal transitions: 0.25s
- Cubic bezier easing: cubic-bezier(0.4, 0, 0.2, 1)

## Application Features

**Core Sections:**
1. **TopNavBar** - Navigation with theme toggle
2. **AISummarySection** - AI-powered content summaries
3. **SportsFeedSection** - Sports news and updates
4. **BestSeatsSection** - Ticket deals and seating options
5. **FanExperiencesSection** - Fan events and experiences

**Current Implementation:**
- Single-page application with routing support
- Responsive design for mobile and desktop
- Dark/light theme switching
- Component-based architecture with TypeScript

## Environment Configuration

The project uses environment variables for configuration:
- `.env` - Local environment variables
- `.env.docker` - Docker-specific environment variables

## Development Guidelines

**Code Style:**
- TypeScript strict mode disabled for flexibility
- ESLint configuration with React hooks support
- No unused variables warnings suppressed
- React Refresh for fast development

**Component Patterns:**
- Use functional components with hooks
- Implement proper TypeScript typing
- Follow shadcn/ui patterns for consistency
- Utilize Tailwind classes for styling

**Build Configuration:**
- Vite for fast development and building
- SWC for JavaScript/TypeScript compilation
- Path aliases configured (`@/` for `src/`)
- Development server on port 8080

## Future Roadmap

Based on the INITIAL.md specification, this project is intended to evolve into a comprehensive sports media platform with:
- FastAPI backend integration
- Supabase/PostgreSQL database
- Real-time WebSocket updates
- Firebase authentication
- Redis caching and job queues
- AI-powered content classification
- Personalized team preferences
- Live scoring and game updates

## Getting Started

1. Install dependencies: `npm install`
2. Start development server: `npm run dev`
3. Open browser to `http://localhost:8080`
4. For production build: `npm run build`

The application follows modern React development practices with a focus on performance, accessibility, and maintainable code architecture.

## Strict Development Rules

### 1. Documentation Review Protocol
**MANDATORY:** Before working with any tool, CLI, MCP server, or application, ALWAYS first review the documentation in Argon using the available documentation tools. If documentation is not available in Argon, explicitly state "Documentation is not available in Argon" and recommend using alternative methods to review documentation (official docs, GitHub repositories, etc.).

### 2. Complex Task Planning
**MANDATORY:** When creating a complex plan to fix bugs or add new features, take the md file that is created and create a sub-document (`.md` file) that breaks down those tasks into detailed sub-tasks. This ensures better development handling and clear progress tracking. The sub-document should include:
- The referenced main md file
- Detailed breakdown of sub-tasks
- Dependencies between tasks
- Acceptance criteria for each sub-task
- Estimated effort and timeline

### 3. Agent Delegation Protocol
**MANDATORY:** ALWAYS use the feature-planner sub-agent and delegation sub-agent to assign the correct specialized sub-agent to each task. This ensures that:
- Each development task is handled by the most appropriate specialized agent
- Proper handoff protocols are established between agents
- Quality gates are met before task delegation
- Development work is consistently performed by the correct sub-agents every single time

**Agent Assignment Guidelines:**
- frontend development → nextjs-frontend-dev agent
- backend API development → fastapi-backend-architect agent
- database work → db-etl-architect agent
- testing infrastructure → validation-testing agent
- CI/CD and releases → release-pr agent
- DevOps and infrastructure → dev-ops-stack agent
- Complex planning and coordination → feature-planner agent

These rules are NON-NEGOTIABLE and must be followed for every development task, bug fix, or feature implementation.