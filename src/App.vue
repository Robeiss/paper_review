<script setup lang="ts">
import { ref } from 'vue';
import AdminPage from './pages/AdminPage.vue';
import LoginPage from './pages/LoginPage.vue';
import ThesisTemplatePage from './pages/ThesisTemplatePage.vue';
import type { AuthSession } from './types/thesis';

const session = ref<AuthSession | null>(null);

function logout() {
  session.value = null;
}
</script>

<template>
  <LoginPage v-if="!session" @success="session = $event" />
  <AdminPage v-else-if="session.user.role === 'admin'" :session="session" @logout="logout" />
  <ThesisTemplatePage v-else :token="session.token" />
</template>
