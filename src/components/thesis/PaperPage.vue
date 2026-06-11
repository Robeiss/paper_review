<script setup lang="ts">
import PaperBlock from './PaperBlock.vue';
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
  <section class="paper-stage" aria-label="论文样张">
    <article class="paper-page">
      <PaperBlock
        v-for="block in blocks"
        :key="block.id"
        :block="block"
        :active="block.id === activeBlockId"
        :changed="changedRuleIds.includes(block.ruleId)"
        @select="$emit('select', block.id, block.ruleId)"
      />
    </article>
  </section>
</template>
