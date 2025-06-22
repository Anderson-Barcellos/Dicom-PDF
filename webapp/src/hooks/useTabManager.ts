import { useCallback } from 'react';
import { usePatientStore } from '../stores/patientStore';
import type { PatientStudy, TabState } from '../types/dicom.types';

export interface UseTabManagerOptions {
  maxTabs?: number;
  autoCloseInactive?: boolean;
  inactiveTimeout?: number; // minutes
}

export function useTabManager(options: UseTabManagerOptions = {}) {
  const { maxTabs = 10, autoCloseInactive = false, inactiveTimeout = 30 } = options;
  
  const {
    tabs,
    activeTabId,
    addTab,
    removeTab,
    setActiveTab,
    updateTabLoading,
  } = usePatientStore();

  // Get active tab
  const getActiveTab = useCallback((): TabState | null => {
    return tabs.find(tab => tab.id === activeTabId) || null;
  }, [tabs, activeTabId]);

  // Get active patient study
  const getActivePatientStudy = useCallback((): PatientStudy | null => {
    const activeTab = getActiveTab();
    return activeTab?.patientStudy || null;
  }, [getActiveTab]);

  // Open new tab for patient study
  const openTab = useCallback((patientStudy: PatientStudy) => {
    // Check if tab already exists
    const existingTab = tabs.find(tab => tab.patientStudy.id === patientStudy.id);
    if (existingTab) {
      setActiveTab(existingTab.id);
      return existingTab;
    }

    // Check max tabs limit
    if (tabs.length >= maxTabs) {
      // Remove oldest inactive tab
      const inactiveTabs = tabs.filter(tab => !tab.isActive);
      if (inactiveTabs.length > 0) {
        removeTab(inactiveTabs[0].id);
      } else {
        // Remove oldest tab if all are active
        removeTab(tabs[0].id);
      }
    }

    // Add new tab
    addTab(patientStudy);
    
    const newTab = tabs.find(tab => tab.patientStudy.id === patientStudy.id);
    return newTab || null;
  }, [tabs, maxTabs, addTab, removeTab, setActiveTab]);

  // Close tab
  const closeTab = useCallback((tabId: string) => {
    removeTab(tabId);
  }, [removeTab]);

  // Close all tabs
  const closeAllTabs = useCallback(() => {
    tabs.forEach(tab => removeTab(tab.id));
  }, [tabs, removeTab]);

  // Close other tabs (keep only active)
  const closeOtherTabs = useCallback(() => {
    tabs.forEach(tab => {
      if (tab.id !== activeTabId) {
        removeTab(tab.id);
      }
    });
  }, [tabs, activeTabId, removeTab]);

  // Switch to tab
  const switchToTab = useCallback((tabId: string) => {
    setActiveTab(tabId);
  }, [setActiveTab]);

  // Switch to next tab
  const switchToNextTab = useCallback(() => {
    if (tabs.length <= 1) return;
    
    const currentIndex = tabs.findIndex(tab => tab.id === activeTabId);
    const nextIndex = (currentIndex + 1) % tabs.length;
    setActiveTab(tabs[nextIndex].id);
  }, [tabs, activeTabId, setActiveTab]);

  // Switch to previous tab
  const switchToPreviousTab = useCallback(() => {
    if (tabs.length <= 1) return;
    
    const currentIndex = tabs.findIndex(tab => tab.id === activeTabId);
    const previousIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
    setActiveTab(tabs[previousIndex].id);
  }, [tabs, activeTabId, setActiveTab]);

  // Set tab loading state
  const setTabLoading = useCallback((tabId: string, isLoading: boolean) => {
    updateTabLoading(tabId, isLoading);
  }, [updateTabLoading]);

  // Get tab by patient study ID
  const getTabByStudyId = useCallback((studyId: string): TabState | null => {
    return tabs.find(tab => tab.patientStudy.id === studyId) || null;
  }, [tabs]);

  // Get tab order for display
  const getTabsInOrder = useCallback((): TabState[] => {
    return tabs.slice().sort((a, b) => {
      // Active tab first, then by creation order
      if (a.isActive) return -1;
      if (b.isActive) return 1;
      return a.id.localeCompare(b.id);
    });
  }, [tabs]);

  // Check if patient study has open tab
  const hasOpenTab = useCallback((studyId: string): boolean => {
    return tabs.some(tab => tab.patientStudy.id === studyId);
  }, [tabs]);

  // Get tab title for display
  const getTabTitle = useCallback((tab: TabState): string => {
    const { patientStudy } = tab;
    const maxLength = 20;
    
    let title = patientStudy.patientName;
    if (title.length > maxLength) {
      title = title.substring(0, maxLength - 3) + '...';
    }
    
    return title;
  }, []);

  // Get tab subtitle for display
  const getTabSubtitle = useCallback((tab: TabState): string => {
    const { patientStudy } = tab;
    const date = patientStudy.studyDate;
    const modality = patientStudy.modality;
    
    // Format date
    let formattedDate = date;
    if (date.length === 8) {
      // YYYYMMDD format
      const year = date.substring(0, 4);
      const month = date.substring(4, 6);
      const day = date.substring(6, 8);
      formattedDate = `${day}/${month}/${year}`;
    }
    
    return `${formattedDate} | ${modality}`;
  }, []);

  // Handle keyboard shortcuts
  const handleKeyboardShortcut = useCallback((event: KeyboardEvent) => {
    // Ctrl/Cmd + W: Close current tab
    if ((event.ctrlKey || event.metaKey) && event.key === 'w') {
      event.preventDefault();
      if (activeTabId) {
        closeTab(activeTabId);
      }
    }
    
    // Ctrl/Cmd + T: This would need to be handled at app level for new tab
    
    // Ctrl/Cmd + Tab: Next tab
    if ((event.ctrlKey || event.metaKey) && event.key === 'Tab' && !event.shiftKey) {
      event.preventDefault();
      switchToNextTab();
    }
    
    // Ctrl/Cmd + Shift + Tab: Previous tab
    if ((event.ctrlKey || event.metaKey) && event.key === 'Tab' && event.shiftKey) {
      event.preventDefault();
      switchToPreviousTab();
    }
    
    // Ctrl/Cmd + 1-9: Switch to tab by index
    if ((event.ctrlKey || event.metaKey) && /^[1-9]$/.test(event.key)) {
      event.preventDefault();
      const index = parseInt(event.key) - 1;
      if (index < tabs.length) {
        setActiveTab(tabs[index].id);
      }
    }
  }, [activeTabId, closeTab, switchToNextTab, switchToPreviousTab, setActiveTab, tabs]);

  // Auto-close inactive tabs (if enabled)
  // This would need to track last access time and run periodically
  
  return {
    // State
    tabs,
    activeTabId,
    activeTab: getActiveTab(),
    activePatientStudy: getActivePatientStudy(),
    
    // Actions
    openTab,
    closeTab,
    closeAllTabs,
    closeOtherTabs,
    switchToTab,
    switchToNextTab,
    switchToPreviousTab,
    setTabLoading,
    
    // Queries
    getTabByStudyId,
    getTabsInOrder,
    hasOpenTab,
    getTabTitle,
    getTabSubtitle,
    
    // Utilities
    handleKeyboardShortcut,
    
    // Configuration
    options: {
      maxTabs,
      autoCloseInactive,
      inactiveTimeout,
    },
    
    // Statistics
    stats: {
      totalTabs: tabs.length,
      maxTabsReached: tabs.length >= maxTabs,
      hasActiveTabs: tabs.length > 0,
    },
  };
}