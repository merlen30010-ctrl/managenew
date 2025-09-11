<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */

	
	page {
		background-color: #f5f7fa;
		min-height: 100vh;
		font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
	}
	
	/* 自定义导航栏样式 */
	.custom-navbar {
		position: relative;
		height: 44px;
		padding-top: 44px;
		background: transparent;
	}
	
	.capsule-button {
		position: fixed;
		top: 54px;
		right: 10px;
		width: 80px;
		height: 30px;
		background: rgba(255, 255, 255, 0.8);
		border-radius: 15px;
		backdrop-filter: blur(10px);
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
		z-index: 1000;
	}
	
	/* 底部导航栏样式 */
	.bottom-nav {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 50px;
		background: #ffffff;
		border-top: 1px solid #e5e7eb;
		display: flex;
		justify-content: space-around;
		align-items: center;
		padding: 5px 0;
		z-index: 999;
	}
	
	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex: 1;
		height: 100%;
		color: #7A7E83;
		text-decoration: none;
	}
	
	.nav-item.active {
		color: #6366f1;
	}
	
	.nav-icon {
		width: 24px;
		height: 24px;
		margin-bottom: 2px;
	}
	
	.nav-text {
		font-size: 12px;
	}
</style>