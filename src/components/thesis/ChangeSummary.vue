<script setup lang="ts">
import type { RuleChange, RuleVersion } from '../../types/thesis';

defineProps<{
  previousVersion: RuleVersion;
  currentVersion: RuleVersion;
  changes: RuleChange[];
}>();

defineEmits<{
  selectRule: [ruleId: string];
}>();
</script>

<template>
  <section class="change-summary" aria-label="版本变更">
    <div class="change-version">
      <span>{{ previousVersion.name }}</span>
      <strong>→</strong>
      <span>{{ currentVersion.name }}</span>
    </div>

    <button
      v-for="change in changes"
      :key="change.ruleId"
      class="change-item"
      :class="`risk-${change.risk}`"
      type="button"
      @click="$emit('selectRule', change.ruleId)"
    >
      <span>{{ change.title }}</span>
      <small>{{ change.risk === 'high' ? '高风险' : change.risk === 'medium' ? '中风险' : '低风险' }}</small>
    </button>
  </section>
</template>
