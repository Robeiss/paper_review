<script setup lang="ts">
import type { RuleChange, RuleVersion, ThesisRule } from '../../types/thesis';

defineProps<{
  rule: ThesisRule;
  blockTitle: string;
  version: RuleVersion;
  change?: RuleChange;
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

    <section v-if="change" class="change-detail" :class="`risk-${change.risk}`">
      <h3>本版变化</h3>
      <div class="change-compare">
        <p><strong>上一版：</strong>{{ change.previous }}</p>
        <p><strong>当前版：</strong>{{ change.current }}</p>
      </div>
      <p class="change-impact">{{ change.impact }}</p>
    </section>

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
