# People Counter Monitor Dashboard

A modern, real-time web dashboard for monitoring people counting systems built with Next.js, TypeScript, Material-UI, and Tailwind CSS.

## 🚀 Features

### 📊 Real-time Dashboard
- **Live Metrics**: Real-time people counting with entry/exit tracking
- **Interactive Charts**: Modern charts with Recharts library
- **Responsive Design**: Mobile-first approach with Material-UI
- **Dark Theme**: Professional dark theme optimized for monitoring

### 📈 Analytics & Reporting
- **Session Management**: Complete session lifecycle tracking
- **Historical Data**: Time-series data visualization
- **Performance Metrics**: FPS, confidence scores, and system health
- **Export Capabilities**: Data export and reporting features

### 🔔 Alert System
- **Real-time Alerts**: Threshold-based notifications
- **Alert Management**: Resolve and track alert status
- **Multiple Alert Types**: System errors, performance warnings, threshold alerts
- **Notification Center**: Centralized alert management

### 🎯 Key Capabilities
- **Low Latency**: Optimized for real-time data updates
- **Modern UI**: Clean, intuitive interface following Material Design
- **CLEAN Code**: Well-structured, maintainable codebase
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized bundle size and loading times

## 🛠️ Technology Stack

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Material-UI**: Component library and theming
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Modern charting library
- **React Hooks**: Custom hooks for data management

### Backend Integration
- **REST API**: Complete API layer for database operations
- **Real-time Updates**: Polling-based real-time data
- **Error Handling**: Comprehensive error management
- **Type Safety**: End-to-end TypeScript types

## 📁 Project Structure

```
monitor/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── api/               # API routes
│   │   ├── live/              # Live monitoring page
│   │   ├── sessions/          # Session management
│   │   ├── alerts/            # Alert management
│   │   └── page.tsx          # Dashboard homepage
│   ├── components/            # React components
│   │   ├── dashboard/         # Dashboard components
│   │   ├── charts/            # Chart components
│   │   └── DashboardLayout.tsx # Main layout
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utility libraries
│   └── types/                 # TypeScript type definitions
├── public/                    # Static assets
└── package.json              # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- PostgreSQL database (from main project)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hoangnph/Dilumination_VisionAI.git
   cd Dilumination_VisionAI/monitor
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env.local
   
   # Configure database connection
   NEXT_PUBLIC_API_URL=http://localhost:3001/api
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   ```
   http://localhost:3000
   ```

## 📊 Dashboard Pages

### 🏠 Main Dashboard (`/`)
- System overview statistics
- Active sessions monitoring
- Quick access to all features
- Real-time status indicators

### 📈 Live Monitoring (`/live`)
- Real-time people counting metrics
- Interactive charts and graphs
- Live session information
- Performance monitoring

### 📋 Session Management (`/sessions`)
- Complete session history
- Session details and analytics
- Search and filter capabilities
- Session control (start/stop)

### 🔔 Alert Center (`/alerts`)
- Active alerts monitoring
- Alert resolution management
- Alert history and statistics
- Notification preferences

## 🔧 API Endpoints

### Sessions
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/active` - Get active sessions
- `GET /api/sessions/[id]` - Get session details
- `POST /api/sessions` - Create new session
- `PUT /api/sessions/[id]` - Update session

### Metrics
- `GET /api/metrics/realtime` - Real-time metrics
- `GET /api/metrics/history/[sessionId]` - Historical data

### Alerts
- `GET /api/alerts` - List alerts
- `PUT /api/alerts/[id]/resolve` - Resolve alert

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/health` - Health check

## 🎨 Customization

### Theme Configuration
The dashboard uses a custom Material-UI theme defined in `src/app/theme.ts`:

```typescript
export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    // ... more theme options
  },
});
```

### Chart Customization
Charts can be customized in `src/components/charts/`:

```typescript
<RealTimeChart
  title="Custom Chart"
  data={chartData}
  type="area" // or "line"
  height={400}
  showLegend={true}
/>
```

## 🔄 Real-time Updates

The dashboard implements real-time updates through:

1. **Custom Hooks**: `useRealtimeMetrics`, `useActiveSessions`
2. **Polling Strategy**: Configurable update intervals
3. **State Management**: React hooks for data management
4. **Error Handling**: Graceful fallbacks and retry logic

## 📱 Responsive Design

- **Mobile-first**: Optimized for mobile devices
- **Breakpoints**: Material-UI responsive breakpoints
- **Flexible Layout**: Adaptive grid system
- **Touch-friendly**: Optimized for touch interactions

## 🚀 Performance Optimization

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Dynamic imports for heavy components
- **Bundle Optimization**: Tree shaking and minification
- **Caching**: Strategic data caching and memoization

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Build & Deployment

### Development Build
```bash
npm run build
npm run start
```

### Production Deployment
```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔧 Configuration

### Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NODE_ENV=production
```

### Database Connection
The dashboard connects to the PostgreSQL database through the API layer. Ensure the database is running and accessible.

## 📈 Monitoring & Analytics

### Performance Metrics
- **Bundle Size**: Optimized for fast loading
- **First Load JS**: ~147kB shared, ~200kB per page
- **Build Time**: ~10s for full build
- **Real-time Updates**: 2-5 second intervals

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Dilumination VisionAI system. See the main project for licensing information.

## 🆘 Support

For support and questions:
- Check the main project documentation
- Review the API documentation
- Open an issue on GitHub

---

**Built with ❤️ using Next.js, TypeScript, and Material-UI**