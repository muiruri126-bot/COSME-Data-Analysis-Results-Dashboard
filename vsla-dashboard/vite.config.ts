import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Set base to './' for relative paths — enables deployment on any sub-path
  // (SharePoint, file share, intranet sub-folder, etc.)
  base: './',
});
