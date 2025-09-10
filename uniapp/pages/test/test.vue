<template>
  <view class="container">
    <text class="title">测试页面</text>
    <text class="content">如果能看到这个页面，说明uni-app项目配置正确</text>
    <button @click="goBack" class="back-button">返回首页</button>
  </view>
</template>

<script>
export default {
  methods: {
    goBack() {
      uni.navigateBack()
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
  padding: 40rpx;
  background-color: #f5f7fa;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 20rpx;
}

.content {
  font-size: 32rpx;
  color: #6b7280;
  margin-bottom: 60rpx;
  text-align: center;
}

.back-button {
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

.back-button:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(99, 102, 241, 0.3);
}
</style>