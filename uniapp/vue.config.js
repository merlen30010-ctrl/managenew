module.exports = {
  // 基本路径
  publicPath: './',
  
  // 输出文件目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'static',
  
  // 是否开启eslint
  lintOnSave: false,
  
  // webpack配置
  configureWebpack: {
    // 性能提示
    performance: {
      hints: false
    }
  },
  
  // 开发服务器配置
  devServer: {
    // 端口
    port: 8080,
    
    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    }
  }
}