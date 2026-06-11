<script setup lang="ts">
import type { ThesisBlock } from '../../types/thesis';

defineProps<{
  blocks: ThesisBlock[];
  activeBlockId: string;
  changedRuleIds: string[];
}>();

defineEmits<{
  select: [blockId: string, ruleId: string];
}>();
</script>

<template>
  <nav class="outline" aria-label="论文结构">
    <a
      v-for="block in blocks"
      :key="block.id"
      :href="`#${block.id}`"
      class="outline-item"
      :class="[`outline-${block.type}`, { active: block.id === activeBlockId, changed: changedRuleIds.includes(block.ruleId) }]"
      @click="$emit('select', block.id, block.ruleId)"
    >
      <span class="outline-type" aria-hidden="true">{{ block.type.slice(0, 1).toUpperCase() }}</span>
      <span class="outline-title">{{ block.title }}</span>
      <span v-if="changedRuleIds.includes(block.ruleId)" class="outline-badge">改</span>
    </a>
  </nav>
</template>
