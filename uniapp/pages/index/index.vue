<template>
  <view class="container">
    <view class="welcome-section">
      <text class="title">欢迎使用管理系统</text>
      <text class="subtitle">企业级管理平台</text>
    </view>
    <button @click="goToLogin" class="login-button">前往登录</button>
    
    <!-- 底部导航栏 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToPage('dashboard')">
        <uni-icons type="home" size="24" color="#7A7E83"></uni-icons>
        <text class="nav-text">主页</text>
      </view>
      <view class="nav-item active" @click="goToPage('news')">
        <uni-icons type="flag" size="24" color="#6366f1"></uni-icons>
        <text class="nav-text">资讯</text>
      </view>
      <view class="nav-item" @click="goToPage('notification')">
        <uni-icons type="notification" size="24" color="#7A7E83"></uni-icons>
        <text class="nav-text">通知</text>
      </view>
      <view class="nav-item" @click="goToPage('profile')">
        <uni-icons type="person" size="24" color="#7A7E83"></uni-icons>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goToLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },
    
    goToPage(page) {
      // 根据页面名称跳转到相应页面
      switch(page) {
        case 'dashboard':
          uni.switchTab({
            url: '/pages/dashboard/dashboard'
          });
          break;
        case 'news':
          // 当前页面，无需跳转
          break;
        case 'notification':
          uni.switchTab({
            url: '/pages/index/index'
          });
          break;
        case 'profile':
          uni.switchTab({
            url: '/pages/profile/profile'
          });
          break;
        default:
          break;
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  padding: 40rpx;
  padding-bottom: 140rpx; /* 为底部导航留出空间 */
}

.welcome-section {
  text-align: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 20rpx;
}

.subtitle {
  font-size: 32rpx;
  color: #6b7280;
}

.login-button {
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 30rpx 60rpx;
  border-radius: 50rpx;
  font-size: 36rpx;
  font-weight: 500;
  box-shadow: 0 4rpx 16rpx rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
}

.login-button:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(99, 102, 241, 0.3);
}

/* 底部导航栏 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20rpx 0;
  z-index: 999;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.nav-item.active .nav-text {
  color: #6366f1;
}

.nav-text {
  font-size: 24rpx;
  color: #7A7E83;
  margin-top: 4rpx;
}
</style>