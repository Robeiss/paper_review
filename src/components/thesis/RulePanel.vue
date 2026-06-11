<script setup lang="ts">
import type { RuleVersion, ThesisRule } from '../../types/thesis';

defineProps<{
  rule: ThesisRule;
  blockTitle: string;
  version: RuleVersion;
}>();
</script>

<template>
  <aside class="rule-panel" aria-label="格式规则">
    <div class="rule-panel-header">
      <span class="panel-kicker">{{ blockTitle }}</span>
      <h2>{{ rule.name }}</h2>
      <p>{{ rule.summary }}</p>
    </div>

    <dl class="spec-list">
      <div v-for="spec in rule.specs" :key="spec.label" class="spec-row">
        <dt>{{ spec.label }}</dt>
        <dd>{{ spec.value }}</dd>
      </div>
    </dl>

    <section>
      <h3>要求说明</h3>
      <ul>
        <li v-for="note in rule.notes" :key="note">{{ note }}</li>
      </ul>
    </section>

    <section>
      <h3>常见错误</h3>
      <ul class="mistakes">
        <li v-for="mistake in rule.commonMistakes" :key="mistake">{{ mistake }}</li>
      </ul>
    </section>

    <footer class="rule-meta">
      <span>规则级别：{{ rule.severity }}</span>
      <span>更新：{{ rule.updatedAt }}</span>
      <span>来源：{{ version.source }}</span>
    </footer>
  </aside>
</template>
