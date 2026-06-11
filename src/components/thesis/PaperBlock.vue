<script setup lang="ts">
import type { ThesisBlock } from '../../types/thesis';

defineProps<{
  block: ThesisBlock;
  active: boolean;
  changed: boolean;
}>();

defineEmits<{
  select: [];
}>();
</script>

<template>
  <section
    :id="block.id"
    class="paper-block"
    :class="[`paper-${block.type}`, block.level ? `level-${block.level}` : '', { active }]"
    tabindex="0"
    @mouseenter="$emit('select')"
    @focus="$emit('select')"
    @click="$emit('select')"
  >
    <span v-if="changed" class="block-change-badge">本版变更</span>

    <template v-if="block.type === 'cover'">
      <p class="school-name">示例大学本科毕业论文</p>
      <h2>{{ block.content[0] }}</h2>
      <p v-for="line in block.content.slice(1)" :key="line" class="cover-line">{{ line }}</p>
    </template>

    <template v-else-if="block.type === 'toc'">
      <h2>{{ block.title }}</h2>
      <p v-for="line in block.content" :key="line" class="toc-line">{{ line }}</p>
    </template>

    <template v-else-if="block.type === 'figure'">
      <div class="figure-box">{{ block.content[0] }}</div>
      <p class="caption">{{ block.title }}</p>
    </template>

    <template v-else-if="block.type === 'table'">
      <p class="caption table-caption">{{ block.title }}</p>
      <div class="sample-table">
        <span v-for="cell in block.content[0].split(' | ')" :key="cell">{{ cell }}</span>
      </div>
    </template>

    <template v-else-if="block.type === 'formula'">
      <p class="formula-line">{{ block.content[0] }}</p>
    </template>

    <template v-else>
      <component :is="block.level === 1 ? 'h2' : block.level === 2 ? 'h3' : block.level === 3 ? 'h4' : 'h2'">
        {{ block.title }}
      </component>
      <p v-for="line in block.content" :key="line">{{ line }}</p>
    </template>
  </section>
</template>
