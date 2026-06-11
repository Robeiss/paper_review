<script setup lang="ts">
import { ref } from 'vue';
import { login } from '../services/authService';
import type { AuthSession } from '../types/thesis';

const emit = defineEmits<{
  success: [session: AuthSession];
}>();

const account = ref('20260001');
const password = ref('student123');
const roleHint = ref<'student' | 'admin'>('student');
const error = ref('');
const loading = ref(false);

function usePreset(role: 'student' | 'admin') {
  roleHint.value = role;
  account.value = role === 'student' ? '20260001' : 'admin';
  password.value = role === 'student' ? 'student123' : 'admin123';
}

async function submit() {
  error.value = '';
  loading.value = true;
  try {
    emit('success', await login(account.value, password.value));
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <span class="brand-mark">PS</span>
        <div>
          <h1>论文格式样张平台</h1>
          <p>一个学校内的格式规则发布、查看与维护入口。</p>
        </div>
      </div>

      <div class="login-presets" aria-label="测试账号">
        <button type="button" :class="{ active: roleHint === 'student' }" @click="usePreset('student')">学生入口</button>
        <button type="button" :class="{ active: roleHint === 'admin' }" @click="usePreset('admin')">后台入口</button>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <label>
          <span>账号</span>
          <input v-model="account" autocomplete="username" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '登录中' : '登录' }}</button>
      </form>

      <div class="login-hints">
        <span>学生：20260001 / student123</span>
        <span>管理员：admin / admin123</span>
      </div>
    </section>
  </main>
</template>
