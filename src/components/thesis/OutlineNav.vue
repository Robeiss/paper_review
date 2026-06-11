<script setup lang="ts">
import type { ThesisBlock } from '../../types/thesis';

defineProps<{
  blocks: ThesisBlock[];
  activeBlockId: string;
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
      :class="[`outline-${block.type}`, { active: block.id === activeBlockId }]"
      @click="$emit('select', block.id, block.ruleId)"
    >
      <span>{{ block.title }}</span>
    </a>
  </nav>
</template>
