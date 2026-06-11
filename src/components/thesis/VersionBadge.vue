<script setup lang="ts">
import type { RuleVersion } from '../../types/thesis';

defineProps<{
  version: RuleVersion;
}>();
</script>

<template>
  <div class="version-badge" :title="version.changes.join('；')">
    <span>{{ version.name }}</span>
    <time :datetime="version.publishedAt">{{ version.publishedAt }}</time>
  </div>
</template>
