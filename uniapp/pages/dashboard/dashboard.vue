<template>
  <view class="dashboard-container">
    <!-- 顶部导航 -->
    <view class="top-nav">
      <view class="nav-content">
        <view class="nav-left">
          <view class="logo-circle">
            <uni-icons type="home" size="20" color="#ffffff"></uni-icons>
          </view>
          <view class="nav-text">
            <text class="nav-title">管理系统</text>
            <text class="nav-subtitle">欢迎回来，管理员</text>
          </view>
        </view>
        <view class="nav-right">
          <view class="notification-btn">
            <uni-icons type="notification" size="24" color="#6b7280"></uni-icons>
            <view class="badge">3</view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 日期和星期信息 -->
    <view class="date-weather-section">
      <view class="date-tag">
        <text class="tag-text">{{ currentDate }} {{ currentWeek }}</text>
      </view>
      <view class="weather-tag">
        <text class="tag-text">锌月均价: {{ monthlyZincPrice }}元/吨</text>
      </view>
    </view>
    
    <!-- 库存信息 -->
    <view class="zinc-price-section">
      <view class="price-card">
        <view class="price-label">原料库存</view>
        <view class="price-value">{{ rawMaterialStock }}</view>
        <view class="price-unit">金吨</view>
      </view>
      <view class="price-card">
        <view class="price-label">焙砂库存</view>
        <view class="price-value">{{ concentrateStock }}</view>
        <view class="price-unit">金吨</view>
      </view>
    </view>
    
    <!-- 快捷功能区 -->
    <view class="quick-actions">
      <view class="section-title">快捷功能</view>
      <view class="actions-grid">
        <!-- 12个按钮 -->
        <view class="action-item" v-for="(item, index) in quickActions" :key="index" @click="handleAction(index)">
          <view class="action-icon-square" :class="item.bgClass">
            <uni-icons :type="item.icon" size="28" color="#ffffff"></uni-icons>
          </view>
          <text class="action-label">{{ item.label }}</text>
        </view>
      </view>
    </view>
    
    <!-- 最新通知 -->
    <view class="notifications-section">
      <view class="section-title">最新通知</view>
      <view class="notification-list">
        <view class="notification-item" v-for="(notification, index) in notifications" :key="index">
          <view class="notification-icon">
            <uni-icons type="notification-filled" size="18" color="#6366f1"></uni-icons>
          </view>
          <view class="notification-content">
            <text class="notification-title">{{ notification.title }}</text>
            <text class="notification-time">{{ notification.time }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
  
  <!-- 底部导航栏 -->
  <view class="bottom-nav">
    <view class="nav-item active" @click="goToPage('dashboard')">
      <uni-icons type="home" size="24" color="#6366f1"></uni-icons>
      <text class="nav-text">主页</text>
    </view>
    <view class="nav-item" @click="goToPage('news')">
      <uni-icons type="flag" size="24" color="#7A7E83"></uni-icons>
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
</template>

<script>
import { request } from '@/api/request.js'

export default {
  data() {
    return {
      currentDate: '',
      currentWeek: '',
      monthlyZincPrice: '24,250',
      rawMaterialStock: '1,250',
      concentrateStock: '860',
      quickActions: [
        { label: '员工管理', icon: 'person', bgClass: 'bg-blue' },
        { label: '办公用车', icon: 'car', bgClass: 'bg-orange' },
        { label: '合同管理', icon: 'file', bgClass: 'bg-purple' },
        { label: '物料管理', icon: 'box', bgClass: 'bg-green' },
        { label: '客户管理', icon: 'contact', bgClass: 'bg-indigo' },
        { label: '部门管理', icon: 'home', bgClass: 'bg-teal' },
        { label: '通知管理', icon: 'notification', bgClass: 'bg-red' },
        { label: '数据统计', icon: 'piechart', bgClass: 'bg-yellow' },
        { label: '系统设置', icon: 'gear', bgClass: 'bg-cyan' },
        { label: '用户管理', icon: 'personadd', bgClass: 'bg-pink' },
        { label: '金属价格', icon: 'medalfill', bgClass: 'bg-lime' },
        { label: '更多功能', icon: 'more', bgClass: 'bg-gray' }
      ],
      notifications: [
        { title: '系统维护通知', time: '2小时前' },
        { title: '新功能上线', time: '1天前' },
        { title: '锌价更新提醒', time: '3天前' }
      ]
    }
  },
  mounted() {
    this.getCurrentDate()
    // this.fetchZincPrices() // 暂时注释掉API调用，使用模拟数据
  },
  methods: {
    getCurrentDate() {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      
      // 获取星期几
      const weeks = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      const week = weeks[now.getDay()]
      
      this.currentDate = `${year}年${month}月${day}日`
      this.currentWeek = week
    },
    
    goToPage(page) {
      // 根据页面名称跳转到相应页面
      switch(page) {
        case 'dashboard':
          // 当前页面，无需跳转
          break;
        case 'news':
          uni.switchTab({
            url: '/pages/index/index'
          });
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
    },
    
    // 暂时注释掉API调用，使用模拟数据
    // async fetchZincPrices() {
    //   try {
    //     // 获取最新锌价
    //     const latestResponse = await request({
    //       url: '/api/metal-prices',
    //       method: 'GET',
    //       data: {
    //         metal_type: '1#锌',
    //         per_page: 1
    //       }
    //     })
    //     
    //     if (latestResponse && latestResponse.prices && latestResponse.prices.length > 0) {
    //       const latest = latestResponse.prices[0]
    //       this.latestZincPrice = latest.average_price.toLocaleString()
    //       this.latestPriceChange = latest.price_change > 0 ? `+${latest.price_change}` : `${latest.price_change}`
    //       this.latestPriceChangeClass = latest.price_change >= 0 ? 'positive' : 'negative'
    //     } else {
    //       this.latestZincPrice = '暂无数据'
    //       this.latestPriceChange = ''
    //     }
    //     
    //     // 获取月均价（这里简化处理，实际应该查询一个月的数据并计算平均值）
    //     // 为了演示，我们使用最近的数据并模拟月均价
    //     this.monthlyZincPrice = '24,250'
    //     this.monthlyPriceChange = '-50'
    //     this.monthlyPriceChangeClass = 'negative'
    //   } catch (error) {
    //     console.error('获取锌价数据失败:', error)
    //     this.latestZincPrice = '获取失败'
    //     this.monthlyZincPrice = '获取失败'
    //     uni.showToast({
    //       title: '获取锌价数据失败',
    //       icon: 'none'
    //     })
    //   }
    // },
    
    handleAction(index) {
      // 根据按钮索引执行不同操作
      switch(index) {
        case 0: // 员工管理
          uni.showToast({ title: '员工管理功能待开发', icon: 'none' });
          break;
        case 1: // 办公用车
          uni.switchTab({ url: '/pages/vehicle/vehicle' });
          break;
        case 2: // 合同管理
          uni.showToast({ title: '合同管理功能待开发', icon: 'none' });
          break;
        case 3: // 物料管理
          uni.showToast({ title: '物料管理功能待开发', icon: 'none' });
          break;
        case 4: // 客户管理
          uni.showToast({ title: '客户管理功能待开发', icon: 'none' });
          break;
        case 5: // 部门管理
          uni.showToast({ title: '部门管理功能待开发', icon: 'none' });
          break;
        case 6: // 通知管理
          uni.showToast({ title: '通知管理功能待开发', icon: 'none' });
          break;
        case 7: // 数据统计
          uni.showToast({ title: '数据统计功能待开发', icon: 'none' });
          break;
        case 8: // 系统设置
          uni.showToast({ title: '系统设置功能待开发', icon: 'none' });
          break;
        case 9: // 用户管理
          uni.showToast({ title: '用户管理功能待开发', icon: 'none' });
          break;
        case 10: // 金属价格
          uni.showToast({ title: '金属价格功能待开发', icon: 'none' });
          break;
        case 11: // 更多功能
          uni.showToast({ title: '更多功能待开发', icon: 'none' });
          break;
        default:
          uni.showToast({ title: '功能待开发', icon: 'none' });
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
  padding-bottom: 140rpx; /* 为底部导航留出空间 */
}

/* 顶部导航 */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
  border-radius: 16rpx;
  margin-bottom: 20rpx;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
}

.nav-left {
  display: flex;
  align-items: center;
}

.logo-circle {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.nav-text {
  display: flex;
  flex-direction: column;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.nav-subtitle {
  font-size: 20rpx;
  color: #6b7280;
  margin-top: 4rpx;
}

.nav-right {
  position: relative;
}

.notification-btn {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #ef4444;
  color: white;
  font-size: 18rpx;
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 日期和星期 */
.date-weather-section {
  display: flex;
  margin-bottom: 20rpx;
  gap: 20rpx;
}

.date-tag, .weather-tag {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 16rpx 24rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.tag-text {
  font-size: 24rpx;
  color: #374151;
}

.ml-1 {
  margin-left: 8rpx;
}

/* 库存信息 */
.zinc-price-section {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.price-card {
  flex: 1;
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.price-label {
  font-size: 24rpx;
  color: #6b7280;
  margin-bottom: 10rpx;
}

.price-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.price-unit {
  font-size: 20rpx;
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

/* 修改为方形图标 */
.action-icon-square {
  width: 100rpx;
  height: 100rpx;
  border-radius: 16rpx; /* 方形图标，圆角较小 */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.bg-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.bg-purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.bg-green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bg-indigo {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

.bg-teal {
  background: linear-gradient(135deg, #0d9488 0%, #115e59 100%);
}

.bg-red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.bg-yellow {
  background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
}

.bg-cyan {
  background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%);
}

.bg-pink {
  background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
}

.bg-lime {
  background: linear-gradient(135deg, #84cc16 0%, #65a30d 100%);
}

.bg-gray {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
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
  margin-bottom: 30rpx; /* 添加底部边距 */
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
  z-index: 999; /* 确保导航栏在最上层 */
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1; /* 确保均匀分布 */
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