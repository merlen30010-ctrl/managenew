<template>
  <view class="login-container">
    <!-- 自定义导航栏 -->
    <view class="custom-navbar"></view>
    
    <!-- 胶囊按钮 -->
    <view class="capsule-button"></view>
    
    <view class="content">
      <!-- Logo区域 -->
      <view class="logo-section">
        <view class="logo-wrapper">
          <text class="iconfont icon-building"></text>
        </view>
        <text class="title">管理系统</text>
        <text class="subtitle">企业级管理平台</text>
      </view>
      
      <!-- 登录表单 -->
      <view class="form-container">
        <view class="form-title">欢迎回来</view>
        
        <form @submit="handleLogin">
          <!-- 用户名输入 -->
          <view class="input-group">
            <view class="input-label">用户名</view>
            <view class="input-wrapper">
              <text class="iconfont icon-user input-icon"></text>
              <input 
                class="input-field" 
                name="username" 
                v-model="loginForm.username"
                placeholder="请输入用户名"
                placeholder-class="placeholder-style"
              />
            </view>
          </view>
          
          <!-- 密码输入 -->
          <view class="input-group">
            <view class="input-label">密码</view>
            <view class="input-wrapper">
              <text class="iconfont icon-lock input-icon"></text>
              <input 
                class="input-field" 
                name="password" 
                v-model="loginForm.password"
                placeholder="请输入密码"
                placeholder-class="placeholder-style"
                password
              />
            </view>
          </view>
          
          <!-- 登录按钮 -->
          <button 
            class="login-btn" 
            @click="handleLogin"
            :loading="loading"
            :disabled="loading"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
        
        <!-- 其他选项 -->
        <view class="other-options">
          <text class="option-link" @click="handleForgotPassword">忘记密码？</text>
          <text class="divider">|</text>
          <text class="option-link" @click="handleRegister">注册账户</text>
        </view>
      </view>
      
      <!-- 底部信息 -->
      <view class="footer">
        <text class="footer-text">© 2025 管理系统. 保留所有权利</text>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '@/api/request.js'

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loading: false
    }
  },
  
  onLoad() {
    // 检查是否已经登录
    const token = uni.getStorageSync('token')
    if (token) {
      // 如果已经登录，直接跳转到仪表盘
      uni.switchTab({
        url: '/pages/dashboard/dashboard'
      })
    }
  },
  
  methods: {
    async handleLogin() {
      // 表单验证
      if (!this.loginForm.username) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }
      
      if (!this.loginForm.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        // 调用登录接口
        const res = await request({
          url: '/api/login', // 根据您的Flask后端API调整路径
          method: 'POST',
          data: this.loginForm
        })
        
        // 检查登录是否成功
        if (res.success) {
          // 保存token
          uni.setStorageSync('token', res.data.token)
          
          // 跳转到首页
          uni.switchTab({
            url: '/pages/dashboard/dashboard'
          })
        } else {
          uni.showToast({
            title: res.message || '登录失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('登录失败', error)
        uni.showToast({
          title: '登录失败，请检查用户名和密码',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    handleForgotPassword() {
      uni.showToast({
        title: '忘记密码功能待开发',
        icon: 'none'
      })
    },
    
    handleRegister() {
      uni.showToast({
        title: '注册功能待开发',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  padding: 0 24rpx;
  position: relative;
}

.content {
  padding-top: 88rpx; /* 适配自定义导航栏 */
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 80rpx;
  margin-top: 120rpx;
}

.logo-wrapper {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20rpx;
  box-shadow: 0 10rpx 20rpx rgba(99, 102, 241, 0.3);
}

.iconfont {
  font-family: "iconfont" !important;
  font-size: 48rpx;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.icon-building {
  color: #ffffff;
}

.title {
  font-size: 44rpx;
  font-weight: bold;
  color: #1f2937;
  display: block;
  margin-bottom: 8rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #6b7280;
}

/* 表单容器 */
.form-container {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  padding: 48rpx 32rpx;
  backdrop-filter: blur(10rpx);
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 48rpx;
}

/* 输入组 */
.input-group {
  margin-bottom: 40rpx;
}

.input-label {
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 16rpx;
  display: block;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 0 24rpx;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 3rpx rgba(99, 102, 241, 0.2);
}

.input-icon {
  color: #9ca3af;
  font-size: 32rpx;
  margin-right: 16rpx;
}

.input-field {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  color: #1f2937;
  background: transparent;
}

.placeholder-style {
  color: #9ca3af;
  font-size: 28rpx;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: #ffffff;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
}

.login-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(99, 102, 241, 0.3);
}

.login-btn[disabled] {
  opacity: 0.7;
}

/* 其他选项 */
.other-options {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
}

.option-link {
  font-size: 26rpx;
  color: #6366f1;
  padding: 10rpx 20rpx;
}

.divider {
  color: #d1d5db;
  font-size: 26rpx;
}

/* 底部信息 */
.footer {
  text-align: center;
  margin-top: 80rpx;
}

.footer-text {
  font-size: 24rpx;
  color: #9ca3af;
}
</style>