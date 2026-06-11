<script setup lang="ts">
import type { DataSourceStatus } from '../../types/thesis';

defineProps<{
  status: DataSourceStatus;
}>();
</script>

<template>
  <span class="data-source-badge" :class="`source-${status}`">
    {{ status === 'remote' ? '后端同步' : status === 'loading' ? '同步中' : '本地备用' }}
  </span>
</template>
