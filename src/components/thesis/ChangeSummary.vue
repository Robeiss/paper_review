<script setup lang="ts">
import { computed } from 'vue';
import type { RuleChange, RuleVersion } from '../../types/thesis';

const props = defineProps<{
  previousVersion: RuleVersion;
  currentVersion: RuleVersion;
  changes: RuleChange[];
}>();

defineEmits<{
  selectRule: [ruleId: string];
}>();

const highRiskCount = computed(() => props.changes.filter((change) => change.risk === 'high').length);
const mediumRiskCount = computed(() => props.changes.filter((change) => change.risk === 'medium').length);
</script>

<template>
  <section class="change-summary" aria-label="版本变更">
    <div class="version-card">
      <span class="version-label">当前版本</span>
      <strong>{{ currentVersion.name }}</strong>
      <time :datetime="currentVersion.publishedAt">{{ currentVersion.publishedAt }}</time>
    </div>

    <div class="change-metrics">
      <div class="metric-card risk-high">
        <strong>{{ highRiskCount }}</strong>
        <span>高风险</span>
      </div>
      <div class="metric-card risk-medium">
        <strong>{{ mediumRiskCount }}</strong>
        <span>中风险</span>
      </div>
      <div class="metric-card risk-low">
        <strong>{{ changes.length }}</strong>
        <span>总变更</span>
      </div>
    </div>

    <div class="change-list">
      <button
        v-for="change in changes"
        :key="change.ruleId"
        class="change-item"
        :class="`risk-${change.risk}`"
        type="button"
        @click="$emit('selectRule', change.ruleId)"
      >
        <span class="risk-dot" aria-hidden="true"></span>
        <span>{{ change.title }}</span>
      </button>
    </div>
  </section>
</template>
