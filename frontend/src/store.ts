import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  fullName: string;
  roles: { roleId: string; roleName: string }[];
  locationId?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      hasRole: (...roles) => {
        const user = get().user;
        if (!user) return false;
        return user.roles.some((r) =>
          roles.some((requested) => r.roleName === requested || r.roleName.includes(requested))
        );
      },
    }),
    { name: 'cosme-auth' }
  )
);
