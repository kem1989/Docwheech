import { create } from 'zustand';
import { User, onAuthStateChange, getIdToken } from '@/lib/auth';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  token: string | null;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateToken: () => Promise<void>;
  clearAuth: () => void;
  login: (email: string, password: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  token: null,
  error: null,

  setUser: (user) => {
    set({ 
      user, 
      isAuthenticated: !!user,
      error: null 
    });
  },

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  updateToken: async () => {
    try {
      const token = await getIdToken();
      set({ token });
    } catch (error) {
      console.error('Failed to update token:', error);
      set({ token: null });
    }
  },

  clearAuth: () => {
    set({
      user: null,
      isAuthenticated: false,
      token: null,
      error: null,
      isLoading: false,
    });
  },

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      await signInWithEmailAndPassword(auth, email, password);
      // The onAuthStateChange listener will handle updating the user state
      set({ isLoading: false });
    } catch (error: any) {
      set({ error: error.message || 'Login failed', isLoading: false });
      throw error;
    }
  },
}));

// Initialize auth state listener
if (typeof window !== 'undefined') {
  onAuthStateChange((user) => {
    const store = useAuthStore.getState();
    store.setUser(user);
    store.setLoading(false);
    
    // Update token when user changes
    if (user) {
      store.updateToken();
    }
  });
}
