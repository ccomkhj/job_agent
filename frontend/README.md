# Job Agent Frontend - React Chat Interface

[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev/)

The frontend component of Job Agent, providing an intuitive chat-based interface for the multi-agent job application assistance system.

## 🎨 Interface Overview

### Chat-Based Interaction Flow

```
Job URL Input → Profile Setup → Content Generation → Feedback Review → Iterative Refinement → Export
```

The interface follows a conversational pattern where users interact naturally with the AI system through:
- **Structured Inputs**: Job URLs, profile information, HR questions
- **AI Responses**: Generated content with automatic feedback
- **Interactive Refinement**: User-controlled content improvement
- **Easy Export**: Copy-to-clipboard functionality

## 🏗️ Architecture Overview

### Component Hierarchy

```
App
├── ChatInterface (Main Container)
│   ├── ChatHeader
│   ├── ChatMessages
│   │   └── MessageBubble[]
│   │       ├── OutputDisplay (for AI content)
│   │       └── FeedbackSelector (for improvement options)
│   └── ChatInputs
│       ├── JobUrlInput
│       ├── ProfileInput
│       │   ├── CareerTabs (Data Science, Engineering, Vision, CTO)
│       │   └── TabPanels
│       ├── QuestionInput
│       │   ├── QuickQuestions (common HR questions)
│       │   └── CustomQuestion
│       └── ActionButtons
```

### State Management

The application uses **React hooks** for state management:

- **Global State**: Current job URL, user profile, message history
- **UI State**: Loading states, error messages, form validation
- **Session State**: Chat history persistence (localStorage)

### Data Flow

```
User Action → State Update → API Call → Response Processing → UI Update → Message Display
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Open browser**
   Navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## 🎯 Key Components Deep Dive

### ChatInterface (Main Container)

**Responsibilities**:
- Manages global application state
- Coordinates between user inputs and AI responses
- Handles API communication and error states
- Maintains chat message history

**State Management**:
```typescript
interface AppState {
  currentJobUrl?: string;
  currentProfile?: UserProfile;
  messages: ChatMessage[];
  isLoading: boolean;
  error?: string;
}
```

### MessageBubble (Conversation Display)

**Features**:
- **Message Types**: User input, system notifications, AI responses
- **Content Rendering**: Text, structured data, interactive components
- **Timestamp Display**: Formatted relative timestamps
- **Dynamic Content**: Conditionally renders different content types

**Supported Content Types**:
- **Plain Text**: Regular chat messages
- **Cover Letters**: Formatted professional content
- **HR Answers**: Structured Q&A responses
- **Feedback Forms**: Interactive improvement selectors

### Input Components

#### JobUrlInput
- **URL Validation**: Real-time format checking
- **Error Handling**: Clear validation messages
- **Submission**: Triggers job description analysis

#### ProfileInput (Multi-Tab Career Editor)
- **Career Variants**: Separate tabs for different career tracks
- **Dynamic Forms**: Context-aware input fields
- **Auto-Save**: Profile persistence across sessions
- **Validation**: Required field checking

#### QuestionInput (HR Question Handler)
- **Quick Select**: Pre-defined common questions
- **Custom Input**: Free-form question entry
- **Smart Suggestions**: Context-aware question recommendations

### Output Components

#### OutputDisplay (Content Viewer)
- **Content Types**: Cover letters and HR answers
- **Formatting**: Professional typography and layout
- **Copy to Clipboard**: One-click content export
- **Metadata Display**: Profile usage information

#### FeedbackSelector (Improvement Interface)
- **Feedback Types**: Tone, alignment, clarity, emphasis, structure
- **Interactive Selection**: Checkbox-based feedback choice
- **Batch Application**: Apply multiple improvements at once
- **Real-time Preview**: Changes applied instantly

## 🎨 Styling & UX

### Design Principles

- **Chat-Based UX**: Familiar messaging interface
- **Progressive Disclosure**: Information revealed contextually
- **Mobile-First**: Responsive design for all devices
- **Accessibility**: WCAG-compliant color contrast and navigation

### CSS Architecture

- **Component-Scoped**: Each component has dedicated styles
- **CSS Variables**: Consistent color scheme and spacing
- **Responsive Grid**: Flexible layouts for different screen sizes
- **Animation**: Subtle transitions and loading states

### Key UI Patterns

- **Message Bubbles**: Differentiated by sender (user/system/AI)
- **Progressive Forms**: Step-by-step data collection
- **Feedback Loops**: Clear success/error states
- **Loading States**: Skeleton screens and progress indicators

## 🔧 Development

### Project Structure

```
frontend/src/
├── components/           # React components
│   ├── ChatInterface.tsx # Main chat container
│   ├── MessageBubble.tsx # Message display component
│   ├── OutputDisplay.tsx # Content viewer
│   ├── FeedbackSelector.tsx # Improvement selector
│   ├── JobUrlInput.tsx   # Job URL input form
│   ├── ProfileInput.tsx  # Multi-tab profile editor
│   ├── QuestionInput.tsx # HR question input
│   └── ActionButtons.tsx # Action triggers
├── services/            # External service integrations
│   └── api.ts          # Backend API client
├── types/              # TypeScript type definitions
│   └── index.ts        # Shared type interfaces
├── styles/             # CSS stylesheets
│   └── App.css         # Global styles
└── main.tsx           # Application entry point
```

### Type Safety

**Comprehensive TypeScript coverage**:
- **API Interfaces**: Backend request/response types
- **Component Props**: Strict prop validation
- **State Types**: Immutable state management
- **Event Handlers**: Typed event callbacks

### API Integration

**Service Layer Architecture**:
```typescript
class ApiService {
  static async generateCoverLetter(request: CoverLetterRequest): Promise<CoverLetterApiResponse>
  static async generateAnswer(request: QuestionAnswerRequest): Promise<QuestionAnswerApiResponse>
  static async modifyOutput(request: ModificationRequest): Promise<ModificationResponse>
}
```

### Error Handling

**Multi-Layer Error Management**:
- **Network Errors**: API failure handling
- **Validation Errors**: Form input validation
- **User Feedback**: Clear error messages and recovery options
- **Graceful Degradation**: Fallback UI states

## 🧪 Testing Strategy

### Component Testing
```typescript
// Example: Testing ChatInterface state management
describe('ChatInterface', () => {
  it('should handle job URL submission', async () => {
    // Test job URL input and validation
  });

  it('should manage chat message history', () => {
    // Test message state updates
  });
});
```

### Integration Testing
- **API Calls**: Mock backend responses
- **User Flows**: End-to-end interaction testing
- **Error Scenarios**: Network failures and edge cases

## 🚀 Performance Optimization

### Code Splitting
- **Route-Based**: Dynamic imports for different views
- **Component Lazy Loading**: Heavy components loaded on demand
- **Vendor Chunking**: Separate third-party libraries

### Rendering Optimization
- **React.memo**: Prevent unnecessary re-renders
- **useCallback**: Stable function references
- **useMemo**: Expensive computation caching

### Bundle Analysis
```bash
npm run build -- --mode analyze
# Generates bundle size analysis
```

## 📱 Responsive Design

### Breakpoint Strategy
- **Mobile**: < 768px - Single column, stacked layout
- **Tablet**: 768px - 1024px - Optimized spacing
- **Desktop**: > 1024px - Multi-column layouts

### Touch-Friendly Interactions
- **Button Sizes**: Minimum 44px touch targets
- **Swipe Gestures**: Message history navigation
- **Keyboard Navigation**: Full keyboard accessibility

## 🔒 Security Considerations

### Client-Side Security
- **Input Sanitization**: XSS prevention
- **Content Security Policy**: Script injection protection
- **Secure Storage**: Safe localStorage usage

### API Security
- **Request Validation**: Type-safe API calls
- **Error Masking**: No sensitive data in error messages
- **Rate Limiting**: Client-side request throttling

## 🎨 Customization

### Theming
- **CSS Variables**: Easy color scheme customization
- **Component Props**: Style overrides via props
- **Dark Mode**: Future dark theme support

### Internationalization
- **Message Templates**: Extensible text content
- **Locale Support**: Multi-language capability
- **Cultural Adaptation**: Region-specific content

## 🔄 Development Workflow

### Local Development
```bash
# Start development server with hot reload
npm run dev

# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Build for production
npm run build
```

### Environment Configuration
```env
# .env.local
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Job Agent
VITE_VERSION=1.0.0
```

## 🤝 Contributing

### Code Standards
- **ESLint**: Automated code quality checks
- **Prettier**: Consistent code formatting
- **TypeScript**: Strict type checking enabled
- **Component Documentation**: JSDoc comments for all components

### Component Development
1. **Create Component**: Add to `components/` directory
2. **Add Types**: Define interfaces in `types/index.ts`
3. **Style Component**: Add styles to `App.css`
4. **Test Component**: Add unit tests
5. **Document**: Update component documentation

---

**Part of the Job Agent multi-agent system.** See [main README](../README.md) for complete project overview and [backend README](../backend/README.md) for API details.