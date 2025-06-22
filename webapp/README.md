# Medical Interface with Dynamic Tabs and A4 Previews

## Overview

A comprehensive **medical interface** that acts as a **proxy layer** over an existing Orthanc Explorer 2 (OE2) system. This interface provides real-time patient monitoring, dynamic tab management, and A4-formatted previews of medical reports and DICOM images.

## 🚀 Features

### Core Functionality
- **Real-time synchronization** with Orthanc Explorer 2
- **Dynamic patient tabs** with automatic detection of new studies
- **A4 preview system** with pixel-perfect layouts (210mm × 297mm)
- **Automatic PDF generation** from DICOM studies
- **Integration** with existing OHIF and Stone viewers
- **WebSocket support** for real-time updates

### Interface Highlights
- **Modern React 18+** with TypeScript
- **TailwindCSS** styling with custom medical UI components
- **Zustand** state management for optimal performance
- **Responsive design** (desktop, tablet, mobile)
- **Error boundaries** and comprehensive error handling
- **Keyboard shortcuts** for efficient navigation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Orthanc OE2   │────│  Medical Interface│────│  DICOM-PDF API  │
│  (Existing)     │    │   (This Project)  │    │   (Existing)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌────────────────────┐             │
         │              │  Frontend React   │             │
         │              │  - Dynamic Tabs   │             │
         │              │  - A4 Previews    │             │
         │              │  - Real-time Sync │             │
         └──────────────┴────────────────────┴─────────────┘
```

## 📁 Project Structure

```
src/
├── components/
│   ├── Layout/
│   │   ├── Header.tsx              # Main header with status indicators
│   │   ├── TabBar.tsx              # Dynamic patient tabs
│   │   └── MainContent.tsx         # Main content area
│   ├── PatientTab/
│   │   ├── PatientTab.tsx          # Patient tab container
│   │   ├── PatientHeader.tsx       # Patient information display
│   │   ├── DropdownPreview.tsx     # A4 preview dropdown
│   │   └── ActionButtons.tsx       # Viewer and PDF actions
│   ├── A4Preview/
│   │   ├── A4Container.tsx         # A4 layout container
│   │   ├── ReportPreview.tsx       # Medical report A4 layout
│   │   ├── ImagePreview.tsx        # DICOM images in A4 grid
│   │   └── PDFViewer.tsx           # PDF document viewer
│   └── Common/
│       ├── LoadingSpinner.tsx      # Loading animations
│       ├── ErrorBoundary.tsx       # Error handling
│       └── StatusIndicator.tsx     # Status indicators
├── hooks/
│   ├── useOrthancSync.ts           # Real-time Orthanc synchronization
│   ├── useDicomPdf.ts              # PDF processing management
│   └── useTabManager.ts            # Tab lifecycle management
├── services/
│   ├── orthancApi.ts               # Orthanc REST API integration
│   ├── dicomPdfApi.ts              # DICOM-PDF processing API
│   └── websocketService.ts         # WebSocket real-time updates
├── stores/
│   └── patientStore.ts             # Zustand state management
├── styles/
│   ├── a4-layouts.css              # A4 specific styles
│   └── medical-ui.css              # Medical interface styles
├── types/
│   └── dicom.types.ts              # TypeScript definitions
├── App.tsx                         # Main application
└── main.tsx                        # Application entry point
```

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Running Orthanc instance
- DICOM-PDF backend service

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Environment Variables:**
   ```env
   # Orthanc Configuration
   REACT_APP_ORTHANC_URL=http://localhost:8042
   REACT_APP_ORTHANC_USERNAME=orthanc
   REACT_APP_ORTHANC_PASSWORD=orthanc

   # DICOM-PDF API Configuration
   REACT_APP_DICOM_PDF_URL=http://localhost:8000

   # WebSocket Configuration
   REACT_APP_WEBSOCKET_URL=ws://localhost:8080

   # Real-time Sync Configuration
   REACT_APP_POLLING_INTERVAL=5000

   # Viewer URLs
   REACT_APP_OHIF_URL=http://localhost:3000
   REACT_APP_STONE_URL=http://localhost:3001
   ```

4. **Development:**
   ```bash
   npm run dev
   ```

5. **Production Build:**
   ```bash
   npm run build
   npm run preview
   ```

## 📋 A4 Layout Specifications

### Dimensions
- **Physical:** 210mm × 297mm
- **Digital:** 794px × 1123px @ 96dpi
- **Margins:** 20mm (75px) on all sides
- **Font:** Times New Roman, 12pt

### Preview Scales
- **Desktop:** 40% (317px × 449px)
- **Tablet:** 30% (238px × 337px)  
- **Mobile:** 20% (159px × 225px)
- **Print:** 100% (794px × 1123px)

## 🎯 Key Components

### Dynamic Tab System
- Automatic patient detection
- Real-time tab updates
- Keyboard navigation (Ctrl+Tab, Ctrl+W)
- Maximum tab limits with smart cleanup

### A4 Preview System
- Medical report with structured layout
- DICOM image grid (4×2 layout)
- PDF document viewer
- Responsive scaling

### Real-time Synchronization
- WebSocket connections for instant updates
- Polling fallback (5-second intervals)
- Connection status monitoring
- Automatic reconnection

## 🔧 Integration Points

### Orthanc Explorer 2
- Patient and study retrieval
- DICOM image access
- Series and instance management
- Archive downloads

### DICOM-PDF Service
- Automatic PDF generation
- Processing status monitoring
- Queue management
- Result caching

### Viewers
- **OHIF Viewer:** Modern web-based DICOM viewer
- **Stone Viewer:** High-performance medical imaging

## 📱 Responsive Design

### Desktop (1920x1080+)
- Horizontal tabs
- Two-column A4 previews
- Full feature set

### Tablet (768px - 1200px)
- Stacked columns
- 30% preview scale
- Touch-optimized controls

### Mobile (<768px)
- Dropdown tab selection
- 20% preview scale
- Simplified navigation

## 🚦 Status Indicators

### Connection Status
- 🟢 **Connected:** Real-time sync active
- 🔵 **Connecting:** Establishing connection
- 🔴 **Disconnected:** Connection failed

### PDF Processing
- 🟡 **Pending:** Awaiting processing
- 🔵 **Processing:** PDF generation in progress
- 🟢 **Completed:** PDF ready for download
- 🔴 **Error:** Processing failed

## 🎯 Performance Features

- **Lazy loading** of inactive tabs
- **Virtual scrolling** for large patient lists
- **Debounced updates** for frequent changes
- **PDF caching** (configurable size)
- **Error boundaries** for fault isolation

## 🔐 Security

- Configurable authentication for Orthanc
- CORS handling for cross-origin requests
- Input validation and sanitization
- Error message sanitization

## 🧪 Development

### Available Scripts
```bash
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint checking
npm run preview      # Preview production build
```

### Code Quality
- **ESLint** with React and TypeScript rules
- **TypeScript** strict mode
- **Error boundaries** for component isolation
- **Comprehensive error handling**

## 🚀 Deployment

### Docker (Recommended)
```bash
# Build the entire project (from repository root)
docker build -t dicom-pdf .

# Run with frontend
docker run --rm -p 4173:4173 dicom-pdf
```

### Manual Deployment
```bash
npm run build
# Deploy dist/ folder to web server
```

## 🤝 Integration with Existing System

This interface is designed to work alongside your existing Orthanc Explorer 2 setup:

1. **Non-intrusive:** Operates as a separate frontend
2. **API Compatible:** Uses standard Orthanc REST APIs
3. **Preserves Functionality:** Maintains access to original viewers
4. **Extends Capabilities:** Adds A4 layouts and PDF generation

## 📚 Medical Data Handling

### Patient Study Interface
```typescript
interface PatientStudy {
  id: string;
  patientId: string;
  patientName: string;
  patientBirthDate: string;
  studyDate: string;
  studyTime: string;
  modality: string;
  studyDescription: string;
  accessionNumber: string;
  seriesCount: number;
  instanceCount: number;
  institutionName?: string;
  referringPhysician?: string;
  ohifUrl: string;
  stoneUrl: string;
  dicomPdfStatus: 'pending' | 'processing' | 'completed' | 'error';
  dicomPdfUrl?: string;
  reportData?: {
    history: string;
    findings: string[];
    impression: string;
    measurements?: BiometricMeasurement[];
  };
}
```

### Biometric Measurements
Supports fetal ultrasound measurements:
- **HC:** Head Circumference
- **BPD:** Biparietal Diameter  
- **AC:** Abdominal Circumference
- **FL:** Femur Length
- **EFW:** Estimated Fetal Weight

## 🔄 Real-time Updates

The system monitors Orthanc for changes and automatically:
- Detects new patients and studies
- Updates existing patient information
- Refreshes DICOM processing status
- Maintains WebSocket connections
- Falls back to polling if WebSocket fails

## 🎨 UI/UX Features

- **Modern medical interface** with professional styling
- **Intuitive navigation** with clear visual hierarchy
- **Status indicators** for all system states
- **Loading animations** for better user experience
- **Error handling** with user-friendly messages
- **Keyboard shortcuts** for power users

---

## 🆘 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify Orthanc connectivity
3. Confirm environment variable configuration
4. Review network requests in developer tools

This interface represents a modern, comprehensive solution for medical DICOM data visualization with automatic PDF generation and real-time synchronization capabilities.
