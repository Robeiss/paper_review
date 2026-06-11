<script setup lang="ts">
import { computed, ref } from 'vue';
import type { RuleChange, RuleVersion, ThesisRule } from '../../types/thesis';

const props = defineProps<{
  rule: ThesisRule;
  blockTitle: string;
  version: RuleVersion;
  change?: RuleChange;
  checkedKeys: string[];
}>();

const emit = defineEmits<{
  progressChange: [checkedKeys: string[]];
}>();

const activeTab = ref<'specs' | 'change' | 'check'>('specs');

const riskLabel = computed(() => {
  if (!props.change) return '稳定';
  return props.change.risk === 'high' ? '高风险' : props.change.risk === 'medium' ? '中风险' : '低风险';
});

const severityLabel = computed(() => {
  const labels = {
    critical: '重点',
    important: '关注',
    normal: '常规',
  };
  return labels[props.rule.severity];
});

const checkItems = computed(() => [
  ...props.rule.notes.map((text) => ({ key: `note:${text}`, text, kind: 'note' })),
  ...props.rule.commonMistakes.map((text) => ({ key: `mistake:${text}`, text, kind: 'mistake' })),
]);

const checkedCount = computed(() => checkItems.value.filter((item) => props.checkedKeys.includes(item.key)).length);

function toggleCheck(key: string) {
  const next = props.checkedKeys.includes(key)
    ? props.checkedKeys.filter((checkedKey) => checkedKey !== key)
    : [...props.checkedKeys, key];
  emit('progressChange', next);
}
</script>

<template>
  <aside class="rule-panel" aria-label="格式规则">
    <div class="rule-panel-header">
      <span class="panel-kicker">{{ blockTitle }}</span>
      <div class="rule-title-row">
        <h2>{{ rule.name }}</h2>
        <span class="status-pill" :class="change ? `risk-${change.risk}` : 'risk-low'">{{ riskLabel }}</span>
      </div>
      <p>{{ rule.summary }}</p>
    </div>

    <div class="rule-tabs" role="tablist" aria-label="规则信息">
      <button type="button" :class="{ active: activeTab === 'specs' }" @click="activeTab = 'specs'">格式</button>
      <button type="button" :class="{ active: activeTab === 'change' }" @click="activeTab = 'change'">变更</button>
      <button type="button" :class="{ active: activeTab === 'check' }" @click="activeTab = 'check'">检查</button>
    </div>

    <section v-if="activeTab === 'specs'" class="tab-panel">
      <dl class="spec-list">
        <div v-for="spec in rule.specs" :key="spec.label" class="spec-card">
          <dt>{{ spec.label }}</dt>
          <dd>{{ spec.value }}</dd>
        </div>
      </dl>
    </section>

    <section v-else-if="activeTab === 'change'" class="tab-panel">
      <div v-if="change" class="change-detail" :class="`risk-${change.risk}`">
        <div class="compare-card previous">
          <span>上一版</span>
          <p>{{ change.previous }}</p>
        </div>
        <div class="compare-card current">
          <span>当前版</span>
          <p>{{ change.current }}</p>
        </div>
        <div class="impact-card">
          <span>影响</span>
          <p>{{ change.impact }}</p>
        </div>
      </div>
      <div v-else class="empty-state">
        <strong>本模块暂无变更</strong>
        <span>按当前版本要求检查即可。</span>
      </div>
    </section>

    <section v-else class="tab-panel">
      <div class="progress-card">
        <strong>{{ checkedCount }} / {{ checkItems.length }}</strong>
        <span>当前模块检查进度</span>
      </div>

      <div class="check-grid">
        <div class="check-column">
          <h3>要点</h3>
          <label v-for="note in rule.notes" :key="note" class="check-row">
            <input type="checkbox" :checked="checkedKeys.includes(`note:${note}`)" @change="toggleCheck(`note:${note}`)" />
            <span>{{ note }}</span>
          </label>
        </div>
        <div class="check-column">
          <h3>易错</h3>
          <label v-for="mistake in rule.commonMistakes" :key="mistake" class="check-row mistake">
            <input
              type="checkbox"
              :checked="checkedKeys.includes(`mistake:${mistake}`)"
              @change="toggleCheck(`mistake:${mistake}`)"
            />
            <span>{{ mistake }}</span>
          </label>
        </div>
      </div>
    </section>

    <footer class="rule-meta">
      <span>{{ severityLabel }}</span>
      <span>{{ rule.updatedAt }}</span>
      <span>{{ version.source }}</span>
    </footer>
  </aside>
</template>
