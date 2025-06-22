import { create } from 'zustand';
import type { PatientStudy, TabState } from '../types/dicom.types';

interface PatientStore {
  // Tabs state
  tabs: TabState[];
  activeTabId: string | null;
  
  // Patient data
  patients: PatientStudy[];
  isLoading: boolean;
  error: string | null;
  
  // Real-time sync
  isConnected: boolean;
  lastSync: Date | null;
  
  // Actions
  addTab: (patientStudy: PatientStudy) => void;
  removeTab: (tabId: string) => void;
  setActiveTab: (tabId: string) => void;
  updatePatientStudy: (id: string, updates: Partial<PatientStudy>) => void;
  updateTabLoading: (tabId: string, isLoading: boolean) => void;
  
  // Data management
  setPatients: (patients: PatientStudy[]) => void;
  addPatient: (patient: PatientStudy) => void;
  updatePatient: (id: string, updates: Partial<PatientStudy>) => void;
  removePatient: (id: string) => void;
  
  // Connection state
  setConnectionState: (isConnected: boolean) => void;
  setLastSync: (date: Date) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Utilities
  getPatientById: (id: string) => PatientStudy | undefined;
  getActivePatient: () => PatientStudy | undefined;
  getTabByPatientId: (patientId: string) => TabState | undefined;
}

export const usePatientStore = create<PatientStore>((set, get) => ({
  // Initial state
  tabs: [],
  activeTabId: null,
  patients: [],
  isLoading: false,
  error: null,
  isConnected: false,
  lastSync: null,

  // Tab management
  addTab: (patientStudy: PatientStudy) => {
    const { tabs, getTabByPatientId } = get();
    
    // Check if tab already exists
    const existingTab = getTabByPatientId(patientStudy.id);
    if (existingTab) {
      set({ activeTabId: existingTab.id });
      return;
    }

    const newTab: TabState = {
      id: `tab-${patientStudy.id}-${Date.now()}`,
      patientStudy,
      isActive: true,
      isLoading: false,
    };

    // Deactivate other tabs and add new one
    const updatedTabs = tabs.map(tab => ({ ...tab, isActive: false }));
    
    set({
      tabs: [...updatedTabs, newTab],
      activeTabId: newTab.id,
    });
  },

  removeTab: (tabId: string) => {
    const { tabs, activeTabId } = get();
    const updatedTabs = tabs.filter(tab => tab.id !== tabId);
    
    let newActiveTabId = activeTabId;
    
    // If we're removing the active tab, select another one
    if (activeTabId === tabId) {
      if (updatedTabs.length > 0) {
        newActiveTabId = updatedTabs[updatedTabs.length - 1].id;
        updatedTabs[updatedTabs.length - 1].isActive = true;
      } else {
        newActiveTabId = null;
      }
    }
    
    set({
      tabs: updatedTabs,
      activeTabId: newActiveTabId,
    });
  },

  setActiveTab: (tabId: string) => {
    const { tabs } = get();
    const updatedTabs = tabs.map(tab => ({
      ...tab,
      isActive: tab.id === tabId,
    }));
    
    set({
      tabs: updatedTabs,
      activeTabId: tabId,
    });
  },

  updatePatientStudy: (id: string, updates: Partial<PatientStudy>) => {
    const { tabs, patients } = get();
    
    // Update in patients array
    const updatedPatients = patients.map(patient =>
      patient.id === id ? { ...patient, ...updates } : patient
    );
    
    // Update in tabs
    const updatedTabs = tabs.map(tab =>
      tab.patientStudy.id === id
        ? { ...tab, patientStudy: { ...tab.patientStudy, ...updates } }
        : tab
    );
    
    set({
      patients: updatedPatients,
      tabs: updatedTabs,
    });
  },

  updateTabLoading: (tabId: string, isLoading: boolean) => {
    const { tabs } = get();
    const updatedTabs = tabs.map(tab =>
      tab.id === tabId ? { ...tab, isLoading } : tab
    );
    
    set({ tabs: updatedTabs });
  },

  // Patient data management
  setPatients: (patients: PatientStudy[]) => {
    set({ patients, lastSync: new Date() });
  },

  addPatient: (patient: PatientStudy) => {
    const { patients } = get();
    set({ 
      patients: [...patients, patient],
      lastSync: new Date(),
    });
  },

  updatePatient: (id: string, updates: Partial<PatientStudy>) => {
    get().updatePatientStudy(id, updates);
  },

  removePatient: (id: string) => {
    const { patients, tabs } = get();
    
    // Remove from patients
    const updatedPatients = patients.filter(patient => patient.id !== id);
    
    // Remove related tabs
    const updatedTabs = tabs.filter(tab => tab.patientStudy.id !== id);
    let newActiveTabId = get().activeTabId;
    
    // Handle active tab removal
    if (tabs.find(tab => tab.patientStudy.id === id && tab.isActive)) {
      if (updatedTabs.length > 0) {
        newActiveTabId = updatedTabs[0].id;
        updatedTabs[0].isActive = true;
      } else {
        newActiveTabId = null;
      }
    }
    
    set({
      patients: updatedPatients,
      tabs: updatedTabs,
      activeTabId: newActiveTabId,
    });
  },

  // Connection management
  setConnectionState: (isConnected: boolean) => {
    set({ isConnected });
  },

  setLastSync: (date: Date) => {
    set({ lastSync: date });
  },

  setLoading: (isLoading: boolean) => {
    set({ isLoading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  // Utility functions
  getPatientById: (id: string) => {
    return get().patients.find(patient => patient.id === id);
  },

  getActivePatient: () => {
    const { tabs, activeTabId } = get();
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    return activeTab?.patientStudy;
  },

  getTabByPatientId: (patientId: string) => {
    return get().tabs.find(tab => tab.patientStudy.id === patientId);
  },
}));