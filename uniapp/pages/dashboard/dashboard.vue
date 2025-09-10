<template>
  <view class="dashboard-container">
    <!-- 顶部统计 -->
    <view class="stats-section">
      <view class="stat-card">
        <view class="stat-icon bg-blue">
          <uni-icons type="person" size="24" color="#ffffff"></uni-icons>
        </view>
        <view class="stat-info">
          <text class="stat-value">128</text>
          <text class="stat-label">用户数</text>
        </view>
      </view>
      
      <view class="stat-card">
        <view class="stat-icon bg-green">
          <uni-icons type="compose" size="24" color="#ffffff"></uni-icons>
        </view>
        <view class="stat-info">
          <text class="stat-value">24</text>
          <text class="stat-label">待办事项</text>
        </view>
      </view>
      
      <view class="stat-card">
        <view class="stat-icon bg-purple">
          <uni-icons type="paperclip" size="24" color="#ffffff"></uni-icons>
        </view>
        <view class="stat-info">
          <text class="stat-value">8</text>
          <text class="stat-label">通知</text>
        </view>
      </view>
    </view>
    
    <!-- 快捷功能 -->
    <view class="quick-actions">
      <view class="section-title">快捷功能</view>
      <view class="actions-grid">
        <view class="action-item" @click="goToVehicle">
          <view class="action-icon bg-orange">
            <uni-icons type="car" size="28" color="#ffffff"></uni-icons>
          </view>
          <text class="action-label">办公用车</text>
        </view>
        
        <view class="action-item" @click="goToProfile">
          <view class="action-icon bg-indigo">
            <uni-icons type="person" size="28" color="#ffffff"></uni-icons>
          </view>
          <text class="action-label">个人中心</text>
        </view>
        
        <view class="action-item" @click="showNotifications">
          <view class="action-icon bg-red">
            <uni-icons type="notification" size="28" color="#ffffff"></uni-icons>
          </view>
          <text class="action-label">通知</text>
        </view>
        
        <view class="action-item" @click="showSettings">
          <view class="action-icon bg-teal">
            <uni-icons type="gear" size="28" color="#ffffff"></uni-icons>
          </view>
          <text class="action-label">设置</text>
        </view>
      </view>
    </view>
    
    <!-- 最新通知 -->
    <view class="notifications-section">
      <view class="section-title">最新通知</view>
      <view class="notification-list">
        <view class="notification-item">
          <view class="notification-icon">
            <uni-icons type="notification-filled" size="18" color="#6366f1"></uni-icons>
          </view>
          <view class="notification-content">
            <text class="notification-title">系统维护通知</text>
            <text class="notification-time">2小时前</text>
          </view>
        </view>
        
        <view class="notification-item">
          <view class="notification-icon">
            <uni-icons type="notification-filled" size="18" color="#6366f1"></uni-icons>
          </view>
          <view class="notification-content">
            <text class="notification-title">新功能上线</text>
            <text class="notification-time">1天前</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  components: {
    // uni-icons组件会自动注册，无需手动导入
  },
  methods: {
    goToVehicle() {
      uni.switchTab({
        url: '/pages/vehicle/vehicle'
      })
    },
    
    goToProfile() {
      uni.switchTab({
        url: '/pages/profile/profile'
      })
    },
    
    showNotifications() {
      uni.showToast({
        title: '通知功能待开发',
        icon: 'none'
      })
    },
    
    showSettings() {
      uni.showToast({
        title: '设置功能待开发',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 统计卡片 */
.stats-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
}

.stat-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  flex: 1;
  margin: 0 10rpx;
  display: flex;
  align-items: center;
}

.stat-card:first-child {
  margin-left: 0;
}

.stat-card:last-child {
  margin-right: 0;
}

.stat-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.bg-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bg-purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #6b7280;
}

/* 快捷功能 */
.quick-actions {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 30rpx;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.bg-orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.bg-indigo {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

.bg-red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.bg-teal {
  background: linear-gradient(135deg, #0d9488 0%, #115e59 100%);
}

.action-label {
  font-size: 24rpx;
  color: #374151;
  text-align: center;
}

/* 通知列表 */
.notifications-section {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.notification-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  margin-right: 20rpx;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 28rpx;
  color: #1f2937;
  margin-bottom: 8rpx;
  display: block;
}

.notification-time {
  font-size: 24rpx;
  color: #9ca3af;
}
</style>