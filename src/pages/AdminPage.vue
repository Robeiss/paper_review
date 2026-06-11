<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  createAdminRule,
  createAdminVersion,
  deleteAdminRule,
  fetchAdminRules,
  fetchAdminVersions,
  fetchAuditLogs,
  publishAdminVersion,
  saveAdminRule,
} from '../services/adminService';
import type { AuthSession, RuleVersion, ThesisRule } from '../types/thesis';

const props = defineProps<{
  session: AuthSession;
}>();

defineEmits<{
  logout: [];
}>();

const rules = ref<ThesisRule[]>([]);
const versions = ref<Array<RuleVersion & { status?: string }>>([]);
const logs = ref<Array<Record<string, string | number>>>([]);
const activeRuleId = ref('');
const message = ref('');
const error = ref('');

const ruleForm = ref<ThesisRule>(emptyRule());
const specsText = ref('[]');
const notesText = ref('[]');
const mistakesText = ref('[]');
const versionForm = ref<RuleVersion & { status: string }>({
  id: '',
  name: '',
  publishedAt: new Date().toISOString().slice(0, 10),
  source: '教务处格式通知',
  status: 'draft',
  changes: [],
});
const versionChangesText = ref('[]');

const selectedRule = computed(() => rules.value.find((rule) => rule.id === activeRuleId.value));

function emptyRule(): ThesisRule {
  return {
    id: '',
    name: '',
    summary: '',
    specs: [{ label: '字体', value: '小四宋体' }],
    notes: [],
    commonMistakes: [],
    severity: 'normal',
    updatedAt: new Date().toISOString().slice(0, 10),
  };
}

function setRuleForm(rule: ThesisRule) {
  activeRuleId.value = rule.id;
  ruleForm.value = JSON.parse(JSON.stringify(rule)) as ThesisRule;
  specsText.value = JSON.stringify(rule.specs, null, 2);
  notesText.value = JSON.stringify(rule.notes, null, 2);
  mistakesText.value = JSON.stringify(rule.commonMistakes, null, 2);
}

function newRule() {
  activeRuleId.value = '';
  setRuleForm(emptyRule());
}

async function loadAdminData() {
  [rules.value, versions.value, logs.value] = await Promise.all([
    fetchAdminRules(props.session.token),
    fetchAdminVersions(props.session.token),
    fetchAuditLogs(props.session.token),
  ]);
  if (!activeRuleId.value && rules.value[0]) {
    setRuleForm(rules.value[0]);
  }
}

function parseFormJson() {
  ruleForm.value.specs = JSON.parse(specsText.value);
  ruleForm.value.notes = JSON.parse(notesText.value);
  ruleForm.value.commonMistakes = JSON.parse(mistakesText.value);
}

async function saveRule() {
  message.value = '';
  error.value = '';
  try {
    parseFormJson();
    if (selectedRule.value) {
      await saveAdminRule(props.session.token, ruleForm.value);
      message.value = '规则已保存';
    } else {
      await createAdminRule(props.session.token, ruleForm.value);
      message.value = '规则已创建';
    }
    await loadAdminData();
    setRuleForm(ruleForm.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败，请检查 JSON 格式';
  }
}

async function removeRule() {
  if (!selectedRule.value) return;
  message.value = '';
  error.value = '';
  try {
    await deleteAdminRule(props.session.token, selectedRule.value.id);
    message.value = '规则已删除';
    activeRuleId.value = '';
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败';
  }
}

async function createVersion() {
  message.value = '';
  error.value = '';
  try {
    versionForm.value.changes = JSON.parse(versionChangesText.value);
    await createAdminVersion(props.session.token, versionForm.value);
    message.value = '版本草稿已创建';
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建版本失败';
  }
}

async function publishVersion(versionId: string) {
  message.value = '';
  error.value = '';
  try {
    await publishAdminVersion(props.session.token, versionId);
    message.value = '版本已发布';
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发布失败';
  }
}

onMounted(loadAdminData);
</script>

<template>
  <main class="admin-shell">
    <header class="admin-topbar">
      <div>
        <h1>后台管理</h1>
        <p>{{ session.user.name }} · {{ session.user.account }}</p>
      </div>
      <button type="button" @click="$emit('logout')">退出</button>
    </header>

    <section class="admin-grid">
      <aside class="admin-list">
        <div class="admin-section-title">
          <h2>规则</h2>
          <button type="button" @click="newRule">新增</button>
        </div>
        <button
          v-for="rule in rules"
          :key="rule.id"
          type="button"
          class="admin-rule-item"
          :class="{ active: rule.id === activeRuleId }"
          @click="setRuleForm(rule)"
        >
          <strong>{{ rule.name }}</strong>
          <span>{{ rule.id }}</span>
        </button>
      </aside>

      <section class="admin-editor">
        <div class="admin-section-title">
          <h2>{{ selectedRule ? '编辑规则' : '新增规则' }}</h2>
          <div class="admin-actions">
            <button type="button" @click="saveRule">保存</button>
            <button type="button" class="danger" :disabled="!selectedRule" @click="removeRule">删除</button>
          </div>
        </div>

        <p v-if="message" class="admin-message">{{ message }}</p>
        <p v-if="error" class="admin-error">{{ error }}</p>

        <div class="form-grid">
          <label>
            <span>规则 ID</span>
            <input v-model="ruleForm.id" :disabled="Boolean(selectedRule)" />
          </label>
          <label>
            <span>名称</span>
            <input v-model="ruleForm.name" />
          </label>
          <label>
            <span>级别</span>
            <select v-model="ruleForm.severity">
              <option value="normal">常规</option>
              <option value="important">关注</option>
              <option value="critical">重点</option>
            </select>
          </label>
          <label>
            <span>更新日期</span>
            <input v-model="ruleForm.updatedAt" />
          </label>
        </div>

        <label class="wide-field">
          <span>摘要</span>
          <textarea v-model="ruleForm.summary" rows="3"></textarea>
        </label>

        <div class="json-grid">
          <label>
            <span>格式项 JSON</span>
            <textarea v-model="specsText" rows="9"></textarea>
          </label>
          <label>
            <span>要求说明 JSON</span>
            <textarea v-model="notesText" rows="9"></textarea>
          </label>
          <label>
            <span>常见错误 JSON</span>
            <textarea v-model="mistakesText" rows="9"></textarea>
          </label>
        </div>
      </section>

      <aside class="admin-side">
        <section class="admin-card">
          <h2>版本发布</h2>
          <label>
            <span>版本 ID</span>
            <input v-model="versionForm.id" placeholder="2026-undergraduate-v2" />
          </label>
          <label>
            <span>版本名称</span>
            <input v-model="versionForm.name" />
          </label>
          <label>
            <span>发布日期</span>
            <input v-model="versionForm.publishedAt" />
          </label>
          <label>
            <span>来源</span>
            <input v-model="versionForm.source" />
          </label>
          <label>
            <span>变更说明 JSON</span>
            <textarea v-model="versionChangesText" rows="5"></textarea>
          </label>
          <button type="button" @click="createVersion">创建草稿</button>

          <div class="version-list">
            <div v-for="version in versions" :key="version.id" class="version-row">
              <div>
                <strong>{{ version.name }}</strong>
                <span>{{ version.status }} · {{ version.publishedAt }}</span>
              </div>
              <button v-if="version.status !== 'published'" type="button" @click="publishVersion(version.id)">发布</button>
            </div>
          </div>
        </section>

        <section class="admin-card">
          <h2>更新日志</h2>
          <div class="audit-list">
            <div v-for="log in logs" :key="log.id" class="audit-row">
              <strong>{{ log.action }}</strong>
              <span>{{ log.actor }} · {{ log.target }}</span>
              <small>{{ log.created_at }}</small>
            </div>
          </div>
        </section>
      </aside>
    </section>
  </main>
</template>
