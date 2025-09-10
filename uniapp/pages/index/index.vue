<template>
  <view class="container">
    <view class="welcome-section">
      <text class="title">欢迎使用管理系统</text>
      <text class="subtitle">企业级管理平台</text>
    </view>
    <button @click="goToLogin" class="login-button">前往登录</button>
  </view>
</template>

<script>
export default {
  methods: {
    goToLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
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
</style>