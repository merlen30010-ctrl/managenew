<template>
  <view class="profile-container">
    <!-- 个人资料头部 -->
    <view class="profile-header">
      <view class="header-content">
        <view class="avatar-container">
          <uni-icons type="person" size="48" color="#ffffff"></uni-icons>
        </view>
        <text class="username">管理员</text>
        <text class="user-role">系统管理员</text>
        <view class="stats">
          <view class="stat-item">
            <text class="stat-value">24</text>
            <text class="stat-label">通知</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">15</text>
            <text class="stat-label">待办</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 菜单列表 -->
    <view class="menu-container">
      <view class="menu-section">
        <!-- 个人信息 -->
        <view class="menu-item" @click="goToProfileDetail">
          <view class="menu-icon bg-blue">
            <uni-icons type="person" size="24" color="#3b82f6"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">个人信息</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <!-- 修改密码 -->
        <view class="menu-item" @click="changePassword">
          <view class="menu-icon bg-green">
            <uni-icons type="locked" size="24" color="#10b981"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">修改密码</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <!-- 我的通知 -->
        <view class="menu-item" @click="goToNotifications">
          <view class="menu-icon bg-yellow">
            <uni-icons type="notification" size="24" color="#f59e0b"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">我的通知</text>
          </view>
          <view class="menu-badge">3</view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <!-- 我的申请 -->
        <view class="menu-item" @click="goToApplications">
          <view class="menu-icon bg-purple">
            <uni-icons type="document" size="24" color="#8b5cf6"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">我的申请</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <!-- 系统设置 -->
        <view class="menu-item" @click="goToSettings">
          <view class="menu-icon bg-indigo">
            <uni-icons type="gear" size="24" color="#6366f1"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">系统设置</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
      </view>
      
      <!-- 系统管理 -->
      <view class="menu-section">
        <view class="menu-item" @click="goToUserManagement">
          <view class="menu-icon bg-red">
            <uni-icons type="personadd" size="24" color="#ef4444"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">用户管理</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <view class="menu-item" @click="goToVehicleManagement">
          <view class="menu-icon bg-teal">
            <uni-icons type="car" size="24" color="#0d9488"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">车辆管理</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
        
        <view class="menu-item" @click="goToDataStatistics">
          <view class="menu-icon bg-orange">
            <uni-icons type="piechart" size="24" color="#f97316"></uni-icons>
          </view>
          <view class="menu-content">
            <text class="menu-title">数据统计</text>
          </view>
          <uni-icons type="arrowright" size="20" color="#d1d5db"></uni-icons>
        </view>
      </view>
      
      <!-- 退出登录 -->
      <view class="logout-section">
        <button class="logout-btn" @click="logout">
          <uni-icons type="forward" size="24" color="#ef4444"></uni-icons>
          <text class="logout-text">退出登录</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goToProfileDetail() {
      uni.showToast({ title: '个人信息功能待开发', icon: 'none' })
    },
    
    changePassword() {
      uni.showToast({ title: '修改密码功能待开发', icon: 'none' })
    },
    
    goToNotifications() {
      uni.showToast({ title: '我的通知功能待开发', icon: 'none' })
    },
    
    goToApplications() {
      uni.showToast({ title: '我的申请功能待开发', icon: 'none' })
    },
    
    goToSettings() {
      uni.showToast({ title: '系统设置功能待开发', icon: 'none' })
    },
    
    goToUserManagement() {
      uni.showToast({ title: '用户管理功能待开发', icon: 'none' })
    },
    
    goToVehicleManagement() {
      uni.switchTab({ url: '/pages/vehicle/vehicle' })
    },
    
    goToDataStatistics() {
      uni.showToast({ title: '数据统计功能待开发', icon: 'none' })
    },
    
    logout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除token
            uni.removeStorageSync('token')
            // 跳转到登录页
            uni.redirectTo({
              url: '/pages/login/login'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
}

/* 个人资料头部 */
.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60rpx 30rpx 40rpx;
  position: relative;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-container {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 8rpx solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.username {
  font-size: 36rpx;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 10rpx;
}

.user-role {
  font-size: 28rpx;
  color: #e0e7ff;
  margin-bottom: 30rpx;
}

.stats {
  display: flex;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 40rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 10rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #e0e7ff;
}

.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.3);
}

/* 菜单容器 */
.menu-container {
  padding: 30rpx;
  padding-bottom: 120rpx; /* 为底部导航栏留出空间 */
}

.menu-section {
  background: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 30rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #f9fafb;
}

.menu-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.bg-blue {
  background: #dbeafe;
}

.bg-green {
  background: #dcfce7;
}

.bg-yellow {
  background: #fef3c7;
}

.bg-purple {
  background: #ede9fe;
}

.bg-indigo {
  background: #e0e7ff;
}

.bg-red {
  background: #fee2e2;
}

.bg-teal {
  background: #ccfbf1;
}

.bg-orange {
  background: #ffedd5;
}

.menu-content {
  flex: 1;
}

.menu-title {
  font-size: 30rpx;
  color: #1f2937;
}

.menu-badge {
  background: #ef4444;
  color: #ffffff;
  font-size: 20rpx;
  border-radius: 18rpx;
  padding: 0 12rpx;
  height: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

/* 退出登录 */
.logout-section {
  padding: 0 30rpx;
}

.logout-btn {
  width: 100%;
  background: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.logout-btn:after {
  border: none;
}

.logout-btn:active {
  background: #f9fafb;
}

.logout-text {
  color: #ef4444;
  font-size: 32rpx;
  font-weight: 500;
  margin-left: 10rpx;
}
</style>