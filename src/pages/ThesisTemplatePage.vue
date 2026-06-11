<script setup lang="ts">
import { computed, ref } from 'vue';
import OutlineNav from '../components/thesis/OutlineNav.vue';
import PaperPage from '../components/thesis/PaperPage.vue';
import RulePanel from '../components/thesis/RulePanel.vue';
import VersionBadge from '../components/thesis/VersionBadge.vue';
import { thesisBlocks } from '../data/thesisSample';
import { currentVersion, thesisRules } from '../data/thesisRules';

const ruleMap = new Map(thesisRules.map((rule) => [rule.id, rule]));
const activeBlockId = ref(thesisBlocks[0].id);
const activeRuleId = ref(thesisBlocks[0].ruleId);

const activeRule = computed(() => ruleMap.get(activeRuleId.value) ?? thesisRules[0]);
const activeBlock = computed(() => thesisBlocks.find((block) => block.id === activeBlockId.value) ?? thesisBlocks[0]);

function selectBlock(blockId: string, ruleId: string) {
  activeBlockId.value = blockId;
  activeRuleId.value = ruleId;
}
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">PS</span>
        <div>
          <h1>论文格式可视化样张</h1>
          <VersionBadge :version="currentVersion" />
        </div>
      </div>
      <OutlineNav :blocks="thesisBlocks" :active-block-id="activeBlockId" @select="selectBlock" />
    </aside>

    <PaperPage :blocks="thesisBlocks" :active-block-id="activeBlockId" @select="selectBlock" />

    <RulePanel :rule="activeRule" :block-title="activeBlock.title" :version="currentVersion" />
  </main>
</template>
