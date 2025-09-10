<template>
  <view class="hello-container">
    <text class="hello-title">{{ msg }}</text>
    <view class="hello-content">
      <text class="hello-text">欢迎使用 uni-app!</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: {
      type: String,
      default: 'Hello World'
    }
  }
}
</script>

<style scoped>
.hello-container {
  padding: 20rpx;
  text-align: center;
}

.hello-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #6366f1;
  margin-bottom: 20rpx;
}

.hello-content {
  background: #f3f4f6;
  padding: 30rpx;
  border-radius: 16rpx;
}

.hello-text {
  font-size: 28rpx;
  color: #4b5563;
}
</style>