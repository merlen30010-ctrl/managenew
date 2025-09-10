<template>
  <view class="vehicle-container">
    <!-- 车辆列表 -->
    <view class="vehicles-section">
      <view class="section-header">
        <text class="section-title">可用车辆</text>
        <view class="search-box">
          <uni-icons type="search" size="20" color="#9ca3af"></uni-icons>
          <input 
            class="search-input" 
            placeholder="搜索车辆" 
            v-model="searchKeyword"
            placeholder-class="placeholder-style"
          />
        </view>
      </view>
      
      <view class="vehicle-list">
        <view class="vehicle-item" v-for="(vehicle, index) in filteredVehicles" :key="index">
          <view class="vehicle-info">
            <view class="vehicle-icon">
              <uni-icons type="car" size="28" color="#6366f1"></uni-icons>
            </view>
            <view class="vehicle-details">
              <text class="vehicle-name">{{ vehicle.name }}</text>
              <text class="vehicle-model">{{ vehicle.model }}</text>
              <text class="vehicle-status" :class="vehicle.statusClass">{{ vehicle.status }}</text>
            </view>
          </view>
          <button 
            class="apply-btn" 
            :class="vehicle.statusClass === 'available' ? 'btn-available' : 'btn-unavailable'"
            :disabled="vehicle.statusClass !== 'available'"
            @click="applyVehicle(vehicle)"
          >
            {{ vehicle.statusClass === 'available' ? '申请' : '不可用' }}
          </button>
        </view>
      </view>
    </view>
    
    <!-- 申请用车按钮 -->
    <view class="apply-section">
      <button class="apply-main-btn" @click="showApplyModal">
        <uni-icons type="plus" size="24" color="#ffffff"></uni-icons>
        <text class="apply-btn-text">申请用车</text>
      </button>
    </view>
    
    <!-- 申请用车弹窗 -->
    <uni-popup ref="applyPopup" type="bottom">
      <view class="apply-popup">
        <view class="popup-header">
          <text class="popup-title">申请用车</text>
          <button class="close-btn" @click="closeApplyModal">
            <uni-icons type="closeempty" size="20" color="#9ca3af"></uni-icons>
          </button>
        </view>
        
        <view class="popup-content">
          <view class="form-group">
            <text class="form-label">用车时间</text>
            <view class="date-picker">
              <view class="date-input" @click="selectStartDate">
                <text>{{ startDate || '请选择开始时间' }}</text>
                <uni-icons type="arrowdown" size="16" color="#9ca3af"></uni-icons>
              </view>
              <text class="date-separator">至</text>
              <view class="date-input" @click="selectEndDate">
                <text>{{ endDate || '请选择结束时间' }}</text>
                <uni-icons type="arrowdown" size="16" color="#9ca3af"></uni-icons>
              </view>
            </view>
          </view>
          
          <view class="form-group">
            <text class="form-label">用车事由</text>
            <textarea 
              class="reason-input" 
              placeholder="请输入用车事由"
              v-model="applyReason"
              placeholder-class="placeholder-style"
            />
          </view>
          
          <view class="form-group">
            <text class="form-label">紧急程度</text>
            <view class="priority-options">
              <view 
                class="priority-option" 
                :class="selectedPriority === 'normal' ? 'selected' : ''"
                @click="selectPriority('normal')"
              >
                <uni-icons type="flag" size="20" color="#10b981"></uni-icons>
                <text class="priority-text">普通</text>
              </view>
              
              <view 
                class="priority-option" 
                :class="selectedPriority === 'urgent' ? 'selected' : ''"
                @click="selectPriority('urgent')"
              >
                <uni-icons type="flag-filled" size="20" color="#f59e0b"></uni-icons>
                <text class="priority-text">紧急</text>
              </view>
              
              <view 
                class="priority-option" 
                :class="selectedPriority === 'very-urgent' ? 'selected' : ''"
                @click="selectPriority('very-urgent')"
              >
                <uni-icons type="flag-filled" size="20" color="#ef4444"></uni-icons>
                <text class="priority-text">非常紧急</text>
              </view>
            </view>
          </view>
        </view>
        
        <view class="popup-footer">
          <button class="cancel-btn" @click="closeApplyModal">取消</button>
          <button class="submit-btn" @click="submitApplication">提交申请</button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchKeyword: '',
      startDate: '',
      endDate: '',
      applyReason: '',
      selectedPriority: 'normal',
      vehicles: [
        {
          name: '奥迪A6L',
          model: '商务轿车',
          status: '可用车辆',
          statusClass: 'available'
        },
        {
          name: '丰田凯美瑞',
          model: '商务轿车',
          status: '使用中',
          statusClass: 'in-use'
        },
        {
          name: '本田奥德赛',
          model: '商务MPV',
          status: '可用车辆',
          statusClass: 'available'
        },
        {
          name: '别克GL8',
          model: '商务MPV',
          status: '维修中',
          statusClass: 'maintenance'
        }
      ]
    }
  },
  computed: {
    filteredVehicles() {
      if (!this.searchKeyword) {
        return this.vehicles
      }
      return this.vehicles.filter(vehicle => 
        vehicle.name.includes(this.searchKeyword) || 
        vehicle.model.includes(this.searchKeyword)
      )
    }
  },
  methods: {
    applyVehicle(vehicle) {
      if (vehicle.statusClass === 'available') {
        uni.showToast({
          title: `申请${vehicle.name}成功`,
          icon: 'success'
        })
      }
    },
    
    showApplyModal() {
      this.$refs.applyPopup.open()
    },
    
    closeApplyModal() {
      this.$refs.applyPopup.close()
    },
    
    selectStartDate() {
      uni.showToast({
        title: '选择开始时间功能待开发',
        icon: 'none'
      })
    },
    
    selectEndDate() {
      uni.showToast({
        title: '选择结束时间功能待开发',
        icon: 'none'
      })
    },
    
    selectPriority(priority) {
      this.selectedPriority = priority
    },
    
    submitApplication() {
      if (!this.startDate || !this.endDate) {
        uni.showToast({
          title: '请选择用车时间',
          icon: 'none'
        })
        return
      }
      
      if (!this.applyReason) {
        uni.showToast({
          title: '请输入用车事由',
          icon: 'none'
        })
        return
      }
      
      uni.showToast({
        title: '申请提交成功',
        icon: 'success'
      })
      
      this.closeApplyModal()
      
      // 重置表单
      this.startDate = ''
      this.endDate = ''
      this.applyReason = ''
      this.selectedPriority = 'normal'
    }
  }
}
</script>

<style scoped>
.vehicle-container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
  padding-bottom: 120rpx; /* 为底部导航栏留出空间 */
}

/* 车辆列表 */
.vehicles-section {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 0 20rpx;
  width: 300rpx;
}

.search-input {
  flex: 1;
  height: 60rpx;
  font-size: 28rpx;
  color: #1f2937;
  background: transparent;
}

.placeholder-style {
  color: #9ca3af;
  font-size: 28rpx;
}

.vehicle-list {
  display: flex;
  flex-direction: column;
}

.vehicle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.vehicle-item:last-child {
  border-bottom: none;
}

.vehicle-info {
  display: flex;
  align-items: center;
}

.vehicle-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.vehicle-details {
  display: flex;
  flex-direction: column;
}

.vehicle-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.vehicle-model {
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 8rpx;
}

.vehicle-status {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  display: inline-flex;
  align-self: flex-start;
}

.available {
  background: #dcfce7;
  color: #10b981;
}

.in-use {
  background: #ffe4b5;
  color: #d97706;
}

.maintenance {
  background: #fee2e2;
  color: #ef4444;
}

.apply-btn {
  padding: 16rpx 32rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  font-weight: 500;
}

.btn-available {
  background: #6366f1;
  color: #ffffff;
}

.btn-unavailable {
  background: #e5e7eb;
  color: #9ca3af;
}

/* 申请用车按钮 */
.apply-section {
  position: fixed;
  bottom: 120rpx; /* 调整位置以避免与底部导航栏重叠 */
  right: 30rpx;
  z-index: 100;
}

.apply-main-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50rpx;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(99, 102, 241, 0.3);
}

.apply-btn-text {
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 500;
  margin-left: 10rpx;
}

/* 申请用车弹窗 */
.apply-popup {
  background: #ffffff;
  border-top-left-radius: 32rpx;
  border-top-right-radius: 32rpx;
  padding: 30rpx;
  max-height: 80vh;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.popup-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: transparent;
  border: none;
  padding: 10rpx;
}

.form-group {
  margin-bottom: 40rpx;
}

.form-label {
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 16rpx;
  display: block;
}

.date-picker {
  display: flex;
  align-items: center;
}

.date-input {
  flex: 1;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-separator {
  margin: 0 20rpx;
  color: #6b7280;
}

.reason-input {
  width: 100%;
  height: 160rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #1f2937;
}

.priority-options {
  display: flex;
  justify-content: space-between;
}

.priority-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  flex: 1;
  margin: 0 10rpx;
}

.priority-option:first-child {
  margin-left: 0;
}

.priority-option:last-child {
  margin-right: 0;
}

.priority-option.selected {
  border-color: #6366f1;
  background: #eef2ff;
}

.priority-text {
  font-size: 24rpx;
  color: #374151;
  margin-top: 10rpx;
}

.popup-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 30rpx;
}

.cancel-btn, .submit-btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 500;
}

.cancel-btn {
  background: #f9fafb;
  color: #374151;
  margin-right: 20rpx;
}

.submit-btn {
  background: #6366f1;
  color: #ffffff;
}
</style>