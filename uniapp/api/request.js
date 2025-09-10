// 请求基础配置
const BASE_URL = 'http://localhost:5000' // Flask后端默认地址和端口

// 请求拦截器
function requestInterceptor(config) {
  // 添加token到请求头
  const token = uni.getStorageSync('token')
  if (token) {
    config.header = config.header || {}
    config.header['Authorization'] = 'Bearer ' + token
  }
  return config
}

// 响应拦截器
function responseInterceptor(response) {
  // 处理响应数据
  if (response.statusCode === 200) {
    return response.data
  } else if (response.statusCode === 401) {
    // token过期，跳转到登录页
    uni.removeStorageSync('token')
    uni.redirectTo({
      url: '/pages/login/login'
    })
  } else {
    uni.showToast({
      title: response.data.message || '请求失败',
      icon: 'none'
    })
    return Promise.reject(response)
  }
}

// 封装请求方法
export function request(options) {
  // 请求拦截
  options = requestInterceptor(options)
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: options.header || {},
      success: (res) => {
        // 响应拦截
        try {
          const data = responseInterceptor(res)
          resolve(data)
        } catch (error) {
          reject(error)
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}