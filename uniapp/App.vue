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
</style>