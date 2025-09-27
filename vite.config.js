import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  build: {
    outDir: 'static/js',
    rollupOptions: {
      input: {
        auth: resolve(__dirname, 'src/auth.js'),
        app: resolve(__dirname, 'src/app.js')
      },
      output: {
        entryFileNames: '[name].bundle.js',
        assetFileNames: '[name].[ext]'
      }
    },
    emptyOutDir: false, // Don't clear the entire static/js directory
    minify: true
  },
  define: {
    global: 'globalThis',
  },
  server: {
    open: false
  }
})