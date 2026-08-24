<template>
  <div class="register-page">
    <van-nav-bar title="用户注册" left-arrow @click-left="onClickLeft" fixed />
    <div class="register-container">
      <div class="register-brand">
        <div class="register-icon">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <rect width="56" height="56" rx="14" fill="#6060e0"/>
            <text x="28" y="36" text-anchor="middle" fill="#08080c" font-family="sans-serif" font-size="24" font-weight="700">N</text>
          </svg>
        </div>
        <h2 class="register-title">创建账号</h2>
        <p class="register-subtitle">注册以获取个性化推荐</p>
      </div>
      <van-form @submit="onSubmit" class="register-form">
        <van-cell-group inset>
          <van-field v-model="username" name="username" label="用户名" placeholder="请输入用户名"
            :rules="[{ required: true, message: '请填写用户名' }]" />
          <van-field v-model="password" type="password" name="password" label="密码" placeholder="请输入密码"
            :rules="[{ required: true, message: '请填写密码' }]" />
          <van-field v-model="confirmPassword" type="password" name="confirmPassword" label="确认密码" placeholder="请再次输入密码"
            :rules="[{ required: true, message: '请确认密码' }, { validator: validatePassword, message: '两次密码不一致' }]" />
        </van-cell-group>
        <div class="submit-btn"><van-button round block type="primary" native-type="submit" size="large">注册</van-button></div>
        <div class="login-link">已有账号？<span @click="goToLogin">去登录</span></div>
      </van-form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'; import { useRouter } from 'vue-router'; import { showToast } from 'vant'; import { useUserStore } from '../store/user';
const router = useRouter(); const userStore = useUserStore();
const username = ref(''); const password = ref(''); const confirmPassword = ref('');
const validatePassword = () => password.value === confirmPassword.value;
const onSubmit = async () => {
  showToast({ type: 'loading', message: '注册中...', forbidClick: true, duration: 0 });
  try {
    const result = await userStore.register({ username: username.value, password: password.value });
    if (result.success) { showToast({ type: 'success', message: result.message }); router.push('/') }
    else { showToast({ type: 'fail', message: result.message }) }
  } catch (e) { showToast({ type: 'fail', message: '注册失败，请稍后再试' }) }
};
const onClickLeft = () => router.back();
const goToLogin = () => router.push('/login');
</script>
<style scoped>
.register-page { min-height: 100vh; }
.register-container { padding-top: 56px; display: flex; flex-direction: column; align-items: center; }
.register-brand { margin: 32px 0 36px; text-align: center; animation: fadeInUp 0.5s var(--ease-out-expo) both; }
.register-icon { margin-bottom: 14px; display: flex; justify-content: center; }
.register-title { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0 0 6px; letter-spacing: 0.05em; }
.register-subtitle { font-size: 14px; color: var(--text-secondary); margin: 0; }
.register-form { width: 100%; padding: 0 20px; }
.submit-btn { margin: 28px 0 16px; }
.login-link { text-align: center; color: var(--text-secondary); font-size: 14px; }
.login-link span { color: var(--accent-blue); font-weight: 500; cursor: pointer; }
</style>