<template>
  <div class="login-page">
    <van-nav-bar title="用户登录" left-arrow @click-left="onClickLeft" fixed />
    <div class="login-container">
      <van-form @submit="onSubmit" class="login-form">
        <van-cell-group inset>
          <van-field v-model="username" name="username" label="用户名" placeholder="请输入用户名"
            :rules="[{ required: true, message: '请填写用户名' }]" />
          <van-field v-model="password" type="password" name="password" label="密码" placeholder="请输入密码"
            :rules="[{ required: true, message: '请填写密码' }]" />
        </van-cell-group>
        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large">登录</van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'; import { useRouter } from 'vue-router'; import { showToast } from 'vant'; import { useUserStore } from '../store/user';
const router = useRouter(); const userStore = useUserStore();
const username = ref(''); const password = ref('');
const onSubmit = async (values) => {
  showToast({ type: 'loading', message: '登录中...', forbidClick: true, duration: 0 });
  try {
    const result = await userStore.login({ username: username.value, password: password.value });
    if (result.success) { showToast({ type: 'success', message: result.message }); router.push('/') }
    else { showToast({ type: 'fail', message: result.message }) }
  } catch (e) { showToast({ type: 'fail', message: '登录失败，请稍后再试' }) }
};
const onClickLeft = () => router.back();
</script>
<style scoped>
.login-page { min-height: 100vh; }
.login-container { padding-top: 46px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: calc(100vh - 46px); box-sizing: border-box; }
.login-form { width: 100%; padding: 0 20px; margin-top: -10vh; }
.submit-btn { margin: 28px 0 16px; }
</style>