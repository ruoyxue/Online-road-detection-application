import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import WindiCSS from 'vite-plugin-windicss'

import path from 'path'


// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "~": path.resolve(__dirname, 'src')
    }
  },

  plugins: [
    vue(),
    WindiCSS(),
  ],

  server: {
	host:'0.0.0.0' ,//ip地址
	port: 80, // 设置服务启动端口号
	open: true, // 设置服务启动时是否自动打开浏览器,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    }
}})
